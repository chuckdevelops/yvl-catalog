from django.core.management.base import BaseCommand
from catalog.models import ArtMedia
import pandas as pd
import os
import requests
from urllib.parse import urlparse
from django.conf import settings
import re
try:
    from bs4 import BeautifulSoup
except ImportError:
    # This will be handled in the command's handle method
    BeautifulSoup = None
import time
import csv

class Command(BaseCommand):
    help = 'Import art media data from a CSV file and download associated images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all entries even if they already exist',
        )
        parser.add_argument(
            '--csv',
            type=str,
            help='Path to the CSV file containing art data',
        )
        parser.add_argument(
            '--download-images',
            action='store_true',
            help='Download images from source links',
        )

    def fetch_image_from_imgur(self, imgur_url):
        """Extract direct image URL from Imgur page"""
        try:
            # Extract imgur ID from URL
            imgur_id = os.path.basename(urlparse(imgur_url).path)
            
            # Make a request to the imgur page
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(imgur_url, headers=headers)
            
            if response.status_code == 200:
                # Parse HTML and find image
                soup = BeautifulSoup(response.text, 'html.parser')
                image_tags = soup.find_all('img')
                
                # Look for the main image - usually contains post ID
                for img in image_tags:
                    src = img.get('src', '')
                    if imgur_id in src and ('imgur' in src or 'i.imgur' in src):
                        # Convert to https if needed
                        if src.startswith('//'):
                            return f'https:{src}'
                        return src
                
                # Fallback - look for any imgur image
                for img in image_tags:
                    src = img.get('src', '')
                    if 'imgur' in src and src.endswith(('.jpg', '.png', '.gif', '.jpeg')):
                        # Convert to https if needed
                        if src.startswith('//'):
                            return f'https:{src}'
                        return src
            
            # If we reach here, we couldn't find the image
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching image from Imgur: {e}"))
            return None

    def fetch_image_from_tumblr(self, tumblr_url):
        """Extract direct image URL from Tumblr page"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(tumblr_url, headers=headers)
            
            if response.status_code == 200:
                # Parse HTML and find image
                soup = BeautifulSoup(response.text, 'html.parser')
                image_tags = soup.find_all('img')
                
                # Look for media and post content images
                for img in image_tags:
                    src = img.get('src', '')
                    if 'media.tumblr.com' in src and src.endswith(('.jpg', '.png', '.gif', '.jpeg')):
                        return src
                
                # Fallback - look for any image with decent size
                largest_image = None
                largest_size = 0
                
                for img in image_tags:
                    src = img.get('src', '')
                    # Skip small icons and avatars
                    if 'avatar' in src.lower() or 'icon' in src.lower():
                        continue
                    
                    # Check if image has width/height attributes
                    width = img.get('width')
                    height = img.get('height')
                    
                    if width and height:
                        try:
                            size = int(width) * int(height)
                            if size > largest_size and src.endswith(('.jpg', '.png', '.gif', '.jpeg')):
                                largest_size = size
                                largest_image = src
                        except (ValueError, TypeError):
                            pass
                
                return largest_image
            
            # If we reach here, we couldn't find the image
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching image from Tumblr: {e}"))
            return None

    def get_direct_image_url(self, source_link):
        """Get a direct image URL from various source links"""
        if not source_link:
            return None
            
        # Check if it's already a direct image URL
        if source_link.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return source_link
            
        # Handle Imgur links
        if 'imgur.com' in source_link:
            return self.fetch_image_from_imgur(source_link)
            
        # Handle Tumblr links
        if 'tumblr.com' in source_link:
            return self.fetch_image_from_tumblr(source_link)
        
        # For other sites, we'd need to implement custom scrapers
        # This function can be expanded as needed
        return None

    def download_image(self, url, art_item):
        """Download an image from URL and save it to media directory"""
        if not url:
            return None
            
        try:
            # Create media directory if it doesn't exist
            media_dir = os.path.join(settings.BASE_DIR, 'media', 'art')
            os.makedirs(media_dir, exist_ok=True)
            
            # Generate a filename based on era and name
            era_slug = re.sub(r'[^\w\s-]', '', art_item['era']).strip().replace(' ', '-').lower() if art_item['era'] else 'unknown'
            name_slug = re.sub(r'[^\w\s-]', '', art_item['name']).strip().replace(' ', '-').lower()
            
            # Get file extension from URL
            ext = os.path.splitext(urlparse(url).path)[1]
            if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                ext = '.jpg'  # Default to jpg
                
            filename = f"{era_slug}-{name_slug}{ext}"
            filepath = os.path.join(media_dir, filename)
            
            # Download the image
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, stream=True)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Return relative URL for database storage
                return f'/media/art/{filename}'
            else:
                self.stdout.write(self.style.WARNING(f"Failed to download image: {url} (Status code: {response.status_code})"))
                return None
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error downloading image: {e}"))
            return None

    def parse_csv(self, csv_path):
        """Parse CSV file into art data list"""
        art_data = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Skip header row or empty rows
                    if not row or 'Era' in row and row['Era'] == 'Era':
                        continue
                        
                    # Extract data from CSV row
                    item = {
                        'era': row.get('Era', '').strip(),
                        'name': row.get('Name', '').strip(),
                        'notes': row.get('Notes', '').strip(),
                        'image_url': '',  # Will be populated later
                        'media_type': row.get('Type', '').strip(),
                        'was_used': row.get('Used?', '').strip().lower() == 'yes',
                        'links': row.get('Link(s)', '').strip()
                    }
                    
                    # Skip rows without a name
                    if not item['name']:
                        continue
                        
                    art_data.append(item)
                    
            return art_data
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error parsing CSV: {e}"))
            return []

    def handle(self, *args, **options):
        # Check for required dependencies
        if download_images and BeautifulSoup is None:
            self.stdout.write(self.style.ERROR("BeautifulSoup4 is required for image downloading. Please install it with: pip install beautifulsoup4"))
            return
            
        force_update = options.get('force', False)
        csv_path = options.get('csv')
        download_images = options.get('download_images', False)
        
        # Try to read from CSV if provided
        if csv_path and os.path.exists(csv_path):
            art_data = self.parse_csv(csv_path)
            self.stdout.write(f"Read {len(art_data)} art items from CSV file")
        else:
            # Sample art data if no CSV is provided
            self.stdout.write(self.style.WARNING("No valid CSV file provided, using sample data"))
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
                }
            ]
            
        if download_images:
            self.stdout.write("Image download enabled. Will attempt to fetch images from source links.")
            
            # Process each item to download images
            for i, item in enumerate(art_data):
                if item['links']:
                    self.stdout.write(f"Processing image [{i+1}/{len(art_data)}] for '{item['name']}' from {item['links']}")
                    
                    # Get direct image URL
                    direct_url = self.get_direct_image_url(item['links'])
                    
                    if direct_url:
                        self.stdout.write(f"  Found direct image URL: {direct_url}")
                        
                        # Download the image
                        local_url = self.download_image(direct_url, item)
                        if local_url:
                            item['image_url'] = local_url
                            self.stdout.write(f"  Downloaded image to: {local_url}")
                        else:
                            # Use placeholder if download fails
                            item['image_url'] = f"https://placehold.co/600x600/png?text={item['name'].replace(' ', '+')}"
                            self.stdout.write(f"  Failed to download, using placeholder")
                    else:
                        # Use placeholder if no direct URL found
                        item['image_url'] = f"https://placehold.co/600x600/png?text={item['name'].replace(' ', '+')}"
                        self.stdout.write(f"  No direct URL found, using placeholder")
                else:
                    # Use placeholder if no source link
                    item['image_url'] = f"https://placehold.co/600x600/png?text={item['name'].replace(' ', '+')}"
                    self.stdout.write(f"  No source link for '{item['name']}', using placeholder")
                    
                # Add a small delay to avoid rate limiting
                time.sleep(0.5)
        else:
            # If not downloading, use placeholders for all items
            for item in art_data:
                if not item.get('image_url'):
                    item['image_url'] = f"https://placehold.co/600x600/png?text={item['name'].replace(' ', '+')}"
        
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