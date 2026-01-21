"""
Custom converters for discord.py commands
"""
import discord
from discord.ext import commands
from typing import Union
import re


class MemberOrUser(commands.Converter):
    """Converter to get Member if in guild, else User"""
    
    async def convert(self, ctx: commands.Context, argument: str) -> Union[discord.Member, discord.User]:
        try:
            return await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return await commands.UserConverter().convert(ctx, argument)
            except commands.BadArgument:
                raise commands.BadArgument(f"User '{argument}' not found.")


class TimeConverter(commands.Converter):
    """Convert time string to seconds (e.g., '1h30m' -> 5400)"""
    
    TIME_REGEX = re.compile(r"(\d+)([smhd])")
    TIME_DICT = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400
    }
    
    async def convert(self, ctx: commands.Context, argument: str) -> int:
        matches = self.TIME_REGEX.findall(argument.lower())
        if not matches:
            raise commands.BadArgument("Invalid time format. Use format like: 1h30m, 2d, 45s")
        
        total_seconds = 0
        for value, unit in matches:
            total_seconds += int(value) * self.TIME_DICT[unit]
        
        if total_seconds <= 0:
            raise commands.BadArgument("Time must be greater than 0.")
        
        return total_seconds


class EmojiConverter(commands.Converter):
    """Convert string to emoji (custom or unicode)"""
    
    async def convert(self, ctx: commands.Context, argument: str) -> Union[discord.Emoji, str]:
        # Try custom emoji
        try:
            return await commands.EmojiConverter().convert(ctx, argument)
        except commands.BadArgument:
            # Return as unicode emoji
            if len(argument) <= 5:  # Basic check for unicode emoji
                return argument
            raise commands.BadArgument(f"Emoji '{argument}' not found.")


class ChannelOrThread(commands.Converter):
    """Converter for text channels or threads"""
    
    async def convert(self, ctx: commands.Context, argument: str) -> Union[discord.TextChannel, discord.Thread]:
        # Try text channel
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            # Try thread
            try:
                return await commands.ThreadConverter().convert(ctx, argument)
            except commands.BadArgument:
                raise commands.BadArgument(f"Channel or thread '{argument}' not found.")


class RoleOrMember(commands.Converter):
    """Converter for role or member"""
    
    async def convert(self, ctx: commands.Context, argument: str) -> Union[discord.Role, discord.Member]:
        try:
            return await commands.RoleConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return await commands.MemberConverter().convert(ctx, argument)
            except commands.BadArgument:
                raise commands.BadArgument(f"Role or member '{argument}' not found.")