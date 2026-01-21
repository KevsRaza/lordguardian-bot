"""
Gestion des extensions/cogs du bot
"""
from pathlib import Path
import importlib
import sys

async def load_extensions(bot):
    """
    Charge toutes les extensions (cogs) du bot
    
    Args:
        bot: Instance du bot Discord
    """
    # Liste des cogs à charger
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
    
    print("🔧 Chargement des extensions...")
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"  ✅ {cog}")
        except Exception as e:
            print(f"  ❌ {cog}: {e}")
    
    print(f"📦 {len(bot.cogs)} cogs chargés sur {len(cogs)}")


async def reload_extensions(bot):
    """
    Recharge toutes les extensions du bot
    
    Args:
        bot: Instance du bot Discord
    """
    print("🔄 Rechargement des extensions...")
    
    for extension in list(bot.extensions.keys()):
        try:
            await bot.reload_extension(extension)
            print(f"  ✅ {extension}")
        except Exception as e:
            print(f"  ❌ {extension}: {e}")


async def unload_extensions(bot):
    """
    Décharge toutes les extensions du bot
    
    Args:
        bot: Instance du bot Discord
    """
    print("🗑️ Déchargement des extensions...")
    
    for extension in list(bot.extensions.keys()):
        try:
            await bot.unload_extension(extension)
            print(f"  ✅ {extension}")
        except Exception as e:
            print(f"  ❌ {extension}: {e}")