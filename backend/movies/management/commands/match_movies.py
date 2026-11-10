from django.core.management.base import BaseCommand

from movies.models import Film
from movies.tmdb import find_exact_tmdb_match, update_film_from_tmdb

class Command(BaseCommand):
    help = 'Find the films from TMDB that match the ones in the watchlist and save their data'
    

    def handle(self, *args, **options):
        films = Film.objects.filter(
            tmdb_id__isnull=True
        ).order_by("id")

        self.stdout.write(
            f"Processing {films.count()} films without TMDB IDs..."
        )

        for film in films:
            try:
                match = find_exact_tmdb_match(film.title, film.year)

                if not match:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No match found: {film.title} ({film.year})"
                        )
                    )
                    continue

                update_film_from_tmdb(film, match["id"])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated: {film.title} ({film.year}) "
                        f"with TMDB ID: {match['id']}"
                    )
                )

            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error processing {film.title} ({film.year}): {error}"
                    )
                )
                continue


        
        