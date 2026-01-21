"""
Gestionnaire d'événements Discord
"""
import discord
from discord.ext import commands
from core.logger import get_logger
from core.embeds import Embeds  # ← Ajout

logger = get_logger(__name__)

class Events(commands.Cog):
    """Gère les événements Discord"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Événement déclenché quand un membre rejoint"""
        try:
            # Récupérer la config du serveur
            config = await self.db.get_guild_config(member.guild.id)
            
            if not config or not config.get('welcome_channel_id'):
                return
            
            channel = member.guild.get_channel(config['welcome_channel_id'])
            if not channel:
                return
            
            # Utiliser l'embed standardisé
            custom_message = config.get('welcome_message')
            embed = Embeds.welcome(member, member.guild, custom_message)
            
            await channel.send(embed=embed)
            logger.info(f"Message de bienvenue envoyé pour {member.name} dans {member.guild.name}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message de bienvenue: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Événement déclenché quand un membre quitte"""
        try:
            config = await self.db.get_guild_config(member.guild.id)
            
            if not config or not config.get('goodbye_channel_id'):
                return
            
            channel = member.guild.get_channel(config['goodbye_channel_id'])
            if not channel:
                return
            
            # Utiliser l'embed standardisé
            custom_message = config.get('goodbye_message')
            embed = Embeds.goodbye(member, member.guild, custom_message)
            
            await channel.send(embed=embed)
            logger.info(f"Message d'au revoir envoyé pour {member.name} dans {member.guild.name}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message d'au revoir: {e}")

async def setup(bot):
    await bot.add_cog(Events(bot))