"""
Modèles de données SQLAlchemy.
Ces classes représentent les tables de la base de données.
"""

from .guild import GuildConfig, GuildStats, GuildLog
from .user import User, UserStats, UserEconomy
from .ticket import Ticket, TicketMessage, TicketCategory
# from .leveling import LevelConfig, LevelReward
from .economy import ShopItem, Transaction, InventoryItem

# Importations de base SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey

Base = declarative_base()

# Tous les modèles disponibles
MODEL_CLASSES = [
    GuildConfig, GuildStats, GuildLog,
    User, UserStats, UserEconomy,
    Ticket, TicketMessage, TicketCategory,
    # LevelConfig, LevelReward,
    ShopItem, Transaction, InventoryItem
]

# Fonctions utilitaires
def get_model_by_name(name: str):
    """Retourne une classe de modèle par son nom."""
    models = {cls.__name__: cls for cls in MODEL_CLASSES}
    return models.get(name)

def get_all_tables():
    """Retourne une liste de tous les noms de tables."""
    return [cls.__tablename__ for cls in MODEL_CLASSES if hasattr(cls, '__tablename__')]

__all__ = [
    "Base",
    # Modèles
    "GuildConfig", "GuildStats", "GuildLog",
    "User", "UserStats", "UserEconomy",
    "Ticket", "TicketMessage", "TicketCategory",
    "LevelConfig", "LevelReward",
    "ShopItem", "Transaction", "InventoryItem",
    # Utilitaires
    "MODEL_CLASSES", "get_model_by_name", "get_all_tables"
]