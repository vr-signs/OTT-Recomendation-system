import { useState, useEffect } from 'react'
import { api } from '../api.js'
import MetricCard from '../components/MetricCard.jsx'
import DataTable from '../components/DataTable.jsx'

export default function Data() {
  const [metrics, setMetrics] = useState(null)
  const [activeTable, setActiveTable] = useState('users')
  const [tableData, setTableData] = useState({})
  const [loading, setLoading] = useState(false)

  // Fetch DB metrics once
  useEffect(() => {
    api.dbMetrics().then(setMetrics).catch(console.error)
  }, [])

  // Fetch table data when activeTable changes if not cached
  useEffect(() => {
    if (!tableData[activeTable]) {
      setLoading(true)
      const fetcher =
        activeTable === 'users'
          ? api.dbUsers()
          : activeTable === 'movies'
          ? api.dbMovies()
          : api.dbWatchHistory()

      fetcher
        .then((res) => {
          setTableData((prev) => ({ ...prev, [activeTable]: res }))
        })
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [activeTable, tableData])

  const currentData = tableData[activeTable] || { columns: [], rows: [] }

  return (
    <div className="data-page">
      <div className="brandline">
        <span className="brand-mark">SG</span>
        <span>StreamGlass</span>
        <span className="brand-divider"></span>
        <span>Engineering & data</span>
      </div>

      <header className="page-header">
        <div className="eyebrow">Live SQLite system view</div>
        <h1 className="page-title">Operationally simple, structurally rigorous.</h1>
        <p className="page-desc">
          Inspect the actual relational tables and storage metrics powering the recommender—without
          leaving the product.
        </p>
      </header>

      {/* Storage metrics cards */}
      <div className="grid-4" style={{ marginBottom: '28px' }}>
        <MetricCard
          label="Subscribers"
          value={metrics ? metrics.user_count : '—'}
          note="registered user profiles"
        />
        <MetricCard
          label="Catalog titles"
          value={metrics ? metrics.movie_count : '—'}
          note="regional media records"
        />
        <MetricCard
          label="Watch events"
          value={metrics ? metrics.interaction_count : '—'}
          note="recorded interactions"
        />
        <MetricCard
          label="SQLite footprint"
          value={metrics ? `${metrics.database_size_kb} KB` : '—'}
          note="on-disk engine size"
        />
      </div>

      <div className="section-heading">
        <div>
          <h2>Table explorer</h2>
          <p>The selected relation is queried from the live local database.</p>
        </div>
      </div>

      {/* Relation selector */}
      <div className="subtabs-bar" role="tablist" style={{ marginBottom: '16px' }}>
        {['users', 'movies', 'watch_history'].map((t) => (
          <button
            key={t}
            className={`subtab-btn${activeTable === t ? ' active' : ''}`}
            onClick={() => setActiveTable(t)}
            role="tab"
            aria-selected={activeTable === t}
          >
            {t}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="spinner" />
      ) : (
        <DataTable columns={currentData.columns} rows={currentData.rows} maxHeight={360} />
      )}

      <div className="section-heading" style={{ marginTop: '32px' }}>
        <div>
          <h2>Runtime</h2>
          <p>The application services currently composing this interface.</p>
        </div>
      </div>

      <div className="grid-4">
        <MetricCard
          label="Python"
          value={metrics ? metrics.python_version : '—'}
          note="service available"
        />
        <MetricCard label="FastAPI" value="v1.0.0" note="service available" />
        <MetricCard
          label="SQLite"
          value={metrics ? metrics.sqlite_version : '—'}
          note="service available"
        />
        <MetricCard label="Graph engine" value="NetworkX" note="service available" />
      </div>
    </div>
  )
}
