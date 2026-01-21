"""
Gestion de la configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration du bot"""
    bot_token: str
    prefix: str = "!"
    database_url: str = "sqlite:///data/bot.db"
    log_level: str = "INFO"
    dev_guild_id: Optional[int] = None
    use_keep_alive: bool = False

# Alias pour compatibilité
BotConfig = Config  # ← AJOUTEZ CETTE LIGNE

def load_config() -> Config:
    """
    Charge la configuration depuis .env
    
    Returns:
        Config: Objet de configuration
    
    Raises:
        ValueError: Si le token Discord est manquant
    """
    # Charger les variables d'environnement
    load_dotenv()
    
    # Récupérer le token
    bot_token = os.getenv('DISCORD_BOT_TOKEN') or os.getenv('BOT_TOKEN')
    
    if not bot_token:
        raise ValueError(
            "❌ Token Discord manquant!\n"
            "Ajoutez DISCORD_BOT_TOKEN ou BOT_TOKEN dans votre fichier .env"
        )
    
    # Gérer DEV_GUILD_ID de manière sécurisée
    dev_guild_id = None
    dev_guild_str = os.getenv("DEV_GUILD_ID", "").strip()
    
    if dev_guild_str and dev_guild_str.isdigit():
        dev_guild_id = int(dev_guild_str)
    elif dev_guild_str and not dev_guild_str.startswith('your_'):
        print(f"⚠️ DEV_GUILD_ID invalide: '{dev_guild_str}' - ignoré")
    
    # Gérer USE_KEEP_ALIVE
    use_keep_alive = os.getenv('USE_KEEP_ALIVE', 'False').lower() in ('true', '1', 'yes')
    
    return Config(
        bot_token=bot_token,
        prefix=os.getenv('BOT_PREFIX', '!'),
        database_url=os.getenv('DATABASE_URL', 'sqlite:///data/bot.db'),
        log_level=os.getenv('LOG_LEVEL', 'INFO').upper(),
        dev_guild_id=dev_guild_id,
        use_keep_alive=use_keep_alive
    )