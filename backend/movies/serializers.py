from rest_framework import serializers

from .models import Film

class FilmSerializer(serializers.ModelSerializer):
    
    """
    Converts the film model into a format used by the API.
    """
    
    # Define which model and fields to use for serialization.
    
    class Meta:
        model = Film
        fields = [
        "id",
        "title",
        "year",
        "release_date",
        "letterboxd_url",
        "date_added",
        "director",
        ]
    