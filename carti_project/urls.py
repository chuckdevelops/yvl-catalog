from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import FileResponse, Http404
import os
import logging

# Custom view to serve audio files with the same headers as the custom server
def serve_media_audio(request, filename):
    """Enhanced media file server for audio files"""
    logger = logging.getLogger(__name__)
    
    # Enable more verbose logging
    logger.info(f"[MEDIA SERVE] Direct media serving audio file: {filename}")
    logger.info(f"[MEDIA SERVE] Request URL: {request.path}")
    logger.info(f"[MEDIA SERVE] Request method: {request.method}")
    logger.info(f"[MEDIA SERVE] User agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
    logger.info(f"[MEDIA SERVE] Referrer: {request.META.get('HTTP_REFERER', 'None')}")
    
    # Security check
    if '..' in filename or filename.startswith('/'):
        logger.error(f"[MEDIA SERVE] Security check failed for filename: {filename}")
        raise Http404("Invalid filename")
    
    # Get file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'previews', filename)
    logger.info(f"[MEDIA SERVE] Looking for file at: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"[MEDIA SERVE] File not found: {file_path}")
        raise Http404(f"Audio file {filename} not found")
    
    logger.info(f"[MEDIA SERVE] File exists, size: {os.path.getsize(file_path)} bytes")
    
    # Check file readability and permissions
    if not os.access(file_path, os.R_OK):
        logger.error(f"[MEDIA SERVE] File not readable: {file_path}")
        raise Http404(f"Audio file {filename} is not readable")
    
    # Get file permissions and log them
    file_permissions = oct(os.stat(file_path).st_mode)[-3:]
    logger.info(f"[MEDIA SERVE] File permissions: {file_permissions}")
    
    # Serve with enhanced headers
    try:
        # Use 'rb' mode to ensure binary reading
        response = FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        # Set content length
        file_size = os.path.getsize(file_path)
        response['Content-Length'] = str(file_size)
        
        # Enable CORS for media files
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Range'
        
        # Disable caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        # Add range support explicitly
        response['Accept-Ranges'] = 'bytes'
        
        logger.info(f"[MEDIA SERVE] Successfully created direct media response for {filename}")
        print(f"[MEDIA SERVE] Successfully serving {filename} from {file_path}")
        return response
    except Exception as e:
        logger.error(f"[MEDIA SERVE] Error serving file {filename}: {str(e)}")

        raise

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('catalog.api_urls')),  # Add API endpoints
    path('', include('catalog.urls')),
    
    # Use our enhanced handler for all preview files
    path('media/previews/<str:filename>', serve_media_audio, name='preview_file'),
]

# Add static URLs only
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add media URLs for non-preview files
# This pattern is too general - it's catching all media files but the previews handler might not trigger
# Let's debug the issue by adding more specific routes
urlpatterns += [
    # Explicit handler for previews before the general media handler
    path('media/previews/<str:filename>', serve_media_audio, name='preview_file_direct'),
    
    # General media route for all other files
    path('media/<path:path>', 
         lambda request, path: serve(
             request, 
             path, 
             document_root=settings.MEDIA_ROOT
         ), 
         name='serve_media'),
]

# TODO: Add API URL routing
# Add this import if not already present:
# from django.conf import settings
# from django.conf.urls.static import static

# TODO: Add API URLs to your urlpatterns
# Add this line to your urlpatterns list:
# path('api/', include('catalog.api_urls')),

# TODO: Add static file serving for development
# Add this at the end of the file (after urlpatterns definition):
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# TODO: Add API documentation URLs (optional)
# path('api-docs/', include('rest_framework.urls')),  # Browsable API

# Example of what your urlpatterns should look like:
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('catalog.api_urls')),  # New API endpoints
#     path('', include('catalog.urls')),  # Your existing URLs
# ]