from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongMetadata
import re

class Command(BaseCommand):
    help = 'Associate songs with sheet tabs based on emoji markers in song names'

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
        except SheetTab.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Sheet tab not found: {e}"))
            return
        
        # Get all songs
        songs = CartiCatalog.objects.all()
        
        updated_count = 0
        created_count = 0
        
        # Iterate through all songs
        for song in songs:
            name = song.name if song.name else ""
            
            # Determine the appropriate sheet tab based on name markers
            sheet_tab = None
            
            # Try to match by emoji first
            if "🏆" in name:
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
            elif song.type and ("OG File" in song.type or "OG" in song.type):
                sheet_tab = og_files_tab
            else:
                # Default to Unreleased
                sheet_tab = unreleased_tab
            
            # Get or create metadata for this song
            metadata, created = SongMetadata.objects.get_or_create(
                song=song,
                defaults={'sheet_tab': sheet_tab}
            )
            
            if not created:
                # Update existing metadata
                metadata.sheet_tab = sheet_tab
                metadata.save()
                updated_count += 1
                self.stdout.write(f"Updated sheet tab for song: {song} to {sheet_tab.name}")
            else:
                created_count += 1
                self.stdout.write(f"Created sheet tab association for song: {song} as {sheet_tab.name}")
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed songs with sheet tab information: created {created_count}, updated {updated_count}'
        ))