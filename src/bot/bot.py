"""
Bot principal avec architecture modulaire (cogs)
"""
import discord
from discord.ext import commands
from discord import app_commands  # IMPORTANT !
from core.config import Config  # PAS de src.
from core.database import DatabaseManager  # PAS de src.
from core.logger import setup_logger  # PAS de src.

logger = setup_logger("Bot")

class GuildGreeterBot(commands.Bot):
    """Bot Discord avec système de cogs"""
    
    def __init__(self, config: Config):
        """Initialise le bot"""
        intents = discord.Intents.all()
        
        super().__init__(
            command_prefix=config.prefix,
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )
        
        self.config = config
        self.db = DatabaseManager(config.database_url)
        self.logger = logger
        
        # Initialiser l'arbre de commandes slash
        if not hasattr(self, 'tree') or self.tree is None:
            self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        """Hook appelé lors du setup du bot"""
        logger.info("🔧 Initialisation du bot...")
        
        # Initialiser la base de données
        try:
            await self.db.connect()  # ← CORRIGÉ : utilisation directe de connect()
            logger.info("✅ Base de données initialisée")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation DB: {e}")
        
        # Charger les cogs - CHEMINS RELATIFS
        cogs = [
            "cogs.welcome",
            "cogs.leveling",
            "cogs.moderation",
            "cogs.utilities",
            "cogs.fun",
            "cogs.admin",
            "cogs.tickets",
            "cogs.economy",
            "cogs.shop",
            "cogs.casino",
            "cogs.help_cog"
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Cog chargé: {cog}")
            except Exception as e:
                logger.error(f"❌ Erreur chargement {cog}: {e}")
        
        # Synchroniser les commandes slash (optionnel en dev)
        if self.config.dev_guild_id:
            guild = discord.Object(id=self.config.dev_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"✅ Commandes slash synchronisées (guild {self.config.dev_guild_id})")
    
    async def on_ready(self):
        """Événement appelé quand le bot est prêt"""
        logger.info(f"🤖 Bot connecté en tant que {self.user}")
        logger.info(f"📊 Connecté à {len(self.guilds)} serveur(s)")
        logger.info(f"👥 {len(self.users)} utilisateurs visibles")
        
        # Statut du bot
        await self.change_presence(
            activity=discord.Game(name=f"{self.config.prefix}help")
        )
    
    async def on_guild_join(self, guild: discord.Guild):
        """Événement quand le bot rejoint un serveur"""
        logger.info(f"✅ Rejoint le serveur: {guild.name} (ID: {guild.id})")
        
        # Créer l'entrée dans la DB
        try:
            # Vérifier que la méthode existe
            if hasattr(self.db, 'ensure_guild'):
                await self.db.ensure_guild(guild.id)
            else:
                # Fallback : créer manuellement
                await self.db.connect()
                async with self.db.connection.cursor() as cursor:
                    await cursor.execute(
                        "INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)",
                        (guild.id,)
                    )
                    await self.db.connection.commit()
                logger.info(f"✅ Serveur {guild.id} ajouté à la DB")
        except Exception as e:
            logger.error(f"❌ Erreur création guild DB: {e}")
    
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Gestion des erreurs de commandes"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas les permissions nécessaires.")
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Argument manquant: `{error.param.name}`")
            return
        
        logger.error(f"Erreur commande: {error}", exc_info=error)
        await ctx.send(f"❌ Une erreur est survenue: {str(error)[:100]}")
    
    async def close(self):
        """Fermeture propre du bot"""
        logger.info("🛑 Fermeture du bot...")
        
        # Fermer la connexion DB
        if hasattr(self, 'db'):
            await self.db.close()
            logger.info("✅ Base de données fermée")
        
        await super().close()