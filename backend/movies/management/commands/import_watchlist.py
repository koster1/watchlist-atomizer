import csv
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from movies.models import Film

class Command(BaseCommand):
    """Import watchlist from CSV file."""
    
    help = "Import watchlist from CSV file."
    
    def add_arguments(self, parser):
        
        #Add the import dry-run option for testing.
        
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Test the import without saving to the database.",
        )
        
        # Allow a custom CSV path for tests and other imports.
        
        parser.add_argument(
            "--file",
            type=str,
            default=None,
            help="Path to the CSV file to import.",
        )

    
    def handle(self, *args, **options):

        # Use the supplied file, or default to the project root CSV.
        if options["file"]:
            csv_path = Path(options["file"])
        else:
            csv_path = Path(__file__).resolve().parents[4] / "watchlist.csv" 
        
        #Checking that the CSV file exists
        if not csv_path.exists():
            raise CommandError(f"CSV file not found at {csv_path}")
        
        # Open the CSV file using UTF-8 encoding
        
        with csv_path.open("r", encoding="utf-8-sig", newline=""
        ) as csv_file:
            
            reader = csv.DictReader(csv_file)
            
            # validate the required column headers.
            required_columns = {
                "Date", 
                "Name", 
                "Year", 
                "Letterboxd URI"
            }
            actual_columns = set(reader.fieldnames or [])
            missing_columns = required_columns - actual_columns
            
            if missing_columns:
                raise CommandError(f"Missing required columns in CSV file: {', '.join(sorted(missing_columns))}"
                )
            
            #Initialize the import counters.
            
            imported = 0
            skipped = 0
            errors = 0
            
            # Process each row in the CSV file.
            
            for row in reader:
                title = (row.get("Name") or "").strip()
                year_value = (row.get("Year") or "").strip()
                letterboxd_url = (row.get("Letterboxd URI") or "").strip()
                date_value = (row.get("Date") or "").strip()
            
                if not title or not letterboxd_url:
                    self.stderr.write(f"Skipping row with missing title or Letterboxd URL: {row}\n")
                    
                    errors += 1
                    continue
                
                # Validate the release year.
                
                try: 
                    year = int(year_value)
                    if year < 1874 or year > date.today().year:
                        raise ValueError
                    
                except ValueError:
                    self.stderr.write(
                        f"Row {reader.line_num}: Skipping row with invalid year '{year_value!r}'")
                    errors += 1
                    continue
                
                #Convert the date when one is provided.
                
                try:
                    date_added = (
                        date.fromisoformat(date_value)
                        if date_value
                        else None
                    )
                except ValueError:
                    self.stderr.write(
                        f"Row {reader.line_num}: Skipping row with invalid date '{date_value!r}'"
                    )
                    errors += 1
                    continue
                
                # Check whether the film already exists in the database.
                existing_film = Film.objects.filter(
                    letterboxd_url=letterboxd_url
                ).exists()
                
                if existing_film:
                    skipped += 1
                elif options["dry_run"]:
                    #Count the film as importable without saving it.
                    imported += 1
                else:
                    Film.objects.create(
                        title=title,
                        year=year,
                        letterboxd_url=letterboxd_url,
                        date_added=date_added,
                        director="",
                    )
                    imported += 1
                
            # Print the import summary.
        self.stdout.write(self.style.SUCCESS(f"Imported: {imported}"))
        self.stdout.write(f"Already existed: {skipped}")
        self.stdout.write(f"Invalid rows: {errors}")
                
                
            
        