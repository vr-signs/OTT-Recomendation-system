import { useState, useEffect } from 'react'
import { api } from '../api.js'
import MetricCard from '../components/MetricCard.jsx'
import PlotWrapper from '../components/PlotWrapper.jsx'

export default function ModelLab() {
  const [k, setK] = useState(5)
  const [alpha, setAlpha] = useState(0.6)
  const [movies, setMovies] = useState([])
  const [movieA, setMovieA] = useState('M101')
  const [movieB, setMovieB] = useState('M102')
  const [similarity, setSimilarity] = useState(null)
  const [networkFig, setNetworkFig] = useState(null)
  const [loadingSim, setLoadingSim] = useState(false)
  const [loadingNet, setLoadingNet] = useState(false)

  // Fetch movies list for dropdowns
  useEffect(() => {
    api
      .dbMovies()
      .then((res) => {
        setMovies(res.rows || [])
        if (res.rows && res.rows.length >= 2) {
          setMovieA(res.rows[0].movie_id)
          setMovieB(res.rows[1].movie_id)
        }
      })
      .catch(console.error)
  }, [])

  // Fetch similarity when movieA or movieB changes
  useEffect(() => {
    if (movieA && movieB) {
      setLoadingSim(true)
      api
        .modelSimilarity(movieA, movieB)
        .then(setSimilarity)
        .catch(console.error)
        .finally(() => setLoadingSim(false))
    }
  }, [movieA, movieB])

  // Fetch network graph figure
  useEffect(() => {
    setLoadingNet(true)
    api
      .modelNetwork()
      .then(setNetworkFig)
      .catch(console.error)
      .finally(() => setLoadingNet(false))
  }, [])

  return (
    <div className="model-lab-page">
      <div className="brandline">
        <span className="brand-mark">SG</span>
        <span>StreamGlass</span>
        <span className="brand-divider"></span>
        <span>Model lab</span>
      </div>

      <header className="page-header">
        <div className="eyebrow">Tune the ranking model</div>
        <h1 className="page-title">Move from an abstract formula to a visible recommendation decision.</h1>
        <p className="page-desc">
          The controls update the existing hybrid scoring engine; the vector view and force graph
          reflect its live database state.
        </p>
      </header>

      {/* Controls */}
      <div className="section-heading">
        <div>
          <h2>Recommendation controls</h2>
          <p>Personal relevance and catalog discovery share a deliberate balance.</p>
        </div>
      </div>

      <div className="surface card" style={{ marginBottom: '20px' }}>
        <div className="grid-2">
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label htmlFor="k-slider" className="form-label" style={{ fontWeight: 600 }}>
                Nearest neighbors (k)
              </label>
              <span style={{ fontWeight: 700, color: 'var(--blue)' }}>{k}</span>
            </div>
            <input
              id="k-slider"
              type="range"
              min="2"
              max="8"
              step="1"
              value={k}
              onChange={(e) => setK(parseInt(e.target.value, 10))}
              style={{ width: '100%', accentColor: 'var(--blue)' }}
            />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label htmlFor="alpha-slider" className="form-label" style={{ fontWeight: 600 }}>
                Collaborative weighting (α)
              </label>
              <span style={{ fontWeight: 700, color: 'var(--blue)' }}>{alpha.toFixed(2)}</span>
            </div>
            <input
              id="alpha-slider"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={alpha}
              onChange={(e) => setAlpha(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--blue)' }}
            />
          </div>
        </div>

        <div className="status-line" style={{ marginTop: '16px' }}>
          <span className="status-dot"></span>
          {Math.round(alpha * 100)}% collaborative filtering · {Math.round((1 - alpha) * 100)}% graph
          centrality · k = {k}
        </div>
      </div>

      {/* Cosine similarity */}
      <div className="section-heading">
        <div>
          <h2>Cosine similarity</h2>
          <p>Choose any two catalog titles to inspect the exact vector calculation.</p>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: '16px' }}>
        <div>
          <label htmlFor="movie-a-select" className="form-label">First title</label>
          <select
            id="movie-a-select"
            value={movieA}
            onChange={(e) => setMovieA(e.target.value)}
            className="select-input"
          >
            {movies.map((m) => (
              <option key={m.movie_id} value={m.movie_id}>
                {m.title} · {m.language}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="movie-b-select" className="form-label">Second title</label>
          <select
            id="movie-b-select"
            value={movieB}
            onChange={(e) => setMovieB(e.target.value)}
            className="select-input"
          >
            {movies.map((m) => (
              <option key={m.movie_id} value={m.movie_id}>
                {m.title} · {m.language}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loadingSim ? (
        <div className="spinner" />
      ) : similarity && !similarity.error ? (
        <div className="grid-4" style={{ marginBottom: '32px' }}>
          <MetricCard
            label="Cosine similarity"
            value={similarity.cosine_similarity}
            note="normalized affinity"
          />
          <MetricCard
            label="Dot product"
            value={similarity.dot_product}
            note="shared rating signal"
          />
          <MetricCard
            label="Norm A"
            value={similarity.norm_a}
            note={movies.find((m) => m.movie_id === movieA)?.title || movieA}
          />
          <MetricCard
            label="Norm B"
            value={similarity.norm_b}
            note={movies.find((m) => m.movie_id === movieB)?.title || movieB}
          />
        </div>
      ) : similarity?.error ? (
        <div className="alert alert-warn" style={{ marginBottom: '32px' }}>
          {similarity.error}
        </div>
      ) : null}

      {/* Network Force Graph */}
      <div className="section-heading">
        <div>
          <h2>Co-watch topology</h2>
          <p>
            Node scale reflects normalized degree centrality; links represent shared viewing behavior.
          </p>
        </div>
      </div>

      <div className="chart-surface" style={{ minHeight: '520px' }}>
        {loadingNet || !networkFig ? (
          <div className="chart-loading">Loading network graph…</div>
        ) : (
          <PlotWrapper
            data={networkFig.data}
            layout={{ ...networkFig.layout, height: 510 }}
            style={{ height: '510px' }}
          />
        )}
      </div>
    </div>
  )
}
