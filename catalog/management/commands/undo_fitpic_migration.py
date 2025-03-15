from django.core.management.base import BaseCommand
from catalog.models import FitPic

class Command(BaseCommand):
    help = 'Removes the recently migrated FitPic entries (IDs 27-56)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be deleted without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Define the ID range based on the migration output
        start_id = 27
        end_id = 56
        
        # Find the FitPic entries in the ID range
        fitpics_to_remove = FitPic.objects.filter(id__gte=start_id, id__lte=end_id)
        count = fitpics_to_remove.count()
        
        self.stdout.write(f"Found {count} FitPic entries to remove (IDs {start_id}-{end_id})")
        
        # Print the entries that will be removed
        for pic in fitpics_to_remove:
            self.stdout.write(f"Would remove: {pic.caption} (ID: {pic.id})")
        
        if not dry_run:
            # Delete the entries
            fitpics_to_remove.delete()
            self.stdout.write(self.style.SUCCESS(f"Successfully removed {count} FitPic entries"))
        else:
            self.stdout.write(self.style.WARNING(f"\nDRY RUN: No changes made to the database"))
            self.stdout.write(f"Would remove {count} FitPic entries")