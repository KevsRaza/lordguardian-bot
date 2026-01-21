"""
Model for Ticket system
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class TicketStatus(Enum):
    """Ticket status enum"""
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class Ticket:
    """Represents a support ticket"""
    
    def __init__(
        self,
        ticket_id: int,
        guild_id: int,
        channel_id: int,
        user_id: int,
        category: str = "general",
        status: str = "open",
        claimed_by: Optional[int] = None,
        created_at: Optional[datetime] = None,
        closed_at: Optional[datetime] = None
    ):
        self.ticket_id = ticket_id
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.user_id = user_id
        self.category = category
        self.status = status
        self.claimed_by = claimed_by
        self.created_at = created_at or datetime.utcnow()
        self.closed_at = closed_at
    
    def close(self, closed_by: int) -> None:
        """Close the ticket"""
        self.status = TicketStatus.CLOSED.value
        self.closed_at = datetime.utcnow()
    
    def claim(self, staff_id: int) -> None:
        """Claim the ticket"""
        self.claimed_by = staff_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "ticket_id": self.ticket_id,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "user_id": self.user_id,
            "category": self.category,
            "status": self.status,
            "claimed_by": self.claimed_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ticket':
        """Create from dictionary"""
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('closed_at'):
            data['closed_at'] = datetime.fromisoformat(data['closed_at'])
        return cls(**data)
    
    def __repr__(self):
        return f"<Ticket ticket_id={self.ticket_id} status={self.status}>"


class TicketConfig:
    """Configuration for ticket system in a guild"""
    
    def __init__(
        self,
        guild_id: int,
        category_id: Optional[int] = None,
        log_channel_id: Optional[int] = None,
        support_role_id: Optional[int] = None,
        enabled: bool = True,
        max_tickets_per_user: int = 3,
        ticket_counter: int = 0
    ):
        self.guild_id = guild_id
        self.category_id = category_id
        self.log_channel_id = log_channel_id
        self.support_role_id = support_role_id
        self.enabled = enabled
        self.max_tickets_per_user = max_tickets_per_user
        self.ticket_counter = ticket_counter
    
    def increment_counter(self) -> int:
        """Increment and return ticket counter"""
        self.ticket_counter += 1
        return self.ticket_counter
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "guild_id": self.guild_id,
            "category_id": self.category_id,
            "log_channel_id": self.log_channel_id,
            "support_role_id": self.support_role_id,
            "enabled": self.enabled,
            "max_tickets_per_user": self.max_tickets_per_user,
            "ticket_counter": self.ticket_counter
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TicketConfig':
        """Create from dictionary"""
        return cls(**data)
    
    def __repr__(self):
        return f"<TicketConfig guild_id={self.guild_id} enabled={self.enabled}>"