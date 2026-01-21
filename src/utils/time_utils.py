"""
Time-related utility functions
"""
from datetime import datetime, timedelta
from typing import Optional
import re


def parse_time(time_string: str) -> Optional[int]:
    """
    Parse time string to seconds
    Examples: '1h', '30m', '1d12h', '2h30m45s'
    Returns seconds or None if invalid
    """
    time_regex = re.compile(r"(\d+)([smhd])")
    time_dict = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400
    }
    
    matches = time_regex.findall(time_string.lower())
    if not matches:
        return None
    
    total_seconds = 0
    for value, unit in matches:
        total_seconds += int(value) * time_dict[unit]
    
    return total_seconds if total_seconds > 0 else None


def format_time(seconds: int, short: bool = False) -> str:
    """
    Format seconds into human readable time
    
    Args:
        seconds: Time in seconds
        short: Use short format (1d 2h vs 1 day, 2 hours)
    """
    if seconds == 0:
        return "0s" if short else "0 seconds"
    
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    
    parts = []
    
    if short:
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if secs or not parts:
            parts.append(f"{secs}s")
    else:
        if days:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if secs or not parts:
            parts.append(f"{secs} second{'s' if secs != 1 else ''}")
    
    return " ".join(parts)


def format_dt(dt: datetime, style: str = "F") -> str:
    """
    Format datetime for Discord timestamp
    
    Styles:
        t: Short Time (16:20)
        T: Long Time (16:20:30)
        d: Short Date (20/04/2021)
        D: Long Date (20 April 2021)
        f: Short Date/Time (20 April 2021 16:20)
        F: Long Date/Time (Tuesday, 20 April 2021 16:20)
        R: Relative Time (2 months ago)
    """
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:{style}>"


def time_until(target_time: datetime) -> str:
    """Get human readable time until target datetime"""
    now = datetime.utcnow()
    if target_time <= now:
        return "now"
    
    delta = target_time - now
    return format_time(int(delta.total_seconds()))


def time_since(past_time: datetime) -> str:
    """Get human readable time since past datetime"""
    now = datetime.utcnow()
    if past_time >= now:
        return "just now"
    
    delta = now - past_time
    return format_time(int(delta.total_seconds()))


def get_relative_time(dt: datetime) -> str:
    """Get relative time string (e.g., '2 hours ago', 'in 3 days')"""
    now = datetime.utcnow()
    delta = dt - now
    
    if delta.total_seconds() < 0:
        # Past
        delta = now - dt
        seconds = int(delta.total_seconds())
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 2592000:  # 30 days
            days = seconds // 86400
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 31536000:  # 365 days
            months = seconds // 2592000
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = seconds // 31536000
            return f"{years} year{'s' if years != 1 else ''} ago"
    else:
        # Future
        seconds = int(delta.total_seconds())
        
        if seconds < 60:
            return "in a moment"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"in {minutes} minute{'s' if minutes != 1 else ''}"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"in {hours} hour{'s' if hours != 1 else ''}"
        elif seconds < 2592000:
            days = seconds // 86400
            return f"in {days} day{'s' if days != 1 else ''}"
        elif seconds < 31536000:
            months = seconds // 2592000
            return f"in {months} month{'s' if months != 1 else ''}"
        else:
            years = seconds // 31536000
            return f"in {years} year{'s' if years != 1 else ''}"


def parse_duration(duration_str: str) -> Optional[timedelta]:
    """
    Parse duration string to timedelta
    Examples: '1 hour', '2 days', '30 minutes'
    """
    duration_str = duration_str.lower().strip()
    
    # Try common patterns
    patterns = [
        (r'(\d+)\s*days?', 'days'),
        (r'(\d+)\s*hours?', 'hours'),
        (r'(\d+)\s*minutes?', 'minutes'),
        (r'(\d+)\s*seconds?', 'seconds'),
        (r'(\d+)\s*d', 'days'),
        (r'(\d+)\s*h', 'hours'),
        (r'(\d+)\s*m', 'minutes'),
        (r'(\d+)\s*s', 'seconds'),
    ]
    
    kwargs = {}
    for pattern, unit in patterns:
        match = re.search(pattern, duration_str)
        if match:
            value = int(match.group(1))
            kwargs[unit] = kwargs.get(unit, 0) + value
    
    if not kwargs:
        return None
    
    return timedelta(**kwargs)


def cooldown_remaining(last_used: datetime, cooldown_seconds: int) -> Optional[int]:
    """
    Calculate remaining cooldown time
    Returns seconds remaining or None if cooldown expired
    """
    now = datetime.utcnow()
    elapsed = (now - last_used).total_seconds()
    remaining = cooldown_seconds - elapsed
    
    return int(remaining) if remaining > 0 else None