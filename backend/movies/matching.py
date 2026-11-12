import re
import unicodedata
import math

from rapidfuzz import fuzz

def normalize_title(title):
    # Normalizing the title of the film for comparison.
    
    title = title.casefold()
    
    # Remove accents from characters (e.g., "é" becomes "e").
    
    title = unicodedata.normalize("NFKD", title)
    title = "".join(
        character
        for character in title
        if not unicodedata.combining(character)
    )
    # Replace punctuation with spaces.
    
    title = re.sub(r"[^\w\s]", " ", title)
    
    # Normalize whitespace.
    
    title = " ".join(title.split())
    
    return title

def calculate_title_similarity(title_a, title_b):
    
    # Calculate title similarity as percentage.
    
    normalized_a = normalize_title(title_a)
    normalized_b = normalize_title(title_b)
    
    return fuzz.ratio(normalized_a, normalized_b)

def score_movie_match(
    watchlist_title,
    watchlist_year,
    tmdb_movie
):
    # Score a TMDB movie candidate against a watchlist entry
    
    tmdb_title = tmdb_movie.get("title", "")
    tmdb_original_title = tmdb_movie.get("original_title") or tmdb_title
    release_date = tmdb_movie.get("release_date","")
    
    if not tmdb_title or not release_date:
        return 0
    
    try: 
        tmdb_year = int(release_date[:4])
        
        if not 1800 <= tmdb_year <= 2100:
            return 0
        
    except (ValueError, TypeError):
        return 0
    
    title_score = max(
        calculate_title_similarity(watchlist_title,tmdb_title),
        calculate_title_similarity(watchlist_title, tmdb_original_title)
    )
    
    year_difference = abs(watchlist_year - tmdb_year)
    
    year_score = 100 * math.exp(-0.7 * year_difference)
    
    total_score = (
        title_score * 0.7
        + year_score * 0.3
    )
    
    return round(total_score, 1)

def get_search_title_variations(title):
    
    """
    Generate alternative search titles for a film.
    """
    
    search_titles = [title]
    normalized_title = title.strip()
    
    # Remove leading articles to generate an alternative search title.
    
    for article in ("the ", "a ", "an "):
        if normalized_title.casefold().startswith(article):
            alternative_title = normalized_title[len(article):].strip()
            
            if alternative_title:
                search_titles.append(alternative_title)
                
            break
        
    return search_titles
        
    

def find_best_match(watchlist_title, 
                    watchlist_year, 
                    minimum_score=70,
                    minimum_score_difference=10):
    
    """
    Find and rank TMDB candidates for a watchlist film.
    """

    # Get alternative title variations.
    search_titles = get_search_title_variations(watchlist_title)

    # Search TMDB and remove duplicate candidates
    candidates = find_movie_candidates(search_titles)

    # Calculate a match score for each candidate.
    scored_candidates = []

    for movie in candidates:
        score = score_movie_match(
            watchlist_title,
            watchlist_year,
            movie
        )

        scored_candidates.append({
            "movie": movie,
            "score": score
        })

    # Sort candidates from highest to lowest score.
    scored_candidates.sort(
        key=lambda candidate: candidate["score"],
        reverse=True
    )
    
    if not scored_candidates:
        return None
    
    best_match = scored_candidates[0]
    
    if best_match["score"] < minimum_score:
        return None
    
    release_date = best_match["movie"].get("release_date", "")
    
    try:
        tmdb_year = int(release_date[:4])
    except (ValueError, TypeError):
        return {
            "status": "uncertain",
            "best_match": best_match,
            "second_best": (
                scored_candidates[1]
                if len(scored_candidates) > 1
                else None
            )
        }
        
    year_difference = abs(watchlist_year - tmdb_year)
    
    if year_difference > 2:
        return {
            "status": "uncertain",
            "best_match": best_match,
            "second_best": (
                scored_candidates[1]
                if len(scored_candidates) > 1
                else None
            )
        }
    
    if len(scored_candidates) > 1:
        second_best = scored_candidates[1]
        
        score_difference = (
            best_match["score"] - second_best["score"]
        )
        
        if score_difference < minimum_score_difference:
            return {
                "status": "uncertain",
                "best_match": best_match,
                "second_best": second_best
            }
    
    return {
        "status": "strong_match",
        "best_match": best_match
    }

def find_movie_candidates(search_titles):
    
    # Search TMDB using multiple title variations
    
    from .tmdb import search_movies
    
    candidates = {}
    
    for title in search_titles:
        results = search_movies(title)
        
        for movie in results.get("results",[]):
            movie_id = movie.get("id")
            
            if movie_id is not None:
                candidates[movie_id] = movie
                
    return list(candidates.values())
            