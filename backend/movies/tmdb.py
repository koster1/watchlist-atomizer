
import json
import os
import urllib.parse
import urllib.request

from .models import Film


TMDB_API_BASE_URL = "https://api.themoviedb.org/3"


def search_movies(query):
    """Search for movies in TMDB. / Hae elokuvia TMDB:stä."""

    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        raise RuntimeError("TMDB_API_KEY is missing.")

    params = urllib.parse.urlencode({
        "api_key": api_key,
        "query": query,
    })

    url = f"{TMDB_API_BASE_URL}/search/movie?{params}"
    request = urllib.request.Request(url)

    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))

def get_theatrical_release_date_by_country(movie_id, country_code):
    """
    Get the theatrical release date for a movie by country code from TMDB.
    """
    api_key = os.getenv("TMDB_API_KEY")
    
    if not api_key:
        raise RuntimeError("TMDB_API_KEY is missing.")
    
    params = urllib.parse.urlencode({
        "api_key": api_key,
    })
    
    url = f"{TMDB_API_BASE_URL}/movie/{movie_id}/release_dates?{params}"
    request = urllib.request.Request(url)
    
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
        
    for country in data["results"]:
        if country["iso_3166_1"] == country_code.upper():
            for release in country["release_dates"]:
                if release["type"] == 3:  # Theatrical release
                    return release["release_date"][:10]  # Return only the date part (YYYY-MM-DD)
    return None  # Return None if no theatrical release date is found for the specified country

def get_movie_details(movie_id):
    
    api_key = os.getenv("TMDB_API_KEY")
    
    if not api_key:
        raise RuntimeError("TMDB_API_KEY is missing.")
    
    params = urllib.parse.urlencode({
        "api_key": api_key,
    })
    
    url = f"{TMDB_API_BASE_URL}/movie/{movie_id}?{params}"
    request = urllib.request.Request(url)
    
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))
    
def save_movie_from_tmdb(movie_id):
    #Save a movie from TMDB to the database.
    
    movie_data = get_movie_details(movie_id)
    
    title = movie_data.get("title")
    release_date = movie_data.get("release_date") or None
    
    if not title:
        raise ValueError("TMDB response does not contain the film title.")
    
    year = None
    if release_date:
        year = int(release_date[:4])
        
    if year is None:
        raise ValueError("TMDB response does not contain a valid release date.")
    
    # Save or update the film using its TMDB ID.
    
    film, created = Film.objects.update_or_create(
        
        tmdb_id=movie_id,
        defaults={
            
            "title": title,
            "year": year,
            "release_date": release_date,
        },
    )
    
    return film, created