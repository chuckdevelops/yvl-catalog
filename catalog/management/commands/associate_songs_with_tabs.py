from django.core.management.base import BaseCommand
from django.db import models
from catalog.models import CartiCatalog, SheetTab, SongMetadata
import re

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
        
        # Process songs
        for song in songs_to_process:
            name = song.name if song.name else ""
            type_ = song.type if song.type else ""
            notes = song.notes if song.notes else ""
            era = song.era if song.era else ""
            
            # Determine the appropriate sheet tab based on various criteria
            sheet_tab = None
            reason = ""
            
            # Check for official releases - fixed the parentheses issue
            if (any(album in era for album in ["Playboi Carti", "Die Lit", "Whole Lotta Red [V4]"]) and 
                ("Single" in type_ or "Album Track" in type_)):
                sheet_tab = released_tab
                reason = "Official release"
            
            # Try to match by emoji first
            elif "🏆" in name:
                sheet_tab = grails_tab
                reason = "Grails emoji in name"
            elif "🥇" in name:
                sheet_tab = wanted_tab
                reason = "Wanted emoji in name"
            elif "⭐" in name:
                sheet_tab = best_of_tab
                reason = "Best Of emoji in name"
            elif "✨" in name:
                sheet_tab = special_tab
                reason = "Special emoji in name"
            elif "🗑️" in name or "🗑" in name:
                sheet_tab = worst_of_tab
                reason = "Worst Of emoji in name"
            elif "🤖" in name:
                sheet_tab = ai_tracks_tab
                reason = "AI emoji in name"
            
            # Check for specific types or keywords
            elif type_ and ("OG File" in type_ or "OG" in type_):
                sheet_tab = og_files_tab
                reason = "OG File type"
            elif "Stem" in type_ or "Stems" in name or "Vocal" in name:
                sheet_tab = stems_tab
                reason = "Stems keyword"
            elif "Remaster" in name or "Remastered" in name:
                sheet_tab = remasters_tab
                reason = "Remaster keyword"
            elif "Fake" in name or "AI" in name:
                sheet_tab = fakes_tab
                reason = "Fake/AI keyword"
            elif "Tracklist" in name:
                sheet_tab = tracklists_tab
                reason = "Tracklist keyword"
            elif "Art" in name or "Cover" in name:
                sheet_tab = art_tab
                reason = "Art/Cover keyword"
            elif "Buy" in notes or "Bought" in notes or "Purchase" in notes:
                sheet_tab = buys_tab
                reason = "Buy keyword in notes"
            elif "Social Media" in name or "Instagram" in name or "Twitter" in name:
                sheet_tab = social_media_tab
                reason = "Social Media keyword"
            elif "Interview" in name:
                sheet_tab = interviews_tab
                reason = "Interview keyword"
            elif "Album Cop" in name:
                sheet_tab = album_copies_tab
                reason = "Album Copy keyword"
            elif "Recently Recorded" in notes or "New Recording" in notes:
                sheet_tab = recently_recorded_tab
                reason = "Recently Recorded in notes"
            elif "Recent" in notes and not "Recently" in notes:
                sheet_tab = recent_tab
                reason = "Recent in notes"
            else:
                # Default to Unreleased
                sheet_tab = unreleased_tab
                reason = "Default assignment (no specific criteria matched)"
            
            # Get or create metadata for this song
            try:
                metadata = SongMetadata.objects.get(song=song)
                
                # If metadata exists but has no sheet_tab or we're forcing an update
                if force_update or metadata.sheet_tab is None:
                    metadata.sheet_tab = sheet_tab
                    metadata.save()
                    updated_count += 1
                    self.stdout.write(f"Updated sheet tab for song: {song} to {sheet_tab.name} [{reason}]")
            except SongMetadata.DoesNotExist:
                # Create new metadata
                metadata = SongMetadata.objects.create(
                    song=song,
                    sheet_tab=sheet_tab
                )
                created_count += 1
                self.stdout.write(f"Created sheet tab association for song: {song} as {sheet_tab.name} [{reason}]")
        
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
            f'Successfully processed songs: created {created_count}, updated {updated_count}'
        ))