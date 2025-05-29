from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from . import api_viewsets

# TODO: Choose between DefaultRouter and SimpleRouter
# DefaultRouter includes a browsable API root view
router = DefaultRouter()

# Register your viewsets here
# TODO: Customize the URL patterns/names as needed
router.register(r'songs', api_viewsets.CartiCatalogViewSet, basename='songs')
router.register(r'tabs', api_viewsets.SheetTabViewSet, basename='tabs')
router.register(r'art', api_viewsets.ArtMediaViewSet, basename='art')
router.register(r'interviews', api_viewsets.InterviewViewSet, basename='interviews')
router.register(r'fitpics', api_viewsets.FitPicViewSet, basename='fitpics')
router.register(r'social', api_viewsets.SocialMediaViewSet, basename='social')

# TODO: Add API documentation view
schema_view = get_schema_view(
    title="Playboi Carti Catalogue API",
    description="API for accessing Playboi Carti's music catalogue and media",
    version="1.0.0"
)

urlpatterns = [
    # API routes
    path('', include(router.urls)),
    
    # TODO: Add custom API endpoints that don't fit into viewsets
    # Example: path('custom-endpoint/', views.custom_view, name='custom-endpoint'),
    
    # TODO: Add API documentation (optional)
    # path('docs/', include_docs_urls(title='Carti API')),
    # path('schema/', schema_view, name='openapi-schema'),
    
    # TODO: Add API authentication endpoints if needed
    # path('auth/', include('rest_framework.urls')),
]

# TODO: Add API versioning
# You might want to wrap these URLs in a versioned pattern like:
# path('v1/', include((urlpatterns, 'api'), namespace='v1'))

# TODO: Consider adding rate limiting at the URL level
# TODO: Add any custom middleware for API requests 