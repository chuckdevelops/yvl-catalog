from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog
from django.db import transaction


class Command(BaseCommand):
    help = 'Deletes incomplete I AM MUSIC [V2] tracks that lack proper formatting'

    def handle(self, *args, **options):
        # Names of the tracks in the album - these should be base names only, without producer or feature info
        track_base_names = [
            "POP OUT",
            "CRUSH",
            "K POP",
            "EVIL J0RDAN",
            "MOJO JOJO",
            "PHILLY",
            "RADAR",
            "RATHER LIE",
            "FINE SHIT",
            "BACKD00R",
            "TOXIC",
            "MUNYUN",
            "CRANK",
            "CHARGE DEM HOES A FEE",
            "GOOD CREDIT",
            "I SEEEEEE YOU BABY BOI",
            "WAKE UP F1LTHY",
            "JUMPIN",
            "TRIM",
            "COCAINE NOSE",
            "WE NEED ALL DA VIBES",
            "OLYMPIAN",
            "OPM BABI",
            "TWIN TRIM",
            "LIKE WEEZY",
            "DIS 1 GOT IT",
            "WALK",
            "HBA",
            "OVERLY",
            "SOUTH ATLANTA BABY"
        ]

        # Find and delete incomplete entries
        with transaction.atomic():
            total_deleted = 0
            
            # First, get counts of songs per base name to find duplicates
            for base_name in track_base_names:
                # Look for songs that match the base name but don't have producer info
                # This will find songs like "TWIN TRIM" but not "TWIN TRIM (feat. Lil Uzi Vert) (prod. KP Beatz & Rok)"
                incomplete_entries = CartiCatalog.objects.filter(
                    era="I AM MUSIC [V2]",
                    name__icontains=base_name
                ).exclude(
                    name__icontains="(prod"  # Exclude entries that have producer info
                )
                
                # Also find entries with emoji prefixes that might be incomplete
                emoji_prefixes = ["⭐", "✨", "🤖"]
                for emoji in emoji_prefixes:
                    emoji_entries = CartiCatalog.objects.filter(
                        era="I AM MUSIC [V2]",
                        name__startswith=f"{emoji} {base_name}"
                    ).exclude(
                        name__icontains="(prod"  # Exclude entries that have producer info
                    )
                    if emoji_entries.exists():
                        incomplete_entries = incomplete_entries | emoji_entries
                
                # Delete incomplete entries
                if incomplete_entries.exists():
                    for entry in incomplete_entries:
                        self.stdout.write(self.style.WARNING(f"Deleting incomplete entry: {entry.name}"))
                        entry.delete()
                        total_deleted += 1
            
            self.stdout.write(self.style.SUCCESS(f"Deleted {total_deleted} incomplete I AM MUSIC [V2] tracks"))