from django.core.management.base import BaseCommand
import csv
import os

class Command(BaseCommand):
    help = 'Create a CSV template for art media data import'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='art_data_template.csv',
            help='Path to the output CSV file',
        )

    def handle(self, *args, **options):
        output_file = options.get('output')
        
        # Create the CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Era', 'Name', 'Notes', 'Type', 'Used?', 'Link(s)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            # Add some sample rows
            writer.writerow({
                'Era': 'Aviation Class',
                'Name': 'TOO FLY KID',
                'Notes': 'unknown purpose',
                'Type': 'Unknown',
                'Used?': 'No',
                'Link(s)': ''
            })
            writer.writerow({
                'Era': 'Killing Me Softly',
                'Name': 'Killing Me Softly',
                'Notes': 'Coverart for Carti\'s 2010 or 2011 project "Killing Me Softly"',
                'Type': 'Album Cover',
                'Used?': 'Yes',
                'Link(s)': 'https://yungcarti.tumblr.com/image/4992098042'
            })
            writer.writerow({
                'Era': 'THC: The High Chronicals',
                'Name': 'The High Chronicals',
                'Notes': 'The art for Playboi Carti\'s (then known as $ir Cartier) mixtape "The High Chronicals"',
                'Type': 'Album Cover',
                'Used?': 'Yes',
                'Link(s)': 'https://imgur.com/6q1dUzi'
            })
            
            # Add an empty row as a template
            writer.writerow({
                'Era': '',
                'Name': '',
                'Notes': '',
                'Type': '',
                'Used?': '',
                'Link(s)': ''
            })
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created art data template CSV: {os.path.abspath(output_file)}'
        ))
        
        # Print instructions
        self.stdout.write("\nInstructions:")
        self.stdout.write("1. Open the CSV file in a spreadsheet application")
        self.stdout.write("2. Fill in the data for each artwork")
        self.stdout.write("3. For the 'Used?' column, use 'Yes' or 'No'")
        self.stdout.write("4. Save the file as CSV")
        self.stdout.write("5. Import the data using the import_art_media command:")
        self.stdout.write("   python manage.py import_art_media --csv=your_file.csv --download-images")