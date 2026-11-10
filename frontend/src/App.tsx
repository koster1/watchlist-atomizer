
import { useEffect, useState } from 'react'
import './App.css'

interface Film {
  id: number
  title: string
  year: number
  director: string
  date_added: string | null
}

type Page = 'home' | 'library'

type SortOrder = 
| 'oldest added'
| 'newest added'
| 'title-asc'
| 'title-desc'
| 'year-asc'
| 'year-desc'

function App() {
  const [films, setFilms] = useState<Film[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState<Page>('home')
  const [libraryPage, setLibraryPage] = useState(1)

  // Load saved sorting or use default
  const [sortOrder, setSortOrder] = useState<SortOrder>(() => {
    const savedOrder = localStorage.getItem('watchlist-atomizer-sortOrder') as SortOrder | null
    
    const validOrders: SortOrder[] = [
      'oldest added',
      'newest added',
      'title-asc',
      'title-desc',
      'year-asc',
      'year-desc'
    ]

    if (savedOrder && validOrders.includes(savedOrder as SortOrder)) {
      return savedOrder as SortOrder
  }

  return 'oldest added'
})


  // Sivutuksen asetukset 
  const filmsPerPage = 105
  const totalPages = Math.max(1, Math.ceil(films.length / filmsPerPage))

  // sort films by seleceted order.
  const sortedFilms = [...films].sort((a, b) => {
    switch (sortOrder) {
      case 'oldest added':
        if (!a.date_added) return 1
        if (!b.date_added) return -1
        return a.date_added.localeCompare(b.date_added)

      case 'newest added':
        if (!a.date_added) return 1
        if (!b.date_added) return -1
        return b.date_added.localeCompare(a.date_added)

      case 'title-asc':
        return a.title.localeCompare(b.title)

      case 'title-desc':
        return b.title.localeCompare(a.title)
        
      case 'year-asc':
        return a.year - b.year
      
      case 'year-desc':
        return b.year - a.year
        
      default:
        return 0
    }
  })

  // Films on the current page
  const startIndex = (libraryPage - 1) * filmsPerPage
  const visibleFilms = sortedFilms.slice(startIndex, startIndex + filmsPerPage)

  //Save sorting preference in browser

  useEffect(() => {
    localStorage.setItem('watchlist-atomizer-sortOrder', sortOrder)
  }, [sortOrder])

  useEffect(() => {
    // Fetch films from the Django API
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
        <div className="logo">Watchlist Atomizer</div>

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
            <h1>Watchlist Atomizer</h1>
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
                
                <select
                  value={sortOrder}
                  onChange={(event) => {
                    setSortOrder(event.target.value as SortOrder)
                    setLibraryPage(1) // Reset to first page when sorting changes
                  }}
                  aria-label="Sort films"
                >
                  <option value="oldest added">Oldest Added</option>
                  <option value="newest added">Newest Added</option>
                  <option value="title-asc">Title (A-Z)</option>
                  <option value="title-desc">Title (Z-A)</option>
                  <option value="year-asc">Release year (oldest)</option>
                  <option value="year-desc">Release Year (newest)</option>
                </select>
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
