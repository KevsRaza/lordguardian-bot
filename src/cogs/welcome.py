"""
Cog pour les messages de bienvenue et départ
"""
import discord
from discord import app_commands
from discord.ext import commands
from core.logger import setup_logger
from core.embeds import Embeds  # ← AJOUT

logger = setup_logger("Welcome")

class Welcome(commands.Cog):
    """Gestion des messages de bienvenue"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Événement déclenché quand un membre rejoint le serveur"""
        try:
            # S'assurer que la DB est connectée
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                # Récupérer la configuration du serveur
                await cursor.execute(
                    "SELECT welcome_channel_id, welcome_message, auto_role_id FROM guilds WHERE guild_id = ?",
                    (member.guild.id,)
                )
                result = await cursor.fetchone()
                
                if not result or not result[0]:  # welcome_channel_id
                    return
                
                welcome_channel_id, welcome_message, auto_role_id = result
                
                # Trouver le canal
                channel = member.guild.get_channel(welcome_channel_id)
                if not channel:
                    return
                
                # Préparer le message personnalisé
                custom_message = None
                if welcome_message:
                    custom_message = welcome_message.replace("{user}", member.mention)
                    custom_message = custom_message.replace("{server}", member.guild.name)
                    custom_message = custom_message.replace("{count}", str(member.guild.member_count))
                
                # ← UTILISER L'EMBED STANDARDISÉ
                embed = Embeds.welcome(member, member.guild, custom_message)
                
                await channel.send(embed=embed)
                
                # Auto-role si configuré
                if auto_role_id:
                    role = member.guild.get_role(auto_role_id)
                    if role:
                        await member.add_roles(role)
                        logger.info(f"Rôle automatique donné à {member.name}")
                        
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message de bienvenue: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Événement déclenché quand un membre quitte le serveur"""
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT welcome_channel_id, leave_message FROM guilds WHERE guild_id = ?",
                    (member.guild.id,)
                )
                result = await cursor.fetchone()
                
                if not result or not result[0]:  # welcome_channel_id
                    return
                
                welcome_channel_id, leave_message = result
                
                channel = member.guild.get_channel(welcome_channel_id)
                if not channel:
                    return
                
                # Préparer le message personnalisé
                custom_message = None
                if leave_message:
                    custom_message = leave_message.replace("{user}", member.name)
                    custom_message = custom_message.replace("{server}", member.guild.name)
                
                # ← UTILISER L'EMBED STANDARDISÉ
                embed = Embeds.goodbye(member, member.guild, custom_message)
                
                await channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message de départ: {e}")
    
    @app_commands.command(name="setwelcome", description="Configure le canal de bienvenue")
    @app_commands.describe(channel="Le canal pour les messages de bienvenue")
    @app_commands.default_permissions(administrator=True)
    async def set_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Définit le canal de bienvenue"""
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                # Vérifier si le serveur existe déjà
                await cursor.execute("SELECT guild_id FROM guilds WHERE guild_id = ?", (interaction.guild_id,))
                existing = await cursor.fetchone()
                
                if existing:
                    # Mettre à jour
                    await cursor.execute(
                        "UPDATE guilds SET welcome_channel_id = ? WHERE guild_id = ?",
                        (channel.id, interaction.guild_id)
                    )
                else:
                    # Insérer nouveau
                    await cursor.execute(
                        "INSERT INTO guilds (guild_id, welcome_channel_id) VALUES (?, ?)",
                        (interaction.guild_id, channel.id)
                    )
                
                await self.bot.db.connection.commit()
            
            # ← UTILISER L'EMBED STANDARDISÉ
            embed = Embeds.success(
                "Canal de bienvenue configuré",
                f"Les messages de bienvenue seront envoyés dans {channel.mention}"
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur set_welcome: {e}")
            # ← UTILISER L'EMBED STANDARDISÉ
            embed = Embeds.error(
                "Erreur de configuration",
                f"Impossible de configurer le canal: {str(e)[:100]}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="welcomemsg", description="Personnalise le message de bienvenue")
    @app_commands.describe(message="Message personnalisé (utilisez {user}, {server}, {count})")
    @app_commands.default_permissions(administrator=True)
    async def welcome_message(self, interaction: discord.Interaction, message: str):
        """Définit le message de bienvenue personnalisé"""
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                # Vérifier si le serveur existe
                await cursor.execute("SELECT guild_id FROM guilds WHERE guild_id = ?", (interaction.guild_id,))
                existing = await cursor.fetchone()
                
                if existing:
                    # Mettre à jour
                    await cursor.execute(
                        "UPDATE guilds SET welcome_message = ? WHERE guild_id = ?",
                        (message, interaction.guild_id)
                    )
                else:
                    # Insérer nouveau
                    await cursor.execute(
                        "INSERT INTO guilds (guild_id, welcome_message) VALUES (?, ?)",
                        (interaction.guild_id, message)
                    )
                
                await self.bot.db.connection.commit()
            
            # Aperçu du message
            preview = message.replace("{user}", interaction.user.mention)
            preview = preview.replace("{server}", interaction.guild.name)
            preview = preview.replace("{count}", str(interaction.guild.member_count))
            
            # ← UTILISER L'EMBED STANDARDISÉ
            embed = Embeds.success(
                "Message de bienvenue configuré",
                f"**Aperçu du message :**\n{preview}"
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur welcome_message: {e}")
            # ← UTILISER L'EMBED STANDARDISÉ
            embed = Embeds.error(
                "Erreur de configuration",
                f"Impossible de configurer le message: {str(e)[:100]}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="setleavemsg", description="Configure le message de départ")
    @app_commands.describe(message="Message personnalisé (utilisez {user}, {server})")
    @app_commands.default_permissions(administrator=True)
    async def set_leave_message(self, interaction: discord.Interaction, message: str):
        """Définit le message de départ personnalisé"""
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                await cursor.execute("SELECT guild_id FROM guilds WHERE guild_id = ?", (interaction.guild_id,))
                existing = await cursor.fetchone()
                
                if existing:
                    await cursor.execute(
                        "UPDATE guilds SET leave_message = ? WHERE guild_id = ?",
                        (message, interaction.guild_id)
                    )
                else:
                    await cursor.execute(
                        "INSERT INTO guilds (guild_id, leave_message) VALUES (?, ?)",
                        (interaction.guild_id, message)
                    )
                
                await self.bot.db.connection.commit()
            
            # Aperçu du message
            preview = message.replace("{user}", interaction.user.name)
            preview = preview.replace("{server}", interaction.guild.name)
            
            # ← UTILISER L'EMBED STANDARDISÉ
            embed = Embeds.success(
                "Message de départ configuré",
                f"**Aperçu du message :**\n{preview}"
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur set_leave_message: {e}")
            # ← UTILISER L'EMBED STANDARDISÉ
            embed = Embeds.error(
                "Erreur de configuration",
                f"Impossible de configurer le message: {str(e)[:100]}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Welcome(bot))