from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CartiCatalog

def index(request):
    """Home page with stats and recent songs"""
    song_count = CartiCatalog.objects.count()
    era_count = CartiCatalog.objects.values('era').distinct().count()
    recent_songs = CartiCatalog.objects.all().order_by('-id')[:10]
    
    context = {
        'song_count': song_count,
        'era_count': era_count,
        'recent_songs': recent_songs,
    }
    return render(request, 'catalog/index.html', context)

def song_list(request):
    """List all songs with filtering"""
    # Get filter parameters
    era = request.GET.get('era', '')
    quality = request.GET.get('quality', '')
    query = request.GET.get('q', '')
    
    # Start with all songs
    songs = CartiCatalog.objects.all()
    
    # Apply filters
    if era:
        songs = songs.filter(era=era)
    if quality:
        songs = songs.filter(quality=quality)
    if query:
        songs = songs.filter(Q(name__icontains=query) | Q(notes__icontains=query))
    
    # Pagination
    paginator = Paginator(songs, 25)  # Show 25 songs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    eras = CartiCatalog.objects.values_list('era', flat=True).distinct().order_by('era')
    qualities = CartiCatalog.objects.values_list('quality', flat=True).distinct().order_by('quality')
    
    context = {
        'page_obj': page_obj,
        'eras': eras,
        'qualities': qualities,
        'era_filter': era,
        'quality_filter': quality,
        'query': query,
    }
    return render(request, 'catalog/song_list.html', context)

def song_detail(request, song_id):
    """Display detailed information about a specific song"""
    song = get_object_or_404(CartiCatalog, id=song_id)
    
    # Get songs from the same era for recommendations
    related_songs = CartiCatalog.objects.filter(era=song.era).exclude(id=song.id)[:5]
    
    context = {
        'song': song,
        'related_songs': related_songs,
    }
    return render(request, 'catalog/song_detail.html', context)