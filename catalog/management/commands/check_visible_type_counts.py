from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab
from django.db.models import Count, Q

class Command(BaseCommand):
    help = 'Check counts for each Type value excluding stems-only songs'

    def handle(self, *args, **options):
        # Get the Stems tab ID
        try:
            stems_tab = SheetTab.objects.filter(name="Stems").first()
            stems_tab_id = stems_tab.id if stems_tab else None
        except Exception:
            stems_tab_id = None
            
        # Base query filtering out stems-only songs
        if stems_tab_id:
            base_query = CartiCatalog.objects.exclude(
                Q(metadata__sheet_tab_id=stems_tab_id) & 
                ~Q(categories__sheet_tab__isnull=False)  # Only exclude if not in any other tab
            )
        else:
            base_query = CartiCatalog.objects.all()
            
        # Get counts for each Type value
        type_counts = base_query.values('type').annotate(count=Count('id', distinct=True)).order_by('-count')
        
        self.stdout.write("Type values and their counts (excluding stems-only songs):")
        for type_item in type_counts:
            self.stdout.write(f"- {type_item['type'] or 'None/Empty'}: {type_item['count']} songs")
            
        # Check for types with 0 songs
        empty_types = []
        all_types = CartiCatalog.objects.values_list('type', flat=True).distinct()
        for type_val in all_types:
            if type_val and type_val not in ["NaN", "nan"]:
                # Check if it's in the filtered results
                if not any(t['type'] == type_val and t['count'] > 0 for t in type_counts):
                    empty_types.append(type_val)
        
        if empty_types:
            self.stdout.write(self.style.WARNING(f"Found {len(empty_types)} type values with no visible songs:"))
            for t in empty_types:
                self.stdout.write(f"- {t}")
        else:
            self.stdout.write(self.style.SUCCESS("No type values with 0 visible songs found."))