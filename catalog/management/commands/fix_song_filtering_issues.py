from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix filtering issues for specific songs'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Fix Other Shit (prod. Hit-Boy) - Change era from Self-Titled to Playboi Carti
            song1 = CartiCatalog.objects.get(id=68306)
            old_era1 = song1.era
            song1.era = "Playboi Carti"
            song1.save()
            self.stdout.write(f"Updated Song ID 68306 '{song1.name}' era from '{old_era1}' to '{song1.era}'")
            
            # Check Lame Niggaz and make sure it's properly set
            song2 = CartiCatalog.objects.get(id=1676)
            self.stdout.write(f"Verified Song ID 1676 '{song2.name}' era='{song2.era}' type='{song2.type}'")
            
            # Verify the songs are now correctly filtered
            playboi_carti_streaming = CartiCatalog.objects.filter(
                era="Playboi Carti", 
                type="Streaming"
            ).values_list('id', 'name')
            
            self.stdout.write("Songs in Playboi Carti era with Streaming type:")
            for id, name in playboi_carti_streaming:
                self.stdout.write(f"- ID: {id}, Name: {name}")