# src/core/__init__.py
from .config import Config, load_config

# Alias pour compatibilité
BotConfig = Config

from .database import DatabaseManager
from .logger import setup_logger

__all__ = [
    'Config',
    'BotConfig',  # ← Export de l'alias
    'load_config',
    'DatabaseManager',
    'setup_logger'
]