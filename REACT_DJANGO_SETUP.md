# React + Django API Setup Guide

## Step 1: Install Django Packages

```bash
# In your Django project root
pip install -r requirements-api.txt
```

## Step 2: Update Django Settings

Edit `carti_project/settings.py`:

1. **Add to INSTALLED_APPS:**
```python
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'corsheaders',
    'django_filters',
]
```

2. **Add CORS middleware (FIRST in MIDDLEWARE):**
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... existing middleware
]
```

3. **Add REST Framework configuration:**
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
```

4. **Add CORS settings:**
```python
# Development settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_ALL_ORIGINS = True  # Remove in production
CORS_ALLOW_CREDENTIALS = True
```

## Step 3: Update Django URLs

Edit `carti_project/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('catalog.api_urls')),  # Add this line
    path('', include('catalog.urls')),
]
```

## Step 4: Complete the Serializers

Edit `catalog/serializers.py` and uncomment the TODO fields you need.

## Step 5: Complete the ViewSets

Edit `catalog/api_viewsets.py` and implement the TODO methods.

## Step 6: Install React Dependencies

```bash
# In your React project root
cd playboi-catalogue-explorer
npm install axios
```

## Step 7: Update React API Service

The `src/services/api.ts` file is ready, but you need to:
1. Fix the axios import error by installing axios
2. Update the API_BASE_URL if needed
3. Implement error handling

## Step 8: Create Environment File

Create `playboi-catalogue-explorer/.env`:
```
REACT_APP_API_URL=http://localhost:8000/api
```

## Step 9: Test the Connection

1. **Start Django server:**
```bash
python manage.py runserver
```

2. **Start React server (in another terminal):**
```bash
cd playboi-catalogue-explorer
npm run dev
```

3. **Test API endpoints:**
- Visit http://localhost:8000/api/ (Django browsable API)
- Test in React: Import and use the API service

## Step 10: Implement Your First Endpoint

Start with the songs endpoint:

1. **Complete CartiCatalogSerializer** - add computed fields
2. **Complete CartiCatalogViewSet.get_queryset()** - add filtering
3. **Implement CartiCatalogViewSet.recent()** - for homepage
4. **Test in React** - use `songsApi.getRecent()`

## Step 11: Handle Static Files

Make sure your Django settings include:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

And in urls.py (for development):
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Common Issues to Watch For:

1. **CORS errors** - Make sure CORS is configured properly
2. **404 on API calls** - Check URL patterns and base URL
3. **Import errors** - Make sure all packages are installed
4. **Preview file serving** - Configure static/media file serving
5. **Database queries** - Use select_related/prefetch_related for performance

## Next Steps:

1. Start with the homepage API call
2. Implement song filtering
3. Add error handling in React
4. Add loading states
5. Implement voting/bookmarking
6. Add media endpoints
7. Add search functionality

## Development Workflow:

1. **Django First:** Implement and test API endpoints using browsable API
2. **React Second:** Connect React components to working endpoints
3. **Iterate:** Add features incrementally, testing both sides 