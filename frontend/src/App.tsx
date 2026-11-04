
import { useEffect, useState } from 'react'
import './App.css'

interface Film {
  id: number
  title: string
  year: number
  director: string
}

function App() {
  const [films, setFilms] = useState<Film[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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

  if (loading) {
    return <p>Loading films...</p>
  }

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <main>
      <h1>Watchlist Atomizer</h1>
      <h2>My Watchlist</h2>

      <p>You have {films.length} films in your watchlist.</p>

      <ul>
        {films.map((film) => (
          <li key={film.id}>
            <strong>{film.title}</strong> ({film.year})
            {film.director && <span> – {film.director}</span>}
          </li>
        ))}
      </ul>
    </main>
  )
}

export default App
