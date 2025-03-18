from django import template
import re
from catalog.utils import get_embedded_player

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

@register.filter
def remove_urls(text):
    """
    Remove URLs from text, returning non-URL portions only
    """
    if not text:
        return ""
        
    # URL pattern to match http/https links
    url_pattern = r'https?://\S+'
    
    # Remove URLs
    cleaned_text = re.sub(url_pattern, '', text)
    
    # Clean up any leftover artifacts like empty parentheses, extra commas, etc.
    cleaned_text = re.sub(r'\(\s*\)', '', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text
    
@register.filter(is_safe=True)
def get_player(links_text):
    """
    Generate an embedded player for the song links
    """
    return get_embedded_player(links_text)
    
@register.filter
def extract_urls(text):
    """Extract all URLs from a text string"""
    if not text:
        return []
    
    # Find all URLs in the text
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    return urls
    
@register.filter
def get_domain(url):
    """Extract domain name from URL"""
    if 'music.froste.lol' in url:
        return 'music.froste.lol'
    elif 'pillowcase.su' in url:
        return 'pillowcase.su'
    elif 'soundcloud.com' in url:
        return 'SoundCloud'
    elif 'spotify.com' in url:
        return 'Spotify'
    elif 'youtube.com' in url or 'youtu.be' in url:
        return 'YouTube'
    else:
        # Extract domain name
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            return domain_match.group(1)
        return 'External Site'
        
@register.filter
def get_download_url(url):
    """Convert a song URL to its download URL if available"""
    if 'music.froste.lol/song/' in url:
        # Extract song ID and construct download URL
        song_id = url.split('/song/')[1].split('/')[0]
        return f"http://music.froste.lol/song/{song_id}/download"
    
    # Handle pillowcase.su downloads
    elif 'pillowcase.su/f/' in url:
        file_id = url.split('/f/')[1]
        return f"https://pillowcase.su/f/{file_id}/download"
    
    # Return None if no download URL can be constructed
    return None

@register.filter
def extract_preview_filename(preview_url):
    """Extract filename from preview URL, safely handling different URL formats"""
    if not preview_url:
        return ""
    
    # If URL contains /media/previews/, extract filename
    if '/media/previews/' in preview_url:
        return preview_url.split('/media/previews/')[1]
    
    # Otherwise, just use basename
    import os
    return os.path.basename(preview_url)