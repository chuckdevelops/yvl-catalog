from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, FitPic, Interview
import re

class Command(BaseCommand):
    help = 'Migrates songs with URL qualities to the FitPic and Interview models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be migrated without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all songs with link-based qualities (Instagram, Imgur, etc.)
        instagram_pattern = r'https://www\.instagram\.com/p/'
        imgur_pattern = r'https://imgur\.com'
        office_pattern = r'https://officemagazine\.net'
        youtube_pattern = r'https://www\.youtube\.com'
        
        # Find songs with link qualities
        link_songs = CartiCatalog.objects.filter(
            quality__startswith='http'
        )
        
        self.stdout.write(f"Found {link_songs.count()} songs with URL-based qualities")
        
        # Keep track of migration counts
        fit_pics_migrated = 0
        interviews_migrated = 0
        skipped = 0
        
        # Process each song
        for song in link_songs:
            quality = song.quality
            
            # Determine target model based on URL pattern
            if re.match(youtube_pattern, quality):
                # YouTube link should go to Interviews
                target = "Interview"
                
                if not dry_run:
                    # Create a new Interview entry
                    outlet = "YouTube"
                    subject_matter = song.name if song.name else "Unlabeled Interview/Video"
                    era = song.era if song.era else "Unknown Era"
                    date = song.leak_date if song.leak_date else "Unknown Date"
                    special_notes = song.notes if song.notes else ""
                    interview_type = "Video Interview"
                    available = True
                    source_links = quality
                    
                    # Create the Interview object
                    new_interview = Interview.objects.create(
                        outlet=outlet,
                        subject_matter=subject_matter,
                        era=era,
                        date=date,
                        special_notes=special_notes,
                        interview_type=interview_type,
                        available=available,
                        source_links=source_links
                    )
                    self.stdout.write(self.style.SUCCESS(f"Migrated to Interview: {song.name} → Interview #{new_interview.id}"))
                    interviews_migrated += 1
                else:
                    self.stdout.write(f"Would migrate to Interview: {song.name}")
                    interviews_migrated += 1
                
            elif re.match(instagram_pattern, quality) or re.match(imgur_pattern, quality) or re.match(office_pattern, quality):
                # Instagram/Imgur/Office links should go to FitPics
                target = "FitPic"
                
                if not dry_run:
                    # Create a new FitPic entry
                    caption = song.name if song.name else "Untitled Pic"
                    era = song.era if song.era else "Unknown Era"
                    notes = song.notes if song.notes else ""
                    
                    # Detect photographer from notes if possible
                    photographer = None
                    if notes and "photographer:" in notes.lower():
                        photographer_match = re.search(r'photographer:\s*([^\.;,\n]+)', notes, re.IGNORECASE)
                        if photographer_match:
                            photographer = photographer_match.group(1).strip()
                    
                    # Extract date from song data
                    release_date = song.leak_date if song.leak_date else "Unknown Date"
                    
                    # Determine pic_type based on pattern
                    if "officemagazine" in quality:
                        pic_type = "Magazine"
                    else:
                        pic_type = "Social Media Post"
                        
                    # Other fields with default values
                    portion = "Full"
                    pic_quality = "Standard Quality"
                    
                    # Create the FitPic object
                    new_fitpic = FitPic.objects.create(
                        caption=caption,
                        notes=notes,
                        photographer=photographer,
                        era=era,
                        release_date=release_date,
                        pic_type=pic_type,
                        portion=portion,
                        quality=pic_quality,
                        source_links=quality
                    )
                    self.stdout.write(self.style.SUCCESS(f"Migrated to FitPic: {song.name} → FitPic #{new_fitpic.id}"))
                    fit_pics_migrated += 1
                else:
                    self.stdout.write(f"Would migrate to FitPic: {song.name}")
                    fit_pics_migrated += 1
            else:
                # Unrecognized URL pattern
                self.stdout.write(self.style.WARNING(f"Skipping: {song.name} - Unrecognized URL pattern: {quality}"))
                skipped += 1
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f"\nDRY RUN: No changes made to the database"))
            self.stdout.write(f"Would migrate {fit_pics_migrated} songs to FitPics")
            self.stdout.write(f"Would migrate {interviews_migrated} songs to Interviews")
            self.stdout.write(f"Would skip {skipped} songs with unrecognized URL patterns")
        else:
            self.stdout.write(self.style.SUCCESS(f"\nSuccessfully migrated:"))
            self.stdout.write(f"- {fit_pics_migrated} songs to FitPics")
            self.stdout.write(f"- {interviews_migrated} songs to Interviews")
            self.stdout.write(f"Skipped {skipped} songs with unrecognized URL patterns")