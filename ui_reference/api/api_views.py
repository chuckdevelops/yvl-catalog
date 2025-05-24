import os
import time
import json
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from .models import CartiCatalog, SheetTab, SongMetadata, SongCategory

def react_app(request, path=None):
    """
    Serve the React Single Page Application
    """
    return render(request, 'catalog/react_app.html', {
        'timestamp': int(time.time())  # For cache busting
    })

def api_home(request):
    """API endpoint for home page data"""
    try:
        # Get all songs for stats - limit to 20 recent ones for display
        songs = CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab').order_by('-id')[:20]
        
        # Calculate statistics
        total_songs = CartiCatalog.objects.count()
        distinct_eras = CartiCatalog.objects.values('era').distinct().count()
        
        # Get sheet tabs with counts
        sheet_tabs = []
        for tab in SheetTab.objects.all():
            # Count songs either having this as primary tab or in categories
            count = CartiCatalog.objects.filter(
                Q(metadata__sheet_tab=tab) | Q(categories__sheet_tab=tab)
            ).distinct().count()
            
            # Get icon and description based on name
            icon = '🎵'  # Default icon
            description = 'Song collection'
            
            if 'Grails' in tab.name:
                icon = '🏆'
                description = 'Top tier unreleased songs'
            elif 'Wanted' in tab.name:
                icon = '🥇'
                description = 'Highly anticipated leaks'
            elif 'Best Of' in tab.name:
                icon = '⭐'
                description = 'High quality tracks'
            elif 'Special' in tab.name:
                icon = '✨'
                description = 'Noteworthy tracks'
            elif 'Released' in tab.name:
                icon = '📀'
                description = 'Official releases'
            elif 'Unreleased' in tab.name:
                icon = '🎵'
                description = 'Unreleased songs'
            
            sheet_tabs.append({
                'id': tab.id,
                'name': tab.name.replace(f'{icon} ', '') if tab.name.startswith(icon) else tab.name,  # Remove icon from name if present
                'count': count,
                'icon': icon,
                'description': description
            })
        
        # Sort tabs by count (descending)
        sheet_tabs.sort(key=lambda x: x['count'], reverse=True)
        
        # Process recent songs for API
        recent_songs = []
        for song in songs:
            # Get primary tab info
            primary_tab_name = "Unknown"
            subsection_name = None
            
            try:
                if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab:
                    primary_tab_name = song.metadata.sheet_tab.name
                    subsection_name = song.metadata.subsection if song.metadata.subsection else None
            except Exception:
                pass
            
            # Check if preview file exists
            has_preview = os.path.exists(os.path.join(settings.MEDIA_ROOT, 'previews', f'{song.id}.mp3'))
            
            # Create the song data dictionary
            song_data = {
                'id': song.id,
                'name': song.name,
                'era': song.era or '',
                'type': song.type or '',
                'quality': song.quality or '',
                'primary_tab_name': primary_tab_name,
                'subsection_name': subsection_name,
                'leak_date': song.leak_date or '',
                'file_date': song.file_date or '',
                'producer': song.producer or '',
                'features': song.features or '',
                'preview_file_exists': has_preview,
                'preview_audio_url': f'/media/previews/{song.id}.mp3' if has_preview else song.preview_url or '',
            }
            
            recent_songs.append(song_data)
        
        # Create response
        response_data = {
            'stats': {
                'total_songs': total_songs,
                'distinct_eras': distinct_eras,
                'sheet_tabs': sheet_tabs
            },
            'recent_songs': recent_songs
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        error_details = traceback.format_exc()
        return JsonResponse({
            'error': str(e),
            'details': error_details
        }, status=500)

def api_songs(request):
    """API endpoint for songs list with filtering"""
    try:
        # Get query parameters
        era = request.GET.get('era', '')
        quality = request.GET.get('quality', '')
        type_filter = request.GET.get('type', '')
        sheet_tab_id = request.GET.get('sheet_tab', '')
        producer = request.GET.get('producer', '')
        query = request.GET.get('q', '')
        sort_field = request.GET.get('sort_field', 'name')
        sort_direction = request.GET.get('sort_direction', 'asc')
        
        # Get songs from database
        songs = CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab')
        
        # Apply filters
        if era:
            songs = songs.filter(era=era)
        if quality:
            songs = songs.filter(quality=quality)
        if type_filter:
            songs = songs.filter(type=type_filter)
        if sheet_tab_id:
            try:
                sheet_tab = SheetTab.objects.get(id=sheet_tab_id)
                # Look in both primary and secondary tabs
                songs = songs.filter(
                    Q(metadata__sheet_tab=sheet_tab) | Q(categories__sheet_tab=sheet_tab)
                ).distinct()
            except Exception:
                pass
        if producer:
            songs = songs.filter(Q(producer__icontains=producer))
        if query:
            songs = songs.filter(
                Q(name__icontains=query) | 
                Q(producer__icontains=query) | 
                Q(features__icontains=query) | 
                Q(notes__icontains=query)
            )
        
        # Process songs for the API
        processed_songs = []
        for song in songs:
            # Get primary tab info
            primary_tab_name = "Unknown"
            subsection_name = None
            
            try:
                if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab:
                    primary_tab_name = song.metadata.sheet_tab.name
                    subsection_name = song.metadata.subsection if song.metadata.subsection else None
            except Exception:
                pass
            
            # Check if preview file exists
            has_preview = os.path.exists(os.path.join(settings.MEDIA_ROOT, 'previews', f'{song.id}.mp3'))
            
            # Create the song data dictionary
            song_data = {
                'id': song.id,
                'name': song.name,
                'era': song.era or '',
                'type': song.type or '',
                'quality': song.quality or '',
                'primary_tab_name': primary_tab_name,
                'subsection_name': subsection_name,
                'leak_date': song.leak_date or '',
                'producer': song.producer or '',
                'features': song.features or '',
                'preview_file_exists': has_preview,
                'preview_audio_url': f'/media/previews/{song.id}.mp3' if has_preview else song.preview_url or '',
            }
            
            processed_songs.append(song_data)
        
        # Get filter options
        eras = list(CartiCatalog.objects.values_list('era', flat=True).distinct().order_by('era'))
        eras = [era for era in eras if era]
        
        qualities = list(CartiCatalog.objects.values_list('quality', flat=True).distinct().order_by('quality'))
        qualities = [q for q in qualities if q]
        
        types = list(CartiCatalog.objects.values_list('type', flat=True).distinct().order_by('type'))
        types = [t for t in types if t]
        
        sheet_tabs = [{'id': tab.id, 'name': tab.name} for tab in SheetTab.objects.all().order_by('name')]
        
        # Pagination
        page = int(request.GET.get('page', 1))
        items_per_page = int(request.GET.get('per_page', 40))
        paginator = Paginator(processed_songs, items_per_page)
        
        try:
            page_obj = paginator.page(page)
        except Exception:
            page_obj = paginator.page(1)
        
        # Create response
        response_data = {
            'songs': list(page_obj),
            'filters': {
                'eras': eras,
                'qualities': qualities,
                'types': types,
                'sheet_tabs': sheet_tabs,
                'current_filters': {
                    'era': era,
                    'quality': quality,
                    'type': type_filter,
                    'sheet_tab': sheet_tab_id,
                    'producer': producer,
                    'query': query,
                },
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'items_per_page': items_per_page
                }
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        error_details = traceback.format_exc()
        return JsonResponse({
            'error': str(e),
            'details': error_details
        }, status=500)

def api_song_detail(request, song_id):
    """API endpoint for song detail"""
    try:
        song = CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab').get(id=song_id)
        
        # Get primary tab info
        primary_tab_name = "Unknown"
        subsection_name = None
        
        try:
            if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab:
                primary_tab_name = song.metadata.sheet_tab.name
                subsection_name = song.metadata.subsection if song.metadata.subsection else None
        except Exception:
            pass
        
        # Check if preview file exists
        has_preview = os.path.exists(os.path.join(settings.MEDIA_ROOT, 'previews', f'{song.id}.mp3'))
        
        # Get secondary categories/tabs
        secondary_tab_names = []
        try:
            secondary_tabs = [category.sheet_tab for category in song.categories.all()]
            secondary_tab_names = [tab.name for tab in secondary_tabs]
        except Exception:
            pass
        
        # Create the song data dictionary
        song_data = {
            'id': song.id,
            'name': song.name,
            'era': song.era or '',
            'type': song.type or '',
            'quality': song.quality or '',
            'primary_tab_name': primary_tab_name,
            'subsection_name': subsection_name,
            'leak_date': song.leak_date or '',
            'file_date': song.file_date or '',
            'available_length': song.available_length or '',
            'track_length': song.track_length or '',
            'producer': song.producer or '',
            'features': song.features or '',
            'notes': song.notes or '',
            'secondary_tab_names': secondary_tab_names,
            'preview_file_exists': has_preview,
            'preview_audio_url': f'/media/previews/{song.id}.mp3' if has_preview else song.preview_url or '',
        }
        
        return JsonResponse(song_data)
        
    except CartiCatalog.DoesNotExist:
        return JsonResponse({'error': 'Song not found'}, status=404)
    except Exception as e:
        error_details = traceback.format_exc()
        return JsonResponse({
            'error': str(e),
            'details': error_details
        }, status=500)