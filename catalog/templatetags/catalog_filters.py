from django import template

register = template.Library()

@register.filter
def filter_ai_badge(emoji_tabs, song_name):
    """
    Filter out AI badges for non-AI songs
    Only show AI badge for songs starting with 🤖
    
    Note: This filter is now primarily a passthrough since the view handles
    the filtering of AI badges. Keeping it for template compatibility.
    """
    # Now just return the tabs without extra filtering since view handles this
    return emoji_tabs