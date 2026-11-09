
import { useEffect, useState } from 'react'
import './App.css'

interface Film {
  id: number
  title: string
  year: number
  director: string
}

type Page = 'home' | 'library'

function App() {
  const [films, setFilms] = useState<Film[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState<Page>('home')
  const [libraryPage, setLibraryPage] = useState(1)

  // Sivutuksen asetukset / Pagination settings
  const filmsPerPage = 105
  const totalPages = Math.max(1, Math.ceil(films.length / filmsPerPage))

  // Nykyisen sivun elokuvat / Films on the current page
  const startIndex = (libraryPage - 1) * filmsPerPage
  const visibleFilms = films.slice(startIndex, startIndex + filmsPerPage)

  useEffect(() => {
    // Hae elokuvat Django-rajapinnasta / Fetch films from the Django API
    fetch('http://127.0.0.1:8000/api/films/')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch films')
        }
        return response.json()
      })
      .then((data: Film[]) => {
        setFilms(data)
      })
      .catch((error: Error) => {
        setError(error.message)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  return (
    <div className="app">
      <header>
        <div className="logo">Cineboxd</div>

        <nav>
          <button
            className={currentPage === 'home' ? 'active' : ''}
            onClick={() => setCurrentPage('home')}
          >
            Home
          </button>

          <button
            className={currentPage === 'library' ? 'active' : ''}
            onClick={() => setCurrentPage('library')}
          >
            My Library
          </button>
        </nav>
      </header>

      <main>
        {currentPage === 'home' && (
          <section className="home-page">
            <h1>Cineboxd</h1>
            <br></br>
            <p>What films from your watchlist are screening in your city?</p>
            <br></br>
            <p>You currently have {films.length} films in your library.</p>
            <br></br>
            <button
              className="primary-button"
              onClick={() => setCurrentPage('library')}
            >
              Explore My Watchlist
            </button>
          </section>
        )}

        {currentPage === 'library' && (
          <section className="library-page">
            <h1>My Library</h1>

            {loading && <p>Loading films...</p>}

            {error && <p>Error: {error}</p>}

            {!loading && !error && (
              <>
                <div className="library-toolbar">
                  <p>{films.length} films in your collection</p>
                </div>

                <div className="film-grid">
                  {visibleFilms.map((film) => (
                    <article className="film-card" key={film.id}>
                      <div className="poster-placeholder">
                        <span>{film.title}</span>
                      </div>

                      <h3>{film.title}</h3>
                      <p>{film.year}</p>
                    </article>
                  ))}
                </div>

                {totalPages > 1 && (
                  <div className="pagination">
                    <button
                      onClick={() => setLibraryPage(libraryPage - 1)}
                      disabled={libraryPage === 1}
                    >
                      Previous
                    </button>

                    <span>
                      Page {libraryPage} of {totalPages}
                    </span>

                    <button
                      onClick={() => setLibraryPage(libraryPage + 1)}
                      disabled={libraryPage === totalPages}
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </section>
        )}
      </main>
    </div>
  )
}

export default App
