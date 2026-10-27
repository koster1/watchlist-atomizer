from django.db import models

class Film(models.Model):
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    
    release_date = models.DateField(null=True, blank=True)
    
    letterboxd_url = models.URLField(unique=True, null=True, blank=True)
    date_added = models.DateField(null=True, blank=True)
    director = models.CharField(max_length=255, blank=True)
    

    def __str__(self):
        return self.title