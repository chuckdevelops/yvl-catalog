from django.core.management.base import BaseCommand
from catalog.models import ArtMedia
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Import sample art media data for the Playboi Carti Catalog'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all entries even if they already exist',
        )

    def handle(self, *args, **options):
        force_update = options.get('force', False)
        
        # Sample art data based on the structure shared by the user
        art_data = [
            {
                'era': 'Aviation Class',
                'name': 'TOO FLY KID',
                'notes': 'unknown purpose',
                'image_url': 'https://placehold.co/600x600/png?text=TOO+FLY+KID',
                'media_type': 'Unknown',
                'was_used': False,
                'links': ''
            },
            {
                'era': 'Killing Me Softly',
                'name': 'Killing Me Softly',
                'notes': 'Coverart for Carti\'s 2010 or 2011 project "Killing Me Softly. The album uses the same image as it\'s cover as Nas\'s NASIR, even though the album was concieved 6 years before NASIR.',
                'image_url': 'https://placehold.co/600x600/png?text=Killing+Me+Softly',
                'media_type': 'Album Cover',
                'was_used': True,
                'links': 'https://yungcarti.tumblr.com/image/4992098042'
            },
            {
                'era': 'THC: The High Chronicals',
                'name': 'The High Chronicals',
                'notes': 'The art for Playboi Carti\'s (then known as $ir Cartier) mixtape "The High Chronicals"',
                'image_url': 'https://placehold.co/600x600/png?text=The+High+Chronicals',
                'media_type': 'Album Cover',
                'was_used': True,
                'links': 'https://imgur.com/6q1dUzi'
            },
            {
                'era': 'THC: The High Chronicals',
                'name': 'Living Reckless',
                'notes': 'Cover of Living Reckless',
                'image_url': 'https://placehold.co/600x600/png?text=Living+Reckless',
                'media_type': 'Single Art',
                'was_used': True,
                'links': ''
            },
            {
                'era': 'THC: The High Chronicals',
                'name': 'Carolina Blue [OG Cover]',
                'notes': 'Carolina Blue\'s OG Cover without any edits, found in Carti\'s Tumblr.',
                'image_url': 'https://placehold.co/600x600/png?text=Carolina+Blue',
                'media_type': 'Single Art',
                'was_used': False,
                'links': 'https://yungcarti.tumblr.com/post/16736117122'
            },
            {
                'era': 'Kream',
                'name': 'Sir Cartier - Carolina Blue (chopped n screwed by A$3 CliChe)',
                'notes': 'Cover art for Sir Cartier - Carolina Blue ( chopped n screwed by A$3 CliChe ) Cover art made by @DiamondsnCaviar',
                'image_url': 'https://placehold.co/600x600/png?text=Carolina+Blue+Chopped',
                'media_type': 'Single Art',
                'was_used': True,
                'links': ''
            },
            {
                'era': 'Kream',
                'name': 'Kream',
                'notes': 'Coverart for Kream. The project later evolved into Young Mi$fit.',
                'image_url': 'https://placehold.co/600x600/png?text=Kream',
                'media_type': 'Album Cover',
                'was_used': False,
                'links': 'https://www.tumblr.com/yungcarti/27219823849/sir-cartier?source=share'
            },
            {
                'era': 'Self-Titled',
                'name': 'Playboi Carti Album Cover',
                'notes': 'Official album cover for Playboi Carti\'s self-titled debut album released in 2017.',
                'image_url': 'https://placehold.co/600x600/png?text=Playboi+Carti',
                'media_type': 'Album Cover',
                'was_used': True,
                'links': ''
            },
            {
                'era': 'Die Lit',
                'name': 'Die Lit Album Cover',
                'notes': 'Official album cover for Playboi Carti\'s second studio album "Die Lit" released in 2018.',
                'image_url': 'https://placehold.co/600x600/png?text=Die+Lit',
                'media_type': 'Album Cover',
                'was_used': True,
                'links': ''
            },
            {
                'era': 'Whole Lotta Red',
                'name': 'Whole Lotta Red Album Cover',
                'notes': 'Official album cover for Playboi Carti\'s third studio album "Whole Lotta Red" released in 2020.',
                'image_url': 'https://placehold.co/600x600/png?text=Whole+Lotta+Red',
                'media_type': 'Album Cover',
                'was_used': True,
                'links': ''
            }
        ]
        
        self.stdout.write(f"Processing {len(art_data)} art media items")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for item in art_data:
            if not item['name']:
                continue  # Skip items without a name
            
            try:
                # Try to find an existing record by name and era
                existing = ArtMedia.objects.filter(name=item['name'])
                if item['era']:
                    existing = existing.filter(era=item['era'])
                
                if existing.exists() and not force_update:
                    skipped_count += 1
                    continue
                
                if existing.exists():
                    # Update existing record
                    art_media = existing.first()
                    art_media.notes = item['notes']
                    art_media.image_url = item['image_url']
                    art_media.media_type = item['media_type']
                    art_media.was_used = item['was_used']
                    art_media.links = item['links']
                    art_media.save()
                    updated_count += 1
                else:
                    # Create new record
                    ArtMedia.objects.create(
                        era=item['era'],
                        name=item['name'],
                        notes=item['notes'],
                        image_url=item['image_url'],
                        media_type=item['media_type'],
                        was_used=item['was_used'],
                        links=item['links']
                    )
                    created_count += 1
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing art item '{item['name']}': {e}"))
                
        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed art media: created {created_count}, updated {updated_count}, skipped {skipped_count}'
        ))