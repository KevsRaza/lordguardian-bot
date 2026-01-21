"""
Module principal du bot Discord.
Contient la classe principale du bot et les extensions.
"""

from .bot import GuildGreeterBot
from .extensions import load_extensions, unload_extensions, reload_extensions
from .keep_alive import keep_alive

__all__ = [
    "GuildGreeterBot",
    "load_extensions",
    "unload_extensions", 
    "reload_extensions",
    "keep_alive"
]

# Version spécifique au module
__version__ = "1.0.0"
__description__ = "Bot Discord GuildGreeter - Gestion avancée de serveurs"