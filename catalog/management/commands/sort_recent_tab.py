from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongCategory
from django.db.models import Q
from datetime import datetime, timedelta
import re

class Command(BaseCommand):
    help = 'Sort songs in the Recent tab by leak date (most recent first)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be changed without actually making changes',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days to look back for recent leaks (default: 365)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_lookback = options['days']
        
        self.stdout.write(f'Looking for songs leaked within the last {days_lookback} days...')
        
        # 1. Identify the "Recent" tab
        try:
            recent_tab = SheetTab.objects.get(name="Recent")
        except SheetTab.DoesNotExist:
            self.stdout.write(self.style.ERROR('Recent tab not found in the database'))
            return
            
        # 2. Get all songs in the Recent tab
        recent_songs = CartiCatalog.objects.filter(
            categories__sheet_tab=recent_tab
        ).distinct()
        
        self.stdout.write(f'Found {recent_songs.count()} songs in the Recent tab')
        
        # 3. Parse leak dates and filter for songs within the lookback period
        one_year_ago = datetime.now() - timedelta(days=days_lookback)
        
        # Dictionary to store songs with parsed dates
        songs_with_dates = []
        
        # Date formats to try (from most to least specific)
        date_formats = [
            '%m/%d/%Y',     # 03/15/2024
            '%m/%d/%y',     # 03/15/24
            '%B %d, %Y',    # March 15, 2024
            '%b %d, %Y',    # Mar 15, 2024
            '%d-%m-%Y',     # 15-03-2024
            '%Y-%m-%d',     # 2024-03-15
            '%m/%Y',        # 03/2024
            '%B %Y',        # March 2024
            '%b %Y',        # Mar 2024
        ]
        
        for song in recent_songs:
            leak_date_str = song.leak_date
            file_date_str = song.file_date
            parsed_date = None
            
            # Try to parse the leak date first
            if leak_date_str:
                # Try each format
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(leak_date_str, fmt)
                        break
                    except ValueError:
                        continue
            
            # If leak date couldn't be parsed, try file date
            if parsed_date is None and file_date_str:
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(file_date_str, fmt)
                        break
                    except ValueError:
                        continue
            
            # Always include the song, even if we couldn't parse its date
            # Songs with valid dates will be sorted to the top
            songs_with_dates.append((song, parsed_date))
        
        # 4. Sort the songs by leak date (most recent first)
        # Put songs with valid dates at the top (sorted by date), then songs without dates
        sorted_songs = sorted(
            songs_with_dates,
            key=lambda x: (x[1] is None, -int(x[1].timestamp()) if x[1] else 0)
        )
        
        # 5. Display and update the order in the database
        if not sorted_songs:
            self.stdout.write(self.style.WARNING('No songs found in the Recent tab'))
            return
        
        # Count songs with valid dates within lookback period
        recent_count = sum(1 for _, date in sorted_songs if date and date >= one_year_ago)
        total_count = len(sorted_songs)
        
        self.stdout.write(f'Found {recent_count} songs with valid leak dates within the last {days_lookback} days')
        self.stdout.write(f'Total songs in Recent tab: {total_count}')
        
        # Display the sorted songs
        self.stdout.write('\nSorted songs:')
        for i, (song, date) in enumerate(sorted_songs, 1):
            date_str = date.strftime("%Y-%m-%d") if date else "Unknown date"
            is_recent = date and date >= one_year_ago
            recent_marker = " (RECENT)" if is_recent else ""
            self.stdout.write(f'{i}. {song.name} - Leaked on: {date_str}{recent_marker}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN: No changes made to the database'))
            return
            
        # Actually update the songs in the database
        self.stdout.write('\nUpdating song order in the database...')
        
        # Remove all songs from the Recent tab
        SongCategory.objects.filter(sheet_tab=recent_tab).delete()
        self.stdout.write('Removed all songs from the Recent tab')
        
        # Add songs back in the sorted order
        for i, (song, date) in enumerate(sorted_songs, 1):
            SongCategory.objects.create(
                song=song,
                sheet_tab=recent_tab
            )
            self.stdout.write(f'Added {song.name} back to Recent tab (position {i})')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully updated {total_count} songs in the Recent tab'))