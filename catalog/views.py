from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import models
from django.template.defaulttags import register
import re
from .models import CartiCatalog, SheetTab, SongMetadata

# Add template filter to get items from a list by index
@register.filter
def get_item(lst, index):
    try:
        return lst[index]
    except:
        return None

def index(request):
    """Home page with stats and recent songs"""
    song_count = CartiCatalog.objects.count()
    era_count = CartiCatalog.objects.values('era').distinct().count()
    
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
            
            # Get emoji tabs that actually exist for this song
            song.emoji_tab_names = []
            song.other_tab_names = []
            
            # Separate emoji and non-emoji tabs - handle all emoji tabs consistently
            # Create a mapping of emoji to their respective tab names
            emoji_tab_map = {
                "🏆": "🏆 Grails",
                "🥇": "🥇 Wanted",
                "⭐": "⭐ Best Of",
                "✨": "✨ Special",
                "🗑️": "🗑️ Worst Of",
                "🤖": "🤖 AI Tracks"
            }
            
            for tab in song.secondary_tab_names:
                # Check if this is an emoji tab
                is_emoji_tab = False
                for emoji, tab_name in emoji_tab_map.items():
                    if tab == tab_name:
                        # Only add emoji tab if song name starts with matching emoji
                        if song.name and song.name.startswith(emoji):
                            song.emoji_tab_names.append(tab)
                        is_emoji_tab = True
                        break
                
                # If not an emoji tab, add to other tabs
                if not is_emoji_tab:
                    song.other_tab_names.append(tab)
        except Exception:
            song.secondary_tab_names = []
            song.emoji_tab_names = []
            song.other_tab_names = []
        
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
    producer = request.GET.get('producer', '')
    type_filter = request.GET.get('type', '')
    
    # Start with all songs - use select_related to optimize queries for metadata
    songs = CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab').all()
    
    # Apply filters
    if era:
        songs = songs.filter(era=era)
    if quality:
        songs = songs.filter(quality=quality)
    if type_filter:
        songs = songs.filter(type=type_filter)
    if producer:
        # Producer filter works on song name or notes fields
        # Using a more general approach to find the producer name anywhere in the production credits
        songs = songs.filter(
            Q(name__iregex=r'prod(?:\.|\s+by)?\s+.*?\b' + producer + r'\b') |
            Q(name__iregex=r'produced\s+by\s+.*?\b' + producer + r'\b') |
            Q(notes__iregex=r'prod(?:\.|\s+by)?\s+.*?\b' + producer + r'\b') |
            Q(notes__iregex=r'produced\s+by\s+.*?\b' + producer + r'\b') |
            # Also check for cases where the producer is explicitly mentioned
            Q(name__icontains=producer) |
            Q(notes__icontains=f"producer: {producer}") |
            Q(notes__icontains=f"produced by {producer}")
        )
        
    if sheet_tab_id:
        # Handle emoji tabs consistently - only include songs with matching emoji prefix
        try:
            sheet_tab_id = int(sheet_tab_id)
            sheet_tab = SheetTab.objects.get(id=sheet_tab_id)
            
            # Create a mapping of emoji tabs to their emoji prefixes
            emoji_tab_map = {
                "🏆 Grails": "🏆",
                "🥇 Wanted": "🥇",
                "⭐ Best Of": "⭐",
                "✨ Special": "✨",
                "🗑️ Worst Of": "🗑️",
                "🤖 AI Tracks": "🤖"
            }
            
            # Check if this is an emoji tab
            if sheet_tab.name in emoji_tab_map:
                # For any emoji tab, only include songs with matching emoji prefix
                emoji_prefix = emoji_tab_map[sheet_tab.name]
                songs = songs.filter(name__startswith=emoji_prefix).distinct()
            else:
                # For non-emoji tabs, use the normal query
                songs = songs.filter(
                    Q(metadata__sheet_tab_id=sheet_tab_id) | 
                    Q(categories__sheet_tab_id=sheet_tab_id)
                ).distinct()
        except (ValueError, SheetTab.DoesNotExist):
            # If there's any error, fall back to normal filtering
            songs = songs.filter(
                Q(metadata__sheet_tab_id=sheet_tab_id) | 
                Q(categories__sheet_tab_id=sheet_tab_id)
            ).distinct()
    if query:
        songs = songs.filter(Q(name__icontains=query) | Q(notes__icontains=query))
    
    # Track if we're filtering for the Released tab
    is_released_tab = False
    if sheet_tab_id:
        try:
            tab = SheetTab.objects.get(id=sheet_tab_id)
            is_released_tab = (tab.name == "Released")
        except SheetTab.DoesNotExist:
            pass
    
    # Add sheet tab info to song objects and prepare for album sorting
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
            
            # Get emoji tabs that actually exist for this song
            song.emoji_tab_names = []
            song.other_tab_names = []
            
            # Separate emoji and non-emoji tabs - handle all emoji tabs consistently
            # Create a mapping of emoji to their respective tab names
            emoji_tab_map = {
                "🏆": "🏆 Grails",
                "🥇": "🥇 Wanted",
                "⭐": "⭐ Best Of",
                "✨": "✨ Special",
                "🗑️": "🗑️ Worst Of",
                "🤖": "🤖 AI Tracks"
            }
            
            # Get the current filtered tab (if any)
            current_filtered_tab_name = None
            if sheet_tab_id:
                try:
                    current_filtered_tab = SheetTab.objects.get(id=sheet_tab_id)
                    current_filtered_tab_name = current_filtered_tab.name
                except SheetTab.DoesNotExist:
                    pass
            
            for tab in song.secondary_tab_names:
                # Skip adding this tab if we're already filtering by it
                if tab == current_filtered_tab_name:
                    continue
                    
                # Check if this is an emoji tab
                is_emoji_tab = False
                for emoji, tab_name in emoji_tab_map.items():
                    if tab == tab_name:
                        # Only add emoji tab if song name starts with matching emoji
                        if song.name and song.name.startswith(emoji):
                            song.emoji_tab_names.append(tab)
                        is_emoji_tab = True
                        break
                
                # If not an emoji tab, add to other tabs
                if not is_emoji_tab:
                    song.other_tab_names.append(tab)
        except Exception as e:
            print(f"ERROR processing {song.name}: {str(e)}")
            song.secondary_tab_names = []
            song.emoji_tab_names = []
            song.other_tab_names = []
        
        # All tabs combined
        all_tab_names = [song.primary_tab_name] + song.secondary_tab_names
        song.all_tab_names = list(set(all_tab_names))  # Remove duplicates
        
        # For album sorting - extract album name and track number
        if is_released_tab or song.primary_tab_name == "Released":
            # Store the result of the properties in different attributes for template use
            # Only keep official albums, skip unreleased ones
            album_name = song.album_name
            if album_name and "(Official)" in album_name:
                song.display_album_name = album_name
                song.display_track_number = song.album_track_number
            else:
                song.display_album_name = None
                song.display_track_number = None
        else:
            song.display_album_name = None
            song.display_track_number = None
        
        songs_with_tabs.append(song)
    
    # Sort songs by album and track number for Released tab
    if is_released_tab:
        # Group songs by album
        albums = {}
        versions = []  # To store version variants
        non_album_songs = []
        
        for song in songs_with_tabs:
            # Check if this is a version variant (contains [V])
            import re
            is_version = re.search(r'\s*\[V\d+\]', song.name or "")
            
            if song.display_album_name and not is_version:
                # Regular album track (original)
                if song.display_album_name not in albums:
                    albums[song.display_album_name] = []
                albums[song.display_album_name].append(song)
            elif song.display_album_name and is_version:
                # Version variant - add to separate list
                versions.append(song)
            else:
                non_album_songs.append(song)
        
        # Sort each album's songs by track number and add placeholder tracks
        sorted_songs = []
        
        # Define order of official albums to display at the top
        official_album_order = [
            "Playboi Carti (Official)",
            "Die Lit (Official)",
            "Whole Lotta Red (Official)",
            "Young Mi$fit (Official)",
        ]
        
        # First add official albums in order
        for album_name in official_album_order:
            if album_name in albums:
                album_songs = albums.pop(album_name)  # Remove from dict after processing
                # Sort by track number if available 
                album_songs.sort(key=lambda s: (s.display_track_number or 999, s.name))
                
                # Mark only the first song as having a header and only the last as having a footer
                for i, song in enumerate(album_songs):
                    song.is_in_album_group = True
                    song.album_group_name = album_name
                    
                    # Only the first song in each album gets a header
                    if i == 0:
                        song.needs_album_header = True
                    else:
                        song.needs_album_header = False
                    
                    # Only the last song in each album gets a footer
                    if i == len(album_songs) - 1:
                        song.needs_album_footer = True
                    else:
                        song.needs_album_footer = False
                
                sorted_songs.extend(album_songs)
        
        # Now process any remaining albums (non-official)
        for album_name, album_songs in albums.items():
            # Sort by track number if available
            album_songs.sort(key=lambda s: (s.display_track_number or 999, s.name))
            sorted_songs.extend(album_songs)
        
        # Add songs without album information at the end
        sorted_songs.extend(non_album_songs)
        
        # Add version variants at the very end, after all regular songs
        # Sort versions to group them by original track and then by version number
        if versions:
            versions.sort(key=lambda s: (
                re.sub(r'\s*\[V\d+\].*', '', s.name or ""),  # Group by base name
                re.search(r'\[V(\d+)\]', s.name or "").group(1) if re.search(r'\[V(\d+)\]', s.name or "") else "0"  # Then by version number
            ))
            sorted_songs.extend(versions)
            
        songs_with_tabs = sorted_songs
    
    # Pagination
    paginator = Paginator(songs_with_tabs, 25)  # Show 25 songs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options - filter out eras with only one song
    from django.db.models import Count
    era_counts = CartiCatalog.objects.values('era').annotate(count=Count('id')).filter(count__gt=1).order_by('era')
    eras = [era['era'] for era in era_counts if era['era']]  # Only include non-empty eras
    
    qualities = CartiCatalog.objects.values_list('quality', flat=True).distinct().order_by('quality')
    
    # Get unique type values for filter
    types = CartiCatalog.objects.values_list('type', flat=True).distinct().order_by('type')
    types = [t for t in types if t and t not in ["NaN", "nan"]]  # Filter out None and NaN values
    # Custom ordering for specific tabs
    tab_order_map = {
        'Released': 1,
        'Unreleased': 2,
        '🏆 Grails': 3,
        '🥇 Wanted': 4,
        '⭐ Best Of': 5,
        '✨ Special': 6,
        '🤖 AI Tracks': 7,
        '🗑️ Worst Of': 8,
        'OG Files': 9,
        'Recent': 10,
        'Stems': 11,
        'Tracklists': 12,
    }
    
    # Sort tabs with custom order first, then alphabetically
    sheet_tabs = sorted(
        SheetTab.objects.all(),
        key=lambda tab: (tab_order_map.get(tab.name, 999), tab.name)
    )
    
    # Get top producers
    top_producers = [
        "Pi'erre Bourne",
        "Ethereal",
        "MexikoDro",
        "Art Dealer",
        "Richie Souf",
        "F1lthy",
        "Metro Boomin",
        "ICYTWAT",
        "StarBoy",
        "Southside",
        "Maaly Raw",
        "Juberlee",
        "TM88",
        "Cardo",
        "DP Beats"
    ]
    
    context = {
        'page_obj': page_obj,
        'eras': eras,
        'qualities': qualities,
        'types': types,
        'sheet_tabs': sheet_tabs,
        'top_producers': top_producers,
        'era_filter': era,
        'quality_filter': quality,
        'type_filter': type_filter,
        'sheet_tab_filter': sheet_tab_id,
        'producer_filter': producer,
        'query': query,
    }
    return render(request, 'catalog/song_list.html', context)

def media_page(request):
    """Media hub page with links to different media categories"""
    # Get counts for each media type if we had models implemented
    art_count = 0  # Replace with ArtMedia.objects.count() when implemented
    interviews_count = 0
    fit_pics_count = 0
    social_media_count = 0
    
    context = {
        'art_count': art_count,
        'interviews_count': interviews_count,
        'fit_pics_count': fit_pics_count,
        'social_media_count': social_media_count
    }
    return render(request, 'catalog/media.html', context)

def art_page(request):
    """Art page displaying album covers, single art, etc."""
    # Get filter parameters
    era_filter = request.GET.get('era', '')
    type_filter = request.GET.get('type', '')
    used_filter = request.GET.get('used', '')
    query = request.GET.get('q', '')
    
    # Sample art data (placeholder until database is implemented)
    art_items = [
        {
            'id': 1,
            'name': 'TOO FLY KID',
            'era': 'Aviation Class',
            'notes': 'unknown purpose',
            'image_url': 'https://placehold.co/400x400',
            'media_type': 'Unknown',
            'was_used': False,
            'links': ''
        },
        {
            'id': 2,
            'name': 'Killing Me Softly',
            'era': 'Killing Me Softly',
            'notes': 'Coverart for Carti\'s 2010 or 2011 project "Killing Me Softly. The album uses the same image as it\'s cover as Nas\'s NASIR, even though the album was concieved 6 years before NASIR.',
            'image_url': 'https://placehold.co/400x400',
            'media_type': 'Album Cover',
            'was_used': True,
            'links': 'https://yungcarti.tumblr.com/image/4992098042'
        },
        {
            'id': 3,
            'name': 'The High Chronicals',
            'era': 'THC: The High Chronicals',
            'notes': 'The art for Playboi Carti\'s (then known as $ir Cartier) mixtape "The High Chronicals"',
            'image_url': 'https://placehold.co/400x400',
            'media_type': 'Album Cover',
            'was_used': True,
            'links': 'https://imgur.com/6q1dUzi'
        },
        {
            'id': 4,
            'name': 'Living Reckless',
            'era': 'THC: The High Chronicals',
            'notes': 'Cover of Living Reckless',
            'image_url': 'https://placehold.co/400x400',
            'media_type': 'Single Art',
            'was_used': True,
            'links': ''
        },
        {
            'id': 5,
            'name': 'Carolina Blue [OG Cover]',
            'era': 'THC: The High Chronicals',
            'notes': 'Carolina Blue\'s OG Cover without any edits, found in Carti\'s Tumblr.',
            'image_url': 'https://placehold.co/400x400',
            'media_type': 'Single Art',
            'was_used': False,
            'links': 'https://yungcarti.tumblr.com/post/16736117122'
        }
    ]
    
    # Apply filters
    if era_filter:
        art_items = [item for item in art_items if item['era'] == era_filter]
    if type_filter:
        art_items = [item for item in art_items if item['media_type'] == type_filter]
    if used_filter:
        was_used = used_filter == 'used'
        art_items = [item for item in art_items if item['was_used'] == was_used]
    if query:
        art_items = [item for item in art_items if query.lower() in item['name'].lower() or (item['notes'] and query.lower() in item['notes'].lower())]
    
    # Get filter options
    eras = sorted(list(set(item['era'] for item in art_items if item['era'])))
    media_types = sorted(list(set(item['media_type'] for item in art_items if item['media_type'])))
    
    # Pagination
    paginator = Paginator(art_items, 12)  # Show 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'eras': eras,
        'media_types': media_types,
        'era_filter': era_filter,
        'type_filter': type_filter,
        'used_filter': used_filter,
        'query': query
    }
    return render(request, 'catalog/art.html', context)

def song_detail(request, song_id):
    """Display detailed information about a specific song"""
    # Use select_related to optimize query and prefetch_related for categories
    song = get_object_or_404(
        CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab'), 
        id=song_id
    )
    
    # Get songs from the same era for recommendations
    related_songs = CartiCatalog.objects.filter(era=song.era).exclude(id=song.id)[:5]
    
    # Clean song name by removing version indicators like [V2], [V3], etc.
    import re
    if song.name:
        song.clean_name = re.sub(r'\s*\[V\d+\].*', '', song.name)
    
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
        
        # Get emoji tabs that actually exist for this song
        song.emoji_tab_names = []
        song.other_tab_names = []
        
        # Separate emoji and non-emoji tabs - handle all emoji tabs consistently
        # Create a mapping of emoji to their respective tab names
        emoji_tab_map = {
            "🏆": "🏆 Grails",
            "🥇": "🥇 Wanted",
            "⭐": "⭐ Best Of",
            "✨": "✨ Special",
            "🗑️": "🗑️ Worst Of",
            "🤖": "🤖 AI Tracks"
        }
        
        # Track processed tabs to avoid duplicates
        processed_tabs = set()
        
        for tab in song.secondary_tab_names:
            # Skip if we already processed this tab
            if tab in processed_tabs:
                continue
                
            processed_tabs.add(tab)
            
            # Check if this is an emoji tab
            is_emoji_tab = False
            for emoji, tab_name in emoji_tab_map.items():
                if tab == tab_name:
                    # Only add emoji tab if song name starts with matching emoji
                    if song.name and song.name.startswith(emoji):
                        song.emoji_tab_names.append(tab)
                    is_emoji_tab = True
                    break
            
            # If not an emoji tab, add to other tabs
            if not is_emoji_tab:
                song.other_tab_names.append(tab)
    except Exception:
        song.secondary_tab_names = []
        song.emoji_tab_names = []
        song.other_tab_names = []
    
    # All tabs combined
    all_tab_names = [song.primary_tab_name] + song.secondary_tab_names
    song.all_tab_names = list(set(all_tab_names))  # Remove duplicates
    
    # Extract album information
    album_name = song.album_name
    if album_name and "(Official)" in album_name:
        song.display_album_name = album_name
        song.display_track_number = song.album_track_number
    else:
        song.display_album_name = None
        song.display_track_number = None
    
    # Get similar songs from the same album if applicable
    album_related_songs = []
    if song.display_album_name:
        # Extract the album name without the (Official)/(Unreleased) suffix
        clean_album_name = song.display_album_name.split(' (')[0]
        
        # Find other songs from the same album - use more complex query to find more matches
        album_related_songs = []
        
        # First search: direct album name mentions
        direct_matches = CartiCatalog.objects.filter(
            notes__icontains=clean_album_name
        ).exclude(id=song.id)
        
        # Second search: track number mentions that might be from this album
        track_pattern_matches = CartiCatalog.objects.filter(
            notes__iregex=r'[Tt]rack\s+\d+\s+(?:on|of|from)'
        ).exclude(id=song.id)
        
        # Combine and filter potential matches
        all_potential_matches = list(direct_matches) + list(track_pattern_matches)
        
        # Separate regular tracks from version variants
        regular_tracks = []
        version_variants = []
        
        # Process each song to check if it's truly related
        for potential_song in all_potential_matches:
            # Check if this is a version variant
            is_version = re.search(r'\s*\[V\d+\]', potential_song.name or "")
            
            # Clean song name from versions to prevent duplicates
            if potential_song.name:
                potential_song.clean_name = re.sub(r'\s*\[V\d+\].*', '', potential_song.name)
                
            # Get album name and track number for this song
            potential_song.display_album_name = potential_song.album_name
            potential_song.display_track_number = potential_song.album_track_number
            
            # Check if this song belongs to the same album as our main song
            same_album = False
            if potential_song.display_album_name:
                potential_album_clean = potential_song.display_album_name.split(' (')[0]
                same_album = (potential_album_clean.lower() == clean_album_name.lower())
            
            # If it's from the same album and has a track number
            if same_album and potential_song.display_track_number:
                if is_version:
                    # Version variant
                    version_variants.append(potential_song)
                else:
                    # Only add regular tracks if we don't already have this track number
                    existing_track_nums = [s.display_track_number for s in regular_tracks]
                    if potential_song.display_track_number not in existing_track_nums:
                        regular_tracks.append(potential_song)
        
        # Add regular tracks to the album tracklist
        album_related_songs = regular_tracks
        
        # Add version variants after the regular tracks for display after the album section
        song.version_variants = version_variants
        
        # Add potential missing tracks (for complete 1-N tracks in album)
        # Get the maximum track number in the album
        max_track = 0
        for related_song in album_related_songs:
            if related_song.display_track_number and related_song.display_track_number > max_track:
                max_track = related_song.display_track_number
        
        if song.display_track_number and song.display_track_number > max_track:
            max_track = song.display_track_number
            
        # Limit to reasonable album size
        max_track = min(max_track, 20)
        
        # Find existing track numbers
        existing_tracks = set()
        for related_song in album_related_songs:
            if related_song.display_track_number:
                existing_tracks.add(related_song.display_track_number)
                
        if song.display_track_number:
            existing_tracks.add(song.display_track_number)
            
        # Add placeholders for missing tracks to make the list complete
        for track_num in range(1, max_track + 1):
            if track_num not in existing_tracks:
                # Look for a track name in the corresponding track dictionaries
                track_name = None
                if clean_album_name == "Playboi Carti":
                    # Find track name from self-titled album
                    for name, num in CartiCatalog.selftitled_tracks.items():
                        if num == track_num:
                            track_name = name
                            break
                elif clean_album_name == "Die Lit":
                    # Find track name from Die Lit
                    for name, num in CartiCatalog.die_lit_tracks.items():
                        if num == track_num:
                            track_name = name
                            break
                elif clean_album_name == "Whole Lotta Red":
                    # Find track name from WLR
                    for name, num in CartiCatalog.wlr_tracks.items():
                        if num == track_num:
                            track_name = name
                            break
                elif clean_album_name == "Young Mi$fit":
                    # Find track name from Young Mi$fit
                    for name, num in CartiCatalog.young_misfit_tracks.items():
                        if num == track_num:
                            track_name = name
                            break
                
                # Create the placeholder with the proper track name if found
                display_name = track_name if track_name else f'Track {track_num} - Unknown'
                placeholder = type('PlaceholderSong', (), {
                    'id': f'placeholder-{track_num}',
                    'name': display_name,
                    'display_track_number': track_num,
                    'is_placeholder': True
                })
                album_related_songs.append(placeholder)
                
        # Sort by track number
        album_related_songs = sorted(album_related_songs, key=lambda s: s.display_track_number or 999)
    
    context = {
        'song': song,
        'related_songs': related_songs,
        'album_related_songs': album_related_songs,
    }
    return render(request, 'catalog/song_detail.html', context)