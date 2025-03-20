from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Case, When, IntegerField
from django.db import models, transaction
from django.template.defaulttags import register
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import re
from .models import CartiCatalog, SheetTab, SongMetadata, SongVote, HomepageSettings, ArtMedia, Interview, FitPic, SocialMedia, SongBookmark, ClientIdentifier
from .utils import get_client_ip, check_and_update_client, generate_client_hash

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
    
    # Get homepage settings
    homepage_settings = HomepageSettings.objects.first()
    
    # Get songs for the Recently Leaked section (sidebar)
    try:
        if homepage_settings and homepage_settings.enable_custom_recently_leaked:
            # Use the custom Recently Leaked songs (max 5)
            recently_leaked = homepage_settings.recently_leaked_songs.select_related('metadata__sheet_tab')\
                .prefetch_related('categories__sheet_tab').all()[:5]
            if recently_leaked.exists():
                # Convert to list as we're using a limited QuerySet
                recently_leaked = list(recently_leaked)
            else:
                # Fall back to default behavior if no songs selected
                raise HomepageSettings.DoesNotExist()
        else:
            # Fall back to default behavior if custom setting not enabled
            raise HomepageSettings.DoesNotExist()
    except (HomepageSettings.DoesNotExist, AttributeError):
        # Default: Get most recent leak songs (sort by leak_date)
        recently_leaked = CartiCatalog.objects.filter(
            Q(leak_date__isnull=False) & ~Q(leak_date='')
        ).order_by('-leak_date')[:5]
        
        # If no recent leaks found, fall back to ID order
        if not recently_leaked.exists():
            recently_leaked = CartiCatalog.objects.all().order_by('-id')[:5]
    
    # Get songs for the main Recent Songs section (bottom of page)
    try:
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
    
    # Also add sheet tab info to the recently leaked songs
    for song in recently_leaked:
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
    
    context = {
        'song_count': song_count,
        'era_count': era_count,
        'recent_songs': recent_songs,
        'recently_leaked': recently_leaked,
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
    
    # Process preview URL for audio player
    if song.preview_url:
        import os
        # Extract the correct filename
        if song.preview_url.startswith('/media/previews/'):
            preview_filename = song.preview_url[16:]  # Extract filename from URL
        else:
            preview_filename = os.path.basename(song.preview_url)
            
        # Check if file exists - try both direct media path and audio-serve pattern
        preview_file_path = os.path.join(settings.MEDIA_ROOT, 'previews', preview_filename)
        song.preview_file_exists = os.path.exists(preview_file_path)
        
        # Log file existence check for debugging
        # Use print instead of logger which wasn't defined
        print(f"File existence check for {preview_file_path}: {song.preview_file_exists}")
        
        # Even if the file doesn't appear to exist, still set the URLs
        # to allow the JavaScript audio-url-fixer to try both methods
        song.preview_audio_url = f'/audio-serve/{preview_filename}'
        song.direct_audio_url = f'/media/previews/{preview_filename}'
        
        # If the file has been properly re-encoded, it should exist
        # Force preview_file_exists to True to allow client-side handling
        if preview_filename and preview_filename.endswith('.mp3'):
            song.preview_file_exists = True
    else:
        # For songs without preview URLs, try to find a source URL that can be played
        song.preview_file_exists = False
        song.preview_audio_url = None
        song.direct_audio_url = None
        
        # Extract URL from links if possible
        if song.links:
            import re
            import uuid
            import urllib.parse
            
            # Find direct links to music.froste.lol, pillowcase.su, or krakenfiles.com which can be played
            source_url = None
            original_url = None
            is_froste = False
            is_pillowcase = False
            is_krakenfiles = False
            
            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', song.links)
            for url in urls:
                if 'music.froste.lol/song/' in url:
                    source_url = url
                    original_url = url
                    is_froste = True
                    break
                elif 'pillowcase.su/f/' in url:
                    # Keep track of the original URL
                    original_url = url
                    # Convert pillowcase.su link to a direct download link
                    file_id = url.split('/f/')[1].split('/')[0] if '/' in url.split('/f/')[1] else url.split('/f/')[1]
                    source_url = f"https://pillowcase.su/f/{file_id}/download"
                    is_pillowcase = True
                    break
                elif 'krakenfiles.com/view/' in url:
                    # Keep track of the original URL
                    original_url = url
                    # For krakenfiles, use the original view URL
                    source_url = url
                    is_krakenfiles = True
                    break
            
            if source_url:
                # Generate a random parameter for cache busting
                # Use a properly formatted UUID with dashes to match existing files
                random_id = str(uuid.uuid4())  # This already includes the dashes
                
                # Create a proxy URL using our serve_audio_proxy endpoint
                encoded_url = urllib.parse.quote(source_url)
                proxy_filename = f"{random_id}.mp3"  # Use UUID format to match existing files
                
                # Set URLs for the various playback methods
                song.original_source_url = original_url  # The original URL as it appears in links
                song.source_url = source_url  # The actual source URL (might be modified for direct download)
                song.direct_audio_url = f"/static/proxy-{random_id}-{proxy_filename}?url={encoded_url}"  # Keep original format for backward compatibility
                song.preview_url = f"/audio-serve/{proxy_filename}?source={encoded_url}"  # Use the working audio-serve route instead
                song.preview_file_exists = True  # Set to True to show player
                song.preview_audio_url = song.preview_url
                
                # Set additional properties to identify source
                song.is_froste_link = is_froste
                song.is_pillowcase_link = is_pillowcase
                song.is_krakenfiles_link = is_krakenfiles
    
    # Get recommended songs based on collaborative filtering
    from django.db.models import Count, Q
    
    # Get current client identifier if available
    client = None
    client_hash = None
    try:
        client_hash = generate_client_hash(request)
        client, _ = ClientIdentifier.objects.get_or_create(client_hash=client_hash)
    except Exception:
        pass
    
    # 1. Find users who liked this song
    users_who_liked = SongVote.objects.filter(song=song, vote_type='like').values_list('client_identifier', flat=True)
    
    # 2. Find users who bookmarked this song
    users_who_bookmarked = SongBookmark.objects.filter(song=song).values_list('client_identifier', flat=True)
    
    # Combine users who showed interest in this song
    interested_users = list(set(list(users_who_liked) + list(users_who_bookmarked)))
    
    # 3. Find what songs these users also liked or bookmarked
    song_scores = {}
    
    # Add songs these users liked
    for vote in SongVote.objects.filter(
        client_identifier__in=interested_users, 
        vote_type='like'
    ).exclude(song=song):
        if vote.song_id not in song_scores:
            song_scores[vote.song_id] = 0
        song_scores[vote.song_id] += 1
    
    # Add songs these users bookmarked (with higher weight)
    for bookmark in SongBookmark.objects.filter(
        client_identifier__in=interested_users
    ).exclude(song=song):
        if bookmark.song_id not in song_scores:
            song_scores[bookmark.song_id] = 0
        song_scores[bookmark.song_id] += 2  # Bookmarks count double
    
    # Sort songs by score (highest first)
    sorted_song_ids = sorted(song_scores.items(), key=lambda x: x[1], reverse=True)
    recommended_ids = [song_id for song_id, score in sorted_song_ids]
    
    # Get the recommended songs
    if recommended_ids:
        # Use a Case/When to preserve the order from our scores
        from django.db.models import Case, When
        preserved_order = Case(*[When(id=id, then=pos) for pos, id in enumerate(recommended_ids)])
        recommended_songs = CartiCatalog.objects.filter(id__in=recommended_ids).order_by(preserved_order)
    else:
        recommended_songs = CartiCatalog.objects.none()
    
    # If we don't have enough recommendations, add songs from the same era
    if recommended_songs.count() < 5:
        # Get other songs from the same era and same primary tab
        try:
            primary_tab = song.metadata.sheet_tab if hasattr(song, 'metadata') and song.metadata else None
            era_songs = CartiCatalog.objects.filter(era=song.era).exclude(id=song.id)
            
            # Add similar tab songs first if available
            if primary_tab:
                tab_era_songs = era_songs.filter(metadata__sheet_tab=primary_tab)
                # Add songs from same tab and era if any available
                existing_ids = set(recommended_songs.values_list('id', flat=True))
                for era_song in tab_era_songs:
                    if era_song.id not in existing_ids and recommended_songs.count() < 5:
                        recommended_songs = recommended_songs | CartiCatalog.objects.filter(id=era_song.id)
            
            # If still not enough, add more from the same era
            existing_ids = set(recommended_songs.values_list('id', flat=True))
            for era_song in era_songs:
                if era_song.id not in existing_ids and recommended_songs.count() < 5:
                    recommended_songs = recommended_songs | CartiCatalog.objects.filter(id=era_song.id)
        except Exception as e:
            # If any error occurs, fall back to basic era recommendations
            existing_ids = set(recommended_songs.values_list('id', flat=True))
            era_songs = CartiCatalog.objects.filter(era=song.era).exclude(id=song.id)
            for era_song in era_songs:
                if era_song.id not in existing_ids and recommended_songs.count() < 5:
                    recommended_songs = recommended_songs | CartiCatalog.objects.filter(id=era_song.id)
    
    # Limit to 5 songs
    recommended_songs = recommended_songs[:5]
    
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
    
    # Helper function to compare song name similarity
    def similar_names(name1, name2):
        # Convert to lowercase and remove any special characters
        name1 = re.sub(r'[^\w\s]', '', name1.lower())
        name2 = re.sub(r'[^\w\s]', '', name2.lower())
        
        # Split into words
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        # Calculate Jaccard similarity
        if not words1 or not words2:
            return 0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0

    # Get similar songs from the same album if applicable
    album_related_songs = []
    
    # Extract base song name (without version indicators)
    base_song_name = None
    if song.name:
        base_song_name = re.sub(r'\s*\[V\d+\].*', '', song.name) 
    
    # Find version variants regardless of album
    version_variants = []
    if base_song_name:
        # Look for all songs with the same base name but different version numbers
        # This will find songs like "Song Name [V1]", "Song Name [V2]", etc.
        versions_query = CartiCatalog.objects.filter(
            name__icontains=base_song_name,
            name__regex=r'\[V\d+\]'  # Must have a version tag
        ).exclude(id=song.id)  # Exclude the current song
        
        for version in versions_query:
            # Double check that this is really a variant of our song
            version_base_name = re.sub(r'\s*\[V\d+\].*', '', version.name)
            # Use a more forgiving match to handle slight differences
            name_similarity = similar_names(base_song_name, version_base_name)
            if name_similarity >= 0.8:  # 80% similarity should indicate it's a variant
                version_variants.append(version)
        
        # If current song has a version indicator, also find the "main" version
        # This handles the case where we're viewing a version but want to see the original
        current_is_version = re.search(r'\s*\[V\d+\]', song.name)
        if current_is_version:
            main_versions = CartiCatalog.objects.filter(
                name__iexact=base_song_name  # Exact match for the base name
            ).exclude(id=song.id)
            
            for main_version in main_versions:
                # Make sure this doesn't have a version tag
                if not re.search(r'\s*\[V\d+\]', main_version.name):
                    version_variants.append(main_version)
    
    # Set the version variants to be displayed
    song.version_variants = version_variants
    
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
        album_version_variants = []
        
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
                    album_version_variants.append(potential_song)
                else:
                    # Only add regular tracks if we don't already have this track number
                    existing_track_nums = [s.display_track_number for s in regular_tracks]
                    if potential_song.display_track_number not in existing_track_nums:
                        regular_tracks.append(potential_song)
        
        # Add regular tracks to the album tracklist
        album_related_songs = regular_tracks
        
        # Add album-specific versions to the version_variants list
        for album_variant in album_version_variants:
            if album_variant.id not in [v.id for v in version_variants]:
                version_variants.append(album_variant)
        
        # Update the song's version variants
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
    
    # Generate current timestamp for cache busting
    import time
    
    context = {
        'song': song,
        'recommended_songs': recommended_songs,
        'timestamp': int(time.time() * 1000),  # Current time in milliseconds
        'album_related_songs': album_related_songs,
        'like_count': like_count,
        'dislike_count': dislike_count,
        'user_vote': user_vote,
    }
    return render(request, 'catalog/song_detail.html', context)

@require_POST
def vote_song(request, song_id):
    """Handle song voting with protection against multiple votes"""
    song = get_object_or_404(CartiCatalog, id=song_id)
    vote_type = request.POST.get('vote_type')
    
    if vote_type not in ['like', 'dislike']:
        return JsonResponse({'status': 'error', 'message': 'Invalid vote type'}, status=400)
    
    # Check client fingerprint and rate limits
    client, time_since_last_vote = check_and_update_client(request)
    
    # Check if client is voting too frequently
    if time_since_last_vote and time_since_last_vote.total_seconds() < 3:
        return JsonResponse({
            'status': 'error', 
            'message': 'Please wait before voting again'
        }, status=429)
    
    # Check if client has too many votes overall for the day
    MAX_VOTES_PER_DAY = 50
    from django.utils import timezone
    from django.db.models import Q
    votes_today = SongVote.objects.filter(
        Q(client_identifier=client.client_hash) &
        Q(created_at__date=timezone.now().date())
    ).count()
    
    if votes_today >= MAX_VOTES_PER_DAY:
        return JsonResponse({
            'status': 'error', 
            'message': 'Daily voting limit reached'
        }, status=429)
    
    # Get user's IP address as secondary identifier
    ip_address = get_client_ip(request)
    session_key = request.session.session_key
    
    # Create session if it doesn't exist
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    try:
        with transaction.atomic():
            # Check if client has already voted on this song
            try:
                existing_vote = SongVote.objects.get(
                    song=song, 
                    client_identifier=client.client_hash
                )
                
                # If client is changing their vote
                if existing_vote.vote_type != vote_type:
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    message = f"Changed your vote to {vote_type}"
                else:
                    # Remove the vote if clicking the same button again
                    existing_vote.delete()
                    message = "Vote removed"
            except SongVote.DoesNotExist:
                # Create a new vote with client identifier
                SongVote.objects.create(
                    song=song,
                    ip_address=ip_address,
                    session_key=session_key,
                    client_identifier=client.client_hash,
                    vote_type=vote_type
                )
                message = f"Thanks for your {vote_type}!"
            
            # Update the client's voting stats
            client.vote_count += 1
            client.last_vote_time = timezone.now()
            client.save()
                
        # Get updated vote counts
        like_count = SongVote.objects.filter(song=song, vote_type='like').count()
        dislike_count = SongVote.objects.filter(song=song, vote_type='dislike').count()
        
        # Send the client's vote to store in localStorage
        return JsonResponse({
            'status': 'success',
            'message': message,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'user_vote': vote_type if message != "Vote removed" else None
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def coming_soon(request):
    """Coming soon page"""
    return render(request, 'catalog/coming_soon.html')

def serve_audio_proxy(request, random, filename):
    """Proxy audio file server with random parameter in URL to prevent caching"""
    import os
    import requests
    import urllib.parse
    from django.conf import settings
    from django.http import FileResponse, HttpResponse, Http404, StreamingHttpResponse
    import logging
    import hashlib
    
    # Setup logging
    logger = logging.getLogger(__name__)
    
    # Enhanced logging with more context
    logger.info(f"[AUDIO PROXY] Serving audio via proxy: {filename}")
    logger.info(f"[AUDIO PROXY] Random parameter: {random}")
    logger.info(f"[AUDIO PROXY] Request URL: {request.path}")
    logger.info(f"[AUDIO PROXY] Request GET params: {request.GET}")
    logger.info(f"[AUDIO PROXY] Request method: {request.method}")
    logger.info(f"[AUDIO PROXY] Headers: {request.headers}")
    
    # Check if this is a remote URL proxy request
    source_url = request.GET.get('url')
    if source_url:
        logger.info(f"[AUDIO PROXY] Proxying remote URL: {source_url}")
        
        try:
            # Decode URL if needed
            if '%' in source_url:
                source_url = urllib.parse.unquote(source_url)
                
            # Setup headers for the request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'identity;q=1, *;q=0',  # Avoid compressed responses
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': source_url,
                'Origin': 'https://music.froste.lol' if 'music.froste.lol' in source_url else ('https://pillowcase.su' if 'pillowcase.su' in source_url else ('https://krakenfiles.com' if 'krakenfiles.com' in source_url else 'https://example.com')),
                'Cache-Control': 'no-cache',
            }
            
            # Add Range header if present in original request
            if 'HTTP_RANGE' in request.META:
                headers['Range'] = request.META['HTTP_RANGE']
                logger.info(f"[AUDIO PROXY] Forwarding Range header: {request.META['HTTP_RANGE']}")
                
            # Make request to source URL
            source_response = requests.get(source_url, headers=headers, stream=True, allow_redirects=True, timeout=10)
            
            # Check response status
            if source_response.status_code >= 400:
                logger.error(f"[AUDIO PROXY] Remote URL returned error: {source_response.status_code}")
                return HttpResponse(f"Error fetching remote audio: {source_response.status_code}", status=source_response.status_code)
                
            # Get content type
            content_type = source_response.headers.get('Content-Type', 'audio/mpeg')
            
            # Create streaming response
            response = StreamingHttpResponse(source_response.iter_content(chunk_size=8192), content_type=content_type)
            
            # Copy relevant headers from the source response
            for header in ['Content-Length', 'Content-Range', 'Accept-Ranges', 'ETag']:
                if header in source_response.headers:
                    response[header] = source_response.headers[header]
                    
            # Set random filename in Content-Disposition to prevent browser caching
            random_filename = f"preview-{random}-{filename}"
            response['Content-Disposition'] = f'inline; filename="{random_filename}"'
            
            # Enable CORS
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Range'
            
            # Extreme anti-caching headers
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '-1'
            response['Vary'] = '*'
            
            logger.info(f"[AUDIO PROXY] Successfully proxying remote URL via proxy with random={random}")
            return response
            
        except Exception as e:
            logger.exception(f"[AUDIO PROXY] Error proxying remote URL: {str(e)}")
            return HttpResponse(f"Error proxying remote audio: {str(e)}", status=500)
    
    # If we get here, it's a local file request
    # Get the absolute path to the file
    file_path = os.path.join(settings.MEDIA_ROOT, 'previews', filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"[AUDIO PROXY] File not found: {file_path}")
        raise Http404(f"Audio file {filename} not found")
    
    # Calculate and log file hash
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    logger.info(f"[AUDIO PROXY] File hash: {file_hash}")
    
    # Serve the file with extreme anti-caching measures
    try:
        # Use fresh file handle each time
        file_handle = open(file_path, 'rb')
        
        # Create response
        response = FileResponse(file_handle, content_type='audio/mpeg')
        
        # Set random filename in Content-Disposition to prevent browser caching
        random_filename = f"preview-{random}-{filename}"
        response['Content-Disposition'] = f'inline; filename="{random_filename}"'
        
        # Set content length
        file_size = os.path.getsize(file_path)
        response['Content-Length'] = str(file_size)
        
        # Enable CORS
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Range'
        
        # Extreme anti-caching headers
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '-1'
        response['Vary'] = '*'
        
        # Add unique ETag
        etag = hashlib.md5(f"{random}:{filename}:{file_hash}").hexdigest()
        response['ETag'] = f'"{etag}"'
        
        # Add range support
        response['Accept-Ranges'] = 'bytes'
        
        logger.info(f"[AUDIO PROXY] Successfully serving {filename} via proxy with random={random}")
        return response
    except Exception as e:
        logger.error(f"[AUDIO PROXY] Error serving file {filename}: {str(e)}")
        raise

def serve_audio(request, filename):
    """Direct audio file server that can also proxy remote URLs"""
    import os
    import requests
    import urllib.parse
    from django.conf import settings
    import logging
    import time
    
    # Setup logging
    logger = logging.getLogger(__name__)
    
    # Enhanced logging for debugging
    logger.info(f"[AUDIO SERVE] Serving audio: {filename}")
    logger.info(f"[AUDIO SERVE] Request URL: {request.path}")
    logger.info(f"[AUDIO SERVE] Request GET params: {request.GET}")
    logger.info(f"[AUDIO SERVE] Request method: {request.method}")
    logger.info(f"[AUDIO SERVE] Headers: {request.headers}")
    from django.http import FileResponse, HttpResponse, Http404, StreamingHttpResponse
    import logging
    import hashlib
    
    # Setup logging
    logger = logging.getLogger(__name__)
    
    # Enhanced logging with more context
    logger.info(f"[AUDIO SERVE] Attempting to serve audio file: {filename}")
    logger.info(f"[AUDIO SERVE] Request URL: {request.path}")
    logger.info(f"[AUDIO SERVE] Request method: {request.method}")
    logger.info(f"[AUDIO SERVE] User agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
    logger.info(f"[AUDIO SERVE] Referrer: {request.META.get('HTTP_REFERER', 'None')}")
    
    # Get any query parameters
    query_params = request.GET.dict()
    if query_params:
        logger.info(f"[AUDIO SERVE] Query params: {query_params}")
    
    # Check if this is a remote source request
    source_url = request.GET.get('source')
    if source_url:
        logger.info(f"[AUDIO SERVE] Proxying remote source: {source_url}")
        
        try:
            # Decode URL if needed
            if '%' in source_url:
                source_url = urllib.parse.unquote(source_url)
                
            # Setup headers for the request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'identity;q=1, *;q=0',  # Avoid compressed responses
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': source_url,
                'Origin': 'https://music.froste.lol' if 'music.froste.lol' in source_url else ('https://pillowcase.su' if 'pillowcase.su' in source_url else ('https://krakenfiles.com' if 'krakenfiles.com' in source_url else 'https://example.com')),
                'Cache-Control': 'no-cache',
            }
            
            # Add Range header if present in original request
            if 'HTTP_RANGE' in request.META:
                headers['Range'] = request.META['HTTP_RANGE']
                logger.info(f"[AUDIO SERVE] Forwarding Range header: {request.META['HTTP_RANGE']}")
                
            # Make request to source URL
            source_response = requests.get(source_url, headers=headers, stream=True, allow_redirects=True, timeout=10)
            
            # Check response status
            if source_response.status_code >= 400:
                logger.error(f"[AUDIO SERVE] Remote URL returned error: {source_response.status_code}")
                return HttpResponse(f"Error fetching remote audio: {source_response.status_code}", status=source_response.status_code)
                
            # Get content type
            content_type = source_response.headers.get('Content-Type', 'audio/mpeg')
            
            # Create streaming response
            response = StreamingHttpResponse(source_response.iter_content(chunk_size=8192), content_type=content_type)
            
            # Copy relevant headers from the source response
            for header in ['Content-Length', 'Content-Range', 'Accept-Ranges', 'ETag']:
                if header in source_response.headers:
                    response[header] = source_response.headers[header]
                    
            # Set filename in Content-Disposition
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            
            # Enable CORS
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Range'
            
            # Disable caching
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            logger.info(f"[AUDIO SERVE] Successfully proxying remote source: {source_url}")
            return response
            
        except Exception as e:
            logger.exception(f"[AUDIO SERVE] Error proxying remote source: {str(e)}")
            return HttpResponse(f"Error proxying remote audio: {str(e)}", status=500)
    
    # Security check to prevent directory traversal for local files
    if '..' in filename or filename.startswith('/'):
        logger.error(f"[AUDIO SERVE] Security check failed for filename: {filename}")
        raise Http404("Invalid filename")
    
    # Get the absolute path to the file
    file_path = os.path.join(settings.MEDIA_ROOT, 'previews', filename)
    logger.info(f"[AUDIO SERVE] Looking for file at: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"[AUDIO SERVE] File not found: {file_path}")
        raise Http404(f"Audio file {filename} not found")
    
    # Calculate and log file hash
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    logger.info(f"[AUDIO SERVE] File exists, size: {os.path.getsize(file_path)} bytes, hash: {file_hash}")
    
    # Check file readability and permissions
    if not os.access(file_path, os.R_OK):
        logger.error(f"[AUDIO SERVE] File not readable: {file_path}")
        raise Http404(f"Audio file {filename} is not readable")
    
    # Get file permissions and log them
    file_permissions = oct(os.stat(file_path).st_mode)[-3:]
    logger.info(f"[AUDIO SERVE] File permissions: {file_permissions}")
    
    # Serve the file
    try:
        # Use fresh file handle each time to avoid caching issues
        file_handle = open(file_path, 'rb')
        
        # Create response with proper content type
        response = FileResponse(file_handle, content_type='audio/mpeg')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        # Set content length
        file_size = os.path.getsize(file_path)
        response['Content-Length'] = str(file_size)
        
        # Enable CORS for media files
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Range'
        
        # Aggressively disable caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        # Add unique ETag to force browsers to revalidate
        etag = hashlib.md5(f"{filename}:{os.path.getmtime(file_path)}:{file_hash}".encode()).hexdigest()
        response['ETag'] = f'"{etag}"'
        
        # Add range support explicitly
        response['Accept-Ranges'] = 'bytes'
        
        logger.info(f"[AUDIO SERVE] Successfully created audio response with ETag: {etag}")
        logger.info(f"[AUDIO SERVE] Successfully created response for {filename}")
        print(f"[AUDIO SERVE] Successfully serving {filename} from {file_path}")
        return response
    except Exception as e:
        logger.error(f"[AUDIO SERVE] Error serving file {filename}: {str(e)}")
        raise

def log_audio_play(request):
    """Endpoint to log audio play events from the frontend"""
    import json
    import logging
    from django.http import JsonResponse
    from django.views.decorators.http import require_POST
    from django.views.decorators.csrf import csrf_exempt
    
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            song_id = data.get('song_id')
            src = data.get('src')
            timestamp = data.get('timestamp')
            
            logger.info(f"[AUDIO PLAY] Song ID: {song_id}, Source: {src}, Time: {timestamp}")
            print(f"[AUDIO PLAY] Song ID: {song_id}, Source: {src}, Time: {timestamp}")
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"[AUDIO PLAY] Error logging play event: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def audio_test_view(request):
    """Combined test view for all audio approaches"""
    import os
    from django.conf import settings
    
    # Get a list of all MP3 files in the previews directory
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    mp3_files = []
    
    if os.path.exists(preview_dir):
        mp3_files = [f for f in os.listdir(preview_dir) if f.endswith('.mp3')]
    
    # Check file details
    file_details = []
    for filename in mp3_files:
        file_path = os.path.join(preview_dir, filename)
        details = {
            'filename': filename,
            'size': os.path.getsize(file_path),
            'readable': os.access(file_path, os.R_OK),
            'permissions': oct(os.stat(file_path).st_mode)[-3:],
            'direct_url': f'/media/previews/{filename}',
            'custom_url': f'/audio-serve/{filename}',
        }
        file_details.append(details)
    
    # Sort by modification time (newest first)
    file_details.sort(key=lambda x: os.path.getmtime(os.path.join(preview_dir, x['filename'])), reverse=True)
    
    context = {
        'mp3_files': file_details,
        'media_root': settings.MEDIA_ROOT,
        'media_url': settings.MEDIA_URL,
    }
    
    return render(request, 'catalog/audio_test.html', context)

def preview_test(request):
    """Testing page for previews"""
    # Get all songs with previews
    songs_with_previews = CartiCatalog.objects.exclude(preview_url__isnull=True).order_by('-id')
    
    # Get a list of actual MP3 files in the previews directory
    import os
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    valid_files = os.listdir(preview_dir) if os.path.exists(preview_dir) else []
    
    # Process song data
    processed_songs = []
    for song in songs_with_previews:
        # Extract the original preview URL
        original_url = song.preview_url
        
        # Get the correct filename no matter what format the URL is in
        if original_url.startswith('/media/previews/'):
            filename = original_url[16:]  # Extract filename from URL
        else:
            filename = os.path.basename(original_url)
            
        # Check if file exists
        file_exists = filename in valid_files
        file_path = os.path.join(preview_dir, filename)
        
        # Add info to the song object
        song_data = {
            'id': song.id,
            'name': song.name,
            'original_url': original_url,
            'filename': filename,
            'audio_url': f'/media/previews/{filename}',  # Simple direct URL
            'file_exists': file_exists,
        }
        
        # Add file details if it exists
        if file_exists:
            song_data['file_size'] = os.path.getsize(file_path)
            song_data['file_readable'] = os.access(file_path, os.R_OK)
            song_data['file_permissions'] = oct(os.stat(file_path).st_mode)[-3:]
        else:
            song_data['file_size'] = 0
            song_data['file_readable'] = False
            song_data['file_permissions'] = 'N/A'
            
        processed_songs.append(song_data)
    
    context = {
        'songs': processed_songs,
        'media_path': settings.MEDIA_ROOT,
        'media_url': settings.MEDIA_URL,
        'base_dir': settings.BASE_DIR,
        'preview_files': valid_files,
    }
    
    return render(request, 'catalog/preview_test.html', context)
    
# Preview generation API endpoint
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
import json
from catalog.preview_processor import generate_preview_for_song

@require_POST
@user_passes_test(lambda u: u.is_staff)
def generate_preview_api(request, song_id):
    """AJAX endpoint for staff to generate preview clips"""
    try:
        # Parse request body
        data = json.loads(request.body)
        url = data.get('url')
        
        if not url:
            return JsonResponse({'status': 'error', 'message': 'URL is required'}, status=400)
        
        # Generate the preview
        preview_url = generate_preview_for_song(song_id)
        
        if preview_url:
            return JsonResponse({
                'status': 'success',
                'preview_url': preview_url,
                'message': 'Preview generated successfully'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to generate preview'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# Bookmark functionality
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from .models import SongBookmark

@require_POST
def bookmark_song(request, song_id):
    """Handle song bookmarking with client identification"""
    song = get_object_or_404(CartiCatalog, id=song_id)
    collection_name = request.POST.get('collection_name', 'My Collection')
    action = request.POST.get('action', 'add')  # Options: add, remove
    
    # Get client identifier using same fingerprinting as votes
    client, _ = check_and_update_client(request)
    
    if action == 'add':
        # Create bookmark if it doesn't exist
        bookmark, created = SongBookmark.objects.get_or_create(
            song=song,
            client_identifier=client.client_hash,
            collection_name=collection_name
        )
        message = "Song bookmarked" if created else "Song already in collection"
    elif action == 'remove':
        # Remove bookmark if it exists
        try:
            bookmark = SongBookmark.objects.get(
                song=song,
                client_identifier=client.client_hash,
                collection_name=collection_name
            )
            bookmark.delete()
            message = "Bookmark removed"
        except SongBookmark.DoesNotExist:
            message = "Bookmark not found"
    else:
        return JsonResponse({"status": "error", "message": "Invalid action"}, status=400)
    
    # Return updated list of collections this song is in for this user
    collections = SongBookmark.objects.filter(
        song=song,
        client_identifier=client.client_hash
    ).values_list('collection_name', flat=True)
    
    return JsonResponse({
        "status": "success",
        "message": message,
        "collections": list(collections),
        "song_id": song_id
    })

@require_GET
def get_bookmarks(request):
    """Get all bookmarked songs for the current client"""
    # Get client identifier using same fingerprinting as votes
    client, _ = check_and_update_client(request)
    collection_name = request.GET.get('collection', None)
    
    # Build query for bookmarks
    bookmarks_query = SongBookmark.objects.filter(client_identifier=client.client_hash)
    
    # Filter by collection if specified
    if collection_name:
        bookmarks_query = bookmarks_query.filter(collection_name=collection_name)
    
    # Get bookmarked songs with details
    bookmarks = bookmarks_query.select_related('song', 'song__metadata__sheet_tab')\
                               .order_by('-created_at')
    
    # Prepare data for JSON response
    songs_data = []
    for bookmark in bookmarks:
        song = bookmark.song
        # Add basic song details
        song_data = {
            "id": song.id,
            "name": song.name,
            "era": song.era,
            "collection": bookmark.collection_name,
            "bookmarked_at": bookmark.created_at.isoformat(),
        }
        
        # Add metadata if available
        try:
            if song.metadata and song.metadata.sheet_tab:
                song_data["primary_tab"] = song.metadata.sheet_tab.name
                song_data["subsection"] = song.metadata.subsection
        except (SongMetadata.DoesNotExist, AttributeError):
            pass
            
        songs_data.append(song_data)
    
    return JsonResponse({
        "status": "success",
        "count": len(songs_data),
        "bookmarks": songs_data
    })

@require_GET
def get_collections(request):
    """Get all collections for the current client"""
    # Get client identifier using same fingerprinting as votes
    client, _ = check_and_update_client(request)
    
    # Get distinct collections with counts
    from django.db.models import Count
    collections = SongBookmark.objects.filter(client_identifier=client.client_hash)\
                                     .values('collection_name')\
                                     .annotate(count=Count('id'))\
                                     .order_by('collection_name')
    
    return JsonResponse({
        "status": "success",
        "collections": list(collections)
    })