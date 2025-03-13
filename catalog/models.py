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