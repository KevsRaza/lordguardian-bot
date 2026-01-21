"""
Model for Economy system (coins, inventory, shop)
"""
from datetime import datetime
from typing import Optional, Dict, Any, List


class EconomyUser:
    """Represents a user's economy data"""
    
    def __init__(
        self,
        user_id: int,
        guild_id: int,
        balance: int = 0,
        bank: int = 0,
        inventory: Optional[Dict[str, int]] = None,
        last_daily: Optional[datetime] = None,
        last_work: Optional[datetime] = None,
        created_at: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.guild_id = guild_id
        self.balance = balance
        self.bank = bank
        self.inventory = inventory or {}
        self.last_daily = last_daily
        self.last_work = last_work
        self.created_at = created_at or datetime.utcnow()
    
    @property
    def total_wealth(self) -> int:
        """Total coins (balance + bank)"""
        return self.balance + self.bank
    
    def add_coins(self, amount: int, to_bank: bool = False) -> None:
        """Add coins to balance or bank"""
        if to_bank:
            self.bank += amount
        else:
            self.balance += amount
    
    def remove_coins(self, amount: int, from_bank: bool = False) -> bool:
        """
        Remove coins from balance or bank
        Returns False if insufficient funds
        """
        if from_bank:
            if self.bank >= amount:
                self.bank -= amount
                return True
        else:
            if self.balance >= amount:
                self.balance -= amount
                return True
        return False
    
    def add_item(self, item_name: str, quantity: int = 1) -> None:
        """Add item to inventory"""
        self.inventory[item_name] = self.inventory.get(item_name, 0) + quantity
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """
        Remove item from inventory
        Returns False if item not found or insufficient quantity
        """
        if item_name in self.inventory and self.inventory[item_name] >= quantity:
            self.inventory[item_name] -= quantity
            if self.inventory[item_name] == 0:
                del self.inventory[item_name]
            return True
        return False
    
    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """Check if user has item in inventory"""
        return self.inventory.get(item_name, 0) >= quantity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "guild_id": self.guild_id,
            "balance": self.balance,
            "bank": self.bank,
            "inventory": self.inventory,
            "last_daily": self.last_daily.isoformat() if self.last_daily else None,
            "last_work": self.last_work.isoformat() if self.last_work else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EconomyUser':
        """Create from dictionary"""
        if data.get('last_daily'):
            data['last_daily'] = datetime.fromisoformat(data['last_daily'])
        if data.get('last_work'):
            data['last_work'] = datetime.fromisoformat(data['last_work'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)
    
    def __repr__(self):
        return f"<EconomyUser user_id={self.user_id} balance={self.balance} bank={self.bank}>"


class ShopItem:
    """Represents an item in the shop"""
    
    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        price: int,
        emoji: str = "📦",
        role_id: Optional[int] = None,
        buyable: bool = True,
        sellable: bool = True,
        sell_price: Optional[int] = None
    ):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.price = price
        self.emoji = emoji
        self.role_id = role_id
        self.buyable = buyable
        self.sellable = sellable
        self.sell_price = sell_price or (price // 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "emoji": self.emoji,
            "role_id": self.role_id,
            "buyable": self.buyable,
            "sellable": self.sellable,
            "sell_price": self.sell_price
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShopItem':
        """Create from dictionary"""
        return cls(**data)
    
    def __repr__(self):
        return f"<ShopItem {self.name} price={self.price}>"