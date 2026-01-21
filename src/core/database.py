"""
Gestion de la base de données
"""
import aiosqlite
from pathlib import Path
from typing import Optional

class DatabaseManager:
    """Gestionnaire de base de données SQLite"""
    
    def __init__(self, database_url: str = "sqlite:///data/bot.db"):
        """
        Initialise le gestionnaire de base de données
        
        Args:
            database_url: URL de la base de données
        """
        # Extraire le chemin du fichier depuis l'URL
        self.db_path = database_url.replace("sqlite:///", "")
        
        # Créer le dossier data s'il n'existe pas
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """Établit la connexion à la base de données"""
        if not self.connection:
            self.connection = await aiosqlite.connect(self.db_path)
            await self.create_tables()
            print(f"✅ Base de données connectée : {self.db_path}")
    
    async def close(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            await self.connection.close()
            print("🔌 Base de données déconnectée")
    
    async def create_tables(self):
        """Crée les tables de base si elles n'existent pas"""
        async with self.connection.cursor() as cursor:
            # Table des guilds
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS guilds (
                    guild_id INTEGER PRIMARY KEY,
                    welcome_channel_id INTEGER,
                    log_channel_id INTEGER,
                    auto_role_id INTEGER,
                    prefix TEXT DEFAULT '!',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des utilisateurs
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 0,
                    coins INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guilds(guild_id)
                )
            """)
            
            await self.connection.commit()