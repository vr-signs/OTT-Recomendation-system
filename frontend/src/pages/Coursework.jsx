import { useState, useEffect } from 'react'
import { api } from '../api.js'
import Formula from '../components/Formula.jsx'
import ProofCard from '../components/ProofCard.jsx'

const TABS = ['DBMS', 'DMGT', 'ADSA', 'OOPJ + Python']

export default function Coursework() {
  const [subTab, setSubTab] = useState('DBMS')
  const [dmgtData, setDmgtData] = useState(null)
  const [adsaData, setAdsaData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (subTab === 'DMGT' && !dmgtData) {
      setLoading(true)
      api
        .courseworkDmgt()
        .then(setDmgtData)
        .catch(console.error)
        .finally(() => setLoading(false))
    } else if (subTab === 'ADSA' && !adsaData) {
      setLoading(true)
      api
        .courseworkAdsa()
        .then(setAdsaData)
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [subTab, dmgtData, adsaData])

  return (
    <div className="coursework-page">
      <div className="brandline">
        <span className="brand-mark">SG</span>
        <span>StreamGlass</span>
        <span className="brand-divider"></span>
        <span>Coursework</span>
      </div>

      <header className="page-header">
        <div className="eyebrow">JNTUK R23 · II B.Tech I Sem</div>
        <h1 className="page-title">Formal foundations, presented as a product surface.</h1>
        <p className="page-desc">
          Proofs, relational integrity, graph traversal, and collaborative filtering remain live
          rather than becoming static documentation.
        </p>
      </header>

      {/* Sub-tabs */}
      <div className="subtabs-bar" role="tablist">
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

      {/* Tab: DBMS */}
      {subTab === 'DBMS' && (
        <section className="tab-panel">
          <div className="section-heading">
            <div>
              <h2>Relational model</h2>
              <p>Entities stay normalized while interactions retain their own transaction history.</p>
            </div>
          </div>

          <div className="grid-2">
            <div className="formula-surface">
              <Formula
                math={
                  '\\text{Users}(\\underline{\\text{user\\_id}},\\; \\text{name},\\; \\text{age},\\; \\text{primary\\_language},\\; \\text{secondary\\_language})'
                }
                block
              />
              <div style={{ height: '14px' }} />
              <Formula
                math={
                  '\\text{Movies}(\\underline{\\text{movie\\_id}},\\; \\text{title},\\; \\text{year},\\; \\text{language},\\; \\text{primary\\_genre},\\; \\text{director})'
                }
                block
              />
              <div style={{ height: '14px' }} />
              <Formula
                math={
                  '\\text{WatchHistory}(\\underline{\\text{history\\_id}},\\; \\text{user\\_id}^{*},\\; \\text{movie\\_id}^{*},\\; \\text{watch\\_percentage},\\; \\text{rating})'
                }
                block
              />
            </div>

            <section className="surface card">
              <h3 className="section-title">3NF validation</h3>
              <p className="body-copy">
                Each entity is identified by a candidate key. User, movie, and interaction
                attributes are fully dependent on their own key, avoiding transitive dependencies
                between content and viewing events.
              </p>
              <p className="body-copy" style={{ marginTop: '10px' }}>
                <strong>Indexes</strong> accelerate subscriber, title, language–genre, and
                popularity lookup paths.
              </p>
            </section>
          </div>

          <div className="formula-surface" style={{ marginTop: '16px' }}>
            <div style={{ fontWeight: 600, marginBottom: '8px' }}>Functional dependencies</div>
            <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', lineHeight: '1.7' }}>
              F₁: user_id → {'{name, age, primary_language}'}
              <br />
              F₂: movie_id → {'{title, year, language, primary_genre}'}
              <br />
              F₃: history_id → {'{user_id, movie_id, watch_pct, rating}'}
            </div>
          </div>
        </section>
      )}

      {/* Tab: DMGT */}
      {subTab === 'DMGT' && (
        <section className="tab-panel">
          <div className="section-heading">
            <div>
              <h2>Equivalence relation</h2>
              <p>Live verification over the catalog—not a mocked proof state.</p>
            </div>
          </div>

          <div className="formula-surface" style={{ marginBottom: '16px', textAlign: 'center' }}>
            <Formula
              math={
                '(x, y) \\in R \\iff \\text{Genre}(x) = \\text{Genre}(y) \\land \\text{Language}(x) = \\text{Language}(y)'
              }
              block
            />
          </div>

          {loading ? (
            <div className="spinner" />
          ) : dmgtData ? (
            <>
              <div className="grid-3">
                <ProofCard proof={dmgtData.reflexivity} />
                <ProofCard proof={dmgtData.symmetry} />
                <ProofCard proof={dmgtData.transitivity} />
              </div>

              {dmgtData.partition && (
                <section className="surface card" style={{ marginTop: '16px' }}>
                  <h3 className="section-title">Partition theorem</h3>
                  <p className="body-copy">
                    The quotient set produces{' '}
                    <strong>{dmgtData.partition.num_classes} pairwise-disjoint classes</strong>. Its
                    union covers{' '}
                    <strong>
                      {dmgtData.partition.union_coverage_size} of{' '}
                      {dmgtData.partition.total_universe_size} catalog items
                    </strong>
                    ; disjointness and exhaustive coverage both pass.
                  </p>
                </section>
              )}
            </>
          ) : (
            <p style={{ color: 'var(--muted)' }}>Loading verification proofs…</p>
          )}
        </section>
      )}

      {/* Tab: ADSA */}
      {subTab === 'ADSA' && (
        <section className="tab-panel">
          <div className="section-heading">
            <div>
              <h2>Co-watch graph</h2>
              <p>A custom weighted adjacency list turns shared viewing behavior into topology.</p>
            </div>
          </div>

          <div className="formula-surface" style={{ marginBottom: '16px', textAlign: 'center' }}>
            <Formula
              math={
                'W(u,v) = \\sum_{s \\in S_{uv}} \\left[\\left(\\frac{r_{s,u}+r_{s,v}}{10}\\right)\\times\\left(\\frac{\\min(w_{s,u},w_{s,v})}{100}\\right)\\right]'
              }
              block
            />
          </div>

          {loading ? (
            <div className="spinner" />
          ) : adsaData ? (
            <div className="grid-2">
              <section className="surface card">
                <h3 className="section-title">Traversal and centrality</h3>
                <p className="body-copy">
                  <strong>Breadth-first search</strong> visits related titles through a FIFO queue in
                  O(|V| + |E|). Normalized weighted degree centrality identifies titles that bridge
                  regional co-watch communities.
                </p>
              </section>

              <section className="surface card">
                <h3 className="section-title">Live topology</h3>
                <p className="body-copy">
                  Vertices <strong>{adsaData.num_nodes}</strong> · Edges{' '}
                  <strong>{adsaData.num_edges}</strong> · Density{' '}
                  <strong>{adsaData.density}</strong>
                </p>
                <p className="body-copy" style={{ marginTop: '8px' }}>
                  Top bridge: <strong>{adsaData.top_hub_movie}</strong> · centrality{' '}
                  {adsaData.top_hub_centrality}
                </p>
              </section>
            </div>
          ) : (
            <p style={{ color: 'var(--muted)' }}>Loading topology metrics…</p>
          )}
        </section>
      )}

      {/* Tab: OOPJ + Python */}
      {subTab === 'OOPJ + Python' && (
        <section className="tab-panel">
          <div className="section-heading">
            <div>
              <h2>Hybrid recommendation model</h2>
              <p>A clear model contract for personal relevance and catalog discovery.</p>
            </div>
          </div>

          <div className="formula-surface">
            <Formula
              math={
                '\\text{Cosine Similarity}(i,j)=\\frac{\\vec{v}_i\\cdot\\vec{v}_j}{\\|\\vec{v}_i\\|_2\\|\\vec{v}_j\\|_2}'
              }
              block
            />
            <div style={{ height: '14px' }} />
            <Formula
              math={
                '\\text{Score}(u,i)=\\left[\\alpha\\cdot\\frac{\\widehat{r}_{u,i}}{5.0}+(1-\\alpha)\\cdot\\frac{C_D(i)}{\\max_k C_D(k)}\\right]\\times\\beta_{\\text{lang}}(u,i)\\times\\gamma_{\\text{genre}}(u,i)'
              }
              block
            />
          </div>

          <section className="surface card" style={{ marginTop: '16px' }}>
            <h3 className="section-title">Interpretation</h3>
            <p className="body-copy">
              The α control balances collaborative ratings with graph connectivity. Language and
              genre modifiers preserve the regional relevance that a popularity-only feed ignores.
            </p>
          </section>
        </section>
      )}
    </div>
  )
}
