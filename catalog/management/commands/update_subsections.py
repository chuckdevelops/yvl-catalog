from django.core.management.base import BaseCommand
import csv
import os
from catalog.models import CartiCatalog, SongMetadata, SheetTab

class Command(BaseCommand):
    help = 'Update the subsection field for songs based on the CSV structure'

    def handle(self, *args, **options):
        csv_path = os.path.join(os.getcwd(), 'sheetsdata.csv')
        
        self.stdout.write(f"Reading from CSV file: {csv_path}")
        
        # Default to the "Unreleased" sheet tab since that's what the primary CSV contains
        default_sheet_tab, _ = SheetTab.objects.get_or_create(
            sheet_id="0",
            defaults={"name": "Unreleased"}
        )
        
        current_era = None
        current_subsection = None
        updated_count = 0
        created_count = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                for i, row in enumerate(csv_reader):
                    if i == 0:  # Skip header row
                        continue
                    
                    # Skip empty rows
                    if not any(row):
                        continue
                        
                    # If the row only has entries in the first few columns and the rest are empty,
                    # it might be a section header or subsection
                    if row[0] and not row[1] and not row[3] and not row[4]:
                        # This is likely a subsection
                        current_subsection = row[0].strip()
                        self.stdout.write(f"Found subsection: {current_subsection}")
                        continue
                    
                    # If the first column has a value like "X Total Full Y OG File...", it's an era header
                    if row[0] and "Total Full" in row[0]:
                        # Extract the era name from the second column
                        if row[1]:
                            current_era = row[1].strip()
                            self.stdout.write(f"Found era: {current_era}")
                        current_subsection = None
                        continue
                    
                    # If we get here, this is likely a song row with actual data
                    era = row[0].strip() if row[0] else current_era
                    name = row[1].strip() if row[1] else None
                    
                    if not name:
                        continue  # Skip rows without a song name
                    
                    # Try to find and update the song in the database
                    try:
                        songs = CartiCatalog.objects.filter(era=era, name=name)
                        if songs.exists():
                            for song in songs:
                                # Get or create metadata for this song
                                metadata, created = SongMetadata.objects.get_or_create(
                                    song=song,
                                    defaults={
                                        'sheet_tab': default_sheet_tab,
                                        'subsection': current_subsection
                                    }
                                )
                                
                                if not created:
                                    # Update existing metadata
                                    metadata.subsection = current_subsection
                                    metadata.save()
                                    updated_count += 1
                                    self.stdout.write(f"Updated metadata for song: {song} with subsection: {current_subsection}")
                                else:
                                    created_count += 1
                                    self.stdout.write(f"Created metadata for song: {song} with subsection: {current_subsection}")
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error updating song {era} - {name}: {e}"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing CSV file: {e}"))
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed songs with subsection information: created {created_count}, updated {updated_count}'
        ))