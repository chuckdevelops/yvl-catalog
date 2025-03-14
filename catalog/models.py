from django.db import models

class SheetTab(models.Model):
    """Model to represent the different tabs in the Google Spreadsheet"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)  # e.g., "Unreleased", "Released", "Grails"
    sheet_id = models.CharField(max_length=100, null=True, blank=True)  # The sheet ID from Google Sheets
    
    class Meta:
        managed = True
        db_table = 'sheet_tab'
        verbose_name = 'Sheet Tab'
        verbose_name_plural = 'Sheet Tabs'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class SongMetadata(models.Model):
    """Model to store additional metadata for songs that doesn't exist in the original database"""
    id = models.AutoField(primary_key=True)
    song = models.OneToOneField('CartiCatalog', on_delete=models.CASCADE, related_name='metadata')
    # Primary sheet tab (Released or Unreleased)
    sheet_tab = models.ForeignKey(SheetTab, on_delete=models.SET_NULL, null=True, blank=True, related_name='songs')
    subsection = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        managed = True
        db_table = 'song_metadata'
        verbose_name = 'Song Metadata'
        verbose_name_plural = 'Song Metadata'
    
    def __str__(self):
        return f"Metadata for {self.song}"

class SongCategory(models.Model):
    """Model to store additional categories (tabs) that a song belongs to besides its primary tab"""
    id = models.AutoField(primary_key=True)
    song = models.ForeignKey('CartiCatalog', on_delete=models.CASCADE, related_name='categories')
    sheet_tab = models.ForeignKey(SheetTab, on_delete=models.CASCADE, related_name='categorized_songs')
    
    class Meta:
        managed = True
        db_table = 'song_category'
        verbose_name = 'Song Category'
        verbose_name_plural = 'Song Categories'
        # Make sure we don't duplicate song-tab pairs
        unique_together = ('song', 'sheet_tab')
    
    def __str__(self):
        return f"{self.song} - {self.sheet_tab}"

class CartiCatalog(models.Model):
    """Model mapped to existing carti_catalog table"""
    id = models.AutoField(primary_key=True)
    era = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    track_length = models.CharField(max_length=100, null=True, blank=True)
    leak_date = models.CharField(max_length=100, null=True, blank=True)
    file_date = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    available_length = models.CharField(max_length=100, null=True, blank=True)
    quality = models.CharField(max_length=100, null=True, blank=True)
    links = models.TextField(null=True, blank=True)
    primary_link = models.TextField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True, null=True)
    # FIXED: Removed extra_1, extra_2, etc. fields that don't exist in the database
    
    # Album track mappings as static class attributes
    selftitled_tracks = {
        'Location': 1,
        'Magnolia': 2,
        'Lookin': 3,
        'wokeuplikethis*': 4,
        'Let It Go': 5,
        'Half & Half': 6,
        'New Choppa': 7,
        'Other Shit': 8,
        'NO. 9': 9,
        'dothatshit!': 10,
        'Lame Niggaz': 11,
        'Yah Mean': 12,
        'Flex': 13,
        'Kelly K': 14,
        'Had 2': 15,
    }
    
    die_lit_tracks = {
        'Long Time - Intro': 1,
        'R.I.P.': 2,
        'Lean 4 Real (feat. Skepta)': 3,
        'Old Money': 4,
        'Love Hurts (feat. Travis Scott)': 5,
        'Shoota (feat. Lil Uzi Vert)': 6,
        'Right Now (feat. Pi\'erre Bourne)': 7,
        'Poke It Out (feat. Nicki Minaj)': 8,
        'Home (KOD)': 9,
        'Fell In Luv (feat. Bryson Tiller)': 10,
        'Foreign': 11,
        'Pull Up': 12,
        'Mileage (feat. Chief Keef)': 13,
        'FlatBed Freestyle': 14,
        'No Time (feat. Gunna)': 15,
        'Middle Of The Summer (feat. Red Coldhearted)': 16,
        'Choppa Won\'t Miss (feat. Young Thug)': 17,
        'R.I.P. Fredo - Notice Me (feat. Young Nudy)': 18,
        'Top (feat. Pi\'erre Bourne)': 19,
    }
    
    wlr_tracks = {
        'Rockstar Made': 1,
        'Go2DaMoon': 2,
        'Stop Breathing': 3,
        'Beno!': 4,
        'JumpOutTheHouse': 5,
        'M3tamorphosis': 6,
        'Slay3r': 7,
        'No Sl33p': 8,
        'New Tank': 9,
        'Teen X': 10,
        'Meh': 11,
        'Vamp Anthem': 12,
        'New N3on': 13,
        'Control': 14,
        'Punk Monk': 15,
        'On That Time': 16,
        'King Vamp': 17,
        'Place': 18,
        'Sky': 19,
        'Over': 20,
        'ILoveUIHateU': 21,
        'Die4Guy': 22,
        'Not PLaying': 23,
        'F33l Lik3 Dyin': 24,
    }
    
    young_misfit_tracks = {
        '36 Villanz': 1,
        'ZOMBIE$': 2,
        '$kit 1': 3,
        'Blue Crystal$': 4,
        '$teeze': 5,
        'Club Pink': 6,
        'Van Go': 7,
        '$kit 2': 8,
        'Paper Cha$in': 9,
    }

    class Meta:
        managed = False  # Don't modify the existing table
        db_table = 'carti_catalog'
        verbose_name = 'Song'
        verbose_name_plural = 'Songs'
        unique_together = ('era', 'name')
        ordering = ['era', 'name']

    def __str__(self):
        return f"{self.name} ({self.era or 'Unknown Era'})"
        
    @property
    def sheet_tab(self):
        """Get the primary sheet tab from the metadata (Released or Unreleased)"""
        try:
            return self.metadata.sheet_tab
        except (SongMetadata.DoesNotExist, AttributeError):
            return None
            
    @property
    def subsection(self):
        """Get the subsection from the metadata"""
        try:
            return self.metadata.subsection
        except (SongMetadata.DoesNotExist, AttributeError):
            return None
            
    @property
    def all_tabs(self):
        """Get all sheet tabs for this song (primary + secondary categories)"""
        tabs = []
        # Get primary tab first
        primary_tab = self.sheet_tab
        if primary_tab:
            tabs.append(primary_tab)
        
        # Get secondary tabs
        try:
            for category in self.categories.all():
                if category.sheet_tab != primary_tab:  # Avoid duplicates
                    tabs.append(category.sheet_tab)
        except Exception:
            pass
            
        return tabs
        
    @property
    def is_released(self):
        """Check if song is in the Released tab"""
        tab = self.sheet_tab
        return tab and tab.name == "Released"
        
    @property
    def is_unreleased(self):
        """Check if song is in the Unreleased tab"""
        tab = self.sheet_tab
        return tab and tab.name == "Unreleased"
        
    @property
    def album_track_number(self):
        """Extract the track number from notes if available"""
        # Check if we have a Young Mi$fit track number set from album_name property
        if hasattr(self, '_young_misfit_track_num'):
            return self._young_misfit_track_num
            
        if not self.notes:
            return None
            
        import re
        # Look for patterns like "Track 5", "track 5", "track #5", etc.
        track_patterns = [
            r'[Tt]rack\s+#?(\d+)',  # Track 5 or track #5
            r'[Tt]rack\s+(\d+)\s+(?:on|of|from)',  # Track 5 on/of/from
            r'[Tt]rack\s+(?:number\s+)?(\d+)',  # Track number 5
            r'\b(\d+)(?:st|nd|rd|th)\s+track',  # 5th track
            r'track\s+(?:no\.|number|#)\s*(\d+)',  # track no. 5
            r'appears\s+as\s+(?:track|song)\s+(\d+)',  # appears as track 5
        ]
        
        for pattern in track_patterns:
            match = re.search(pattern, self.notes, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        
        # Check for title prefixed with track number (e.g., "01 - Song Name")
        if self.name and re.match(r'^\d+\s*[-:.]', self.name):
            try:
                track_num = int(re.match(r'^(\d+)', self.name).group(1))
                return track_num
            except (ValueError, AttributeError):
                pass
                
        return None
        
    @property
    def album_name(self):
        """Extract the album name from notes if available"""
        if not self.notes:
            return None
            
        import re
        # Common album names in Playboi Carti's discography
        official_albums = {
            'Die Lit': 'Die Lit (Official)',
            'Whole Lotta Red': 'Whole Lotta Red (Official)',
            'Playboi Carti': 'Playboi Carti (Official)',  # Self-titled
            'Young Mi$fit': 'Young Mi$fit (Official)',
        }
        
        import re
        
        # Clean song name by removing version indicators like [V2], [V3], etc.
        clean_name = re.sub(r'\s*\[V\d+\].*', '', self.name)
        
        # Check if this is a self-titled album track by name
        for track_name, track_num in CartiCatalog.selftitled_tracks.items():
            # Use more flexible matching because track names might be slightly different
            track_words = track_name.lower().split()
            song_words = clean_name.lower().split()
            
            # Check if main words match (at least 70% overlap)
            matches = 0
            for word in track_words:
                if any(word in sw for sw in song_words):
                    matches += 1
            
            # If most words match or exact track name is in song name
            if (matches / len(track_words) >= 0.7) or track_name.lower() in clean_name.lower():
                # Set the track number for this song (will be used by album_track_number)
                self._young_misfit_track_num = track_num  # Reusing this attribute for all track numbers
                return "Playboi Carti (Official)"
                
        # Check if this is a Die Lit track by name
        for track_name, track_num in CartiCatalog.die_lit_tracks.items():
            # Use more flexible matching because track names might be slightly different
            track_words = track_name.lower().split()
            song_words = clean_name.lower().split()
            
            # Check if main words match (at least 70% overlap)
            matches = 0
            for word in track_words:
                if any(word in sw for sw in song_words):
                    matches += 1
            
            # If most words match or exact track name is in song name
            if (len(track_words) > 0 and matches / len(track_words) >= 0.7) or track_name.lower() in clean_name.lower():
                # Set the track number for this song (will be used by album_track_number)
                self._young_misfit_track_num = track_num  # Reusing this attribute for all track numbers
                return "Die Lit (Official)"
        
        # Check if this is a Whole Lotta Red track by name
        for track_name, track_num in CartiCatalog.wlr_tracks.items():
            # Use more flexible matching because track names might be slightly different
            track_words = track_name.lower().split()
            song_words = clean_name.lower().split()
            
            # Check if main words match (at least 70% overlap)
            matches = 0
            for word in track_words:
                if any(word in sw for sw in song_words):
                    matches += 1
            
            # If most words match or exact track name is in song name
            if (len(track_words) > 0 and matches / len(track_words) >= 0.7) or track_name.lower() in clean_name.lower():
                # Set the track number for this song (will be used by album_track_number)
                self._young_misfit_track_num = track_num  # Reusing this attribute for all track numbers
                return "Whole Lotta Red (Official)"
                
        # Check if this is a Young Mi$fit track by name
        for track_name, track_num in CartiCatalog.young_misfit_tracks.items():
            # Use more flexible matching because track names might be slightly different
            track_words = track_name.lower().split()
            song_words = clean_name.lower().split()
            
            # Check if main words match (at least 70% overlap)
            matches = 0
            for word in track_words:
                if any(word in sw for sw in song_words):
                    matches += 1
            
            # If most words match or exact track name is in song name
            if (len(track_words) > 0 and matches / len(track_words) >= 0.7) or track_name.lower() in clean_name.lower():
                # Set the track number for this song (will be used by album_track_number)
                self._young_misfit_track_num = track_num
                return "Young Mi$fit (Official)"
        
        # Patterns to detect official releases vs leaks
        official_markers = [
            'official release',
            'official album',
            'studio album',
            'release version',
            'released by carti',
            'commercially released',
        ]
        
        # Try to find an exact album name match first (case insensitive)
        for album, formatted_name in official_albums.items():
            if re.search(rf'\b{re.escape(album.lower())}\b', self.notes.lower()):
                if any(marker in self.notes.lower() for marker in official_markers):
                    return formatted_name
                
                # Check if this is a released song
                if self.is_released:
                    return formatted_name
                    
        # Additional album detection for tracks on official albums
        track_album_patterns = None
        try:
            # Check if the primary_tab_name property has been set by the view
            if hasattr(self, 'primary_tab_name') and self.primary_tab_name == "Released":
                for album, formatted_name in official_albums.items():
                    # Check for track number patterns with album names
                    track_album_patterns = [
                        rf'[Tt]rack\s+\d+\s+(?:on|of|from)\s+.*?\b{re.escape(album.lower())}\b',
                        rf'\b{re.escape(album.lower())}\b.*?[Tt]rack\s+\d+',
                    ]
                    
                    if track_album_patterns:
                        for pattern in track_album_patterns:
                            if re.search(pattern, self.notes.lower()):
                                return formatted_name
        except AttributeError:
            pass
        
        # Check for specific song metadata that indicates album membership
        if (self.name and 
            hasattr(self, 'primary_tab_name') and self.primary_tab_name == "Released" and 
            self.album_track_number and 
            not self.type == "Feature"):
            
            # Match album era to album name
            era_album_map = {
                "2017-2018": "Die Lit (Official)",
                "2018-2020": "Whole Lotta Red (Official)",
                "Whole Lotta Red": "Whole Lotta Red (Official)",
                "Die Lit": "Die Lit (Official)",
                "Self-Titled": "Playboi Carti (Official)"
            }
            
            if self.era and self.era in era_album_map:
                return era_album_map[self.era]
                
        return None