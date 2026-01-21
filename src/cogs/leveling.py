"""
Système de niveaux et d'XP
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import random
from core.logger import setup_logger

logger = setup_logger("Leveling")

class Leveling(commands.Cog):
    """Système de leveling basé sur l'activité"""
    
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldown = {}
    
    def calculate_level(self, xp: int) -> int:
        """Calcule le niveau en fonction de l'XP"""
        return int((xp / 100) ** 0.5)
    
    def xp_for_level(self, level: int) -> int:
        """Calcule l'XP nécessaire pour un niveau"""
        return (level ** 2) * 100
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Donne de l'XP pour chaque message"""
        if message.author.bot or not message.guild:
            return
        
        # Cooldown de 5 secondes entre chaque gain d'XP
        user_key = f"{message.author.id}_{message.guild.id}"
        now = datetime.utcnow()
        
        if user_key in self.xp_cooldown:
            if now - self.xp_cooldown[user_key] < timedelta(seconds=5):
                return
        
        self.xp_cooldown[user_key] = now
        
        # Gain d'XP aléatoire entre 10 et 20
        xp_gain = random.randint(10, 20)
        
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                # Vérifier si l'utilisateur existe déjà
                await cursor.execute(
                    "SELECT xp, level, messages FROM users WHERE user_id = ? AND guild_id = ?",
                    (message.author.id, message.guild.id)
                )
                result = await cursor.fetchone()
                
                if not result:
                    # Créer un nouvel utilisateur
                    await cursor.execute(
                        """INSERT INTO users 
                        (user_id, guild_id, xp, level, messages, created_at) 
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (message.author.id, message.guild.id, xp_gain, 0, 1, now)
                    )
                    old_level = 0
                    new_xp = xp_gain
                    messages_count = 1
                else:
                    old_xp, old_level, messages_count = result
                    new_xp = old_xp + xp_gain
                    messages_count += 1
                    
                    # Mettre à jour l'utilisateur
                    await cursor.execute(
                        """UPDATE users 
                        SET xp = ?, messages = ?, last_message = ? 
                        WHERE user_id = ? AND guild_id = ?""",
                        (new_xp, messages_count, now, message.author.id, message.guild.id)
                    )
                
                # Vérifier si le niveau a augmenté
                new_level = self.calculate_level(new_xp)
                if new_level > old_level:
                    # Mettre à jour le niveau
                    await cursor.execute(
                        "UPDATE users SET level = ? WHERE user_id = ? AND guild_id = ?",
                        (new_level, message.author.id, message.guild.id)
                    )
                    
                    # Envoyer le message de level up
                    await self.send_levelup_message(message, new_level)
                
                await self.bot.db.connection.commit()
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message pour l'XP: {e}")
    
    async def send_levelup_message(self, message: discord.Message, level: int):
        """Envoie un message de montée de niveau"""
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                # Chercher un canal personnalisé pour les level up
                await cursor.execute(
                    "SELECT level_up_channel_id FROM guilds WHERE guild_id = ?",
                    (message.guild.id,)
                )
                result = await cursor.fetchone()
                
                embed = discord.Embed(
                    title="🎉 Level Up!",
                    description=f"{message.author.mention} vient d'atteindre le **niveau {level}** !",
                    color=discord.Color.gold()
                )
                embed.set_thumbnail(url=message.author.display_avatar.url)
                
                # Canal personnalisé ou canal actuel
                channel = message.channel
                if result and result[0]:  # level_up_channel_id
                    custom_channel = message.guild.get_channel(result[0])
                    if custom_channel:
                        channel = custom_channel
                
                await channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message de level up: {e}")
    
    @app_commands.command(name="rank", description="Affiche ton niveau et XP")
    @app_commands.describe(user="L'utilisateur dont voir le niveau")
    async def rank(self, interaction: discord.Interaction, user: discord.Member = None):
        """Affiche le niveau d'un utilisateur"""
        target = user or interaction.user
        
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT xp, level, messages FROM users WHERE user_id = ? AND guild_id = ?",
                    (target.id, interaction.guild_id)
                )
                result = await cursor.fetchone()
                
                if not result:
                    await interaction.response.send_message(
                        f"{target.mention} n'a pas encore d'XP sur ce serveur.",
                        ephemeral=True
                    )
                    return
                
                xp, level, messages = result
                
                current_level_xp = self.xp_for_level(level)
                next_level_xp = self.xp_for_level(level + 1)
                xp_needed = next_level_xp - xp if xp < next_level_xp else 0
                
                if next_level_xp - current_level_xp > 0:
                    progress = ((xp - current_level_xp) / (next_level_xp - current_level_xp)) * 100
                    progress = min(progress, 100)
                else:
                    progress = 100
                
                # Barre de progression
                filled = int(progress // 5)
                empty = 20 - filled
                progress_bar = "█" * filled + "░" * empty
                
                embed = discord.Embed(
                    title=f"📊 Niveau de {target.display_name}",
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=target.display_avatar.url)
                embed.add_field(name="Niveau", value=f"**{level}**", inline=True)
                embed.add_field(name="XP Total", value=f"**{xp:,}**", inline=True)
                embed.add_field(name="Messages", value=f"**{messages:,}**", inline=True)
                embed.add_field(
                    name="Progression",
                    value=f"{progress_bar} {progress:.1f}%\n"
                          f"**{xp_needed:,}** XP jusqu'au niveau {level + 1}",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            logger.error(f"Erreur rank command: {e}")
            await interaction.response.send_message(
                f"❌ Erreur: {str(e)[:100]}",
                ephemeral=True
            )
    
    @app_commands.command(name="leaderboard", description="Affiche le classement du serveur")
    async def leaderboard(self, interaction: discord.Interaction):
        """Affiche le top 10 des utilisateurs"""
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT user_id, xp, level 
                    FROM users 
                    WHERE guild_id = ? 
                    ORDER BY xp DESC 
                    LIMIT 10""",
                    (interaction.guild_id,)
                )
                results = await cursor.fetchall()
                
                if not results:
                    await interaction.response.send_message(
                        "Aucun utilisateur n'a encore d'XP sur ce serveur.",
                        ephemeral=True
                    )
                    return
                
                embed = discord.Embed(
                    title=f"🏆 Classement de {interaction.guild.name}",
                    color=discord.Color.gold()
                )
                
                medals = ["🥇", "🥈", "🥉"]
                for i, row in enumerate(results, 1):
                    user_id, xp, level = row
                    member = interaction.guild.get_member(user_id)
                    
                    if member:
                        medal = medals[i-1] if i <= 3 else f"#{i}"
                        embed.add_field(
                            name=f"{medal} {member.display_name}",
                            value=f"Niveau: **{level}** | XP: **{xp:,}**",
                            inline=False
                        )
                
                await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            logger.error(f"Erreur leaderboard command: {e}")
            await interaction.response.send_message(
                f"❌ Erreur: {str(e)[:100]}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Leveling(bot))