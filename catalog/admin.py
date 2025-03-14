from django.contrib import admin
from .models import CartiCatalog, SheetTab, SongMetadata, SongCategory, ArtMedia

class SongMetadataInline(admin.StackedInline):
    model = SongMetadata
    can_delete = False
    verbose_name_plural = 'Metadata'

@admin.register(SheetTab)
class SheetTabAdmin(admin.ModelAdmin):
    list_display = ('name', 'sheet_id')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(SongMetadata)
class SongMetadataAdmin(admin.ModelAdmin):
    list_display = ('song', 'sheet_tab', 'subsection')
    list_filter = ('sheet_tab', 'subsection')
    search_fields = ('song__name', 'song__era')
    ordering = ('song__era', 'song__name')

@admin.register(CartiCatalog)
class CartiCatalogAdmin(admin.ModelAdmin):
    list_display = ('name', 'era', 'type', 'quality', 'leak_date', 'get_sheet_tab', 'get_subsection')
    list_filter = ('era', 'quality', 'type', 'metadata__sheet_tab', 'metadata__subsection')
    search_fields = ('name', 'notes')
    ordering = ('era', 'name')
    inlines = [SongMetadataInline]
    
    def get_sheet_tab(self, obj):
        return obj.sheet_tab
    get_sheet_tab.short_description = 'Sheet Tab'
    
    def get_subsection(self, obj):
        return obj.subsection
    get_subsection.short_description = 'Subsection'
    
@admin.register(ArtMedia)
class ArtMediaAdmin(admin.ModelAdmin):
    list_display = ('name', 'era', 'media_type', 'was_used')
    list_filter = ('era', 'media_type', 'was_used')
    search_fields = ('name', 'notes')
    ordering = ('era', 'name')
    
    # Add fieldsets to make editing more organized
    fieldsets = (
        (None, {
            'fields': ('name', 'era', 'media_type')
        }),
        ('Image Information', {
            'fields': ('image_url', 'was_used')
        }),
        ('Additional Information', {
            'fields': ('notes', 'links')
        })
    )