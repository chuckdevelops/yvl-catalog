#!/usr/bin/env python3
"""
Script to fix the CartiCatalog API issues in views.py
"""
import re
import os
import sys

def main():
    # Read views.py file
    with open('catalog/views.py', 'r') as f:
        content = f.read()

    # Add necessary imports
    if "import os" not in content:
        content = content.replace(
            "import re",
            "import re\nimport os\nimport traceback"
        )

    # Fix all preview_file_exists checks
    content = content.replace(
        "'preview_file_exists': song.preview_file_exists,", 
        "'preview_file_exists': os.path.exists(os.path.join(settings.MEDIA_ROOT, 'previews', f'{song.id}.mp3')),"
    )

    # Fix all preview_audio_url checks
    content = content.replace(
        "'preview_audio_url': f'/media/previews/{song.id}.mp3' if song.preview_file_exists else '',", 
        "'preview_audio_url': f'/media/previews/{song.id}.mp3' if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'previews', f'{song.id}.mp3')) else song.preview_url or '',"
    )

    # Add try-except block to api_songs_list if needed
    api_songs_list_pattern = re.compile(r'def api_songs_list\(request\):\s+"""API endpoint for getting songs with filters"""(?!\s+try:)')
    if api_songs_list_pattern.search(content):
        content = api_songs_list_pattern.sub(
            'def api_songs_list(request):\n    """API endpoint for getting songs with filters"""\n    try:', 
            content
        )

    # Add except block at the end of api_songs_list if needed
    end_api_songs_list_pattern = re.compile(r'return JsonResponse\(response_data\)\s*(?!\s+except)')
    if end_api_songs_list_pattern.search(content):
        content = end_api_songs_list_pattern.sub(
            'return JsonResponse(response_data)\n\n    except Exception as e:\n        error_details = traceback.format_exc()\n        return JsonResponse({\n            "error": str(e),\n            "details": error_details\n        }, status=500)', 
            content
        )

    # Add try-except block to api_song_detail if needed
    api_song_detail_pattern = re.compile(r'def api_song_detail\(request, song_id\):\s+"""API endpoint for getting song details"""(?!\s+try:)')
    if api_song_detail_pattern.search(content):
        content = api_song_detail_pattern.sub(
            'def api_song_detail(request, song_id):\n    """API endpoint for getting song details"""\n    try:', 
            content
        )

    # Fix any direct references to preview_file_exists attribute in api_song_detail
    song_detail_pattern = re.compile(r'(song\.preview_file_exists)\s*=\s*os\.path\.exists\(preview_file_path\)')
    if song_detail_pattern.search(content):
        # This pattern is fine, as it's setting the attribute dynamically
        pass
    else:
        # Add property comment for documentation
        if '# Note: preview_file_exists is not a model attribute but set dynamically' not in content:
            content = content.replace(
                'def song_detail(request, song_id):',
                '# Note: preview_file_exists is not a model attribute but set dynamically\ndef song_detail(request, song_id):'
            )
    
    # Check if the CartiCatalog model could have a preview_file_exists property added
    # Create a property definition replacement
    model_property = """
    @property
    def preview_file_exists(self):
        \"\"\"Check if a preview file exists for this song\"\"\"
        if not self.id:
            return False
        import os
        from django.conf import settings
        preview_path = os.path.join(settings.MEDIA_ROOT, 'previews', f'{self.id}.mp3')
        return os.path.exists(preview_path)
    """
    
    # Write the instructions for model changes to SOLUTION.md
    with open('SOLUTION.md', 'a') as f:
        f.write("\n\n## API Fix Implementation\n")
        f.write("The preview_file_exists attribute issue has been fixed in multiple places:\n\n")
        f.write("1. Changed all direct references to `song.preview_file_exists` to use direct file checking with `os.path.exists`\n")
        f.write("2. Added proper error handling with try/except blocks in API endpoints\n")
        f.write("3. Created a consistent pattern for audio file path checking\n\n")
        f.write("### Optional Future Enhancement\n")
        f.write("For better code structure, consider adding the following property to the CartiCatalog model:\n\n")
        f.write("```python\n")
        f.write(model_property)
        f.write("```\n\n")
        f.write("This would provide a consistent interface for checking file existence without requiring code changes in multiple places.\n")

    # Write the fixed content
    with open('catalog/views.py', 'w') as f:
        f.write(content)
    
    # Create a backup of the original fixed_api_songs_list.py
    if os.path.exists('fixed_api_songs_list.py'):
        with open('fixed_api_songs_list.py', 'r') as f:
            backup_content = f.read()
        with open('fixed_api_songs_list.py.bak', 'w') as f:
            f.write(backup_content)
            
    # Write an improved version of fixed_api_songs_list.py
    with open('fixed_api_songs_list.py', 'w') as f:
        f.write('''def api_songs_list(request):
    """API endpoint for getting songs with filters"""
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
            except (SheetTab.DoesNotExist, ValueError):
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
            except (SongMetadata.DoesNotExist, AttributeError):
                pass
            
            # Get secondary categories/tabs
            secondary_tab_names = []
            emoji_tab_names = []
            other_tab_names = []
            
            try:
                secondary_tabs = [category.sheet_tab for category in song.categories.all()]
                secondary_tab_names = [tab.name for tab in secondary_tabs]
                
                # Process emoji tabs
                emoji_tab_map = {
                    "🏆": "🏆 Grails",
                    "🥇": "🥇 Wanted",
                    "⭐": "⭐ Best Of",
                    "✨": "✨ Special",
                    "🗑️": "🗑️ Worst Of",
                    "🤖": "🤖 AI Tracks"
                }
                
                for tab in secondary_tab_names:
                    is_emoji_tab = False
                    for emoji, tab_name in emoji_tab_map.items():
                        if tab == tab_name:
                            if song.name and song.name.startswith(emoji):
                                emoji_tab_names.append(tab)
                            is_emoji_tab = True
                            break
                    
                    if not is_emoji_tab:
                        other_tab_names.append(tab)
            except Exception:
                pass
            
            # Check if preview file exists using direct file check
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
                'available_length': song.available_length or '',
                'track_length': song.track_length or '',
                'producer': song.producer or '',
                'features': song.features or '',
                'notes': song.notes or '',
                'secondary_tab_names': secondary_tab_names,
                'emoji_tab_names': emoji_tab_names,
                'other_tab_names': other_tab_names,
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
        
        # Define top producers
        top_producers = [
            "Pi'erre Bourne",
            "Art Dealer",
            "F1lthy",
            "Richie Souf",
            "Starboy",
            "Maaly Raw",
            "Metro Boomin",
            "Wheezy",
            "MexikoDro",
            "Ethereal",
            "TM88",
            "Cardo",
            "DP Beats"
        ]
        
        # Apply sorting
        if sort_field and sort_field != 'none':
            reverse_sort = sort_direction == 'desc'
            def get_sort_key(song):
                if sort_field == 'name':
                    return (song.get('name') or '').lower()
                elif sort_field == 'era':
                    return (song.get('era') or '').lower()
                elif sort_field == 'leak_date':
                    return song.get('leak_date') or ''
                elif sort_field == 'track_length':
                    return song.get('track_length') or ''
                elif sort_field == 'quality':
                    return (song.get('quality') or '').lower()
                elif sort_field == 'type':
                    return (song.get('type') or '').lower()
                return (song.get('name') or '').lower()
                    
            processed_songs.sort(key=get_sort_key, reverse=reverse_sort)
        
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
                'top_producers': top_producers,
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
        import traceback
        error_details = traceback.format_exc()
        return JsonResponse({
            'error': str(e),
            'details': error_details
        }, status=500)''')

    print("Fixed views.py and created comprehensive solution documentation!")

if __name__ == "__main__":
    main()