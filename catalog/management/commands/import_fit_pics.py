import csv
import re
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from catalog.models import FitPic

class Command(BaseCommand):
    help = 'Import fit pics data from provided information and scrape images from Instagram'

    def handle(self, *args, **options):
        # Data from the provided Google Sheets-like table
        fit_pic_data = [
            # Die Lit Era
            {
                'era': 'Die Lit',
                'caption': 'i wanted to let u know as soon as i could but i was shy ! its meh birthday !!! . * ! _ i should drop some :/ ! +:)',
                'notes': '',
                'photographer': '',
                'release_date': 'Sep 13, 2018',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS33MTwLbEl/',
            },
            # Whole Lotta Red [V1] Era
            {
                'era': 'WLR V1',
                'caption': '⭐ phone died ! ^',
                'notes': 'Get Dripped video shoot (features some of cartis best fit pics)',
                'photographer': 'chadwicktyler',
                'release_date': 'Nov 26, 2018',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS33RaBrLSP/',
            },
            # Whole Lotta Red [V2] Era - Zesty Blonde Era
            {
                'era': 'WLR V2',
                'caption': 'him <3 red incoming .',
                'notes': '',
                'photographer': '',
                'release_date': 'Oct 15, 2019',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS34xTWrSxm/',
            },
            {
                'era': 'WLR V2',
                'caption': '<48hours! locked in.',
                'notes': '',
                'photographer': '',
                'release_date': 'Oct 16, 2019',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS35x4Orhpa/',
            },
            {
                'era': 'WLR V2',
                'caption': 'i jus made 10 vibes<3',
                'notes': '',
                'photographer': 'gunnerstahl.us',
                'release_date': 'Oct 18, 2019',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS36vnhrEKA/\nhttps://www.instagram.com/p/B3-vYxaHKIm/',
            },
            {
                'era': 'WLR V2',
                'caption': '',
                'notes': '',
                'photographer': '',
                'release_date': 'Oct 30, 2019',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS37PsyrZll/',
            },
            {
                'era': 'WLR V2',
                'caption': 'opium. < 3 /',
                'notes': '',
                'photographer': '',
                'release_date': 'Nov 2, 2019',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS37k7MLkAO/',
            },
            {
                'era': 'WLR V2',
                'caption': '.jus shot ah movie .',
                'notes': 'Possible MV',
                'photographer': '',
                'release_date': 'Nov 5, 2019',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS37wSmrcXV/',
            },
            {
                'era': 'WLR V2',
                'caption': 'red <3',
                'notes': '',
                'photographer': '',
                'release_date': 'Nov 7, 2019',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS37_FML4uK/',
            },
            {
                'era': 'WLR V2',
                'caption': 'new phone .',
                'notes': '',
                'photographer': '',
                'release_date': 'Dec 1, 2019',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS38Iw2LK-S/',
            },
            {
                'era': 'WLR V2',
                'caption': 'vampire weekend . red.com .',
                'notes': '',
                'photographer': '',
                'release_date': 'Jan 2, 2020',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS38O4fLlg-/',
            },
            {
                'era': 'WLR V2',
                'caption': 'u n meh .',
                'notes': '',
                'photographer': '',
                'release_date': 'Mar 19, 2020',
                'pic_type': 'Post',
                'portion': 'Full',
                'quality': 'High Quality',
                'source_links': 'https://www.instagram.com/p/CS38V-3L',
            },
        ]
        
        # Clear existing data if needed
        if FitPic.objects.exists():
            self.stdout.write(self.style.WARNING('Clearing existing fit pics data...'))
            FitPic.objects.all().delete()
        
        # Function to try to scrape image URL from Instagram links
        def get_instagram_image(url):
            try:
                # Note: Instagram may block scraping, in a real implementation
                # you might need to use a more sophisticated approach or Instagram API
                # This is a simplified placeholder that may not work due to Instagram's anti-scraping measures
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Try to find image tags
                    images = soup.find_all('img')
                    for img in images:
                        if 'src' in img.attrs and ('instagram' in img['src'] or 'cdninstagram' in img['src']):
                            if 'profile_pic' not in img['src'] and 'favicon' not in img['src']:
                                return img['src']
                return None
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error scraping Instagram image from {url}: {str(e)}'))
                return None
        
        # Import the data
        fit_pics_created = 0
        for data in fit_pic_data:
            # Try to fetch image from Instagram links
            image_url = None
            if data['source_links']:
                # Split multiple links and try each one
                links = data['source_links'].strip().split('\n')
                for link in links:
                    image_url = get_instagram_image(link.strip())
                    if image_url:
                        break
            
            fit_pic = FitPic.objects.create(
                era=data['era'],
                caption=data['caption'],
                notes=data['notes'],
                photographer=data['photographer'],
                release_date=data['release_date'],
                pic_type=data['pic_type'],
                portion=data['portion'],
                quality=data['quality'],
                image_url=image_url,  # This may be None if scraping failed
                source_links=data['source_links'],
            )
            fit_pics_created += 1
            
            # If scraping failed, let the user know
            if not image_url:
                self.stdout.write(self.style.WARNING(f'Could not scrape image for fit pic ID {fit_pic.id} ({data["caption"][:30]}...)'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {fit_pics_created} fit pics'))
        
        # Additional information about missing images
        missing_images = FitPic.objects.filter(image_url__isnull=True).count()
        if missing_images > 0:
            self.stdout.write(self.style.WARNING(f'{missing_images} fit pics are missing images. You may need to manually add them.'))
            self.stdout.write(self.style.WARNING('Instagram blocks scraping in most cases, so manual image collection may be required.'))