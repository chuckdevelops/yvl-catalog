import hashlib
import re
from django.utils import timezone
from django.utils.html import format_html
from .models import ClientIdentifier

def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Get the client's IP (first one in case of proxies)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_client_hash(request):
    """Generate a unique client hash based on multiple factors"""
    # Get identifying information (make it hard to manipulate)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip = get_client_ip(request)
    # Add other browser characteristics from request headers
    accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
    
    # Combine all these pieces
    client_string = f"{user_agent}|{ip}|{accept_lang}|{accept_encoding}"
    
    # Create a hash (one-way transformation)
    client_hash = hashlib.sha256(client_string.encode()).hexdigest()
    
    return client_hash

def check_and_update_client(request):
    """Check if client is allowed to vote and update records"""
    # Generate the client hash
    client_hash = generate_client_hash(request)
    
    # Find or create client record
    client, created = ClientIdentifier.objects.get_or_create(client_hash=client_hash)
    
    # Always update last_seen
    client.last_seen = timezone.now()
    
    # Check voting patterns and rate limits
    time_since_last_vote = None
    if client.last_vote_time:
        time_since_last_vote = timezone.now() - client.last_vote_time
    
    # Save the updated record
    client.save()
    
    return client, time_since_last_vote
    
def get_embedded_player(links_text):
    """Extract embed player from song links"""
    if not links_text:
        return None
    
    # Extract URLs from the links text
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', links_text)
    if not urls:
        return None
    
    # Create a simple but effective player interface that works without relying on external sites
    first_url = urls[0]
    song_url = first_url
    
    # Create a direct access button styled as a music player
    player_html = format_html(
        '''
        <div class="card mt-3">
            <div class="card-body p-3">
                <div class="d-flex align-items-center">
                    <a href="{}" target="_blank" class="btn btn-primary me-3">
                        <i class="fas fa-play"></i>
                    </a>
                    <div>
                        <div><strong>Play on Source Site</strong></div>
                        <small class="text-muted">{}</small>
                    </div>
                </div>
            </div>
        </div>
        ''',
        song_url,
        get_site_name(song_url)
    )
    
    return player_html

def get_site_name(url):
    """Get a friendly name for a URL's domain"""
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