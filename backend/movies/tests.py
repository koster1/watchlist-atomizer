from rest_framework import status
from rest_framework.test import APITestCase

from .models import Film

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
        