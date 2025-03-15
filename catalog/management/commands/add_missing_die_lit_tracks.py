from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata, SheetTab
from django.db import transaction


class Command(BaseCommand):
    help = 'Adds missing Die Lit album tracks and ensures they have Album Track badge'

    def handle(self, *args, **options):
        # Die Lit tracks data from user input
        die_lit_tracks = [
            {
                "name": "Pull Up",
                "notes": "Track 12 off Playboi Carti's album \"Die Lit\".",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/424qpX6swdUdhLq95cecNu?si=16d8006950c54799",
                "producer": "Pi'erre Bourne"
            },
            {
                "name": "Mileage (feat. Chief Keef)",
                "notes": "Track 13 off Playboi Carti's album \"Die Lit\".",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1oNcc2isuz7d3hc1fMoHqj?si=1629c5b37b7e4dce",
                "producer": "Pi'erre Bourne"
            },
            {
                "name": "Top (feat. Pi'erre Bourne)",
                "notes": "Track 19 off Playboi Carti's album \"Die Lit\".",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/7HsvTUJcXRQVK6QuALkAvW?si=428feafafa994789",
                "producer": "Pi'erre Bourne"
            }
        ]

        # Get or create the Released tab
        released_tab, _ = SheetTab.objects.get_or_create(name="Released")

        # Find or create the Die Lit subsection
        die_lit_subsection = "Die Lit"

        with transaction.atomic():
            for track_data in die_lit_tracks:
                # Check if the song already exists
                song_name = track_data["name"]
                existing_songs = CartiCatalog.objects.filter(name=song_name, era="Die Lit")

                if existing_songs.exists():
                    song = existing_songs.first()
                    self.stdout.write(self.style.WARNING(f"Song '{song_name}' already exists. Updating file_date to 'Album Track'"))
                    song.file_date = "Album Track"
                    song.type = "Streaming"
                    song.save()
                else:
                    # Create the new song
                    song = CartiCatalog.objects.create(
                        era="Die Lit",
                        name=song_name,
                        notes=track_data["notes"],
                        leak_date=track_data["leak_date"],
                        file_date="Album Track",
                        type="Streaming",
                        links=track_data["links"],
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created new song: {song_name}"))

                # Make sure it has the proper metadata
                metadata, created = SongMetadata.objects.get_or_create(
                    song=song,
                    defaults={
                        "sheet_tab": released_tab,
                        "subsection": die_lit_subsection
                    }
                )
                
                if not created:
                    metadata.sheet_tab = released_tab
                    metadata.subsection = die_lit_subsection
                    metadata.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated metadata for: {song_name}"))

            self.stdout.write(self.style.SUCCESS("All Die Lit tracks have been added/updated with 'Album Track' badge"))