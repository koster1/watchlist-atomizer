from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Film
from .serializers import FilmSerializer
from .tmdb import search_movies, save_movie_from_tmdb

@api_view(['GET'])
def film_list(request):
    
    # Fetch films from the database.
    
    films = Film.objects.all()
    
    #Filter films by title when a search query is provided.
    
    search_query = request.query_params.get("search")
    
    if search_query:
        films = films.filter(title__icontains=search_query)
    
    serializer = FilmSerializer(films, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
def tmdb_movie_search(request):
    
    # Read the sarch term from the URL parameter.
    
    query = request.query_params.get("query", "").strip()
    
    
    if not query:
        return Response(
            {"error": "Search query is required."},
            status=400,
        )
            
    results = search_movies(query)
        
    return Response(results)

@api_view(['POST'])
def tmdb_movie_save(request):
    
    # Read the TMDB movie ID from the request data.
    
    movie_id = request.data.get("movie_id")
    
    if not movie_id:
        return Response(
            {"error": "movie_id is required."},
            status=400
        )
        
    try:
        movie_id = int(movie_id)
        if movie_id <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return Response(
            {"error": "movie_id must be a positive integer."},
            status=400
        )
        
    try:
        film, created = save_movie_from_tmdb(movie_id)
    except Exception:
        return Response(
            {"error", "Could not save the movie from TMDB."},
            status=502
        )                 
        
    serializer = FilmSerializer(film)
    
    return Response(
        {
            "created": created,
            "film": serializer.data,
        },
        status=201 if created else 200
    )
