from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import models
from .models import CartiCatalog, SheetTab, SongMetadata

def index(request):
    """Home page with stats and recent songs"""
    song_count = CartiCatalog.objects.count()
    era_count = CartiCatalog.objects.values('era').distinct().count()
    sheet_tab_count = SheetTab.objects.count()
    
    # Get recent songs with tab information
    recent_songs = CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab').all().order_by('-id')[:10]
    
    # Add sheet tab info to recent songs
    for song in recent_songs:
        try:
            song.primary_tab_name = song.metadata.sheet_tab.name if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab else "Unknown"
            song.subsection_name = song.metadata.subsection if hasattr(song, 'metadata') and song.metadata and song.metadata.subsection else None
        except (SongMetadata.DoesNotExist, AttributeError):
            song.primary_tab_name = "Unknown"
            song.subsection_name = None
            
        # Get secondary categories/tabs
        try:
            secondary_tabs = [category.sheet_tab for category in song.categories.all()]
            song.secondary_tab_names = [tab.name for tab in secondary_tabs]
        except Exception:
            song.secondary_tab_names = []
        
        # All tabs combined
        all_tab_names = [song.primary_tab_name] + song.secondary_tab_names
        song.all_tab_names = list(set(all_tab_names))  # Remove duplicates
    
    # Get popular tabs (count both primary and secondary assignments)
    from django.db.models import Count, Q
    
    primary_counts = SheetTab.objects.annotate(
        primary_count=Count('songs')
    )
    
    secondary_counts = SheetTab.objects.annotate(
        secondary_count=Count('categorized_songs')
    )
    
    # Combine counts
    tab_counts = {}
    for tab in primary_counts:
        tab_counts[tab.id] = {
            'tab': tab,
            'count': tab.primary_count,
        }
    
    for tab in secondary_counts:
        if tab.id in tab_counts:
            tab_counts[tab.id]['count'] += tab.secondary_count
        else:
            tab_counts[tab.id] = {
                'tab': tab,
                'count': tab.secondary_count,
            }
    
    # Sort by count and get top 5
    popular_tabs = sorted(
        tab_counts.values(), 
        key=lambda x: x['count'], 
        reverse=True
    )[:5]
    
    context = {
        'song_count': song_count,
        'era_count': era_count,
        'sheet_tab_count': sheet_tab_count,
        'recent_songs': recent_songs,
        'popular_tabs': popular_tabs,
    }
    return render(request, 'catalog/index.html', context)

def song_list(request):
    """List all songs with filtering"""
    # Get filter parameters
    era = request.GET.get('era', '')
    quality = request.GET.get('quality', '')
    sheet_tab_id = request.GET.get('sheet_tab', '')
    query = request.GET.get('q', '')
    
    # Start with all songs - use select_related to optimize queries for metadata
    songs = CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab').all()
    
    # Apply filters
    if era:
        songs = songs.filter(era=era)
    if quality:
        songs = songs.filter(quality=quality)
    if sheet_tab_id:
        # Look for songs either with primary tab or secondary category
        sheet_tab_id = int(sheet_tab_id)
        songs = songs.filter(
            Q(metadata__sheet_tab_id=sheet_tab_id) | 
            Q(categories__sheet_tab_id=sheet_tab_id)
        ).distinct()
    if query:
        songs = songs.filter(Q(name__icontains=query) | Q(notes__icontains=query))
    
    # Add sheet tab info to song objects
    songs_with_tabs = []
    for song in songs:
        # Get primary tab
        try:
            song.primary_tab_name = song.metadata.sheet_tab.name if song.metadata and song.metadata.sheet_tab else "Unknown"
            song.subsection_name = song.metadata.subsection if song.metadata and song.metadata.subsection else None
        except (SongMetadata.DoesNotExist, AttributeError):
            song.primary_tab_name = "Unknown"
            song.subsection_name = None
        
        # Get secondary categories
        try:
            secondary_tabs = [category.sheet_tab for category in song.categories.all()]
            song.secondary_tab_names = [tab.name for tab in secondary_tabs]
        except Exception:
            song.secondary_tab_names = []
        
        # All tabs combined
        all_tab_names = [song.primary_tab_name] + song.secondary_tab_names
        song.all_tab_names = list(set(all_tab_names))  # Remove duplicates
        
        songs_with_tabs.append(song)
    
    # Pagination
    paginator = Paginator(songs_with_tabs, 25)  # Show 25 songs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    eras = CartiCatalog.objects.values_list('era', flat=True).distinct().order_by('era')
    qualities = CartiCatalog.objects.values_list('quality', flat=True).distinct().order_by('quality')
    sheet_tabs = SheetTab.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'eras': eras,
        'qualities': qualities,
        'sheet_tabs': sheet_tabs,
        'era_filter': era,
        'quality_filter': quality,
        'sheet_tab_filter': sheet_tab_id,
        'query': query,
    }
    return render(request, 'catalog/song_list.html', context)

def song_detail(request, song_id):
    """Display detailed information about a specific song"""
    # Use select_related to optimize query and prefetch_related for categories
    song = get_object_or_404(
        CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab'), 
        id=song_id
    )
    
    # Get songs from the same era for recommendations
    related_songs = CartiCatalog.objects.filter(era=song.era).exclude(id=song.id)[:5]
    
    # Add explicit attributes for primary sheet tab and subsection
    try:
        song.primary_tab_name = song.metadata.sheet_tab.name if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab else "Unknown"
        song.subsection_name = song.metadata.subsection if hasattr(song, 'metadata') and song.metadata and song.metadata.subsection else None
    except (SongMetadata.DoesNotExist, AttributeError):
        song.primary_tab_name = "Unknown"
        song.subsection_name = None
    
    # Get secondary categories/tabs
    try:
        secondary_tabs = [category.sheet_tab for category in song.categories.all()]
        song.secondary_tab_names = [tab.name for tab in secondary_tabs]
    except Exception:
        song.secondary_tab_names = []
    
    # All tabs combined
    all_tab_names = [song.primary_tab_name] + song.secondary_tab_names
    song.all_tab_names = list(set(all_tab_names))  # Remove duplicates
    
    context = {
        'song': song,
        'related_songs': related_songs,
    }
    return render(request, 'catalog/song_detail.html', context)