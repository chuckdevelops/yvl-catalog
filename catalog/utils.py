import hashlib
from django.utils import timezone
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