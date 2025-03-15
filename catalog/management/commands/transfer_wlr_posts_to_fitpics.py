import re
from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongCategory, SongMetadata, FitPic

class Command(BaseCommand):
    help = 'Transfer WLR V2 and WLR V3 posts from CartiCatalog to FitPic model'

    def handle(self, *args, **options):
        # Find the Fit Pics sheet tab
        fit_pics_tab = SheetTab.objects.filter(name='Fit Pics').first()
        if not fit_pics_tab:
            self.stderr.write(self.style.ERROR('Fit Pics sheet tab not found!'))
            return
            
        # Get WLR V2 songs to transfer
        wlr_v2_songs = CartiCatalog.objects.filter(era='WLR V2')
        self.stdout.write(f'Found {wlr_v2_songs.count()} WLR V2 posts to transfer')
        
        # Get WLR V3 songs to transfer
        wlr_v3_songs = CartiCatalog.objects.filter(era='WLR V3')
        self.stdout.write(f'Found {wlr_v3_songs.count()} WLR V3 posts to transfer')
        
        # Transfer WLR V2 posts to FitPic
        v2_created = 0
        for song in wlr_v2_songs:
            # Skip if already a FitPic with the same caption
            if FitPic.objects.filter(caption=song.name).exists():
                continue
                
            # Create a new FitPic
            fit_pic = FitPic.objects.create(
                era='WLR V2',
                caption=song.name,
                notes=song.notes,
                photographer='',  # Default to empty
                release_date=song.leak_date or 'Unknown',
                pic_type='Post',
                portion='Full',
                quality='High Quality',
                image_url='',  # Default to empty
                source_links=song.links or song.primary_link,
            )
            v2_created += 1
        
        # Transfer WLR V3 posts to FitPic
        v3_created = 0
        for song in wlr_v3_songs:
            # Skip if already a FitPic with the same caption
            if FitPic.objects.filter(caption=song.name).exists():
                continue
                
            # Create a new FitPic
            fit_pic = FitPic.objects.create(
                era='WLR V3',
                caption=song.name,
                notes=song.notes,
                photographer='',  # Default to empty
                release_date=song.leak_date or 'Unknown',
                pic_type='Post',
                portion='Full',
                quality='High Quality',
                image_url='',  # Default to empty
                source_links=song.links or song.primary_link,
            )
            v3_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {v2_created} WLR V2 fit pics'))
        self.stdout.write(self.style.SUCCESS(f'Successfully created {v3_created} WLR V3 fit pics'))
        
        # Print instructions for manually handling next steps
        self.stdout.write(self.style.WARNING('\nManual steps required to complete the process:'))
        self.stdout.write('1. Verify the fit pics have been transferred correctly in the admin panel')
        self.stdout.write('2. Delete the WLR V2 and WLR V3 songs using the following command:')
        self.stdout.write('   python3 manage.py shell -c "from catalog.models import CartiCatalog; CartiCatalog.objects.filter(era__in=[\'WLR V2\', \'WLR V3\']).delete()"')
        self.stdout.write('3. Restart the Django server to refresh the era dropdown options')