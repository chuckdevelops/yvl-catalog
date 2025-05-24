from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, HomepageSettings
from django.db.models import Q
from datetime import datetime
import re

class Command(BaseCommand):
    help = 'Update the Recently Leaked section on the homepage with most recent 2025 leaks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be changed without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Finding most recent leaked unreleased songs from 2025...')
        
        # Get Homepage Settings record (create if it doesn't exist)
        homepage_settings, created = HomepageSettings.objects.get_or_create()
        
        if created:
            self.stdout.write('Created new Homepage Settings record')
        
        # 1. Get the most recent songs by their leak date that contains "2025"
        recent_leaks = CartiCatalog.objects.filter(
            Q(leak_date__icontains='2025') & 
            Q(metadata__sheet_tab__name='Unreleased')
        ).order_by('-id')[:15]
        
        # 2. Parse the dates more precisely and sort by most recent
        songs_with_dates = []
        
        # Date formats to try
        date_formats = [
            '%m/%d/%Y',     # 03/15/2024
            '%m/%d/%y',     # 03/15/24
            '%B %d, %Y',    # March 15, 2024
            '%b %d, %Y',    # Mar 15, 2024
            '%B %d %Y',     # April 13 2025
            '%d-%m-%Y',     # 15-03-2024
            '%Y-%m-%d',     # 2024-03-15
            '%m/%Y',        # 03/2024
            '%B %Y',        # March 2024
            '%b %Y',        # Mar 2024
        ]
        
        for song in recent_leaks:
            leak_date_str = song.leak_date
            parsed_date = None
            
            if leak_date_str and '2025' in leak_date_str:
                # Clean the date string (remove ordinal suffixes)
                cleaned_date = re.sub(r'(\d+)(st|nd|rd|th),', r'\1,', leak_date_str.strip())
                cleaned_date = re.sub(r'(\d+)(st|nd|rd|th) ', r'\1 ', cleaned_date)
                
                # Try each format
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(cleaned_date, fmt)
                        break
                    except ValueError:
                        try:
                            # Try original string as fallback
                            parsed_date = datetime.strptime(leak_date_str, fmt)
                            break
                        except ValueError:
                            continue
            
            # Only include songs with parsed dates
            if parsed_date and parsed_date.year == 2025:
                songs_with_dates.append((song, parsed_date))
                
        # Sort by date (newest first)
        sorted_songs = sorted(
            songs_with_dates,
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Extract just the song objects for the top 5
        final_songs = [song for song, _ in sorted_songs[:5]]
        
        # Display what we're going to do
        self.stdout.write(f'Found {len(final_songs)} recent leaked songs to add to Recently Leaked section:')
        for i, song in enumerate(final_songs, 1):
            self.stdout.write(f'{i}. {song.name} (Era: {song.era}, Leak Date: {song.leak_date})')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes were made'))
            return
        
        # Update HomePage Settings
        homepage_settings.enable_custom_recently_leaked = True
        homepage_settings.save()
        
        # Clear existing songs and add new ones
        homepage_settings.recently_leaked_songs.clear()
        for song in final_songs:
            homepage_settings.recently_leaked_songs.add(song)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated Recently Leaked section with {len(final_songs)} songs'))