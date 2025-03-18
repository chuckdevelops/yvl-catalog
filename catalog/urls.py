from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'catalog'  # Namespace for URL naming

urlpatterns = [
    path('', views.index, name='index'),
    path('songs/', views.song_list, name='song_list'),
    path('songs/<int:song_id>/', views.song_detail, name='song_detail'),
    path('songs/<int:song_id>/vote/', views.vote_song, name='vote_song'),
    path('media/', views.media_page, name='media'),
    path('media/art/', views.art_page, name='art'),
    path('media/interviews/', views.interviews_page, name='interviews'),
    path('media/fit-pics/', views.fit_pics_page, name='fit_pics'),
    path('media/social-media/', views.social_media_page, name='social_media'),
    path('coming-soon/', views.coming_soon, name='coming_soon'),
    
    # Bookmark API endpoints
    path('songs/<int:song_id>/bookmark/', views.bookmark_song, name='bookmark_song'),
    path('bookmarks/', views.get_bookmarks, name='get_bookmarks'),
    path('collections/', views.get_collections, name='get_collections'),
    
    # Preview generation API endpoint
    path('api/generate-preview/<int:song_id>/', views.generate_preview_api, name='generate_preview_api'),
    
    # Testing page for previews
    path('previews/', views.preview_test, name='preview_test'),
    
    # Direct HTML file for audio testing (no Django processing)
    path('direct-audio/', TemplateView.as_view(template_name='direct/audio.html'), name='direct_audio'),
    
    # Direct audio serving page (using custom Django view to serve audio)
    path('audio-serve-test/', TemplateView.as_view(template_name='direct/audio_serve.html'), name='audio_serve_test'),
    
    # Fixed audio test page (testing after bitrate fix)
    path('audio-test-fixed/', TemplateView.as_view(template_name='direct/audio_test_fixed.html'), name='audio_test_fixed'),
    
    # Direct audio comparison page (completely bypassing Django views)
    path('audio-compare-direct/', TemplateView.as_view(template_name='direct/audio_compare_direct.html'), name='audio_compare_direct'),
    
    # Custom proxied audio files with random parameter in URL
    path('static/proxy-<str:random>-<str:filename>', views.serve_audio_proxy, name='serve_audio_proxy'),
    
    # Direct audio serving (custom handler for each file)
    path('audio-serve/<str:filename>', views.serve_audio, name='serve_audio'),
    
    # Full audio testing page
    path('audio-test/', views.audio_test_view, name='audio_test'),
    
    # Advanced audio duration testing page
    path('audio-duration-test/', TemplateView.as_view(template_name='catalog/audio_duration_test.html'), name='audio_duration_test'),
    
    # Endpoint to log audio play events
    path('log-audio-play/', views.log_audio_play, name='log_audio_play'),
]