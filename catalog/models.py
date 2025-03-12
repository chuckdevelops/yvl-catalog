from django.db import models

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