"""
Générateur d'embeds pour GuildGreeter
"""
import discord
from datetime import datetime
from typing import Optional

class EmbedColors:
    """Couleurs standards pour les embeds"""
    SUCCESS = 0x00FF00  # Vert
    ERROR = 0xFF0000    # Rouge
    WARNING = 0xFFA500  # Orange
    INFO = 0x3498DB     # Bleu
    WELCOME = 0x9B59B6  # Violet
    GOODBYE = 0x95A5A6  # Gris

class Embeds:
    """Générateur d'embeds standardisés"""
    
    # Exposer les couleurs pour un accès facile
    EmbedColors = EmbedColors
    
    @staticmethod
    def create_base_embed(
        title: str,
        description: str,
        color: int,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None
    ) -> discord.Embed:
        """Crée un embed de base avec les paramètres standards"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if image:
            embed.set_image(url=image)
            
        return embed
    
    @staticmethod
    def success(title: str, description: str) -> discord.Embed:
        """Embed de succès"""
        return Embeds.create_base_embed(
            title=f"✅ {title}",
            description=description,
            color=EmbedColors.SUCCESS
        )
    
    @staticmethod
    def error(title: str, description: str) -> discord.Embed:
        """Embed d'erreur"""
        return Embeds.create_base_embed(
            title=f"❌ {title}",
            description=description,
            color=EmbedColors.ERROR
        )
    
    @staticmethod
    def warning(title: str, description: str) -> discord.Embed:
        """Embed d'avertissement"""
        return Embeds.create_base_embed(
            title=f"⚠️ {title}",
            description=description,
            color=EmbedColors.WARNING
        )
    
    @staticmethod
    def info(title: str, description: str) -> discord.Embed:
        """Embed d'information"""
        return Embeds.create_base_embed(
            title=f"ℹ️ {title}",
            description=description,
            color=EmbedColors.INFO
        )
    
    @staticmethod
    def welcome(member: discord.Member, guild: discord.Guild, custom_message: Optional[str] = None) -> discord.Embed:
        """Embed de bienvenue pour un nouveau membre"""
        description = custom_message or f"Bienvenue sur **{guild.name}** !\n\nNous sommes maintenant **{guild.member_count}** membres 🎉"
        
        embed = discord.Embed(
            title=f"👋 Bienvenue {member.name} !",
            description=description,
            color=EmbedColors.WELCOME,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Membre #{guild.member_count}")
        
        return embed
    
    @staticmethod
    def goodbye(member: discord.Member, guild: discord.Guild, custom_message: Optional[str] = None) -> discord.Embed:
        """Embed d'au revoir pour un membre qui part"""
        description = custom_message or f"**{member.name}** vient de quitter le serveur.\n\nNous sommes maintenant **{guild.member_count}** membres."
        
        embed = discord.Embed(
            title="👋 Au revoir !",
            description=description,
            color=EmbedColors.GOODBYE,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Restants: {guild.member_count} membres")
        
        return embed
    
    @staticmethod
    def member_info(member: discord.Member) -> discord.Embed:
        """Embed d'informations sur un membre"""
        embed = discord.Embed(
            title=f"📋 Informations sur {member.display_name}",
            color=member.color if member.color != discord.Color.default() else EmbedColors.INFO,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Nom d'utilisateur
        username = f"{member.name}#{member.discriminator}" if member.discriminator != "0" else member.name
        embed.add_field(
            name="👤 Nom d'utilisateur",
            value=username,
            inline=True
        )
        
        # ID
        embed.add_field(
            name="🆔 ID",
            value=f"`{member.id}`",
            inline=True
        )
        
        # Statut
        status_emojis = {
            discord.Status.online: "🟢 En ligne",
            discord.Status.idle: "🟡 Inactif", 
            discord.Status.dnd: "🔴 Ne pas déranger",
            discord.Status.offline: "⚫ Hors ligne"
        }
        embed.add_field(
            name="📱 Statut",
            value=status_emojis.get(member.status, "❓ Inconnu"),
            inline=True
        )
        
        # Compte créé le
        embed.add_field(
            name="📅 Compte créé le",
            value=f"<t:{int(member.created_at.timestamp())}:F>\n(<t:{int(member.created_at.timestamp())}:R>)",
            inline=False
        )
        
        # A rejoint le
        if member.joined_at:
            embed.add_field(
                name="📥 A rejoint le",
                value=f"<t:{int(member.joined_at.timestamp())}:F>\n(<t:{int(member.joined_at.timestamp())}:R>)",
                inline=False
            )
        
        # Rôles
        if len(member.roles) > 1:  # Ignore @everyone
            roles = " ".join([role.mention for role in sorted(member.roles[1:], reverse=True)])
            # Limiter à 1024 caractères
            if len(roles) > 1024:
                roles = roles[:1020] + "..."
            embed.add_field(
                name=f"🎭 Rôles ({len(member.roles) - 1})",
                value=roles,
                inline=False
            )
        
        # Badges
        flags = member.public_flags
        badges = []
        
        if flags.staff: badges.append("👨‍💼 Staff Discord")
        if flags.partner: badges.append("🤝 Partenaire")
        if flags.hypesquad: badges.append("🏠 HypeSquad Events")
        if flags.bug_hunter: badges.append("🐛 Bug Hunter")
        if flags.bug_hunter_level_2: badges.append("🐛 Bug Hunter Niveau 2")
        if flags.hypesquad_balance: badges.append("⚖️ HypeSquad Balance")
        if flags.hypesquad_bravery: badges.append("⚔️ HypeSquad Bravery")
        if flags.hypesquad_brilliance: badges.append("🎓 HypeSquad Brilliance")
        if flags.early_supporter: badges.append("🔥 Early Supporter")
        if flags.verified_bot_developer: badges.append("🤖 Développeur de Bot Vérifié")
        if flags.active_developer: badges.append("🔨 Développeur Actif")
        
        if badges:
            embed.add_field(name="🏆 Badges", value="\n".join(badges), inline=False)
        
        # Boost
        if member.premium_since:
            embed.add_field(
                name="✨ Boost",
                value=f"Boost depuis <t:{int(member.premium_since.timestamp())}:R>",
                inline=False
            )
        
        return embed
    
    @staticmethod
    def server_info(guild: discord.Guild) -> discord.Embed:
        """Embed d'informations sur le serveur"""
        embed = discord.Embed(
            title=f"📊 Informations sur {guild.name}",
            color=EmbedColors.INFO,
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Propriétaire
        embed.add_field(
            name="👑 Propriétaire",
            value=guild.owner.mention if guild.owner else "Inconnu",
            inline=True
        )
        
        # ID
        embed.add_field(
            name="🆔 ID",
            value=f"`{guild.id}`",
            inline=True
        )
        
        # Région
        embed.add_field(
            name="🌍 Région",
            value=str(guild.preferred_locale).upper(),
            inline=True
        )
        
        # Créé le
        embed.add_field(
            name="📅 Créé le",
            value=f"<t:{int(guild.created_at.timestamp())}:F>\n(<t:{int(guild.created_at.timestamp())}:R>)",
            inline=False
        )
        
        # Membres
        members = guild.members if hasattr(guild, 'members') else []
        online = len([m for m in members if m.status != discord.Status.offline]) if members else 0
        bots = len([m for m in members if m.bot]) if members else 0
        
        embed.add_field(
            name="👥 Membres",
            value=f"**Total:** {guild.member_count}\n**En ligne:** {online}\n**Bots:** {bots}",
            inline=True
        )
        
        # Salons
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📝 Salons",
            value=f"**Textuels:** {text_channels}\n**Vocaux:** {voice_channels}\n**Catégories:** {categories}",
            inline=True
        )
        
        # Rôles
        embed.add_field(
            name="🎭 Rôles",
            value=f"**{len(guild.roles)}** rôles",
            inline=True
        )
        
        # Emojis
        emoji_count = len(guild.emojis)
        emoji_static = len([e for e in guild.emojis if not e.animated])
        emoji_animated = len([e for e in guild.emojis if e.animated])
        
        if emoji_count > 0:
            embed.add_field(
                name="😀 Emojis",
                value=f"**Total:** {emoji_count}\n**Statiques:** {emoji_static}\n**Animés:** {emoji_animated}",
                inline=True
            )
        
        # Boost
        if guild.premium_subscription_count > 0:
            boost_levels = {0: "Aucun", 1: "Niveau 1 🥉", 2: "Niveau 2 🥈", 3: "Niveau 3 🥇"}
            embed.add_field(
                name="✨ Boost",
                value=f"**{boost_levels.get(guild.premium_tier, '?')}**\n{guild.premium_subscription_count} boost(s)",
                inline=True
            )
        
        # Niveau de vérification
        verification_levels = {
            discord.VerificationLevel.none: "Aucune",
            discord.VerificationLevel.low: "Faible",
            discord.VerificationLevel.medium: "Moyen",
            discord.VerificationLevel.high: "Élevé",
            discord.VerificationLevel.highest: "Maximum"
        }
        
        embed.add_field(
            name="🔒 Vérification",
            value=verification_levels.get(guild.verification_level, "Inconnu"),
            inline=True
        )
        
        return embed
    
    @staticmethod
    def help_command(prefix: str = "/") -> discord.Embed:
        """Embed d'aide avec les commandes disponibles"""
        embed = discord.Embed(
            title="📚 Aide - GuildGreeter",
            description="Voici la liste des commandes disponibles :",
            color=EmbedColors.INFO,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👋 Bienvenue",
            value=(
                f"`{prefix}setwelcome` - Configure le salon de bienvenue\n"
                f"`{prefix}welcomemsg` - Personnalise le message de bienvenue\n"
                f"`{prefix}setleavemsg` - Configure le message de départ"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Modération",
            value=(
                f"`{prefix}kick` - Expulse un membre\n"
                f"`{prefix}ban` - Bannit un membre\n"
                f"`{prefix}unban` - Débannit un utilisateur\n"
                f"`{prefix}mute` - Rend muet un membre\n"
                f"`{prefix}unmute` - Démute un membre\n"
                f"`{prefix}warn` - Avertit un membre\n"
                f"`{prefix}clear` - Supprime des messages"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔧 Utilitaires",
            value=(
                f"`{prefix}serverinfo` - Info sur le serveur\n"
                f"`{prefix}userinfo` - Info sur un utilisateur\n"
                f"`{prefix}avatar` - Affiche l'avatar d'un membre\n"
                f"`{prefix}ping` - Latence du bot\n"
                f"`{prefix}poll` - Crée un sondage"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Administration",
            value=(
                f"`{prefix}reload` - Recharge un cog\n"
                f"`{prefix}sync` - Synchronise les commandes\n"
                f"`{prefix}guilds` - Liste des serveurs"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔗 Liens utiles",
            value="[Support](https://discord.gg/votre-serveur) • [Documentation](https://github.com/votre-repo)",
            inline=False
        )
        
        embed.set_footer(text="GuildGreeter • Bot de bienvenue et modération")
        
        return embed