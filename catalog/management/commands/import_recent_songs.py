from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongMetadata, SongCategory
from django.db import transaction

class Command(BaseCommand):
    help = "Import recent songs that aren't in the database yet"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be changed without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Importing recent songs that are missing from the database...')
        
        # Ensure we have Recent tab
        recent_tab, _ = SheetTab.objects.get_or_create(name="Recent")
        unreleased_tab, _ = SheetTab.objects.get_or_create(name="Unreleased")
        
        # New songs to add
        new_songs = [
            {
                'era': 'MUSIC',
                'name': 'POP YO SHI TWIN* (feat. Lil Yachty) (prod. F1LTHY) (DOYA)',
                'notes': "Leaked on April 13th, 2025. Recorded sometime in 2024. Received lots of backlash from Cartihub members (understood, the song sucks) Was mentioned earlier on in 2024 to be a possible GB option but staff didn't want to disrupt the ongoing 'I AM MUSIC' rollout. Another snippet surfaced on December 12th 2024. Raahim would reveal that the real name is 'POP YO SHI TWIN' on April 2, 2025. Has a short yatchy feat. Song leaked in full on 4/13/2025 after a succesful GB, alongside Dancer.",
                'leak_date': 'Apr 13, 2025',
                'file_date': '',
                'type': 'Throwaway',
                'available_length': 'Full',
                'quality': 'CD Quality',
                'links': 'https://pillowcase.su/f/1c49c9042dd24b0b1919aa5367565b90',
                'primary_link': 'https://pillowcase.su/f/1c49c9042dd24b0b1919aa5367565b90',
            },
            {
                'era': 'MUSIC',
                'name': 'OVERDOSE* (prod. F1LTHY) (SWAG OD, FAKE LOVE)',
                'notes': "Leaked during the April 11th, 2025 GB. Track is untitled, for the moment. (No earrape Hi-Hats, clearer vocals & better mix edit, can be found in 'Remaster' tab). Chosen, cuz comm was so retarded that they rather see a melodic mumble than a finished experimental song. If comm wasnt so retarded Cow would never sell this bs... Sugga chose the name, other owners listen to too much juice wrld and wanted to call it \"Fake Love\".",
                'leak_date': 'Apr 11, 2025',
                'file_date': 'Jul 4, 2023',
                'type': 'Throwaway',
                'available_length': 'Full',
                'quality': 'CD Quality',
                'links': 'https://music.froste.lol/song/691ed60477afe00a2e39e53ce3ad1b69',
                'primary_link': 'https://music.froste.lol/song/691ed60477afe00a2e39e53ce3ad1b69',
            },
            {
                'era': 'TMB Collab',
                'name': '🏆 Dancer (prod. TrapMoneyBenny)', 
                'notes': 'Leaked on April 13th, 2025 through a Krakenfiles link. Grail found by guybrushthreep & Raahim on KTT. Spirdark put the snippets on his YT channel. TrapMoneyBenny played this song in the studio because he had "an opportunity with Carti".',
                'leak_date': 'Apr 13, 2025',
                'file_date': 'Jul 19, 2017',
                'type': 'Throwaway',
                'available_length': 'Full',
                'quality': 'CD Quality',
                'links': 'https://krakenfiles.com/view/8iRoKphOSf/file.html',
                'primary_link': 'https://krakenfiles.com/view/8iRoKphOSf/file.html',
            }
        ]
        
        # Track which songs we've added
        added_songs = []
        
        with transaction.atomic():
            # Import each song
            for song_data in new_songs:
                # Check if song already exists (by era and name)
                existing = CartiCatalog.objects.filter(
                    era=song_data['era'],
                    name=song_data['name']
                ).first()
                
                if existing:
                    self.stdout.write(f"Song already exists: {song_data['name']} (ID: {existing.id})")
                    continue
                
                # Create new song
                if not dry_run:
                    song = CartiCatalog.objects.create(
                        era=song_data['era'],
                        name=song_data['name'],
                        notes=song_data['notes'],
                        leak_date=song_data['leak_date'],
                        file_date=song_data['file_date'],
                        type=song_data['type'],
                        available_length=song_data['available_length'],
                        quality=song_data['quality'],
                        links=song_data['links'],
                        primary_link=song_data['primary_link']
                    )
                    
                    # Create metadata for Unreleased tab
                    SongMetadata.objects.create(
                        song=song,
                        sheet_tab=unreleased_tab,
                        subsection=None
                    )
                    
                    # Add to Recent tab as a category
                    SongCategory.objects.create(
                        song=song,
                        sheet_tab=recent_tab
                    )
                    
                    added_songs.append(song)
                    self.stdout.write(f"Created song: {song.name} (ID: {song.id})")
                else:
                    self.stdout.write(f"Would create song: {song_data['name']} (DRY RUN)")
        
        # Summary
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f"Successfully added {len(added_songs)} new songs"))
            
            # Make sure they're in the Recent tab
            if added_songs:
                self.stdout.write("Running sort_recent_tab_2025 to update Recent tab ordering...")
                from django.core.management import call_command
                call_command('sort_recent_tab_2025')
        else:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes were made"))