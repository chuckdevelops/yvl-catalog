from django.core.management.base import BaseCommand
from catalog.models import ArtMedia
import random

class Command(BaseCommand):
    help = 'Import a comprehensive set of art data for the Playboi Carti Catalog'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all entries even if they already exist',
        )

    def handle(self, *args, **options):
        force_update = options.get('force', False)
        
        # Base era and type data for generating more items
        eras = [
            'Aviation Class',
            'Killing Me Softly',
            'THC: The High Chronicals',
            'Kream',
            'Young Mi$fit',
            'Cash Carti',
            'Self-Titled',
            'Die Lit',
            'Whole Lotta Red',
            'Narcissist',
            'Music',
            'V2 Era',
            'V3 Era',
            'Opium',
            'Recent Singles'
        ]
        
        media_types = [
            'Album Cover',
            'Single Art',
            'Tour Poster',
            'Promotional Image',
            'Magazine Cover',
            'Photoshoot',
            'Fan Art',
            'Merchandise Design',
            'Music Video Still',
            'Logo Design',
            'Social Media Post',
            'Unknown'
        ]
        
        # Generate a comprehensive set of art items (over 100 items)
        art_data = []
        
        # First add the essential album covers and key artworks
        essentials = [
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
                'era': 'Young Mi$fit',
                'name': 'Young Mi$fit Cover',
                'notes': 'Official artwork for $ir Cartier\'s Young Mi$fit tape',
                'image_url': 'https://placehold.co/600x600/png?text=Young+Mi$fit',
                'media_type': 'Album Cover',
                'was_used': True,
                'links': ''
            },
            {
                'era': 'Cash Carti',
                'name': 'Fetti Single Art',
                'notes': 'Cover art for the "Fetti" single with Da$h and Maxo Kream',
                'image_url': 'https://placehold.co/600x600/png?text=Fetti',
                'media_type': 'Single Art',
                'was_used': True,
                'links': ''
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
            },
            {
                'era': 'Whole Lotta Red',
                'name': 'WLR Vampire Art',
                'notes': 'Artwork used in promotional materials for Whole Lotta Red, featuring vampire imagery.',
                'image_url': 'https://placehold.co/600x600/png?text=WLR+Vampire+Art',
                'media_type': 'Promotional Image',
                'was_used': True,
                'links': ''
            },
            {
                'era': 'Narcissist',
                'name': 'Narcissist Tour Poster',
                'notes': 'Poster for the Narcissist tour that was announced but later became the King Vamp tour.',
                'image_url': 'https://placehold.co/600x600/png?text=Narcissist+Tour',
                'media_type': 'Tour Poster',
                'was_used': True,
                'links': ''
            },
            {
                'era': 'Music',
                'name': 'Music Teaser Image',
                'notes': 'Promotional image for the album "Music"',
                'image_url': 'https://placehold.co/600x600/png?text=Music+Teaser',
                'media_type': 'Promotional Image',
                'was_used': True,
                'links': ''
            }
        ]
        
        art_data.extend(essentials)
        
        # Generate additional items from each era
        for era in eras:
            # Number of additional items for this era (3-8)
            num_items = random.randint(3, 8)
            
            for i in range(num_items):
                # Pick a media type for this item
                media_type = random.choice(media_types)
                
                # Generate a name based on era and media type
                if media_type == 'Single Art':
                    song_names = [
                        'Magnolia', 'wokeuplikethis*', 'R.I.P.', 'Shoota', 'Flatbed Freestyle',
                        'Long Time', 'New Choppa', 'dothatshit!', 'Broke Boi', 'Fetti',
                        'Flex', 'Location', 'Kelly K', 'Other Shit', 'Yah Mean',
                        'Sky', 'Over', 'ILoveUIHateU', 'Stop Breathing', 'New Tank',
                        'Teen X', 'Rockstar Made', 'JumpOutTheHouse', 'Vamp Anthem', 'M3tamorphosis',
                        'FlatBed Freestyle', 'Foreign', 'Pull Up', 'Fell In Luv', 'No Time'
                    ]
                    name = f"{random.choice(song_names)} Single Cover"
                elif media_type == 'Album Cover':
                    name = f"{era} Alternate Cover {i+1}"
                elif media_type == 'Tour Poster':
                    tour_names = [
                        'Die Lit Tour', 'Self-Titled Tour', 'AWGE Tour', 'WLR Tour',
                        'King Vamp Tour', 'Narcissist Tour', 'Cash Carti Tour',
                        'Opium Tour', 'Music Tour', 'Playboi Carti World Tour'
                    ]
                    name = f"{random.choice(tour_names)} Poster {i+1}"
                elif media_type == 'Magazine Cover':
                    magazines = [
                        'XXL', 'Complex', 'The FADER', 'Vogue', 'i-D', 'Paper',
                        'Rolling Stone', 'Dazed', 'Interview', 'Billboard', 'GQ'
                    ]
                    name = f"{random.choice(magazines)} Magazine Cover {i+1}"
                elif media_type == 'Photoshoot':
                    name = f"{era} Photoshoot {i+1}"
                else:
                    name = f"{era} {media_type} {i+1}"
                
                # Determine if it was used
                was_used = random.choice([True, False])
                
                # Generate a placeholder image url
                image_url = f"https://placehold.co/600x600/png?text={name.replace(' ', '+')}"
                
                # Generate notes
                notes_templates = [
                    f"Artwork from the {era} era used for {media_type.lower()}.",
                    f"Created during {era} sessions, this {media_type.lower()} was {'used officially' if was_used else 'never officially released'}.",
                    f"This {media_type.lower()} was designed for {era} but {'used' if was_used else 'ultimately not used'} in the final release.",
                    f"Found on Carti's Tumblr, this {media_type.lower()} is from the {era} era.",
                    f"Rare {media_type.lower()} from the {era} era, {'officially used' if was_used else 'never officially used'}.",
                    f"Leaked {media_type.lower()} from {era}, {'was used in official merchandise' if was_used else 'was scrapped before release'}."
                ]
                notes = random.choice(notes_templates)
                
                # Generate links (some items have them, some don't)
                link = ""
                if random.random() < 0.3:  # 30% chance to have a link
                    link = f"https://example.com/{era.lower().replace(' ', '-')}-artwork-{i+1}"
                
                art_data.append({
                    'era': era,
                    'name': name,
                    'notes': notes,
                    'image_url': image_url,
                    'media_type': media_type,
                    'was_used': was_used,
                    'links': link
                })
        
        # Remove duplicates by name
        seen_names = set()
        unique_art_data = []
        for item in art_data:
            if item['name'] not in seen_names:
                seen_names.add(item['name'])
                unique_art_data.append(item)
        
        art_data = unique_art_data
        
        self.stdout.write(f"Processing {len(art_data)} art media items")
        
        # First clear all existing entries if using force update
        if force_update:
            ArtMedia.objects.all().delete()
            self.stdout.write("Deleted all existing art media items")
        
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