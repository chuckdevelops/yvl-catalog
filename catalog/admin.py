from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import CartiCatalog, SheetTab, SongMetadata, SongCategory, ArtMedia, FitPic, SocialMedia, HomepageSettings

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
    list_display = ('name', 'era', 'media_type', 'was_used', 'has_image', 'preview_image')
    list_filter = ('era', 'media_type', 'was_used')
    search_fields = ('name', 'notes')
    ordering = ('era', 'name')
    list_editable = ('was_used', 'media_type')
    list_per_page = 25
    actions = ['mark_as_used', 'mark_as_unused', 'set_type_album_cover', 'set_type_single_art']
    
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
    
    def has_image(self, obj):
        return bool(obj.image_url)
    has_image.boolean = True
    has_image.short_description = 'Has Image'
    
    def preview_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image_url)
        return "No image"
    preview_image.short_description = 'Preview'
    
    def mark_as_used(self, request, queryset):
        updated = queryset.update(was_used=True)
        self.message_user(request, f'{updated} art items marked as used.')
    mark_as_used.short_description = "Mark selected art as used"
    
    def mark_as_unused(self, request, queryset):
        updated = queryset.update(was_used=False)
        self.message_user(request, f'{updated} art items marked as unused.')
    mark_as_unused.short_description = "Mark selected art as unused"
    
    def set_type_album_cover(self, request, queryset):
        updated = queryset.update(media_type='Album Cover')
        self.message_user(request, f'{updated} art items set to Album Cover type.')
    set_type_album_cover.short_description = "Set selected art to Album Cover type"
    
    def set_type_single_art(self, request, queryset):
        updated = queryset.update(media_type='Single Art')
        self.message_user(request, f'{updated} art items set to Single Art type.')
    set_type_single_art.short_description = "Set selected art to Single Art type"
    
@admin.register(FitPic)
class FitPicAdmin(admin.ModelAdmin):
    list_display = ('caption', 'era', 'photographer', 'release_date', 'pic_type', 'quality', 'has_image', 'preview_image')
    list_filter = ('era', 'pic_type', 'quality')
    search_fields = ('caption', 'notes', 'photographer')
    ordering = ('era', 'release_date')
    list_editable = ('quality', 'pic_type')
    list_per_page = 25
    actions = ['mark_high_quality', 'mark_medium_quality', 'mark_low_quality', 'set_type_to_post']
    
    # Add fieldsets to make editing more organized
    fieldsets = (
        (None, {
            'fields': ('caption', 'era', 'release_date')
        }),
        ('Image Details', {
            'fields': ('photographer', 'pic_type', 'portion', 'quality')
        }),
        ('Media', {
            'fields': ('image_url', 'source_links')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        })
    )
    
    def has_image(self, obj):
        return bool(obj.image_url)
    has_image.boolean = True
    has_image.short_description = 'Has Image'
    
    def preview_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image_url)
        return "No image"
    preview_image.short_description = 'Preview'
    
    def mark_high_quality(self, request, queryset):
        updated = queryset.update(quality='High Quality')
        self.message_user(request, f'{updated} fit pics marked as High Quality.')
    mark_high_quality.short_description = "Mark selected fit pics as High Quality"
    
    def mark_medium_quality(self, request, queryset):
        updated = queryset.update(quality='Medium Quality')
        self.message_user(request, f'{updated} fit pics marked as Medium Quality.')
    mark_medium_quality.short_description = "Mark selected fit pics as Medium Quality"
    
    def mark_low_quality(self, request, queryset):
        updated = queryset.update(quality='Low Quality')
        self.message_user(request, f'{updated} fit pics marked as Low Quality.')
    mark_low_quality.short_description = "Mark selected fit pics as Low Quality"
    
    def set_type_to_post(self, request, queryset):
        updated = queryset.update(pic_type='Post')
        self.message_user(request, f'{updated} fit pics type set to Post.')
    set_type_to_post.short_description = "Set selected fit pics type to Post"
    
@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ('username', 'platform', 'era', 'last_post', 'still_used', 'has_valid_link', 'visit_link')
    list_filter = ('era', 'platform', 'still_used')
    search_fields = ('username', 'notes', 'platform')
    ordering = ('era', 'platform', 'username')
    list_editable = ('still_used',)
    list_per_page = 25
    actions = ['mark_as_active', 'mark_as_inactive', 'set_still_used']
    
    # Add fieldsets to make editing more organized
    fieldsets = (
        (None, {
            'fields': ('username', 'platform', 'era')
        }),
        ('Status', {
            'fields': ('last_post', 'still_used')
        }),
        ('Link Information', {
            'fields': ('link', 'notes')
        })
    )
    
    def has_valid_link(self, obj):
        return bool(obj.link) and obj.link not in ['N/A', 'Deleted']
    has_valid_link.boolean = True
    has_valid_link.short_description = 'Valid Link'
    
    def visit_link(self, obj):
        if obj.link and obj.link not in ['N/A', 'Deleted']:
            return format_html('<a href="{}" target="_blank">Visit</a>', obj.link)
        return "N/A"
    visit_link.short_description = 'Visit'
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(still_used=True, last_post='Still Used')
        self.message_user(request, f'{updated} social media accounts marked as active.')
    mark_as_active.short_description = "Mark selected accounts as active"
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(still_used=False)
        self.message_user(request, f'{updated} social media accounts marked as inactive.')
    mark_as_inactive.short_description = "Mark selected accounts as inactive"
    
    def set_still_used(self, request, queryset):
        updated = queryset.filter(last_post='Still Used').update(still_used=True)
        self.message_user(request, f'Set {updated} accounts with "Still Used" last post to active status.')
    set_still_used.short_description = "Fix: Set accounts with 'Still Used' last post to active"
    
@admin.register(HomepageSettings)
class HomepageSettingsAdmin(admin.ModelAdmin):
    """Admin for homepage settings"""
    filter_horizontal = ('homepage_songs',)
    list_display = ('__str__', 'enable_custom_homepage', 'song_count', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('enable_custom_homepage',),
            'description': 'Enable custom homepage to show selected songs instead of Recent tab songs'
        }),
        ('Song Selection', {
            'fields': ('homepage_songs',),
            'description': 'Select up to 10 songs to display on the homepage. Songs will be shown in the order added.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def song_count(self, obj):
        count = obj.homepage_songs.count()
        return count
    song_count.short_description = 'Number of Songs'
    
    def has_add_permission(self, request):
        # Only allow adding if no instance exists
        return not HomepageSettings.objects.exists()
        
    def has_delete_permission(self, request, obj=None):
        # Don't allow deleting the settings
        return False