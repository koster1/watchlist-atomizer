from rest_framework import serializers

from .models import Film, Director

class DirectorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Director
        fields = [
            "id", 
            "name", 
            "tmdb_id"
        ]

class FilmSerializer(serializers.ModelSerializer):
    
    
    # Converts the film model into a format used by the API.
    # Define which model and fields to use for serialization.
    
    director = DirectorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Film
        fields = [
        "id",
        "tmdb_id",
        "title",
        "year",
        "release_date",
        "letterboxd_url",
        "date_added",
        "director",
        ]
    