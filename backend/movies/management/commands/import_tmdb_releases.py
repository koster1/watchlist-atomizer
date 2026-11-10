from django.core.management.base import BaseCommand

from movies.models import Film
from movies.tmdb import save_movie_releases_by_country

class Command(BaseCommand):
    help = 'Import theatrical release dates from TMDB for all films.'
    
    def handle(self, *args, **options):
        films = Film.objects.exclude(tmdb_id__isnull=True)
        
        total = films.count()
        successful = 0
        failed = 0
        saved_releases = 0
        
        self.stdout.write(f"Processing {total} films...")
        
        for film in films:
            try:
                count = save_movie_releases_by_country(film)
                saved_releases += count
                successful += 1
                
                self.stdout.write(
                    f"Processed: {film.title} ({count} releases)"
                )
            except Exception as e:
                failed += 1
                self.stderr.write(
                    f"Failed to process {film.title}: {str(e)}"
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished processing films. Successful: {successful}, Failed: {failed}, Releases saved: {saved_releases}"
            )
        )
        
