
from django.core.management.base import BaseCommand

from movies.models import Film
from movies.matching import find_best_match
from movies.tmdb import update_film_from_tmdb


class Command(BaseCommand):
    help = "Match watchlist films with TMDB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show matches without saving them."
        )

    def show_candidate(self, number, candidate):
        movie = candidate["movie"]
        release_date = movie.get("release_date") or "Unknown date"
        year = release_date[:4] if release_date != "Unknown date" else release_date

        self.stdout.write(
            f"{number}. {movie.get('title')} ({year}) - Score: {candidate['score']}"
        )

    def choose_match(self, film, result):
        best = result["best_match"]
        second = result.get("second_best")

        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                f"Uncertain match: {film.title} ({film.year})"
            )
        )

        self.show_candidate(1, best)

        if second is None:
            while True:
                answer = input("Add this match to database? (y/n): ").strip().lower()

                if answer == "y":
                    return best["movie"]

                if answer == "n":
                    return None

                self.stdout.write("Please enter y or n.")

        self.show_candidate(2, second)

        while True:
            answer = input("Choose a match (1/2/s to skip): ").strip().lower()

            if answer == "1":
                return best["movie"]

            if answer == "2":
                return second["movie"]

            if answer == "s":
                return None

            self.stdout.write("Please enter 1, 2 or s.")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write("How should uncertain matches be handled?")
        self.stdout.write("1. Automatically skip all uncertain matches")
        self.stdout.write("2. Manually review uncertain matches")

        while True:
            mode = input("Choose mode (1/2): ").strip()

            if mode in ("1", "2"):
                break

            self.stdout.write("Please enter 1 or 2.")

        automatic_mode = mode == "1"

        films = Film.objects.filter(
            tmdb_id__isnull=True
        ).order_by("id")

        self.stdout.write(
            f"\nProcessing {films.count()} films without TMDB IDs..."
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN: No changes will be saved.")
            )

        strong_matches = 0
        manual_matches = 0
        uncertain_skipped = 0
        no_matches = 0
        errors = 0

        for film in films:
            try:
                result = find_best_match(film.title, film.year)

                if not result:
                    no_matches += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"No match: {film.title} ({film.year})"
                        )
                    )
                    continue

                if result["status"] == "uncertain":
                    if automatic_mode:
                        uncertain_skipped += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipped uncertain match: {film.title} ({film.year})"
                            )
                        )
                        continue

                    movie = self.choose_match(film, result)

                    if movie is None:
                        uncertain_skipped += 1
                        self.stdout.write("Skipped.")
                        continue

                    if not dry_run:
                        update_film_from_tmdb(film, movie["id"])

                    manual_matches += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Manually matched: {film.title} "
                            f"with TMDB ID: {movie['id']}"
                        )
                    )
                    continue

                movie = result["best_match"]["movie"]

                if not dry_run:
                    update_film_from_tmdb(film, movie["id"])

                strong_matches += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Matched: {film.title} ({film.year}) "
                        f"with TMDB ID: {movie['id']}"
                    )
                )

            except Exception as error:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Error processing {film.title} ({film.year}): {error}"
                    )
                )

        self.stdout.write("")
        self.stdout.write("Matching completed.")
        self.stdout.write(f"Strong matches: {strong_matches}")
        self.stdout.write(f"Manually confirmed matches: {manual_matches}")
        self.stdout.write(f"Uncertain matches skipped: {uncertain_skipped}")
        self.stdout.write(f"No matches: {no_matches}")
        self.stdout.write(f"Errors: {errors}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN completed. Nothing was saved.")
            )
