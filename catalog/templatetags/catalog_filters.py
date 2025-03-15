from django import template
import re

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all instances of the first character in arg with the second character in arg.
    Example usage: {{ value|replace:'_,' }}
    """
    try:
        old, new = arg.split(',')
        return value.replace(old, new)
    except ValueError:
        return value

@register.filter
def filter_ai_badge(emoji_tabs, song_name):
    """
    Filter out emoji badges for songs that don't start with the corresponding emoji
    """
    # Create a mapping of emoji tabs to their emoji prefixes
    emoji_tab_map = {
        "🏆 Grails": "🏆",
        "🥇 Wanted": "🥇",
        "⭐ Best Of": "⭐",
        "✨ Special": "✨",
        "🗑️ Worst Of": "🗑️",
        "🤖 AI Tracks": "🤖"
    }
    
    # Filter out emoji badges for songs without matching prefixes
    filtered_tabs = []
    for tab in emoji_tabs:
        # If this is an emoji tab, check for matching prefix
        if tab in emoji_tab_map:
            emoji_prefix = emoji_tab_map[tab]
            if song_name and song_name.startswith(emoji_prefix):
                filtered_tabs.append(tab)
        else:
            # Keep all non-emoji tabs
            filtered_tabs.append(tab)
    return filtered_tabs
    
@register.filter
def youtube_embed_url(url):
    """Convert YouTube URL to embed URL format"""
    if not url or 'youtube.com' not in url and 'youtu.be' not in url:
        return ''
    
    youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(youtube_pattern, url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    return ''
    
@register.filter
def split(value, delimiter='\n'):
    """
    Split a string by delimiter.
    Example usage: {{ value|split }} - splits by newlines by default
    Example usage: {{ value|split:',' }} - splits by commas
    """
    if not value:
        return []
    return value.split(delimiter)

@register.filter
def format_type(value):
    """
    Format 'Yes' to 'Streaming' and 'No' to 'Off Streaming'
    This filter handles legacy data in case any values are still 'Yes'/'No'
    """
    if not value:
        return value
        
    if value.lower() == "yes":
        return "Streaming"
    elif value.lower() == "no":
        return "Off Streaming"
    return value