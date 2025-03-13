from django.core.management.base import BaseCommand
from django.db import models
from catalog.models import CartiCatalog, SheetTab, SongMetadata
import re
from datetime import datetime

class Command(BaseCommand):
    help = 'Associate songs with sheet tabs based on scraped sheet structure, with fallback to emoji markers and other criteria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update tab assignments even for songs that already have them',
        )
        parser.add_argument(
            '--respect-scraper',
            action='store_true',
            help='Respect tab assignments from the scraper (default behavior)',
        )

    def handle(self, *args, **options):
        force_update = options.get('force', False)
        respect_scraper = options.get('respect_scraper', True)
        
        if force_update:
            self.stdout.write(self.style.WARNING("Force update mode: Will reassign ALL songs"))
            respect_scraper = False
        
        if respect_scraper:
            self.stdout.write(self.style.WARNING(
                "Respecting scraper assignments: Will only assign tabs to songs without them"
            ))
        
        # Get all sheet tabs
        try:
            unreleased_tab = SheetTab.objects.get(name="Unreleased")
            released_tab = SheetTab.objects.get(name="Released")
            grails_tab = SheetTab.objects.get(name="🏆 Grails")
            wanted_tab = SheetTab.objects.get(name="🥇 Wanted")
            best_of_tab = SheetTab.objects.get(name="⭐ Best Of")
            special_tab = SheetTab.objects.get(name="✨ Special")
            worst_of_tab = SheetTab.objects.get(name="🗑️ Worst Of")
            ai_tracks_tab = SheetTab.objects.get(name="🤖 AI Tracks")
            og_files_tab = SheetTab.objects.get(name="OG Files")
            recent_tab = SheetTab.objects.get(name="Recent")
            stems_tab = SheetTab.objects.get(name="Stems")
            tracklists_tab = SheetTab.objects.get(name="Tracklists")
            remasters_tab = SheetTab.objects.get(name="🔈Remasters")
            misc_tab = SheetTab.objects.get(name="Misc")
            recently_recorded_tab = SheetTab.objects.get(name="Recently Recorded")
            buys_tab = SheetTab.objects.get(name="Buys")
            fakes_tab = SheetTab.objects.get(name="Fakes")
            interviews_tab = SheetTab.objects.get(name="Interviews")
            album_copies_tab = SheetTab.objects.get(name="Album Copies")
            social_media_tab = SheetTab.objects.get(name="Social Media")
            fit_pics_tab = SheetTab.objects.get(name="Fit Pics")
            art_tab = SheetTab.objects.get(name="Art")
        except SheetTab.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Sheet tab not found: {e}"))
            return
        
        # Determine which songs to process
        if force_update:
            songs_to_process = CartiCatalog.objects.all()
            self.stdout.write(f"Processing all {songs_to_process.count()} songs")
        else:
            # Only process songs without tab assignments
            songs_to_process = CartiCatalog.objects.filter(
                models.Q(metadata__isnull=True) | 
                models.Q(metadata__sheet_tab__isnull=True)
            )
            self.stdout.write(f"Found {songs_to_process.count()} songs without tab assignments")
        
        updated_count = 0
        created_count = 0
        
        # Track secondary tabs for multi-categorization
        secondary_tabs = {}
        
        # Process songs
        for song in songs_to_process:
            name = song.name if song.name else ""
            type_ = song.type if song.type else ""
            notes = song.notes if song.notes else ""
            era = song.era if song.era else ""
            leak_date = song.leak_date if song.leak_date else ""
            quality = song.quality if song.quality else ""
            available_length = song.available_length if song.available_length else ""
            
            # Determine the appropriate primary sheet tab (Released or Unreleased)
            primary_sheet_tab = None
            primary_reason = ""
            
            # Secondary tabs to assign in addition to primary tab
            secondary_tab_list = []
            
            # Check for official releases
            if (any(album in era for album in ["Playboi Carti", "Die Lit", "Whole Lotta Red [V4]"]) and 
                ("Single" in type_ or "Album Track" in type_)):
                primary_sheet_tab = released_tab
                primary_reason = "Official release"
            
            # Check for Streaming category
            elif "Streaming" in notes:
                primary_sheet_tab = released_tab
                primary_reason = "Streaming category"
            else:
                # Default to Unreleased for all other songs
                primary_sheet_tab = unreleased_tab
                primary_reason = "Not an official release or streaming"
            
            # Check for Recent category - most recent leak or file dates
            # We'll mark songs with a "Recent" note, but also check for recent dates
            if "Recent" in notes and not "Recently" in notes:
                secondary_tab_list.append((recent_tab, "Recent in notes"))
            
            # Try to check if dates are in 2024 or 2025 (adjust these years as needed)
            # This is a simple string check since dates are stored as strings
            current_year = "2025"
            previous_year = "2024"
            
            file_date = song.file_date if song.file_date else ""
            if (
                (leak_date and (current_year in leak_date or previous_year in leak_date)) or
                (file_date and (current_year in file_date or previous_year in file_date))
            ):
                secondary_tab_list.append((recent_tab, "Recent date detected"))
            
            # Check for category based on type (for Stems)
            if type_ and any(stem_type in type_.lower() for stem_type in ["instrumentals", "samples", "sessions", "others"]):
                secondary_tab_list.append((stems_tab, f"Stem type: {type_}"))
            
            # Check for categories based on emojis in name or notes
            # Grails category
            if "🏆" in name or "Grail" in name or "Grail" in notes:
                secondary_tab_list.append((grails_tab, "Grails category"))
            
            # Wanted category
            if "🥇" in name or "Wanted" in name or "Wanted" in notes:
                secondary_tab_list.append((wanted_tab, "Wanted category"))
            
            # Best Of category
            if "⭐" in name or "Best" in notes:
                secondary_tab_list.append((best_of_tab, "Best Of category"))
            
            # Special category
            if "✨" in name or "Special" in notes:
                secondary_tab_list.append((special_tab, "Special category"))
            
            # Worst Of category
            if "🗑️" in name or "🗑" in name or "Worst" in notes:
                secondary_tab_list.append((worst_of_tab, "Worst Of category"))
            
            # AI Tracks category
            if "🤖" in name or "AI" in name.upper() or "AI Track" in notes:
                secondary_tab_list.append((ai_tracks_tab, "AI Track category"))
            
            # Check for other specific types or keywords
            if type_ and ("OG File" in type_ or "OG" in type_):
                secondary_tab_list.append((og_files_tab, "OG File type"))
            if "Stem" in type_ or "Stems" in name or "Vocal" in name:
                secondary_tab_list.append((stems_tab, "Stems keyword"))
            if "Remaster" in name or "Remastered" in name:
                secondary_tab_list.append((remasters_tab, "Remaster keyword"))
            if "Fake" in name:
                secondary_tab_list.append((fakes_tab, "Fake keyword"))
            if "Tracklist" in name:
                secondary_tab_list.append((tracklists_tab, "Tracklist keyword"))
            if "Art" in name or "Cover" in name:
                secondary_tab_list.append((art_tab, "Art/Cover keyword"))
            if "Buy" in notes or "Bought" in notes or "Purchase" in notes:
                secondary_tab_list.append((buys_tab, "Buy keyword in notes"))
            if "Social Media" in name or "Instagram" in name or "Twitter" in name:
                secondary_tab_list.append((social_media_tab, "Social Media keyword"))
            if "Interview" in name:
                secondary_tab_list.append((interviews_tab, "Interview keyword"))
            if "Album Cop" in name:
                secondary_tab_list.append((album_copies_tab, "Album Copy keyword"))
            if "Recently Recorded" in notes or "New Recording" in notes:
                secondary_tab_list.append((recently_recorded_tab, "Recently Recorded in notes"))
            
            # Create or update primary metadata for this song
            try:
                metadata = SongMetadata.objects.get(song=song)
                
                # If metadata exists but has no sheet_tab or we're forcing an update
                if force_update or metadata.sheet_tab is None:
                    metadata.sheet_tab = primary_sheet_tab
                    metadata.save()
                    updated_count += 1
                    self.stdout.write(f"Updated primary sheet tab for song: {song} to {primary_sheet_tab.name} [{primary_reason}]")
            except SongMetadata.DoesNotExist:
                # Create new metadata
                metadata = SongMetadata.objects.create(
                    song=song,
                    sheet_tab=primary_sheet_tab
                )
                created_count += 1
                self.stdout.write(f"Created primary sheet tab association for song: {song} as {primary_sheet_tab.name} [{primary_reason}]")
            
            # Track secondary tabs for later processing
            if song.id not in secondary_tabs:
                secondary_tabs[song.id] = []
            
            for tab, reason in secondary_tab_list:
                if tab != primary_sheet_tab:  # Don't duplicate the primary tab
                    secondary_tabs[song.id].append((tab, reason))
        
        # Process secondary tabs
        secondary_created = 0
        
        for song_id, tabs in secondary_tabs.items():
            try:
                song = CartiCatalog.objects.get(id=song_id)
                for tab, reason in tabs:
                    # Create a secondary category using the SongCategory model
                    from catalog.models import SongCategory
                    
                    # Create or get the category
                    category, created = SongCategory.objects.get_or_create(
                        song=song,
                        sheet_tab=tab
                    )
                    
                    if created:
                        self.stdout.write(f"Created secondary category {tab.name} for song: {song} [{reason}]")
                        secondary_created += 1
                    else:
                        self.stdout.write(f"Secondary category {tab.name} already exists for song: {song}")
            except CartiCatalog.DoesNotExist:
                continue
        
        if not respect_scraper:
            # Special handling for Released tab - make sure all official released songs are there
            self.stdout.write("Processing special case for Released songs...")
            released_songs = CartiCatalog.objects.filter(type__in=["Single", "Album Track"])
            released_updated = 0
            
            for song in released_songs:
                try:
                    metadata = SongMetadata.objects.get(song=song)
                    if metadata.sheet_tab != released_tab:
                        # Log the change being made
                        self.stdout.write(
                            f"Changing tab for '{song.name}' from '{metadata.sheet_tab.name if metadata.sheet_tab else 'None'}' " + 
                            f"to 'Released' because type is '{song.type}'"
                        )
                        metadata.sheet_tab = released_tab
                        metadata.save()
                        released_updated += 1
                except SongMetadata.DoesNotExist:
                    # Create new metadata
                    SongMetadata.objects.create(
                        song=song,
                        sheet_tab=released_tab
                    )
                    released_updated += 1
            
            if released_updated > 0:
                self.stdout.write(f"Updated {released_updated} songs to Released tab based on type")
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed songs: created {created_count}, updated {updated_count}, identified {secondary_created} secondary tab assignments'
        ))