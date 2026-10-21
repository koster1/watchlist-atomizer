# Watchlist Atomizer

**Find out which films on your Letterboxd watchlist are showing in cinemas.**

Watchlist Atomizer is a full-stack web application in development. Its goal is to help users discover which films from their Letterboxd watchlist are currently screening in cinemas in a selected country.

## Project Goals

- Import a watchlist exported from Letterboxd as a CSV file.
- Store and manage films in a database.
- Select a country and find matching cinema screenings.
- Build a web interface for browsing films and their screening information.

## Current Status

The project is under active development.

### Implemented

- Django backend.
- Django REST Framework API endpoint for listing films.
- Database-backed film model.
- Django admin interface for managing films.
- Initial automated tests for the film list API.

### Planned

- Letterboxd watchlist CSV import.
- Improved film metadata handling.
- Cinema screening data integration.
- Country selection and screening search.
- React frontend.

## Tech Stack

**Backend**
- Python
- Django
- Django REST Framework

**Database**
- SQLite for local development

**Frontend**
- React — planned

## Getting Started

### Prerequisites

- Python 3
- Git

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd watchlist-atomizer
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the URL of your GitHub repository.

### 2. Create a virtual environment

```bash
cd backend
python -m venv .venv
```

Activate it on Windows:

```bat
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

The backend will be available at:

`http://127.0.0.1:8000/`

The film list API endpoint is:

`http://127.0.0.1:8000/api/films/`

## Running Tests

From the `backend` directory, run:

```bash
python manage.py test
```

## Project Structure

```text
watchlist-atomizer/
├── backend/
│   ├── config/
│   ├── movies/
│   │   └── migrations/
│   ├── manage.py
│   └── requirements.txt
├── .gitignore
└── README.md
```

The exact project structure may evolve during development.

## Security Notes

- Do not commit passwords, API keys, secret keys, or other credentials.
- Keep local environment files and development databases out of version control.
- Use environment variables for sensitive configuration before deploying the application.

## License

No license has been selected yet.
