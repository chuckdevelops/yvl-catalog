from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from catalog.models import ArtMedia
import time
import re
from urllib.parse import urlparse
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Scrape art data directly from a Google Sheets public page'

    def add_arguments(self, parser):
        parser.add_argument(
            'url',
            type=str,
            help='The URL of the published Google Sheet',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all entries even if they already exist',
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

    def scrape_sheets_data(self, url):
        """Scrape art data from a published Google Sheet"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch the page: {response.status_code}"))
                return []
                
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the table - this is specific to Google Sheets published format
            # We're looking for a table with the appropriate columns
            tables = soup.find_all('table')
            
            if not tables:
                self.stdout.write(self.style.ERROR("No tables found on the page"))
                return []
                
            # We assume the main table is the one with the data
            # Look for a table with headers matching the expected structure
            art_data = []
            for table in tables:
                headers = [th.get_text().strip() for th in table.find_all('th')]
                
                # Check if this table has the expected headers or similar
                expected_headers = ['Era', 'Name', 'Notes', 'Type', 'Used']
                found_headers = [h for h in expected_headers if any(e.lower() in h.lower() for h in headers)]
                
                if len(found_headers) >= 3:  # At least 3 matching headers
                    # Find the index positions of each required column
                    header_map = {}
                    for i, header in enumerate(headers):
                        header_lower = header.lower()
                        if 'era' in header_lower:
                            header_map['era'] = i
                        elif 'name' in header_lower:
                            header_map['name'] = i
                        elif 'notes' in header_lower:
                            header_map['notes'] = i
                        elif 'type' in header_lower:
                            header_map['type'] = i
                        elif 'used' in header_lower:
                            header_map['used'] = i
                        elif 'link' in header_lower:
                            header_map['links'] = i
                    
                    # If we have at least name and era, we can process this table
                    if 'name' in header_map and 'era' in header_map:
                        # Process rows
                        rows = table.find_all('tr')
                        
                        # Skip header row
                        for row in rows[1:]:
                            cells = row.find_all('td')
                            
                            # Skip rows with insufficient cells
                            if len(cells) <= max(header_map.values()):
                                continue
                                
                            # Extract data based on header positions
                            item = {
                                'era': cells[header_map.get('era', 0)].get_text().strip(),
                                'name': cells[header_map.get('name', 1)].get_text().strip(),
                                'notes': cells[header_map.get('notes', 2)].get_text().strip() if 'notes' in header_map else '',
                                'image_url': '',  # Will be populated later
                                'media_type': cells[header_map.get('type', 3)].get_text().strip() if 'type' in header_map else '',
                                'was_used': 'yes' in cells[header_map.get('used', 4)].get_text().strip().lower() if 'used' in header_map else False,
                                'links': ''  # Will extract links from cells below
                            }
                            
                            # Look for links in this row
                            if 'links' in header_map:
                                # Try to extract an href from the links cell
                                link_cell = cells[header_map['links']]
                                link_a = link_cell.find('a')
                                if link_a and link_a.has_attr('href'):
                                    item['links'] = link_a['href']
                            else:
                                # If no specific links column, look for links in any cell
                                for cell in cells:
                                    link_a = cell.find('a')
                                    if link_a and link_a.has_attr('href'):
                                        link = link_a['href']
                                        # Only use image-related links
                                        if any(domain in link for domain in ['imgur.com', 'tumblr.com', '.jpg', '.png', '.gif']):
                                            item['links'] = link
                                            break
                            
                            # Skip rows without a name or with very short names
                            if len(item['name']) < 2:
                                continue
                                
                            art_data.append(item)
                        
                        # If we found data, stop processing tables
                        if art_data:
                            break
            
            return art_data
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error scraping Google Sheets: {e}"))
            return []

    def handle(self, *args, **options):
        url = options['url']
        force_update = options.get('force', False)
        download_images = options.get('download_images', False)
        
        # Validate URL - basic check for Google Sheets URL
        if 'docs.google.com' not in url and 'sheets.google.com' not in url:
            self.stdout.write(self.style.WARNING("URL doesn't appear to be a Google Sheets URL. The scraper might not work correctly."))
        
        # Scrape the data
        self.stdout.write(f"Scraping art data from: {url}")
        art_data = self.scrape_sheets_data(url)
        
        if not art_data:
            self.stdout.write(self.style.ERROR("No art data could be extracted from the provided URL"))
            return
            
        self.stdout.write(f"Scraped {len(art_data)} art items from Google Sheets")
        
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
        
        self.stdout.write(f"Processing {len(art_data)} art media items for database import")
        
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