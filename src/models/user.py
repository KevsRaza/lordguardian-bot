"""
Model for User data including leveling and stats
"""
from datetime import datetime
from typing import Optional, Dict, Any
import math


class User:
    """Represents a Discord user with leveling and stats"""
    
    def __init__(
        self,
        user_id: int,
        guild_id: int,
        xp: int = 0,
        level: int = 0,
        messages_sent: int = 0,
        last_xp_time: Optional[datetime] = None,
        created_at: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.guild_id = guild_id
        self.xp = xp
        self.level = level
        self.messages_sent = messages_sent
        self.last_xp_time = last_xp_time
        self.created_at = created_at or datetime.utcnow()
    
    @property
    def xp_for_next_level(self) -> int:
        """Calculate XP needed for next level"""
        return int(50 * (self.level + 1) ** 2)
    
    @property
    def xp_progress(self) -> float:
        """Calculate progress to next level as percentage"""
        xp_current_level = self.xp_for_level(self.level)
        xp_next_level = self.xp_for_next_level
        xp_progress = self.xp - xp_current_level
        xp_needed = xp_next_level - xp_current_level
        return (xp_progress / xp_needed) * 100 if xp_needed > 0 else 0
    
    @staticmethod
    def xp_for_level(level: int) -> int:
        """Calculate total XP needed to reach a level"""
        return int(50 * level ** 2)
    
    def add_xp(self, amount: int) -> bool:
        """
        Add XP to user and check for level up
        Returns True if user leveled up
        """
        self.xp += amount
        self.last_xp_time = datetime.utcnow()
        
        leveled_up = False
        while self.xp >= self.xp_for_next_level:
            self.level += 1
            leveled_up = True
        
        return leveled_up
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "user_id": self.user_id,
            "guild_id": self.guild_id,
            "xp": self.xp,
            "level": self.level,
            "messages_sent": self.messages_sent,
            "last_xp_time": self.last_xp_time.isoformat() if self.last_xp_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User from dictionary"""
        if data.get('last_xp_time'):
            data['last_xp_time'] = datetime.fromisoformat(data['last_xp_time'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)
    
    def __repr__(self):
        return f"<User user_id={self.user_id} level={self.level} xp={self.xp}>"