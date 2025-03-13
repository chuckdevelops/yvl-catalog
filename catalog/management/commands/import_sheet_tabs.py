from django.core.management.base import BaseCommand
from catalog.models import SheetTab

class Command(BaseCommand):
    help = 'Import the sheet tabs from the Playboi Carti Tracker spreadsheet'

    def handle(self, *args, **options):
        # Sheet tabs from the HTML
        sheet_tabs = [
            {"name": "Unreleased", "sheet_id": "0"},
            {"name": "Released", "sheet_id": "245504108"},
            {"name": "Recent", "sheet_id": "1962169030"},
            {"name": "🏆 Grails", "sheet_id": "2131545997"},
            {"name": "🥇 Wanted", "sheet_id": "801413102"},
            {"name": "⭐ Best Of", "sheet_id": "334149012"},
            {"name": "✨ Special", "sheet_id": "2032692991"},
            {"name": "🗑️ Worst Of", "sheet_id": "305356845"},
            {"name": "🤖 AI Tracks", "sheet_id": "980475775"},
            {"name": "Stems", "sheet_id": "711785744"},
            {"name": "Art", "sheet_id": "487023460"},
            {"name": "Tracklists", "sheet_id": "1038033313"},
            {"name": "🔈Remasters", "sheet_id": "29911022"},
            {"name": "Misc", "sheet_id": "1033793988"},
            {"name": "Recently Recorded", "sheet_id": "1684992423"},
            {"name": "Buys", "sheet_id": "816874642"},
            {"name": "Fakes", "sheet_id": "1412910635"},
            {"name": "OG Files", "sheet_id": "461795881"},
            {"name": "Interviews", "sheet_id": "2029159276"},
            {"name": "Album Copies", "sheet_id": "19287955"},
            {"name": "Social Media", "sheet_id": "398007157"},
            {"name": "Fit Pics", "sheet_id": "879005069"},
            {"name": "Key", "sheet_id": "2106527010"}
        ]

        # Create SheetTab instances
        for tab in sheet_tabs:
            sheet_tab, created = SheetTab.objects.get_or_create(
                sheet_id=tab["sheet_id"],
                defaults={"name": tab["name"]}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created sheet tab: {tab["name"]}'))
            else:
                self.stdout.write(f'Sheet tab already exists: {tab["name"]}')
        
        self.stdout.write(self.style.SUCCESS('Successfully imported sheet tabs'))