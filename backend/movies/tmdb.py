
"""
This module requests movie data from The Movie Database (TMDB) API and saves it to the Django database.
"""
import json
import os
import urllib.parse
import urllib.request

from .models import Film, FilmRelease, Director


TMDB_API_BASE_URL = "https://api.themoviedb.org/3"

def get_tmdb_api_key():
    
    # Return the TMDB API key.
    
    api_key = os.getenv("TMDB_API_KEY")
    
    if not api_key:
        raise RuntimeError("TMDB_API_KEY is missing.")
    
    return api_key

def search_movies(query):
    """Search for movies in TMDB. / Hae elokuvia TMDB:stä."""
    
    api_key = get_tmdb_api_key()
    
    params = urllib.parse.urlencode({
        "api_key": api_key,
        "query": query,
    })

    url = f"{TMDB_API_BASE_URL}/search/movie?{params}"
    request = urllib.request.Request(url)

    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))

def find_exact_tmdb_match(title, year):
    
    # Find a movie in TMDB that's matching the exact title and release year
    
    results = search_movies(title)
    possible_matches = []
    
    for movie in results.get("results", []):
        tmdb_title = movie.get("title", "").strip()
        original_title = movie.get("original_title", "").strip()
        release_date = movie.get("release_date", "")
        
        if not release_date:
            continue
        
        movie_year = int(release_date[:4])
        
        title_matches = title.strip().casefold() in {
            tmdb_title.casefold(),
            original_title.casefold()
        }
        
        if title_matches and abs(movie_year - year) <= 1:
            possible_matches.append(movie)
            
    if len(possible_matches) == 1:
        return possible_matches[0]

    return None

def get_theatrical_release_date_by_country(movie_id, country_code):
    """
    Get the theatrical release date for a movie by country code from TMDB.
    """
    api_key = get_tmdb_api_key()
    
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
    
    api_key = get_tmdb_api_key()
    
    params = urllib.parse.urlencode({
        "api_key": api_key,
    })
    
    url = f"{TMDB_API_BASE_URL}/movie/{movie_id}?{params}"
    request = urllib.request.Request(url)
    
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))
    
def get_movie_directors(movie_id):
    
    # Get the directors of a movie from TMDB.
    
    api_key = get_tmdb_api_key()
    
    params = urllib.parse.urlencode({
        "api_key": api_key,
    })
    
    url = f"{TMDB_API_BASE_URL}/movie/{movie_id}/credits?{params}"
    request = urllib.request.Request(url)
    
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
        
    directors = [
        person for person in data.get("crew", [])
        if person.get("job") == "Director"
    ]
    
    return directors

def save_movie_directors(film):
    # Save the film's director(s) to the database
    
    if not film.tmdb_id:
        raise ValueError("Film does not have a TMDB ID.")
    
    directors  = get_movie_directors(film.tmdb_id)
    
    for person in directors:
        director, created = Director.objects.get_or_create(
            tmdb_id=person["id"],
            defaults={"name": person["name"]},
        )
        
        film.director.add(director)
    
    return len(directors)  # Return the number of directors added to the film   

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
    save_movie_directors(film)  # Save the directors of the film
    return film, created

def update_film_from_tmdb(film, movie_id):
    # Update an existing film with TMDB data
    
    movie_data = get_movie_details(movie_id)
    
    release_date = movie_data.get("release_date") or None
    
    film.tmdb_id = movie_id
    film.release_date = release_date

    film.save()
    
    save_movie_directors(film)
    
    return film

def save_movie_releases_by_country(film):
    
    # Save the theatrical release dates for all available countries from TMDB.
    
    if not film.tmdb_id:
        raise ValueError("Film does not have a TMDB ID.")

    api_key = get_tmdb_api_key()
    
    params = urllib.parse.urlencode({
        "api_key": api_key,
    })
    
    url = f"{TMDB_API_BASE_URL}/movie/{film.tmdb_id}/release_dates?{params}"
    request = urllib.request.Request(url)
    
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    
    saved_count = 0
    
    for country in data.get("results",[]):
        country_code = country.get("iso_3166_1")
        
        if not country_code:
            continue
        
        for release in country.get("release_dates", []):
            
            # release type 3 means theatrical release, which is what we want to save.
            if release.get("type") != 3:
                continue   
            
            release_date_value = release.get("release_date", "")
            
            if not release_date_value:
                continue
            
            release_date = release_date_value[:10]  # Extract the date part (YYYY-MM-DD)
            
            release, created = FilmRelease.objects.get_or_create(
                film=film,
                country_code=country_code,
                release_date=release_date,
                release_type=3
            )
            
            # Increment the counter only if a new record was created.
            if created:
                saved_count += 1
    return saved_count