"""
Exceptions personnalisées pour le bot
"""

class BotError(Exception):
    """Erreur de base pour le bot"""
    pass

class ConfigError(BotError):
    """Erreur de configuration"""
    pass

class DatabaseError(BotError):
    """Erreur de base de données"""
    pass

class CogError(BotError):
    """Erreur dans un cog"""
    pass

class PermissionError(BotError):
    """Erreur de permission"""
    pass

class ValidationError(BotError):
    """Erreur de validation"""
    pass