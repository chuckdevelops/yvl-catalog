from django.core.management.base import BaseCommand
from django.db import models
from catalog.models import CartiCatalog, SheetTab, SongMetadata
import re

class Command(BaseCommand):
    help = 'Associate songs with sheet tabs based on scraped sheet structure, with fallback to emoji markers and other criteria'

    def handle(self, *args, **options):
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
        
        # Get songs that don't have metadata or don't have a sheet_tab set
        songs_without_tabs = CartiCatalog.objects.filter(
            models.Q(metadata__isnull=True) | 
            models.Q(metadata__sheet_tab__isnull=True)
        )
        
        self.stdout.write(f"Found {songs_without_tabs.count()} songs without tab assignments")
        
        updated_count = 0
        created_count = 0
        
        # Process songs without tab assignments
        for song in songs_without_tabs:
            name = song.name if song.name else ""
            type_ = song.type if song.type else ""
            notes = song.notes if song.notes else ""
            era = song.era if song.era else ""
            
            # Determine the appropriate sheet tab based on various criteria
            sheet_tab = None
            
            # Check for official releases
            if any(album in era for album in ["Playboi Carti", "Die Lit", "Whole Lotta Red [V4]"]) and "Single" in type_ or "Album Track" in type_:
                sheet_tab = released_tab
            
            # Try to match by emoji first
            elif "🏆" in name:
                sheet_tab = grails_tab
            elif "🥇" in name:
                sheet_tab = wanted_tab
            elif "⭐" in name:
                sheet_tab = best_of_tab
            elif "✨" in name:
                sheet_tab = special_tab
            elif "🗑️" in name or "🗑" in name:
                sheet_tab = worst_of_tab
            elif "🤖" in name:
                sheet_tab = ai_tracks_tab
            
            # Check for specific types or keywords
            elif type_ and ("OG File" in type_ or "OG" in type_):
                sheet_tab = og_files_tab
            elif "Stem" in type_ or "Stems" in name or "Vocal" in name:
                sheet_tab = stems_tab
            elif "Remaster" in name or "Remastered" in name:
                sheet_tab = remasters_tab
            elif "Fake" in name or "AI" in name:
                sheet_tab = fakes_tab
            elif "Tracklist" in name:
                sheet_tab = tracklists_tab
            elif "Art" in name or "Cover" in name:
                sheet_tab = art_tab
            elif "Buy" in notes or "Bought" in notes or "Purchase" in notes:
                sheet_tab = buys_tab
            elif "Social Media" in name or "Instagram" in name or "Twitter" in name:
                sheet_tab = social_media_tab
            elif "Interview" in name:
                sheet_tab = interviews_tab
            elif "Album Cop" in name:
                sheet_tab = album_copies_tab
            elif "Recently Recorded" in notes or "New Recording" in notes:
                sheet_tab = recently_recorded_tab
            elif "Recent" in notes and not "Recently" in notes:
                sheet_tab = recent_tab
            else:
                # Default to Unreleased
                sheet_tab = unreleased_tab
            
            # Get or create metadata for this song
            metadata, created = SongMetadata.objects.get_or_create(
                song=song,
                defaults={'sheet_tab': sheet_tab}
            )
            
            if not created and (metadata.sheet_tab is None or metadata.sheet_tab != sheet_tab):
                # Update existing metadata only if the sheet_tab is None or different
                metadata.sheet_tab = sheet_tab
                metadata.save()
                updated_count += 1
                self.stdout.write(f"Updated sheet tab for song: {song} to {sheet_tab.name}")
            elif created:
                created_count += 1
                self.stdout.write(f"Created sheet tab association for song: {song} as {sheet_tab.name}")
        
        # Special handling for Released tab - make sure all official released songs are there
        released_songs = CartiCatalog.objects.filter(type__in=["Single", "Album Track"])
        for song in released_songs:
            metadata, created = SongMetadata.objects.get_or_create(
                song=song,
                defaults={'sheet_tab': released_tab}
            )
            
            if not created and metadata.sheet_tab != released_tab:
                # Update existing metadata
                metadata.sheet_tab = released_tab
                metadata.save()
                updated_count += 1
                self.stdout.write(f"Updated sheet tab for song: {song} to {released_tab.name}")
            elif created:
                created_count += 1
                self.stdout.write(f"Created sheet tab association for song: {song} as {released_tab.name}")
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed songs with sheet tab information: created {created_count}, updated {updated_count}'
        ))