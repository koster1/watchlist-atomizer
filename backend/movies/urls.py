
from django.urls import path
from .views import film_list, tmdb_movie_search, tmdb_movie_save

urlpatterns = [
    path("films/", film_list, name="film-list"),
    path("tmdb/search/",tmdb_movie_search,name="tmdb-movie-search"),
    path("tmdb/save/", tmdb_movie_save, name="tmdb_movie_save"),
]
