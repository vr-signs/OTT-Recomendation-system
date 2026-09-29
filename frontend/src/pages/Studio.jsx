import { useState, useEffect, useCallback } from 'react'
import { api } from '../api.js'
import TitleCard from '../components/TitleCard.jsx'

export default function Studio() {
  const [users, setUsers] = useState([])
  const [selectedUserId, setSelectedUserId] = useState('U101')
  const [profileData, setProfileData] = useState(null)
  const [popularRecs, setPopularRecs] = useState([])
  const [personalizedRecs, setPersonalizedRecs] = useState([])
  const [allMovies, setAllMovies] = useState([])
  const [selectedBrowseGenre, setSelectedBrowseGenre] = useState('All genres')
  const [preferences, setPreferences] = useState({})
  const [loading, setLoading] = useState(false)
  const [isExpanderOpen, setIsExpanderOpen] = useState(false)

  // Interaction form state
  const [targetMovie, setTargetMovie] = useState('')
  const [watchPct, setWatchPct] = useState(95)
  const [rating, setRating] = useState(4.5)
  const [formSubmitting, setFormSubmitting] = useState(false)
  const [feedback, setFeedback] = useState(null)

  // Fetch initial users list, popular feed, and all movies
  useEffect(() => {
    api
      .dbUsers()
      .then((res) => {
        setUsers(res.rows || [])
      })
      .catch(console.error)

    api
      .popularFeed(10)
      .then((res) => setPopularRecs(res.feed || []))
      .catch(console.error)

    api
      .dbMovies()
      .then((res) => setAllMovies(res.rows || []))
      .catch(console.error)
  }, [])

  // Load subscriber profile, preferences, and personalized recommendations
  const loadUserData = useCallback((uid) => {
    if (!uid) return
    setLoading(true)
    Promise.all([
      api.userProfile(uid),
      api.personalizedFeed(uid, 5, 0.6, 10),
      api.userPreferences ? api.userPreferences(uid).catch(() => ({ preferences: {} })) : Promise.resolve({ preferences: {} })
    ])
      .then(([prof, recs, prefRes]) => {
        setProfileData(prof)
        setPersonalizedRecs(recs.recommendations || [])
        setPreferences(prefRes.preferences || {})
        if (prof.unwatched && prof.unwatched.length > 0) {
          setTargetMovie(prof.unwatched[0].movie_id)
        } else {
          setTargetMovie('')
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleTogglePreference = async (movieId, action) => {
    try {
      const res = await api.setUserPreference(selectedUserId, movieId, action)
      setPreferences((prev) => {
        const next = { ...prev }
        if (!res.preference) {
          delete next[movieId]
        } else {
          next[movieId] = res.preference
        }
        return next
      })
      // Reload recommendations to reflect new preference signals
      const recs = await api.personalizedFeed(selectedUserId, 5, 0.6, 10)
      setPersonalizedRecs(recs.recommendations || [])
    } catch (err) {
      console.error('Failed to set preference:', err)
    }
  }

  useEffect(() => {
    loadUserData(selectedUserId)
  }, [selectedUserId, loadUserData])

  const handleRecordInteraction = async (e) => {
    e.preventDefault()
    if (!targetMovie) return
    setFormSubmitting(true)
    setFeedback(null)

    try {
      const res = await api.recordInteraction(selectedUserId, targetMovie, watchPct, rating)
      setFeedback({
        type: 'success',
        text: `Interaction ${res.history_id} was committed. The ranking engine has refreshed.`,
      })
      // Reload user data to reflect new interaction
      loadUserData(selectedUserId)
    } catch (err) {
      setFeedback({ type: 'error', text: err.message || 'Failed to record interaction' })
    } finally {
      setFormSubmitting(false)
    }
  }

  const subscriber = profileData?.profile

  const genres = ['All genres', ...Array.from(new Set(allMovies.flatMap((m) => {
    if (!m.genres) return []
    return Array.isArray(m.genres) ? m.genres : m.genres.split(',').map((g) => g.trim())
  }))).sort()]

  const filteredBrowseMovies = selectedBrowseGenre === 'All genres'
    ? allMovies
    : allMovies.filter((m) => {
        const glist = Array.isArray(m.genres) ? m.genres : (m.genres ? m.genres.split(',').map(g => g.trim()) : [])
        return glist.includes(selectedBrowseGenre)
      })

  return (
    <div className="studio-page">
      <div className="brandline">
        <span className="brand-mark">SG</span>
        <span>StreamGlass</span>
        <span className="brand-divider"></span>
        <span>Live studio</span>
      </div>

      <header className="page-header">
        <div className="eyebrow">Recommendation, side by side</div>
        <h1 className="page-title">
          See the cost of popularity-only ranking—and the benefit of personal context.
        </h1>
        <p className="page-desc">
          Select an active subscriber to compare the static platform feed with the StreamGlass
          hybrid feed from the same database.
        </p>
      </header>

      {/* Subscriber selector */}
      <div style={{ marginBottom: '16px' }}>
        <label htmlFor="active-subscriber-select" className="form-label">Active subscriber</label>
        <select
          id="active-subscriber-select"
          value={selectedUserId}
          onChange={(e) => setSelectedUserId(e.target.value)}
          className="select-input"
        >
          {users.map((u) => (
            <option key={u.user_id} value={u.user_id}>
              {u.name} · {u.primary_language} · {u.persona_desc?.slice(0, 44)}…
            </option>
          ))}
        </select>
      </div>

      {/* Profile Card */}
      {subscriber && (
        <section className="profile-card" style={{ marginBottom: '28px' }}>
          <div>
            <div className="profile-title">
              {subscriber.name}{' '}
              <span style={{ color: '#86868b', fontWeight: 500, fontSize: '0.83rem' }}>
                · {subscriber.user_id} · {subscriber.age}
              </span>
            </div>
            <div className="profile-copy">{subscriber.persona_desc}</div>
          </div>
          <div className="chip-row">
            <span className="chip chip-blue">{subscriber.primary_language}</span>
            <span className="chip">
              {subscriber.secondary_language || 'No secondary language'}
            </span>
            {Array.isArray(subscriber.preferred_genres) &&
              subscriber.preferred_genres.map((g) => (
                <span key={g} className="chip">
                  {g}
                </span>
              ))}
            <span className="chip">{profileData?.history_count ?? 0} watched</span>
          </div>
        </section>
      )}

      {/* Feeds side-by-side */}
      <div className="grid-2" style={{ marginBottom: '32px' }}>
        {/* Popular now (Baseline) */}
        <section className="feed-column">
          <div className="feed-head">
            <h2>Popular now</h2>
            <span>STATIC BASELINE</span>
          </div>
          <p className="feed-copy">
            The same ordering is delivered to every subscriber, regardless of language or prior
            viewing.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {popularRecs.map((item) => (
              <TitleCard
                key={item.movie_id}
                item={item}
                personalized={false}
                primaryLanguage={subscriber?.primary_language}
                secondaryLanguage={subscriber?.secondary_language}
                preference={preferences[item.movie_id]}
                onLike={(id) => handleTogglePreference(id, 'like')}
                onDislike={(id) => handleTogglePreference(id, 'dislike')}
              />
            ))}
          </div>
        </section>

        {/* StreamGlass (Personalized) */}
        <section className="feed-column">
          <div className="feed-head">
            <h2>For this subscriber</h2>
            <span>STREAMGLASS</span>
          </div>
          <p className="feed-copy">
            Hybrid ranking uses observed ratings, co-watch topology, language affinity, and preferred
            genres.
          </p>
          {loading ? (
            <div className="spinner" />
          ) : personalizedRecs.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {personalizedRecs.map((item) => (
                <TitleCard
                  key={item.movie_id}
                  item={item}
                  personalized={true}
                  preference={preferences[item.movie_id]}
                  onLike={(id) => handleTogglePreference(id, 'like')}
                  onDislike={(id) => handleTogglePreference(id, 'dislike')}
                />
              ))}
            </div>
          ) : (
            <div className="alert alert-info">
              This subscriber has no remaining unwatched titles to recommend.
            </div>
          )}
        </section>
      </div>

      {/* Browse All Movies Section */}
      <section style={{ marginBottom: '32px' }}>
        <div className="feed-head" style={{ marginBottom: '8px' }}>
          <h2>Browse all movies</h2>
          <span>CATALOG</span>
        </div>
        <p className="feed-copy">
          Complete platform catalog with dynamic genre filtering.
        </p>

        {/* Genre filter pills */}
        <div className="chip-row" style={{ marginBottom: '16px', gap: '8px' }}>
          {genres.map((g) => (
            <button
              key={g}
              type="button"
              className={`chip ${selectedBrowseGenre === g ? 'chip-blue' : ''}`}
              style={{
                cursor: 'pointer',
                border: 'none',
                fontWeight: selectedBrowseGenre === g ? 600 : 500
              }}
              onClick={() => setSelectedBrowseGenre(g)}
            >
              {g}
            </button>
          ))}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
          {filteredBrowseMovies.map((movie) => (
            <TitleCard
              key={movie.movie_id}
              item={{
                ...movie,
                why_recommended: `Catalog Title · ${movie.language}`
              }}
              personalized={false}
              primaryLanguage={subscriber?.primary_language}
              secondaryLanguage={subscriber?.secondary_language}
              preference={preferences[movie.movie_id]}
              onLike={(id) => handleTogglePreference(id, 'like')}
              onDislike={(id) => handleTogglePreference(id, 'dislike')}
            />
          ))}
        </div>
      </section>

      {/* Interaction Recording Form */}
      <div className="section-heading">
        <div>
          <h2>Record a viewing event</h2>
          <p>Commit a real interaction, then immediately refresh the recommendation engine.</p>
        </div>
      </div>

      <div className="expander">
        <button
          type="button"
          className="expander-head"
          onClick={() => setIsExpanderOpen((prev) => !prev)}
        >
          <span>Watch and rate a title</span>
          <span>{isExpanderOpen ? '▲' : '▼'}</span>
        </button>

        {isExpanderOpen && (
          <div className="expander-body">
            {profileData?.unwatched && profileData.unwatched.length === 0 ? (
              <div className="alert alert-success">
                This subscriber has rated every title in the catalog.
              </div>
            ) : (
              <form onSubmit={handleRecordInteraction}>
                <div className="form-grid-3">
                  <div>
                    <label htmlFor="unwatched-title-select" className="form-label">Title</label>
                    <select
                      id="unwatched-title-select"
                      value={targetMovie}
                      onChange={(e) => setTargetMovie(e.target.value)}
                      className="select-input"
                      required
                    >
                      {profileData?.unwatched?.map((m) => (
                        <option key={m.movie_id} value={m.movie_id}>
                          {m.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        marginBottom: '6px',
                      }}
                    >
                      <label htmlFor="watch-completion-slider" className="form-label">Completion</label>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{watchPct}%</span>
                    </div>
                    <input
                      id="watch-completion-slider"
                      type="range"
                      min="10"
                      max="100"
                      step="5"
                      value={watchPct}
                      onChange={(e) => setWatchPct(parseFloat(e.target.value))}
                      style={{ width: '100%', accentColor: 'var(--blue)' }}
                    />
                  </div>

                  <div>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        marginBottom: '6px',
                      }}
                    >
                      <label htmlFor="user-rating-slider" className="form-label">Rating</label>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>
                        {rating.toFixed(1)} / 5
                      </span>
                    </div>
                    <input
                      id="user-rating-slider"
                      type="range"
                      min="1.0"
                      max="5.0"
                      step="0.5"
                      value={rating}
                      onChange={(e) => setRating(parseFloat(e.target.value))}
                      style={{ width: '100%', accentColor: 'var(--blue)' }}
                    />
                  </div>
                </div>

                <div style={{ marginTop: '16px' }}>
                  <button
                    type="submit"
                    className="btn-primary"
                    disabled={formSubmitting || !targetMovie}
                  >
                    {formSubmitting ? 'Recording…' : 'Record interaction'}
                  </button>
                </div>

                {feedback && (
                  <div
                    className={`alert ${
                      feedback.type === 'success' ? 'alert-success' : 'alert-warn'
                    }`}
                  >
                    {feedback.text}
                  </div>
                )}
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
