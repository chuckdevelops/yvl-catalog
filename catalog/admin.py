from django.contrib import admin
from .models import CartiCatalog

@admin.register(CartiCatalog)
class CartiCatalogAdmin(admin.ModelAdmin):
    list_display = ('name', 'era', 'type', 'quality', 'leak_date')
    list_filter = ('era', 'quality', 'type')
    search_fields = ('name', 'notes')
    ordering = ('era', 'name')