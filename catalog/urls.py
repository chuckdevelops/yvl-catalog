from django.urls import path
from . import views

app_name = 'catalog'  # Namespace for URL naming

urlpatterns = [
    path('', views.index, name='index'),
    path('songs/', views.song_list, name='song_list'),
    path('songs/<int:song_id>/', views.song_detail, name='song_detail'),
    path('media/', views.media_page, name='media'),
]