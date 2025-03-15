from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Case, When, IntegerField
from django.db import models, transaction
from django.template.defaulttags import register
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import re
from .models import CartiCatalog, SheetTab, SongMetadata, SongVote, HomepageSettings

# Add template filter to get items from a list by index
@register.filter
def get_item(lst, index):
    try:
        return lst[index]
    except:
        return None

def index(request):
    """Home page with stats and recent songs"""
    # Count songs only once (even if they appear in multiple tabs)
    song_count = CartiCatalog.objects.distinct().count()
    era_count = CartiCatalog.objects.values('era').distinct().count()
    
    # Check if we have custom homepage settings enabled
    try:
        homepage_settings = HomepageSettings.objects.first()
        if homepage_settings and homepage_settings.enable_custom_homepage:
            # Use the custom homepage songs (max 10)
            recent_songs = homepage_settings.homepage_songs.select_related('metadata__sheet_tab')\
                .prefetch_related('categories__sheet_tab').all()[:10]
            if recent_songs.exists():
                # Convert to list as we're using a limited QuerySet
                recent_songs = list(recent_songs)
            else:
                # Fall back to Recent tab if no songs selected in settings
                raise HomepageSettings.DoesNotExist()
        else:
            # Fall back to Recent tab if custom homepage not enabled
            raise HomepageSettings.DoesNotExist()
    except (HomepageSettings.DoesNotExist, AttributeError):
        # Fall back to default behavior with Recent tab
        try:
            recent_tab = SheetTab.objects.get(name="Recent")
            # Get songs from the Recent tab, already sorted newest first by the management command
            recent_songs = CartiCatalog.objects.select_related('metadata__sheet_tab')\
                .prefetch_related('categories__sheet_tab')\
                .filter(categories__sheet_tab=recent_tab)\
                .distinct()[:10]
        except SheetTab.DoesNotExist:
            # Fallback: if Recent tab doesn't exist, just get newest songs by ID
            recent_songs = CartiCatalog.objects.select_related('metadata__sheet_tab')\
                .prefetch_related('categories__sheet_tab')\
                .all().order_by('-id')[:10]
                
        # If no songs found, fall back to the hardcoded priority list
        if not recent_songs.exists():
            # These are specific songs to display in the order specified
            specific_recent_songs = []
            recent_song_queries = [
                {'name': '🏆 Dancer', 'era': 'TMB Collab'},
                {'name': '🏆 Paramount', 'era': 'Whole Lotta Red'},
                {'name': 'DEMONSLURK', 'era': 'MUSIC'},
                {'name': '⭐ Not Real', 'era': 'Whole Lotta Red'},
                {'name': 'Cartier', 'era': 'Chucky Era'}
            ]
            
            # Find each song by name and era
            for query in recent_song_queries:
                match = CartiCatalog.objects.filter(
                    Q(name__icontains=query['name']) & 
                    Q(era__icontains=query['era'])
                ).first()
                if match:
                    specific_recent_songs.append(match)
            
            # Use our specific song list or fall back to most recent by ID
            if specific_recent_songs:
                recent_songs = specific_recent_songs
            else:
                recent_songs = CartiCatalog.objects.select_related('metadata__sheet_tab')\
                    .prefetch_related('categories__sheet_tab').all().order_by('-id')[:10]
    
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
    # Note: Count is already imported at the top, no need to reimport
    
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
            
            # Check if the Stems tab is explicitly selected
            stems_tab_selected = (sheet_tab.name == "Stems")
            
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
    else:
        # When no specific tab is selected, exclude songs from the Stems tab
        try:
            stems_tab = SheetTab.objects.filter(name="Stems").first()
            if stems_tab:
                songs = songs.exclude(
                    Q(metadata__sheet_tab_id=stems_tab.id) & 
                    ~Q(categories__sheet_tab__isnull=False)  # Only exclude if not in any other tab
                ).distinct()
        except Exception:
            pass  # If there's an error, don't apply the exclusion
            
    if query:
        songs = songs.filter(Q(name__icontains=query) | Q(notes__icontains=query))
    
    # Track if we're filtering for the Released tab or Recent tab
    is_released_tab = False
    is_recent_tab = False
    if sheet_tab_id:
        try:
            tab = SheetTab.objects.get(id=sheet_tab_id)
            is_released_tab = (tab.name == "Released")
            is_recent_tab = (tab.name == "Recent")
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
    
    # Sort songs by leak date for Recent tab (newest first)
    if is_recent_tab:
        import re
        from datetime import datetime
        
        # Define common date formats to try
        def parse_date(date_str):
            if not date_str:
                return None
                
            date_formats = [
                '%B %d, %Y',      # March 15, 2024
                '%b %d, %Y',      # Mar 15, 2024
                '%Y-%m-%d',       # 2024-03-15
                '%m/%d/%Y',       # 03/15/2024
                '%d %B %Y',       # 15 March 2024
                '%d %b %Y',       # 15 Mar 2024
                '%B %Y',          # March 2024
                '%b %Y',          # Mar 2024
                '%m/%Y',          # 03/2024
                '%Y',             # 2024
                '%m/%d/%y',       # 03/15/24
                '%d/%m/%y',       # 15/03/24
            ]
            
            # Try each format
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If no format matches, try to extract year at least
            year_match = re.search(r'20\d{2}', date_str)
            if year_match:
                year = year_match.group(0)
                return datetime(int(year), 1, 1)  # Default to Jan 1 of the year
                
            return None
        
        # Custom sorting function with date parsing
        def sort_by_leak_date(song):
            # Try leak_date first
            if hasattr(song, 'leak_date') and song.leak_date:
                date_obj = parse_date(song.leak_date)
                if date_obj:
                    return -date_obj.timestamp()  # Negative for descending order
            
            # Try file_date if leak_date wasn't available or couldn't be parsed
            if hasattr(song, 'file_date') and song.file_date:
                date_obj = parse_date(song.file_date)
                if date_obj:
                    return -date_obj.timestamp()  # Negative for descending order
            
            # Fall back to ID sorting if no date (bigger ID = more recent)
            return -song.id
        
        # Sort songs by leak date, newest first
        songs_with_tabs.sort(key=sort_by_leak_date)
        
    # Sort songs by album and track number for Released tab
    elif is_released_tab:
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
    # Get counts for each media type
    from .models import ArtMedia, Interview, FitPic, SocialMedia
    art_count = ArtMedia.objects.count()
    interviews_count = Interview.objects.count()
    fit_pics_count = FitPic.objects.count()
    social_media_count = SocialMedia.objects.count()
    
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
    
    # Get data from the database
    from .models import ArtMedia
    art_items = ArtMedia.objects.all()
    
    # Apply filters
    if era_filter:
        art_items = art_items.filter(era=era_filter)
    if type_filter:
        art_items = art_items.filter(media_type=type_filter)
    if used_filter:
        was_used = used_filter == 'used'
        art_items = art_items.filter(was_used=was_used)
    if query:
        art_items = art_items.filter(
            models.Q(name__icontains=query) | models.Q(notes__icontains=query)
        )
    
    # Get filter options from the database
    eras = ArtMedia.objects.values_list('era', flat=True).distinct().order_by('era')
    eras = [era for era in eras if era]  # Filter out None or empty values
    
    media_types = ArtMedia.objects.values_list('media_type', flat=True).distinct().order_by('media_type')
    media_types = [mt for mt in media_types if mt]  # Filter out None or empty values
    
    # If database is empty, provide sample data
    if not art_items.exists():
        # Create some sample placeholder items for initial display
        placeholders = [
            {
                'id': 1,
                'name': 'Album Cover Example',
                'era': 'Sample Era',
                'notes': 'This is a placeholder item since no art media has been imported yet.',
                'image_url': 'https://placehold.co/400x400',
                'media_type': 'Album Cover',
                'was_used': True,
                'links': ''
            },
            {
                'id': 2,
                'name': 'Single Art Example',
                'era': 'Sample Era',
                'notes': 'Run the import_art_media management command to import actual art data.',
                'image_url': 'https://placehold.co/400x400',
                'media_type': 'Single Art',
                'was_used': False,
                'links': ''
            }
        ]
        
        from django.forms.models import model_to_dict
        # Convert raw dicts to a structure similar to model instances for template compatibility
        class PlaceholderObj:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        art_items = [PlaceholderObj(item) for item in placeholders]
        eras = ["Sample Era"]
        media_types = ["Album Cover", "Single Art"]
    
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

def interviews_page(request):
    """Interviews page displaying interviews, conversations and media appearances"""
    # Get filter parameters
    era_filter = request.GET.get('era', '')
    type_filter = request.GET.get('type', '')
    available_filter = request.GET.get('available', '')
    query = request.GET.get('q', '')
    
    # Get data from the database
    from .models import Interview
    interviews = Interview.objects.all()
    
    # Apply filters
    if era_filter:
        interviews = interviews.filter(era=era_filter)
    if type_filter:
        interviews = interviews.filter(interview_type=type_filter)
    if available_filter:
        is_available = available_filter == 'yes'
        interviews = interviews.filter(available=is_available)
    if query:
        interviews = interviews.filter(
            models.Q(outlet__icontains=query) | 
            models.Q(subject_matter__icontains=query) | 
            models.Q(special_notes__icontains=query)
        )
    
    # Get filter options from the database
    eras = Interview.objects.values_list('era', flat=True).distinct().order_by('era')
    eras = [era for era in eras if era]  # Filter out None or empty values
    
    interview_types = Interview.objects.values_list('interview_type', flat=True).distinct().order_by('interview_type')
    interview_types = [it for it in interview_types if it]  # Filter out None or empty values
    
    # If database is empty, provide sample data
    if not interviews.exists():
        # Create some sample placeholder items for initial display
        placeholders = [
            {
                'id': 1,
                'outlet': 'Know Nothing Presents',
                'subject_matter': 'Frank Whitelemon sits down with Playboi Carti',
                'era': 'Awful Records',
                'date': 'July 14, 2014',
                'special_notes': 'First Carti Interview ever! Original video was taken down',
                'interview_type': 'Interview',
                'available': True,
                'archived_link': '',
                'source_links': 'https://www.youtube.com/watch?v=Z3mjPSoQhPk'
            },
            {
                'id': 2,
                'outlet': 'HotNewHipHop',
                'subject_matter': "Meet Awful Records'Father, Archibald Slim & Playboi Carti",
                'era': 'Awful Records',
                'date': 'January 27, 2015',
                'special_notes': '',
                'interview_type': 'Interview',
                'available': True,
                'archived_link': '',
                'source_links': 'https://www.youtube.com/watch?v=4Z8xXD90wFA'
            }
        ]
        
        # Convert raw dicts to a structure similar to model instances for template compatibility
        class PlaceholderObj:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
            
            @property
            def thumbnail(self):
                if hasattr(self, 'source_links') and self.source_links and 'youtube.com' in self.source_links:
                    import re
                    youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
                    match = re.search(youtube_pattern, self.source_links)
                    if match:
                        video_id = match.group(1)
                        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                return None
        
        interviews = [PlaceholderObj(item) for item in placeholders]
        eras = ["Awful Records"]
        interview_types = ["Interview"]
    
    # Pagination
    paginator = Paginator(interviews, 12)  # Show 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'eras': eras,
        'interview_types': interview_types,
        'era_filter': era_filter,
        'type_filter': type_filter,
        'available_filter': available_filter,
        'query': query
    }
    return render(request, 'catalog/interviews.html', context)
    
def fit_pics_page(request):
    """Fit Pics page displaying fashion photos and outfit pictures"""
    # Get filter parameters
    era_filter = request.GET.get('era', '')
    type_filter = request.GET.get('type', '')
    quality_filter = request.GET.get('quality', '')
    query = request.GET.get('q', '')
    
    # Get data from the database
    from .models import FitPic
    fit_pics = FitPic.objects.all()
    
    # Apply filters
    if era_filter:
        fit_pics = fit_pics.filter(era=era_filter)
    if type_filter:
        fit_pics = fit_pics.filter(pic_type=type_filter)
    if quality_filter:
        fit_pics = fit_pics.filter(quality=quality_filter)
    if query:
        fit_pics = fit_pics.filter(
            models.Q(caption__icontains=query) | 
            models.Q(notes__icontains=query) | 
            models.Q(photographer__icontains=query)
        )
    
    # Custom date-based sorting
    import re
    from datetime import datetime
    
    # Define common date formats to try
    def parse_date(date_str):
        if not date_str:
            return None
            
        date_formats = [
            '%B %d, %Y',      # March 15, 2024
            '%b %d, %Y',      # Mar 15, 2024
            '%Y-%m-%d',       # 2024-03-15
            '%m/%d/%Y',       # 03/15/2024
            '%d %B %Y',       # 15 March 2024
            '%d %b %Y',       # 15 Mar 2024
            '%B %Y',          # March 2024
            '%b %Y',          # Mar 2024
            '%m/%Y',          # 03/2024
            '%Y',             # 2024
            '%m/%d/%y',       # 03/15/24
            '%d/%m/%y',       # 15/03/24
        ]
        
        # Try each format
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If no format matches, try to extract year at least
        year_match = re.search(r'20\d{2}', date_str)
        if year_match:
            year = year_match.group(0)
            return datetime(int(year), 1, 1)  # Default to Jan 1 of the year
            
        return None
    
    # Custom sorting function
    def sort_by_date(item):
        # Sort by parsed date (newest first)
        date_obj = parse_date(item.release_date)
        if date_obj:
            # Use timestamp for comparison
            return -date_obj.timestamp()
        
        # Fall back to ID sorting if no date (bigger ID = more recent)
        return -item.id
    
    # Get all fit pics as a list to apply custom sorting
    fit_pics_list = list(fit_pics)
    
    # Apply custom sorting by date
    fit_pics_sorted = sorted(fit_pics_list, key=sort_by_date)
    
    # Get filter options from the database
    eras = FitPic.objects.values_list('era', flat=True).distinct().order_by('era')
    eras = [era for era in eras if era]  # Filter out None or empty values
    
    pic_types = FitPic.objects.values_list('pic_type', flat=True).distinct().order_by('pic_type')
    pic_types = [pt for pt in pic_types if pt]  # Filter out None or empty values
    
    qualities = FitPic.objects.values_list('quality', flat=True).distinct().order_by('quality')
    qualities = [q for q in qualities if q]  # Filter out None or empty values
    
    # If database is empty, provide sample data
    if not fit_pics_sorted:
        # Create some sample placeholder items for initial display
        placeholders = [
            {
                'id': 1,
                'caption': 'i wanted to let u know as soon as i could but i was shy ! its meh birthday !!! . * ! _ i should drop some :/ ! +:)',
                'notes': '',
                'photographer': '',
                'era': 'Die Lit',
                'release_date': 'Sep 13, 2018',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'image_url': 'https://placehold.co/400x400?text=Instagram+Image',
                'source_links': 'https://www.instagram.com/p/CS33MTwLbEl/'
            },
            {
                'id': 2,
                'caption': '⭐ phone died ! ^',
                'notes': 'Get Dripped video shoot (features some of cartis best fit pics)',
                'photographer': 'chadwicktyler',
                'era': 'WLR V1',
                'release_date': 'Nov 26, 2018',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'image_url': 'https://placehold.co/400x400?text=Instagram+Image',
                'source_links': 'https://www.instagram.com/p/CS33RaBrLSP/'
            }
        ]
        
        # Convert raw dicts to a structure similar to model instances for template compatibility
        class PlaceholderObj:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
                    
            @property
            def thumbnail(self):
                if hasattr(self, 'image_url') and self.image_url:
                    return self.image_url
                return None
        
        fit_pics_sorted = [PlaceholderObj(item) for item in placeholders]
        eras = ["Die Lit", "WLR V1"]
        pic_types = ["Post"]
        qualities = ["High Quality"]
    
    # Pagination
    paginator = Paginator(fit_pics_sorted, 12)  # Show 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'eras': eras,
        'pic_types': pic_types,
        'qualities': qualities,
        'era_filter': era_filter,
        'type_filter': type_filter,
        'quality_filter': quality_filter,
        'query': query
    }
    return render(request, 'catalog/fit_pics.html', context)

def social_media_page(request):
    """Social Media page displaying Carti's social media accounts"""
    # Get filter parameters
    era_filter = request.GET.get('era', '')
    platform_filter = request.GET.get('platform', '')
    active_filter = request.GET.get('active', '')
    query = request.GET.get('q', '')
    
    # Get data from the database
    from .models import SocialMedia
    social_accounts = SocialMedia.objects.all()
    
    # Apply filters
    if era_filter:
        social_accounts = social_accounts.filter(era=era_filter)
    if platform_filter:
        social_accounts = social_accounts.filter(platform=platform_filter)
    if active_filter:
        is_active = active_filter == 'yes'
        social_accounts = social_accounts.filter(still_used=is_active)
    if query:
        social_accounts = social_accounts.filter(
            models.Q(username__icontains=query) | 
            models.Q(notes__icontains=query) | 
            models.Q(platform__icontains=query)
        )
    
    # Get filter options from the database
    eras = SocialMedia.objects.values_list('era', flat=True).distinct().order_by('era')
    eras = [era for era in eras if era]  # Filter out None or empty values
    
    platforms = SocialMedia.objects.values_list('platform', flat=True).distinct().order_by('platform')
    platforms = [p for p in platforms if p]  # Filter out None or empty values
    
    # If database is empty, provide sample data
    if not social_accounts.exists():
        # Create some sample placeholder items for initial display
        placeholders = [
            {
                'id': 1,
                'username': '@yungcarti',
                'notes': "Cartis tumblr where he posted and promoted his music in early stages of his carrer. His first post was on Nov 30, 2010",
                'era': '$ir Cartier',
                'platform': 'TUMBLR',
                'last_post': 'May 16, 2014',
                'still_used': False,
                'link': 'https://yungcarti.tumblr.com',
            },
            {
                'id': 2,
                'username': '@playboicarti',
                'notes': "Carti's official IG",
                'era': 'Ca$h Carti Season',
                'platform': 'Instagram',
                'last_post': 'Still Used',
                'still_used': True,
                'link': 'https://www.instagram.com/playboicarti/',
            }
        ]
        
        # Convert raw dicts to a structure similar to model instances for template compatibility
        class PlaceholderObj:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
                    
            @property
            def thumbnail(self):
                platform_icons = {
                    'Instagram': 'https://placehold.co/400x400?text=Instagram',
                    'X': 'https://placehold.co/400x400?text=X/Twitter',
                    'Twitter': 'https://placehold.co/400x400?text=X/Twitter',
                    'Soundcloud': 'https://placehold.co/400x400?text=Soundcloud',
                    'Youtube': 'https://placehold.co/400x400?text=Youtube',
                    'TikTok': 'https://placehold.co/400x400?text=TikTok',
                    'TUMBLR': 'https://placehold.co/400x400?text=Tumblr',
                }
                
                if hasattr(self, 'platform') and self.platform in platform_icons:
                    return platform_icons[self.platform]
                return 'https://placehold.co/400x400?text=Social+Media'
        
        social_accounts = [PlaceholderObj(item) for item in placeholders]
        eras = ["$ir Cartier", "Ca$h Carti Season"]
        platforms = ["TUMBLR", "Instagram"]
    
    # Pagination
    paginator = Paginator(social_accounts, 12)  # Show 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'eras': eras,
        'platforms': platforms,
        'era_filter': era_filter,
        'platform_filter': platform_filter,
        'active_filter': active_filter,
        'query': query
    }
    return render(request, 'catalog/social_media.html', context)

def song_detail(request, song_id):
    """Display detailed information about a specific song"""
    # Use select_related to optimize query and prefetch_related for categories
    song = get_object_or_404(
        CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab'), 
        id=song_id
    )
    
    # Get songs from the same era for recommendations
    related_songs = CartiCatalog.objects.filter(era=song.era).exclude(id=song.id)[:5]
    
    # Get vote counts
    like_count = SongVote.objects.filter(song=song, vote_type='like').count()
    dislike_count = SongVote.objects.filter(song=song, vote_type='dislike').count()
    
    # Check if current user has voted
    user_ip = get_client_ip(request)
    user_vote = None
    if user_ip:
        try:
            user_vote = SongVote.objects.get(song=song, ip_address=user_ip).vote_type
        except SongVote.DoesNotExist:
            pass
    
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
        'like_count': like_count,
        'dislike_count': dislike_count,
        'user_vote': user_vote,
    }
    return render(request, 'catalog/song_detail.html', context)
    
def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@require_POST
def vote_song(request, song_id):
    """Handle song voting (like/dislike)"""
    song = get_object_or_404(CartiCatalog, id=song_id)
    vote_type = request.POST.get('vote_type')
    
    if vote_type not in ['like', 'dislike']:
        return JsonResponse({'status': 'error', 'message': 'Invalid vote type'}, status=400)
    
    # Get user's IP address
    ip_address = get_client_ip(request)
    session_key = request.session.session_key
    
    # Create session if it doesn't exist
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    try:
        with transaction.atomic():
            # Check if user has already voted
            try:
                existing_vote = SongVote.objects.get(song=song, ip_address=ip_address)
                
                # If user is changing their vote
                if existing_vote.vote_type != vote_type:
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    message = f"Changed your vote to {vote_type}"
                else:
                    # Remove the vote if clicking the same button again
                    existing_vote.delete()
                    message = "Vote removed"
            except SongVote.DoesNotExist:
                # Create a new vote
                SongVote.objects.create(
                    song=song,
                    ip_address=ip_address,
                    session_key=session_key,
                    vote_type=vote_type
                )
                message = f"Thanks for your {vote_type}!"
                
        # Get updated vote counts
        like_count = SongVote.objects.filter(song=song, vote_type='like').count()
        dislike_count = SongVote.objects.filter(song=song, vote_type='dislike').count()
        
        return JsonResponse({
            'status': 'success',
            'message': message,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'user_vote': vote_type if message != "Vote removed" else None
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)