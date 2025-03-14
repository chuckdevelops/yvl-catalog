from django.core.management.base import BaseCommand
from catalog.models import SheetTab
from django.db import models

class Command(BaseCommand):
    help = 'Reorders the sheet tabs to display in a specific order in the dropdown'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be changed without actually changing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Define the order (tabs not in this list will be ordered alphabetically after these)
        ordered_tabs = [
            'Released',
            'Unreleased',
            '🏆 Grails',
            '🥇 Wanted',
            '⭐ Best Of',
            '✨ Special',
        ]
        
        # Update the view to show tabs in the specified order
        self.stdout.write('Modifying sheet tabs order in views.py...')
        
        if not dry_run:
            # Modify views.py to update tab ordering
            from catalog.views import song_list
            with open('/Users/garypayton/Desktop/nberworking3/catalog/views.py', 'r') as file:
                content = file.read()
            
            # Find and replace the line that sets sheet_tabs in the context
            old_line = "    sheet_tabs = SheetTab.objects.all().order_by('name')"
            new_line = """    # Custom ordering for specific tabs
    tab_order_map = {
        'Released': 1,
        'Unreleased': 2,
        '🏆 Grails': 3,
        '🥇 Wanted': 4,
        '⭐ Best Of': 5,
        '✨ Special': 6,
    }
    
    # Sort tabs with custom order first, then alphabetically
    sheet_tabs = sorted(
        SheetTab.objects.all(),
        key=lambda tab: (tab_order_map.get(tab.name, 999), tab.name)
    )"""
            
            if old_line in content:
                new_content = content.replace(old_line, new_line)
                with open('/Users/garypayton/Desktop/nberworking3/catalog/views.py', 'w') as file:
                    file.write(new_content)
                self.stdout.write(self.style.SUCCESS('Successfully updated views.py to use custom tab ordering'))
            else:
                self.stdout.write(self.style.ERROR('Could not find the expected line in views.py. Manual editing required.'))
        else:
            self.stdout.write('In views.py, would replace:')
            self.stdout.write('    sheet_tabs = SheetTab.objects.all().order_by(\'name\')')
            self.stdout.write('with custom ordering code to prioritize specific tabs')
            
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN: No changes were made'))