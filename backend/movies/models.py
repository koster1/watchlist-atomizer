from django.db import models

class Film(models.Model):
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    
    tmdb_id=models.PositiveIntegerField(unique=True,null=True, blank=True)
    
    # The general release date of the film, if available.
    release_date = models.DateField(null=True, blank=True)
    
    letterboxd_url = models.URLField(unique=True, null=True, blank=True)
    date_added = models.DateField(null=True, blank=True)
    
    # Some films may have multiple directors.
    director = models.ManyToManyField('Director', related_name='films', blank=True)

    def __str__(self):
        return self.title
    
class Director(models.Model):
    # The name of the director.
    name = models.CharField(max_length=255, unique=True)
    
    # Unique TMDB person ID for the director, if available.
    tmdb_id = models.PositiveIntegerField(unique=True)
    
    def __str__(self):
        return self.name
    
class FilmRelease(models.Model):
    # Link to the film.
    film = models.ForeignKey(
        Film, on_delete=models.CASCADE,
        related_name='releases')
    # The ISO Code of the Country.
    
    country_code = models.CharField(max_length=2)
    
    # Release date in the specific country.
    release_date = models.DateField()
    
    # TMDB Release type
    release_type = models.PositiveSmallIntegerField()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['film', 'country_code', 'release_date', 'release_type'],
                name='unique_film_country_release'
            )
        ]
        
    def __str__(self):
        return f"{self.film.title} - {self.country_code} - {self.release_date}"
    