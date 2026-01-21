"""
Helper utility functions
"""
import discord
from typing import Optional, Union, List
import re
import asyncio


def clean_prefix(bot, message: discord.Message) -> str:
    """Get clean prefix for display"""
    prefix = bot.command_prefix
    if callable(prefix):
        prefix = prefix(bot, message)
    if isinstance(prefix, list):
        prefix = prefix[0]
    return prefix


def format_time(seconds: int) -> str:
    """Format seconds into human readable time"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


def format_number(num: int) -> str:
    """Format number with commas"""
    return f"{num:,}"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_member_color(member: discord.Member) -> discord.Color:
    """Get member's top role color or default"""
    if member.color != discord.Color.default():
        return member.color
    return discord.Color.blurple()


def progress_bar(current: int, total: int, length: int = 10, fill: str = "█", empty: str = "░") -> str:
    """Create a progress bar"""
    if total == 0:
        return empty * length
    
    filled = int(length * current / total)
    bar = fill * filled + empty * (length - filled)
    return bar


def create_invite_url(client_id: int, permissions: discord.Permissions = None) -> str:
    """Generate bot invite URL"""
    if permissions is None:
        permissions = discord.Permissions(administrator=True)
    
    return discord.utils.oauth_url(
        client_id,
        permissions=permissions,
        scopes=["bot", "applications.commands"]
    )


async def send_or_reply(ctx, *args, **kwargs) -> discord.Message:
    """Send message or reply based on context"""
    try:
        return await ctx.reply(*args, **kwargs)
    except (discord.HTTPException, discord.Forbidden):
        return await ctx.send(*args, **kwargs)


async def confirm_action(
    ctx,
    message: str,
    timeout: float = 30.0,
    delete_after: bool = True
) -> Optional[bool]:
    """
    Ask user to confirm an action
    Returns True if confirmed, False if denied, None if timeout
    """
    embed = discord.Embed(
        description=message,
        color=discord.Color.orange()
    )
    embed.set_footer(text="React with ✅ to confirm or ❌ to cancel")
    
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    
    def check(reaction, user):
        return (
            user == ctx.author
            and str(reaction.emoji) in ["✅", "❌"]
            and reaction.message.id == msg.id
        )
    
    try:
        reaction, user = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=check)
        confirmed = str(reaction.emoji) == "✅"
        
        if delete_after:
            try:
                await msg.delete()
            except discord.HTTPException:
                pass
        
        return confirmed
    
    except asyncio.TimeoutError:
        if delete_after:
            try:
                await msg.delete()
            except discord.HTTPException:
                pass
        return None


def escape_markdown(text: str) -> str:
    """Escape markdown characters"""
    return discord.utils.escape_markdown(text)


def chunked_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def ordinal(n: int) -> str:
    """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return f"{n}{suffix}"


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)