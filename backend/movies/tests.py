import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from movies.models import Film
from movies.tmdb import (
    search_movies,
    get_theatrical_release_date_by_country,
    get_movie_details,
    save_movie_from_tmdb,
)


class FilmListTestCase(APITestCase):
    
    """
    Testit elokuvalistan API-rajapinnalle.
    Tests for the film list API endpoint.
    """
    
    def test_film_list_returns_successful_response(self):
        """
        Varmistaa, että elokuvalistan hakeminen onnistuu.
        Verifies that retrieving the film list succeeds.
        """
        
        # Lähetetään GET-pyyntö elokuvalistan API-osoitteeseen.
        # Send a GET request to the film list API endpoint.
        
        response = self.client.get('/api/films/')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            )
        
    def test_film_list_returns_expected_fields(self):
        
        Film.objects.create(
            title='Test Film',
            director='Test Director',
            year=2026
        )
        
        response = self.client.get('/api/films/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data), 1)
        
        film = response.data[0]
        
        self.assertIn('id', film)
        self.assertIn('title', film)
        self.assertIn('director', film)
        self.assertIn('year', film)
        
        self.assertEqual(film['title'], 'Test Film')
        self.assertEqual(film['director'], 'Test Director')
        self.assertEqual(film['year'], 2026)

    def test_film_list_returns_empty_list(self):
        """
        Varmistaa, että elokuvalista palauttaa tyhjän listan, jos elokuvia ei ole.
        Verifies that the film list returns an empty list if there are no films.
        """
        
        response = self.client.get('/api/films/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual((response.data), [])
    
    def test_film_list_returns_multiple_films(self):
        """
        Varmistaa, että elokuvalista palauttaa useita elokuvia oikein.
        Verifies that the film list returns multiple films correctly.
        """
        
        Film.objects.create(
            title='Film 1',
            director='Director 1',
            year=2025
        )
        
        Film.objects.create(
            title='Film 2',
            director='Director 2',
            year=2026
        )
        
        response = self.client.get('/api/films/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data), 2)
        
        titles = [film['title'] for film in response.data]
        
        self.assertIn('Film 1', titles)
        self.assertIn('Film 2', titles)
        
    def test_film_list_filters_by_title(self):
        # Create two test films.
        
        Film.objects.create(title="Digger", year=2026)
        Film.objects.create(title="The Matrix", year=1999)
        
        # Search films by title
        
        response = self.client.get("/api/films/?search=Digger")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Digger")

class ImportWatchlistTestCase(TestCase):
    """
    Testit CSV-tuontikomennolle.
    Tests for the CSV import command.
    """

    def test_import_one_valid_film(self):
        """
        Testaa yhden kelvollisen elokuvan tuonnin.
        Tests importing one valid film.
        """
        csv_content = (
            "Date,Name,Year,Letterboxd URI\n"
            "2024-01-01,Test Film,2000,"
            "https://letterboxd.com/film/test-film/\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "test_watchlist.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            call_command("import_watchlist", file=str(csv_path))

        film = Film.objects.get(
            letterboxd_url="https://letterboxd.com/film/test-film/"
        )

        self.assertEqual(film.title, "Test Film")
        self.assertEqual(film.year, 2000)
        self.assertEqual(film.date_added.isoformat(), "2024-01-01")
        
    def test_import_film_with_future_year(self):
        # Test that future release years are accepted.
        
        csv_content = (
            "Date,Name,Year,Letterboxd URI\n"
            "2026-10-01,Future Film, 2030,"
            "https://letterboxd.com/film/future-film/\n"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "watchlist.csv"
            csv_path.write_text(csv_content, encoding="utf-8")
            
            call_command("import_watchlist", file=str(csv_path))
            
        film = Film.objects.get(title="Future Film")
        self.assertEqual(film.year, 2030)
    
    def test_skips_existing_film(self):
        """
        Testaa, että jo olemassa oleva elokuva ohitetaan.
        Tests that an existing film is skipped.
        """
        Film.objects.create(
            title="Existing Film",
            year=2000,
            letterboxd_url="https://letterboxd.com/film/existing-film/",
        )

        csv_content = (
            "Date,Name,Year,Letterboxd URI\n"
            "2024-01-01,Existing Film,2000,"
            "https://letterboxd.com/film/existing-film/\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "test_watchlist.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            call_command("import_watchlist", file=str(csv_path))

        self.assertEqual(Film.objects.count(), 1)
        self.assertEqual(
            Film.objects.get().title,
            "Existing Film",
        )
    
    def test_skips_film_with_invalid_year(self):
        """
        Testaa virheellisen julkaisuvuoden ohittamisen.
        Tests that a film with an invalid year is skipped.
        """
        csv_content = (
            "Date,Name,Year,Letterboxd URI\n"
            "2024-01-01,Invalid Film,not-a-year,"
            "https://letterboxd.com/film/invalid-film/\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "test_watchlist.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            call_command("import_watchlist", file=str(csv_path))

        self.assertEqual(Film.objects.count(), 0)
    
    def test_dry_run_does_not_save_films(self):
        """
        Varmistaa, ettei dry-run tallenna elokuvia.
        Verifies that dry-run does not save films.
        """
        csv_content = (
            "Date,Name,Year,Letterboxd URI\n"
            "2024-01-01,Dry Run Film,2000,"
            "https://letterboxd.com/film/dry-run-film/\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "test_watchlist.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            call_command(
                "import_watchlist",
                file=str(csv_path),
                dry_run=True,
            )

        self.assertEqual(Film.objects.count(), 0)
        
    
    def test_missing_required_column_raises_error(self):
        """
        Testaa pakollisen sarakkeen puuttumisen.
        Tests that a missing required column raises an error.
        """
        csv_content = (
            "Date,Name,Year\n"
            "2024-01-01,Test Film,2000\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "test_watchlist.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            with self.assertRaises(CommandError):
                call_command(
                    "import_watchlist",
                    file=str(csv_path),
                )

        self.assertEqual(Film.objects.count(), 0)

class TMDBSearchMoviesTest(TestCase):
    
    @patch("movies.tmdb.urllib.request.urlopen")
    def test_search_movies_returns_api_response(self, mock_urlopen):
        #Simulate a TMDB response.
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = (
            b'{"results": [{"id": 1248832, "title": "Digger"}]}'
        )
        
        result = search_movies("Digger")
        
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], 1248832)
        self.assertEqual(result["results"][0]["title"], "Digger")
        
    @patch.dict("os.environ", {}, clear=True)
    def test_search_movies_raises_error_when_api_key_is_missing(self):
        # Check that a missing API key raises an error.
        # Tarkistaa, että puuttuva API-avain aiheuttaa virheen.
        with self.assertRaises(RuntimeError):
            search_movies("Digger")
            
    
    @patch("movies.tmdb.urllib.request.urlopen")
    def test_get_movie_details_returns_api_response(self, mock_urlopen):
        # Simulate a TMDB movie details response.
        # Jäljittelee TMDB:n elokuvan tietovastausta.
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = (
            b'{"id": 1248832, "title": "Digger", "release_date": "2026-09-28"}'
        )

        result = get_movie_details(1248832)

        self.assertEqual(result["id"], 1248832)
        self.assertEqual(result["title"], "Digger")
        self.assertEqual(result["release_date"], "2026-09-28")

            
class TMDBReleaseDateTest(TestCase):
    
    #Tests for country-spesific release dates.
    
    @patch("movies.tmdb.urllib.request.urlopen")
    def test_returns_theatrical_release_date_for_country(self, mock_urlopen):
        # Simulate TMDB release date response. / Jäljittelee TMDB:n julkaisupäivävastausta.
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = (
            b'{"results": [{"iso_3166_1": "FI", "release_dates": '
            b'[{"release_date": "2026-10-02T00:00:00.000Z", "type": 3}]}]}'
        )

        result = get_theatrical_release_date_by_country(1248832, "FI")

        self.assertEqual(result, "2026-10-02")
        
    
    @patch("movies.tmdb.urllib.request.urlopen")
    def test_returns_none_when_country_is_missing(self, mock_urlopen):
        # Simulate a response without Finnish release data.
        # Jäljittelee vastausta, jossa ei ole Suomen julkaisutietoja.
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = (
            b'{"results": [{"iso_3166_1": "DE", "release_dates": '
            b'[{"release_date": "2026-10-01T00:00:00.000Z", "type": 3}]}]}'
        )

        result = get_theatrical_release_date_by_country(1248832, "FI")

        self.assertIsNone(result)

class TMDBSaveMovieTest(TestCase):
    """Tests for saving TMDB movies. / TMDB-elokuvien tallennustestit."""

    @patch("movies.tmdb.get_movie_details")
    def test_saves_new_movie(self, mock_get_movie_details):
        # Simulate a TMDB movie response.
        # Jäljittelee TMDB:n elokuvavastausta.
        mock_get_movie_details.return_value = {
            "id": 1248832,
            "title": "Digger",
            "release_date": "2026-09-28",
        }

        film, created = save_movie_from_tmdb(1248832)

        self.assertTrue(created)
        self.assertEqual(film.title, "Digger")
        self.assertEqual(film.year, 2026)
        self.assertEqual(str(film.release_date), "2026-09-28")
        self.assertEqual(Film.objects.count(), 1)

    @patch("movies.tmdb.get_movie_details")
    def test_updates_existing_movie(self, mock_get_movie_details):
        # Create a movie that already exists.
        # Luodaan elokuva, joka on jo tietokannassa.
        existing_film = Film.objects.create(
            title="Digger",
            year=2026,
            tmdb_id=1248832
        )

        mock_get_movie_details.return_value = {
            "id": 1248832,
            "title": "Digger",
            "release_date": "2026-09-28",
        }

        film, created = save_movie_from_tmdb(1248832)

        self.assertFalse(created)
        self.assertEqual(film.pk, existing_film.pk)
        self.assertEqual(str(film.release_date), "2026-09-28")
        self.assertEqual(Film.objects.count(), 1)
        
class TMDBMovieSaveAPITest(APITestCase):
    
    #Tests for the TMDB movie save API endpoint.
    @patch("movies.views.save_movie_from_tmdb")
    def test_saves_new_movie(self, mock_save_movie):
        # Simulate saving a new movie.
        # Jäljittelee uuden elokuvan tallennusta.
        film = Film.objects.create(
            title="Digger",
            year=2026,
            tmdb_id=1248832,
        )
        mock_save_movie.return_value = (film, True)

        response = self.client.post(
            "/api/tmdb/save/",
            {"movie_id": 1248832},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["created"])
        self.assertEqual(response.data["film"]["title"], "Digger")
        mock_save_movie.assert_called_once_with(1248832)

    @patch("movies.views.save_movie_from_tmdb")
    def test_updates_existing_movie(self, mock_save_movie):
        # Simulate updating an existing movie.
        # Jäljittelee olemassa olevan elokuvan päivitystä.
        film = Film.objects.create(
            title="Digger",
            year=2026,
            tmdb_id=1248832,
        )
        mock_save_movie.return_value = (film, False)

        response = self.client.post(
            "/api/tmdb/save/",
            {"movie_id": 1248832},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["created"])
        self.assertEqual(Film.objects.count(), 1)
        mock_save_movie.assert_called_once_with(1248832)

    def test_missing_movie_id_returns_bad_request(self):
        # Verify that the movie ID is required.
        # Varmistaa, että elokuvan tunniste on pakollinen.
        response = self.client.post(
            "/api/tmdb/save/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("error", response.data)

    def test_invalid_movie_id_returns_bad_request(self):
        # Verify that an invalid movie ID is rejected.
        # Varmistaa, että virheellinen elokuvatunniste hylätään.
        response = self.client.post(
            "/api/tmdb/save/",
            {"movie_id": "not-a-number"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("error", response.data)
