
import json
import os
import urllib.parse
import urllib.request


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