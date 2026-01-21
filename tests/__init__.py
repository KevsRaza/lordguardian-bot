"""
Tests automatisés pour GuildGreeter.
"""

import sys
import os

# Ajouter le répertoire src au PYTHONPATH pour les tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Fixtures globales disponibles
__all__ = []

# Configuration pytest
pytest_plugins = []

# Mode de test
TEST_MODE = True

# URLs de test
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_DISCORD_TOKEN = "test_token_123"
TEST_GUILD_ID = 1441412296927740035
TEST_USER_ID = 758771006671159327