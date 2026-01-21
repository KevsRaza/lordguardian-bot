"""
Cogs (modules) du bot Discord.
Chaque cog est une classe qui étend commands.Cog.
"""

import importlib
import pkgutil
from pathlib import Path

# Liste dynamique des cogs disponibles
COG_EXTENSIONS = [
    "src.cogs.admin",
    "src.cogs.welcome", 
    "src.cogs.moderation",
    "src.cogs.leveling",
    "src.cogs.tickets",
    "src.cogs.utilities",
    "src.cogs.fun",
    "src.cogs.economy"
]

# Fonction pour charger tous les cogs
async def load_all_cogs(bot):
    """Charge tous les cogs disponibles."""
    loaded_cogs = []
    failed_cogs = []
    
    for cog_path in COG_EXTENSIONS:
        try:
            await bot.load_extension(cog_path)
            loaded_cogs.append(cog_path.split(".")[-1])
        except Exception as e:
            failed_cogs.append((cog_path, str(e)))
    
    return loaded_cogs, failed_cogs

# Fonction pour obtenir la description d'un cog
def get_cog_description(cog_name):
    """Retourne la description d'un cog spécifique."""
    descriptions = {
        "admin": "Commandes d'administration du serveur",
        "welcome": "Système de bienvenue avancé",
        "moderation": "Outils de modération et de sécurité",
        "leveling": "Système de niveaux et d'XP",
        "tickets": "Système de tickets de support",
        "utilities": "Utilitaires divers",
        "fun": "Commandes divertissantes",
        "economy": "Économie virtuelle"
    }
    return descriptions.get(cog_name, "Pas de description disponible")

__all__ = [
    "COG_EXTENSIONS",
    "load_all_cogs",
    "get_cog_description"
]