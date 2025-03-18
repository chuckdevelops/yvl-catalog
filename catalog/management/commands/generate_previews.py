from django.core.management.base import BaseCommand
from catalog.preview_processor import process_all_songs, generate_preview_for_song
import json

class Command(BaseCommand):
    help = 'Generate 30-second preview clips for songs'

    def add_arguments(self, parser):
        parser.add_argument('--song_id', type=int, help='Process a specific song by ID')
        parser.add_argument('--all', action='store_true', help='Process all songs without previews')
        parser.add_argument('--output', type=str, help='Output JSON results to file')

    def handle(self, *args, **options):
        song_id = options.get('song_id')
        process_all = options.get('all')
        output_file = options.get('output')
        
        if song_id:
            self.stdout.write(self.style.SUCCESS(f'Processing preview for song {song_id}...'))
            preview_url = generate_preview_for_song(song_id)
            
            if preview_url:
                self.stdout.write(self.style.SUCCESS(f'Successfully generated preview: {preview_url}'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to generate preview for song {song_id}'))
                
        elif process_all:
            self.stdout.write(self.style.SUCCESS('Processing previews for all songs without previews...'))
            results = process_all_songs()
            
            self.stdout.write(self.style.SUCCESS(f'Completed processing:'))
            self.stdout.write(f'  Success: {results["success"]}')
            self.stdout.write(f'  Failed: {results["failed"]}')
            
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
                self.stdout.write(self.style.SUCCESS(f'Results saved to {output_file}'))
                
        else:
            self.stdout.write(self.style.WARNING('No action specified. Use --song_id or --all to generate previews.'))