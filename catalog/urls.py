from django.urls import path
from . import views

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
]