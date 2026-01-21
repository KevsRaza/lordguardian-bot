"""
Permission checks and decorators
"""
import discord
from discord.ext import commands
from typing import Callable, Optional


def is_guild_owner():
    """Check if user is guild owner"""
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return False
        return ctx.author.id == ctx.guild.owner_id
    
    return commands.check(predicate)


def is_admin():
    """Check if user has administrator permission"""
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return False
        return ctx.author.guild_permissions.administrator
    
    return commands.check(predicate)


def is_mod():
    """Check if user has moderation permissions"""
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return False
        
        perms = ctx.author.guild_permissions
        return (
            perms.administrator
            or perms.ban_members
            or perms.kick_members
            or perms.manage_messages
        )
    
    return commands.check(predicate)


def has_guild_permissions(**perms):
    """Check if user has specific guild permissions"""
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return False
        
        permissions = ctx.author.guild_permissions
        return all(getattr(permissions, perm, False) for perm in perms)
    
    return commands.check(predicate)


def bot_has_permissions(**perms):
    """Check if bot has specific permissions"""
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return False
        
        bot_perms = ctx.guild.me.guild_permissions
        return all(getattr(bot_perms, perm, False) for perm in perms)
    
    return commands.check(predicate)


def is_bot_owner():
    """Check if user is bot owner"""
    async def predicate(ctx: commands.Context):
        return await ctx.bot.is_owner(ctx.author)
    
    return commands.check(predicate)


def has_role(role_id: int):
    """Check if user has specific role"""
    async def predicate(ctx: commands.Context):
        if ctx.guild is None or not isinstance(ctx.author, discord.Member):
            return False
        
        return any(role.id == role_id for role in ctx.author.roles)
    
    return commands.check(predicate)


def has_any_role(*role_ids: int):
    """Check if user has any of the specified roles"""
    async def predicate(ctx: commands.Context):
        if ctx.guild is None or not isinstance(ctx.author, discord.Member):
            return False
        
        return any(role.id in role_ids for role in ctx.author.roles)
    
    return commands.check(predicate)


def can_execute_action(
    member: discord.Member,
    target: discord.Member,
    action: str = "action"
) -> tuple[bool, Optional[str]]:
    """
    Check if member can execute action on target
    Returns (can_execute, error_message)
    """
    # Can't target self for most actions
    if member.id == target.id:
        return False, f"You cannot {action} yourself."
    
    # Can't target bot owner
    if target.id == member.guild.owner_id:
        return False, f"You cannot {action} the server owner."
    
    # Can't target someone with higher/equal role
    if target.top_role >= member.top_role and member.id != member.guild.owner_id:
        return False, f"You cannot {action} someone with a higher or equal role."
    
    # Can't target bot
    if target.bot:
        return False, f"You cannot {action} bots."
    
    return True, None


def check_hierarchy(
    guild: discord.Guild,
    moderator: discord.Member,
    target: discord.Member
) -> bool:
    """
    Check role hierarchy
    Returns True if moderator can act on target
    """
    # Owner can do anything
    if moderator.id == guild.owner_id:
        return True
    
    # Can't act on owner
    if target.id == guild.owner_id:
        return False
    
    # Check role hierarchy
    return moderator.top_role > target.top_role


def check_bot_hierarchy(
    bot_member: discord.Member,
    target: discord.Member
) -> bool:
    """
    Check if bot can act on target based on hierarchy
    """
    # Can't act on owner
    if target.id == target.guild.owner_id:
        return False
    
    # Check bot's role hierarchy
    return bot_member.top_role > target.top_role


class PermissionChecker:
    """Helper class for checking permissions"""
    
    @staticmethod
    def check_manage_messages(member: discord.Member) -> bool:
        """Check if member can manage messages"""
        return member.guild_permissions.manage_messages
    
    @staticmethod
    def check_ban_members(member: discord.Member) -> bool:
        """Check if member can ban members"""
        return member.guild_permissions.ban_members
    
    @staticmethod
    def check_kick_members(member: discord.Member) -> bool:
        """Check if member can kick members"""
        return member.guild_permissions.kick_members
    
    @staticmethod
    def check_administrator(member: discord.Member) -> bool:
        """Check if member has administrator"""
        return member.guild_permissions.administrator
    
    @staticmethod
    def check_manage_guild(member: discord.Member) -> bool:
        """Check if member can manage guild"""
        return member.guild_permissions.manage_guild
    
    @staticmethod
    def check_manage_channels(member: discord.Member) -> bool:
        """Check if member can manage channels"""
        return member.guild_permissions.manage_channels
    
    @staticmethod
    def check_manage_roles(member: discord.Member) -> bool:
        """Check if member can manage roles"""
        return member.guild_permissions.manage_roles