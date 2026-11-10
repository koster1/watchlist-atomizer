from django.contrib import admin

from .models import Film, Director

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    
    list_display = ('title', 'display_directors', 'year', 'date_added')
    
    list_filter = ('year',)
    
    search_fields = ('title', 'director__name')
    
    # Display all the directors of a film.
    
    
    @admin.display(description='Director')
    def display_directors(self, obj):
        return ', '.join(
            director.name for director in obj.director.all()
        )
@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'tmdb_id')
    search_fields = ('name',)