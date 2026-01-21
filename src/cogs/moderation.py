"""
Cog de modération pour le bot
"""
import discord
from discord.ext import commands
from discord import app_commands
from core.logger import setup_logger
from core.embeds import Embeds  # ← AJOUT
from utils.helpers import format_time
import asyncio

logger = setup_logger("Moderation")

class Moderation(commands.Cog):
    """Commandes de modération"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 10):
        """
        Supprime un nombre de messages
        
        Usage: !clear [nombre=10]
        """
        if amount < 1 or amount > 100:
            embed = Embeds.error(
                "Nombre invalide",
                "Le nombre doit être entre 1 et 100."
            )
            await ctx.send(embed=embed, delete_after=5)
            return
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        embed = Embeds.success(
            "Messages supprimés",
            f"**{len(deleted) - 1}** messages ont été supprimés."
        )
        message = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await message.delete()
    
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_member(self, ctx, member: discord.Member, *, reason: str = "Aucune raison donnée"):
        """
        Expulse un membre du serveur
        
        Usage: !kick @membre [raison]
        """
        if member == ctx.author:
            embed = Embeds.error(
                "Action impossible",
                "Vous ne pouvez pas vous expulser vous-même."
            )
            await ctx.send(embed=embed)
            return
        
        if member == ctx.guild.me:
            embed = Embeds.error(
                "Action impossible",
                "Je ne peux pas m'expulser moi-même."
            )
            await ctx.send(embed=embed)
            return
        
        # Vérifier la hiérarchie
        if ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner:
            embed = Embeds.error(
                "Permission insuffisante",
                "Vous ne pouvez pas expulser quelqu'un avec un rôle égal ou supérieur."
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.kick(reason=f"{ctx.author}: {reason}")
            
            embed = Embeds.create_base_embed(
                title="👢 Membre expulsé",
                description=f"{member.mention} a été expulsé du serveur.",
                color=Embeds.EmbedColors.WARNING
            )
            embed.add_field(name="👤 Membre", value=f"{member.name}#{member.discriminator}", inline=True)
            embed.add_field(name="🛡️ Modérateur", value=ctx.author.mention, inline=True)
            embed.add_field(name="📝 Raison", value=reason, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            
            await ctx.send(embed=embed)
            logger.info(f"{member} expulsé par {ctx.author} - Raison: {reason}")
            
        except discord.Forbidden:
            embed = Embeds.error(
                "Permission insuffisante",
                "Je n'ai pas la permission d'expulser ce membre."
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="ban", help="Bannir un membre")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Aucune raison donnée"):
        """Bannit un membre du serveur"""
        
        # Vérifications de base
        if not ctx.guild.me.guild_permissions.ban_members:
            embed = Embeds.error(
                "Permission manquante",
                "Je n'ai pas la permission de bannir des membres."
            )
            await ctx.send(embed=embed)
            return
        
        if member == ctx.author:
            embed = Embeds.error(
                "Action impossible",
                "Vous ne pouvez pas vous bannir vous-même."
            )
            await ctx.send(embed=embed)
            return
        
        if member == ctx.guild.me:
            embed = Embeds.error(
                "Action impossible",
                "Je ne peux pas me bannir moi-même."
            )
            await ctx.send(embed=embed)
            return
        
        # Vérifier la hiérarchie des rôles
        if ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner:
            embed = Embeds.error(
                "Permission insuffisante",
                "Vous ne pouvez pas bannir quelqu'un avec un rôle égal ou supérieur."
            )
            await ctx.send(embed=embed)
            return
        
        # Exécuter le ban
        try:
            await member.ban(reason=f"{ctx.author}: {reason}", delete_message_days=1)
            
            embed = Embeds.create_base_embed(
                title="🔨 Membre banni",
                description=f"{member.mention} a été banni du serveur.",
                color=Embeds.EmbedColors.ERROR
            )
            embed.add_field(name="👤 Membre", value=f"{member.name}#{member.discriminator}", inline=True)
            embed.add_field(name="🛡️ Modérateur", value=ctx.author.mention, inline=True)
            embed.add_field(name="📝 Raison", value=reason, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            
            await ctx.send(embed=embed)
            logger.info(f"{member} banni par {ctx.author} - Raison: {reason}")
            
        except discord.Forbidden:
            embed = Embeds.error(
                "Permission insuffisante",
                "Je n'ai pas les permissions pour bannir ce membre."
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = Embeds.error(
                "Erreur",
                f"Une erreur est survenue: {str(e)[:200]}"
            )
            await ctx.send(embed=embed)
            logger.error(f"Erreur ban: {e}")
    
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_member(self, ctx, *, user_input: str):
        """
        Débannit un utilisateur
        
        Usage: !unban nom#tag ou ID
        """
        try:
            banned_users = [entry async for entry in ctx.guild.bans()]
        except discord.Forbidden:
            embed = Embeds.error(
                "Permission manquante",
                "Je n'ai pas la permission de voir la liste des bannis."
            )
            await ctx.send(embed=embed)
            return
        
        for ban_entry in banned_users:
            user = ban_entry.user
            
            if str(user.id) == user_input or f"{user.name}#{user.discriminator}" == user_input or user.name == user_input:
                await ctx.guild.unban(user)
                
                embed = Embeds.success(
                    "Membre débanni",
                    f"**{user.name}#{user.discriminator}** a été débanni."
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                await ctx.send(embed=embed)
                logger.info(f"{user} débanni par {ctx.author}")
                return
        
        embed = Embeds.error(
            "Utilisateur introuvable",
            f"Aucun utilisateur banni trouvé avec l'identifiant `{user_input}`."
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute_member(self, ctx, member: discord.Member, duration: str = "10m", *, reason: str = "Aucune raison donnée"):
        """
        Rend muet un membre temporairement
        
        Usage: !mute @membre [durée=10m] [raison]
        Formats de durée: 10s, 5m, 2h, 1d
        """
        # Recherche ou création du rôle "Muted"
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role:
            try:
                muted_role = await ctx.guild.create_role(
                    name="Muted",
                    color=discord.Color.dark_grey(),
                    reason="Création automatique du rôle Muted"
                )
                
                # Enlever les permissions d'écriture dans tous les salons
                for channel in ctx.guild.channels:
                    await channel.set_permissions(
                        muted_role,
                        send_messages=False,
                        speak=False,
                        add_reactions=False
                    )
                
                logger.info(f"Rôle Muted créé dans {ctx.guild.name}")
                
            except discord.Forbidden:
                embed = Embeds.error(
                    "Permission manquante",
                    "Je n'ai pas la permission de créer le rôle Muted."
                )
                await ctx.send(embed=embed)
                return
        
        # Vérifier si déjà mute
        if muted_role in member.roles:
            embed = Embeds.warning(
                "Membre déjà muet",
                f"{member.mention} est déjà rendu muet."
            )
            await ctx.send(embed=embed)
            return
        
        # Convertir la durée
        duration_seconds = self.parse_duration(duration)
        if duration_seconds is None:
            embed = Embeds.error(
                "Format de durée invalide",
                "Exemples valides: `10s`, `5m`, `2h`, `1d`"
            )
            await ctx.send(embed=embed)
            return
        
        await member.add_roles(muted_role, reason=f"{ctx.author}: {reason}")
        
        embed = Embeds.create_base_embed(
            title="🔇 Membre rendu muet",
            description=f"{member.mention} ne peut plus parler temporairement.",
            color=Embeds.EmbedColors.WARNING
        )
        embed.add_field(name="👤 Membre", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="⏱️ Durée", value=format_time(duration_seconds), inline=True)
        embed.add_field(name="📝 Raison", value=reason, inline=False)
        embed.set_footer(text=f"Par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
        logger.info(f"{member} rendu muet par {ctx.author} pour {duration} - Raison: {reason}")
        
        # Planifier le démute
        await asyncio.sleep(duration_seconds)
        try:
            await member.remove_roles(muted_role)
            logger.info(f"{member} automatiquement démute après {duration}")
        except:
            pass
    
    def parse_duration(self, duration: str) -> int | None:
        """Convertit une durée textuelle en secondes"""
        try:
            if duration.endswith('s'):
                return int(duration[:-1])
            elif duration.endswith('m'):
                return int(duration[:-1]) * 60
            elif duration.endswith('h'):
                return int(duration[:-1]) * 3600
            elif duration.endswith('d'):
                return int(duration[:-1]) * 86400
            else:
                return int(duration) * 60  # Par défaut minutes
        except ValueError:
            return None
    
    @commands.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute_member(self, ctx, member: discord.Member):
        """Démute un membre"""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role or muted_role not in member.roles:
            embed = Embeds.warning(
                "Membre non muet",
                f"{member.mention} n'est pas rendu muet."
            )
            await ctx.send(embed=embed)
            return
        
        await member.remove_roles(muted_role)
        
        embed = Embeds.success(
            "Membre démute",
            f"{member.mention} peut de nouveau parler."
        )
        await ctx.send(embed=embed)
        logger.info(f"{member} démute par {ctx.author}")
    
    @commands.command(name="warn")
    @commands.has_permissions(kick_members=True)
    async def warn_member(self, ctx, member: discord.Member, *, reason: str):
        """
        Avertit un membre
        
        Usage: !warn @membre [raison]
        """
        # Message privé au membre
        dm_embed = Embeds.create_base_embed(
            title="⚠️ Avertissement",
            description=f"Vous avez reçu un avertissement sur **{ctx.guild.name}**.",
            color=Embeds.EmbedColors.WARNING
        )
        dm_embed.add_field(name="📝 Raison", value=reason, inline=False)
        dm_embed.add_field(name="🛡️ Modérateur", value=ctx.author.mention, inline=True)
        dm_embed.set_footer(text="Les avertissements répétés peuvent mener à des sanctions plus sévères")
        
        # Message dans le salon
        public_embed = Embeds.create_base_embed(
            title="⚠️ Avertissement émis",
            description=f"{member.mention} a reçu un avertissement.",
            color=Embeds.EmbedColors.WARNING
        )
        public_embed.add_field(name="📝 Raison", value=reason, inline=False)
        public_embed.add_field(name="🛡️ Modérateur", value=ctx.author.mention, inline=True)
        
        try:
            await member.send(embed=dm_embed)
            await ctx.send(embed=public_embed)
            logger.info(f"{member} averti par {ctx.author} - Raison: {reason}")
        except discord.Forbidden:
            public_embed.set_footer(text="⚠️ Impossible d'envoyer un MP au membre (MPs désactivés)")
            await ctx.send(embed=public_embed)
            logger.info(f"{member} averti par {ctx.author} (MP échoué) - Raison: {reason}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))