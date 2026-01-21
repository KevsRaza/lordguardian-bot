"""
GuildGreeter - Point d'entrée principal
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le dossier src au path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from bot.bot import GuildGreeterBot
from core.logger import setup_logger
from core.config import load_config

logger = setup_logger()

async def main():
    """Lance le bot Discord"""
    config = load_config()
    bot = GuildGreeterBot(config)
    
    try:
        async with bot:
            await bot.start(config.bot_token)
    except KeyboardInterrupt:
        logger.info("Bot arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur critique: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Interception finale pour éviter le traceback
        print("\n👋 Bot arrêté proprement")
    except Exception:
        sys.exit(1)