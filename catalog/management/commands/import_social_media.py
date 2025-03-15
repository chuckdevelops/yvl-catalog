import csv
import re
from django.core.management.base import BaseCommand
from catalog.models import SocialMedia

class Command(BaseCommand):
    help = 'Import social media accounts data from provided information'

    def handle(self, *args, **options):
        # Data from the provided Google Sheets-like table
        social_media_data = [
            # $ir Cartier era
            {
                'era': '$ir Cartier',
                'username': '@yungcarti',
                'notes': "Cartis tumblr where he posted and promoted his music in early stages of his carrer. His first post was on Nov 30, 2010",
                'platform': 'TUMBLR',
                'last_post': 'May 16, 2014',
                'still_used': False,
                'link': 'https://yungcarti.tumblr.com',
            },
            {
                'era': '$ir Cartier',
                'username': 'JCartier Da Don',
                'notes': "Carti's Flavors account, a website where you could link all your socials (pretty much Linktree but for the early 2010s) was linked on his Tumblr. The link is now dead since the site shut down in 2017.",
                'platform': 'Flavors',
                'last_post': 'Unknown',
                'still_used': False,
                'link': 'http://flavors.me/jcartier#.Tl1q44NhYoQ.tumblr',
            },
            {
                'era': '$ir Cartier',
                'username': '@jceebitchez',
                'notes': "Deleted old X account used by Carti during 2010, found in his Tumblr.",
                'platform': 'X',
                'last_post': 'Unknown',
                'still_used': False,
                'link': 'Deleted',
            },
            {
                'era': '$ir Cartier',
                'username': '@playboicarti',
                'notes': "",
                'platform': 'X',
                'last_post': 'Dec 25, 2022',
                'still_used': True,
                'link': 'https://twitter.com/playboicarti',
            },
            {
                'era': '$ir Cartier',
                'username': 'j-tfz-cartier',
                'notes': "Cartis old Soundcloud. Used in 2011-2012. Everything deleted exept blue crystal$.",
                'platform': 'Soundcloud',
                'last_post': 'Unknown',
                'still_used': False,
                'link': 'https://soundcloud.com/j-tfz-cartier',
            },
            {
                'era': '$ir Cartier',
                'username': 'jctaughtyou@hotmail.com',
                'notes': "First email that Carti made, provided by Carti himself in his Office magazine interview.",
                'platform': 'Hotmail',
                'last_post': 'Unknown',
                'still_used': False,
                'link': 'N/A',
            },
            {
                'era': '$ir Cartier',
                'username': 'jrdncrtr10@yahoo.com',
                'notes': "Old email. Provided by tame1 on dc.",
                'platform': 'Yahoo',
                'last_post': 'Unknown',
                'still_used': False,
                'link': 'N/A',
            },
            {
                'era': '$ir Cartier',
                'username': '@sircartier2572',
                'notes': "Carti's old Youtube channel",
                'platform': 'Youtube',
                'last_post': 'Jan 14, 2013',
                'still_used': False,
                'link': 'https://www.youtube.com/@sircartier2572',
            },
            {
                'era': '$ir Cartier',
                'username': 'YoungCartierHoe',
                'notes': "Cartis old Soundcloud. Used in 2012 to first week of january 2014",
                'platform': 'Soundcloud',
                'last_post': 'Early Jan 2014',
                'still_used': False,
                'link': 'Deleted',
            },
            {
                'era': '$ir Cartier',
                'username': '678carti',
                'notes': "Cartis old Soundcloud",
                'platform': 'Soundcloud',
                'last_post': '~Jan 2014',
                'still_used': False,
                'link': 'Deleted',
            },
            {
                'era': '$ir Cartier',
                'username': 'sircartier',
                'notes': "Carti's old Newgrounds page.",
                'platform': 'Newgrounds',
                'last_post': '2013',
                'still_used': False,
                'link': 'https://sircartier.newgrounds.com/audio',
            },
            
            # Awful Records era
            {
                'era': 'Awful Records',
                'username': '@playboicarti',
                'notes': "Carti's soundcloud",
                'platform': 'Soundcloud',
                'last_post': 'Still Used',
                'still_used': True,
                'link': 'https://soundcloud.com/playboicarti',
            },
            {
                'era': 'Awful Records',
                'username': '@playboicarti3216',
                'notes': "Carti's old YouTube channel. The only thing he posted there is the Talk (ICYTWAT Remix) music video.",
                'platform': 'Youtube',
                'last_post': '~Aug 2015',
                'still_used': False,
                'link': 'https://www.youtube.com/@playboicarti3216',
            },
            {
                'era': 'Awful Records',
                'username': 'playboiconnor@gmail.com',
                'notes': "Carti's email used for his old Youtube also linked to his manager's email and number.",
                'platform': 'Gmail',
                'last_post': 'Unknown',
                'still_used': False,
                'link': 'N/A',
            },
            
            # Chucky Era
            {
                'era': 'Chucky Era',
                'username': 'Playboi Carti',
                'notes': "Carti's official Apple Music account, may have been made even earlier but there is no certain way of knowing.",
                'platform': 'Apple Music',
                'last_post': 'Still Used',
                'still_used': True,
                'link': 'https://music.apple.com/us/artist/playboi-carti/982372505',
            },
            {
                'era': 'Chucky Era',
                'username': 'Playboi Carti',
                'notes': "Carti's official Deezer account, may have been made even earlier but there is no certain way of knowing.",
                'platform': 'Deezer',
                'last_post': 'Still Used',
                'still_used': True,
                'link': 'https://www.deezer.com/us/artist/10002824',
            },
            {
                'era': 'Chucky Era',
                'username': 'Playboi Carti',
                'notes': "Carti's official TIDAL account, may have been made even earlier but there is no certain way of knowing.",
                'platform': 'TIDAL',
                'last_post': 'Still Used',
                'still_used': True,
                'link': 'https://tidal.com/browse/artist/7663291',
            },
            {
                'era': 'Chucky Era',
                'username': 'Playboi Carti',
                'notes': "Carti´s Pandora account, probably made recently but no way of knowing and also was probably made by the label and not Carti.",
                'platform': 'Pandora',
                'last_post': 'Still Used',
                'still_used': True,
                'link': 'https://www.pandora.com/artist/playboi-carti/AR7twf45jK6m4c2',
            },
            {
                'era': 'Chucky Era',
                'username': 'Playboi Carti',
                'notes': "Carti's official Spotify account, may have been made even earlier but there is no certain way of knowing.",
                'platform': 'Spotify',
                'last_post': 'Still Used',
                'still_used': True,
                'link': 'https://open.spotify.com/artist/699OTQXzgjhIYAHMy9RyPD?si=M-SDq3GFT9OiQlst9PJwbA',
            },
            
            # Ca$h Carti Season
            {
                'era': 'Ca$h Carti Season',
                'username': '@playboicarti',
                'notes': "Carti's official IG",
                'platform': 'Instagram',
                'last_post': 'Still Used',
                'still_used': True,
                'link': 'https://www.instagram.com/playboicarti/',
            },
            {
                'era': 'Ca$h Carti Season',
                'username': 'Playboi Carti',
                'notes': "Carti's official facebook page.",
                'platform': 'Facebook',
                'last_post': 'Nov 16, 2022',
                'still_used': False,
                'link': 'https://www.facebook.com/PlayboiCarti',
            },
            
            # Playboi Carti era
            {
                'era': 'Playboi Carti',
                'username': '@playboicarti',
                'notes': "Carti's official Youtube channel",
                'platform': 'Youtube',
                'last_post': 'Still Used',
                'still_used': True,
                'link': 'https://www.youtube.com/@playboicarti/videos',
            },
            
            # Die Lit era
            {
                'era': 'Die Lit',
                'username': '@therealfullmetal2009',
                'notes': "Carti's old instagram burner made in May 2017.",
                'platform': 'Instagram',
                'last_post': 'Unknown',
                'still_used': False,
                'link': 'https://www.instagram.com/therealfullmetal2009/',
            },
            {
                'era': 'Die Lit',
                'username': '@nineninesixteensixteen',
                'notes': "Another old Instagram burner made by Carti in January 2018.",
                'platform': 'Instagram',
                'last_post': 'Unknown',
                'still_used': False,
                'link': 'https://www.instagram.com/nineninesixteensixteen/',
            },
            
            # Whole Lotta Red [V2] era
            {
                'era': 'Whole Lotta Red [V2]',
                'username': '@opium_opiumoo',
                'notes': "Carti burner made in 2019, supposedly hacked and no longer used.",
                'platform': 'Instagram',
                'last_post': 'Unknown',
                'still_used': False,
                'link': 'https://www.instagram.com/opium_opiumoo/',
            },
            
            # Whole Lotta Red [V3] era
            {
                'era': 'Whole Lotta Red [V3]',
                'username': '@opium_00pium',
                'notes': "Carti's burner IG",
                'platform': 'Instagram',
                'last_post': 'Still Used',
                'still_used': True,
                'link': 'https://www.instagram.com/opium_00pium/',
            },
            {
                'era': 'Whole Lotta Red [V3]',
                'username': '@playboicarti',
                'notes': "Carti's official TikTok account.",
                'platform': 'TikTok',
                'last_post': 'Jan 5, 2021',
                'still_used': False,
                'link': 'https://www.tiktok.com/@playboicarti?lang=en',
            },
            
            # Narcissist era
            {
                'era': 'Narcissist',
                'username': '@playboicarti',
                'notes': "Carti's official Audiomack account, only has WLR and a few recent songs.",
                'platform': 'Audiomack',
                'last_post': 'Sep 27, 2024',
                'still_used': True,
                'link': 'https://audiomack.com/playboicarti',
            },
            
            # I AM MUSIC [V1] era
            {
                'era': 'I AM MUSIC [V1]',
                'username': '@swag37964',
                'notes': "Carti Twitter burner made in October 2023 that he used to defend himself against @Lidestywurld. (DO NOT REMOVE, THIS IS HIM)",
                'platform': 'X',
                'last_post': 'Nov 19, 2023',
                'still_used': False,
                'link': 'https://x.com/swag37964',
            },
            
            # I AM MUSIC [V2] era
            {
                'era': 'I AM MUSIC [V2]',
                'username': '@gohomeriri',
                'notes': "Carti's new finsta that joined in March 2024 and ended up leaking it himself. (good job Jordan) Now private and probably no longer used.",
                'platform': 'Instagram',
                'last_post': 'Never Posted',
                'still_used': False,
                'link': 'https://www.instagram.com/gohomeriri?igsh=NzJvN3d1bnJtbWht',
            },
        ]
        
        # Clear existing data if needed
        if SocialMedia.objects.exists():
            self.stdout.write(self.style.WARNING('Clearing existing social media data...'))
            SocialMedia.objects.all().delete()
        
        # Import the data
        social_media_created = 0
        for data in social_media_data:
            # Convert string representation of still_used to boolean
            still_used = data['still_used']
            if isinstance(still_used, str):
                still_used = (still_used.lower() == 'yes' or still_used.lower() == 'true')
            
            # Handle "unknown" and similar values for last_post
            last_post = data['last_post']
            if last_post.lower() in ['unknown', '???', 'n/a', '']:
                last_post = 'Unknown'
                
            # Create the social media account record
            SocialMedia.objects.create(
                era=data['era'],
                username=data['username'],
                notes=data['notes'],
                platform=data['platform'],
                last_post=last_post,
                still_used=still_used,
                link=data['link'],
            )
            social_media_created += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {social_media_created} social media accounts'))