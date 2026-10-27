from rest_framework import status
from rest_framework.test import APITestCase

from .models import Film

import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

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



    