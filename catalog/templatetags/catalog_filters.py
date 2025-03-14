from django import template

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