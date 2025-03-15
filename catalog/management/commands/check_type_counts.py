from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog
from django.db.models import Count

class Command(BaseCommand):
    help = 'Check counts for each Type value and list them'

    def handle(self, *args, **options):
        # Get counts for each Type value
        type_counts = CartiCatalog.objects.values('type').annotate(count=Count('id')).order_by('-count')
        
        self.stdout.write("Type values and their counts:")
        for type_item in type_counts:
            self.stdout.write(f"- {type_item['type'] or 'None/Empty'}: {type_item['count']} songs")
            
        # Check for types with 0 songs
        zero_count_types = [t['type'] for t in type_counts if t['count'] == 0]
        if zero_count_types:
            self.stdout.write(self.style.WARNING(f"Found {len(zero_count_types)} type values with 0 songs:"))
            for t in zero_count_types:
                self.stdout.write(f"- {t or 'None/Empty'}")
        else:
            self.stdout.write(self.style.SUCCESS("No type values with 0 songs found."))