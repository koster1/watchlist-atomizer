from django.contrib import admin

from .models import Film

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    
    list_display = ('title', 'director', 'year', 'date_added')
    
    list_filter = ('year',)
    
    search_fields = ('title', 'director')
