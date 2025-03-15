from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata, SheetTab
from django.db import transaction


class Command(BaseCommand):
    help = 'Adds "Album Track" badge to all official album tracks'

    def handle(self, *args, **options):
        # Get the Released tab
        try:
            released_tab = SheetTab.objects.get(name="Released")
        except SheetTab.DoesNotExist:
            released_tab, _ = SheetTab.objects.get_or_create(name="Released")
            self.stdout.write(self.style.WARNING('Created "Released" tab'))

        with transaction.atomic():
            # Get all songs from Die Lit era
            die_lit_songs = CartiCatalog.objects.filter(era="Die Lit")
            self.stdout.write(f"Found {die_lit_songs.count()} Die Lit songs")

            # Add album track badge to Die Lit songs
            for song in die_lit_songs:
                song_name = song.name.strip()
                # Check if this is one of the official Die Lit tracks in model's die_lit_tracks
                is_official = False
                for official_track in CartiCatalog.die_lit_tracks.keys():
                    if official_track.lower() in song_name.lower():
                        is_official = True
                        break

                if is_official:
                    # Update file_date and type
                    old_file_date = song.file_date
                    old_type = song.type
                    song.file_date = "Album Track"
                    song.type = "Streaming"
                    song.save()
                    
                    # Ensure proper metadata
                    try:
                        metadata = SongMetadata.objects.get(song=song)
                        metadata.sheet_tab = released_tab
                        metadata.subsection = "Die Lit"
                        metadata.save()
                        self.stdout.write(self.style.SUCCESS(
                            f"Updated metadata for: {song_name} - Sheet tab: {metadata.sheet_tab.name}, Subsection: {metadata.subsection}")
                        )
                    except SongMetadata.DoesNotExist:
                        metadata = SongMetadata.objects.create(
                            song=song,
                            sheet_tab=released_tab,
                            subsection="Die Lit"
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f"Created metadata for: {song_name} - Sheet tab: {metadata.sheet_tab.name}, Subsection: {metadata.subsection}")
                        )
                    
                    # Log the update
                    self.stdout.write(self.style.SUCCESS(
                        f"Updated {song_name}: file_date: {old_file_date} -> Album Track, type: {old_type} -> Streaming"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Skipped {song_name}: Not recognized as an official Die Lit track"
                    ))

            # Do the same for other album eras (Self-Titled, Whole Lotta Red)
            # Self-Titled
            self_titled_songs = CartiCatalog.objects.filter(era="Self-Titled")
            self.stdout.write(f"Found {self_titled_songs.count()} Self-Titled songs")

            for song in self_titled_songs:
                song_name = song.name.strip()
                # Check if this is one of the official Self-Titled tracks in model's selftitled_tracks
                is_official = False
                for official_track in CartiCatalog.selftitled_tracks.keys():
                    if official_track.lower() in song_name.lower():
                        is_official = True
                        break

                if is_official:
                    # Update file_date and type
                    old_file_date = song.file_date
                    old_type = song.type
                    song.file_date = "Album Track"
                    song.type = "Streaming"
                    song.save()
                    
                    # Ensure proper metadata
                    try:
                        metadata = SongMetadata.objects.get(song=song)
                        metadata.sheet_tab = released_tab
                        metadata.subsection = "Self-Titled"
                        metadata.save()
                        self.stdout.write(self.style.SUCCESS(
                            f"Updated metadata for: {song_name} - Sheet tab: {metadata.sheet_tab.name}, Subsection: {metadata.subsection}")
                        )
                    except SongMetadata.DoesNotExist:
                        metadata = SongMetadata.objects.create(
                            song=song,
                            sheet_tab=released_tab,
                            subsection="Self-Titled"
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f"Created metadata for: {song_name} - Sheet tab: {metadata.sheet_tab.name}, Subsection: {metadata.subsection}")
                        )
                    
                    # Log the update
                    self.stdout.write(self.style.SUCCESS(
                        f"Updated {song_name}: file_date: {old_file_date} -> Album Track, type: {old_type} -> Streaming"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Skipped {song_name}: Not recognized as an official Self-Titled track"
                    ))

            # Whole Lotta Red
            wlr_songs = CartiCatalog.objects.filter(era="Whole Lotta Red")
            self.stdout.write(f"Found {wlr_songs.count()} Whole Lotta Red songs")

            for song in wlr_songs:
                song_name = song.name.strip()
                # Check if this is one of the official WLR tracks in model's wlr_tracks
                is_official = False
                for official_track in CartiCatalog.wlr_tracks.keys():
                    if official_track.lower() in song_name.lower():
                        is_official = True
                        break

                if is_official:
                    # Update file_date and type
                    old_file_date = song.file_date
                    old_type = song.type
                    song.file_date = "Album Track"
                    song.type = "Streaming"
                    song.save()
                    
                    # Ensure proper metadata
                    try:
                        metadata = SongMetadata.objects.get(song=song)
                        metadata.sheet_tab = released_tab
                        metadata.subsection = "Whole Lotta Red"
                        metadata.save()
                        self.stdout.write(self.style.SUCCESS(
                            f"Updated metadata for: {song_name} - Sheet tab: {metadata.sheet_tab.name}, Subsection: {metadata.subsection}")
                        )
                    except SongMetadata.DoesNotExist:
                        metadata = SongMetadata.objects.create(
                            song=song,
                            sheet_tab=released_tab,
                            subsection="Whole Lotta Red"
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f"Created metadata for: {song_name} - Sheet tab: {metadata.sheet_tab.name}, Subsection: {metadata.subsection}")
                        )
                    
                    # Log the update
                    self.stdout.write(self.style.SUCCESS(
                        f"Updated {song_name}: file_date: {old_file_date} -> Album Track, type: {old_type} -> Streaming"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Skipped {song_name}: Not recognized as an official Whole Lotta Red track"
                    ))

            self.stdout.write(self.style.SUCCESS("All official album tracks have been updated with 'Album Track' badge"))