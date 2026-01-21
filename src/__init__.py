"""
GuildGreeter - Bot Discord multifonction avec dashboard web
Un système complet de gestion de serveur Discord.
"""

__version__ = "1.0.0"
__author__ = "Kevin RAZA"
__license__ = "MIT"

# Importations principales
try:
    from .bot import GuildGreeterBot
    from .core.config import BotConfig
    from .core.database import DatabaseManager
except ImportError:
    pass  # Importation même si certaines dépendances ne sont pas installées

__all__ = [
    "GuildGreeterBot",
    "BotConfig", 
    "DatabaseManager",
    "__version__",
    "__author__",
    "__license__"
]

# Variables globales
BOT_NAME = "GuildGreeter"
SUPPORT_SERVER = "https://discord.gg/votre-lien"
GITHUB_URL = "https://github.com/KevsRaza/GuildGreeter"