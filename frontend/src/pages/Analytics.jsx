import { useState, useEffect } from 'react'
import { api } from '../api.js'
import MetricCard from '../components/MetricCard.jsx'
import PlotWrapper from '../components/PlotWrapper.jsx'

const TABS = ['Catalog partitions', 'Co-watch centrality', 'Utility matrix']

export default function Analytics() {
  const [subTab, setSubTab] = useState('Catalog partitions')
  const [sunburstFig, setSunburstFig] = useState(null)
  const [centralityFig, setCentralityFig] = useState(null)
  const [matrixData, setMatrixData] = useState(null)
  const [loading, setLoading] = useState(false)

  // Fetch charts on demand
  useEffect(() => {
    if (subTab === 'Catalog partitions' && !sunburstFig) {
      setLoading(true)
      api
        .analyticsPartitions()
        .then(setSunburstFig)
        .catch(console.error)
        .finally(() => setLoading(false))
    } else if (subTab === 'Co-watch centrality' && !centralityFig) {
      setLoading(true)
      api
        .analyticsCentrality()
        .then(setCentralityFig)
        .catch(console.error)
        .finally(() => setLoading(false))
    } else if (subTab === 'Utility matrix' && !matrixData) {
      setLoading(true)
      api
        .analyticsMatrix()
        .then(setMatrixData)
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [subTab, sunburstFig, centralityFig, matrixData])

  return (
    <div className="analytics-page">
      <div className="brandline">
        <span className="brand-mark">SG</span>
        <span>StreamGlass</span>
        <span className="brand-divider"></span>
        <span>Analytics</span>
      </div>

      <header className="page-header">
        <div className="eyebrow">Catalog intelligence</div>
        <h1 className="page-title">Three views of a recommendation system’s structure.</h1>
        <p className="page-desc">
          Explore catalog partitions, centrality hubs, and the sparsity that makes hybrid
          recommendation valuable.
        </p>
      </header>

      {/* Subtabs bar */}
      <div className="subtabs-bar" role="tablist" style={{ marginBottom: '24px' }}>
        {TABS.map((t) => (
          <button
            key={t}
            className={`subtab-btn${subTab === t ? ' active' : ''}`}
            onClick={() => setSubTab(t)}
            role="tab"
            aria-selected={subTab === t}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab: Catalog partitions */}
      {subTab === 'Catalog partitions' && (
        <section className="tab-panel">
          <div className="section-heading">
            <div>
              <h2>Language and genre partitions</h2>
              <p>The catalog is divided into language → genre → title equivalence classes.</p>
            </div>
          </div>

          <div className="chart-surface" style={{ minHeight: '560px' }}>
            {loading || !sunburstFig ? (
              <div className="chart-loading">Loading partition sunburst…</div>
            ) : (
              <PlotWrapper
                data={sunburstFig.data}
                layout={{ ...sunburstFig.layout, height: 550 }}
                style={{ height: '550px' }}
              />
            )}
          </div>
        </section>
      )}

      {/* Tab: Co-watch centrality */}
      {subTab === 'Co-watch centrality' && (
        <section className="tab-panel">
          <div className="section-heading">
            <div>
              <h2>Bridge titles</h2>
              <p>
                Weighted degree centrality measures which titles connect the catalog’s co-watch
                communities.
              </p>
            </div>
          </div>

          <div className="chart-surface" style={{ minHeight: '560px' }}>
            {loading || !centralityFig ? (
              <div className="chart-loading">Loading centrality graph…</div>
            ) : (
              <PlotWrapper
                data={centralityFig.data}
                layout={{ ...centralityFig.layout, height: 550 }}
                style={{ height: '550px' }}
              />
            )}
          </div>
        </section>
      )}

      {/* Tab: Utility matrix */}
      {subTab === 'Utility matrix' && (
        <section className="tab-panel">
          <div className="section-heading">
            <div>
              <h2>Observed ratings</h2>
              <p>
                Unobserved cells in the user–item matrix are the space where the model has to infer
                relevance.
              </p>
            </div>
          </div>

          {matrixData && (
            <div style={{ marginBottom: '20px', maxWidth: '320px' }}>
              <MetricCard
                label="Matrix sparsity"
                value={`${(matrixData.sparsity * 100).toFixed(1)}%`}
                note="unobserved user–title rating pairs"
              />
            </div>
          )}

          <div className="chart-surface" style={{ minHeight: '545px' }}>
            {loading || !matrixData?.figure ? (
              <div className="chart-loading">Loading utility matrix heatmap…</div>
            ) : (
              <PlotWrapper
                data={matrixData.figure.data}
                layout={{ ...matrixData.figure.layout, height: 535 }}
                style={{ height: '535px' }}
              />
            )}
          </div>
        </section>
      )}
    </div>
  )
}
