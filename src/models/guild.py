"""
Model for Guild/Server configurations
"""
from datetime import datetime
from typing import Optional, Dict, Any


class Guild:
    """Represents a Discord guild configuration"""
    
    def __init__(
        self,
        guild_id: int,
        prefix: str = "!",
        welcome_channel_id: Optional[int] = None,
        welcome_message: str = "Welcome {user} to {server}!",
        goodbye_message: str = "Goodbye {user}!",
        mod_log_channel_id: Optional[int] = None,
        autorole_id: Optional[int] = None,
        leveling_enabled: bool = True,
        xp_rate: float = 1.0,
        created_at: Optional[datetime] = None
    ):
        self.guild_id = guild_id
        self.prefix = prefix
        self.welcome_channel_id = welcome_channel_id
        self.welcome_message = welcome_message
        self.goodbye_message = goodbye_message
        self.mod_log_channel_id = mod_log_channel_id
        self.autorole_id = autorole_id
        self.leveling_enabled = leveling_enabled
        self.xp_rate = xp_rate
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert guild to dictionary"""
        return {
            "guild_id": self.guild_id,
            "prefix": self.prefix,
            "welcome_channel_id": self.welcome_channel_id,
            "welcome_message": self.welcome_message,
            "goodbye_message": self.goodbye_message,
            "mod_log_channel_id": self.mod_log_channel_id,
            "autorole_id": self.autorole_id,
            "leveling_enabled": self.leveling_enabled,
            "xp_rate": self.xp_rate,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Guild':
        """Create Guild from dictionary"""
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)
    
    def __repr__(self):
        return f"<Guild guild_id={self.guild_id} prefix={self.prefix}>"