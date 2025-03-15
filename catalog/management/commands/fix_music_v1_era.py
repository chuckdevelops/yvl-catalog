from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata
from django.db import transaction

class Command(BaseCommand):
    help = 'Update MUSIC [V1] and MUSIC eras to I AM MUSIC [V1]'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get all songs with era "MUSIC [V1]" or "MUSIC"
                songs_v1 = CartiCatalog.objects.filter(era="MUSIC [V1]")
                songs_music = CartiCatalog.objects.filter(era="MUSIC")
                
                count_v1 = songs_v1.count()
                count_music = songs_music.count()
                
                total_songs = count_v1 + count_music
                
                if total_songs == 0:
                    self.stdout.write(self.style.WARNING("No songs found with era 'MUSIC [V1]' or 'MUSIC'"))
                    return
                
                # Update all these songs to have the correct era "I AM MUSIC [V1]"
                songs_v1.update(era="I AM MUSIC [V1]")
                songs_music.update(era="I AM MUSIC [V1]")
                
                self.stdout.write(f"Updated {count_v1} songs from 'MUSIC [V1]' to 'I AM MUSIC [V1]'")
                self.stdout.write(f"Updated {count_music} songs from 'MUSIC' to 'I AM MUSIC [V1]'")
                
                # Update metadata subsection for these songs
                updated_subsection = 0
                all_songs = CartiCatalog.objects.filter(era="I AM MUSIC [V1]")
                
                for song in all_songs:
                    try:
                        metadata = SongMetadata.objects.get(song=song)
                        if metadata.subsection in ["MUSIC [V1]", "MUSIC"]:
                            metadata.subsection = "I AM MUSIC [V1]"
                            metadata.save()
                            updated_subsection += 1
                    except SongMetadata.DoesNotExist:
                        self.stdout.write(f"No metadata found for song: {song.name}")
                
                self.stdout.write(self.style.SUCCESS(f"Successfully updated {total_songs} songs to era 'I AM MUSIC [V1]'"))
                self.stdout.write(self.style.SUCCESS(f"Updated {updated_subsection} songs with subsection 'I AM MUSIC [V1]'"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))