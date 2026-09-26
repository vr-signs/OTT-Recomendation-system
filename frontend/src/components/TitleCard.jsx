const ACCENT_PALETTE = [
  '#0071e3','#248a3d','#b25000','#5c5ce2','#86357a','#d29652',
]

function accent(movieId) {
  const n = parseInt((movieId || 'M1').replace(/\D/g, ''), 10) || 0
  return ACCENT_PALETTE[n % ACCENT_PALETTE.length]
}

export default function TitleCard({ item, personalized = false, primaryLanguage, secondaryLanguage }) {
  const color = item.accent_color || accent(item.movie_id)
  const isMatch = item.language === primaryLanguage
  const isSecondary = !isMatch && item.language === secondaryLanguage

  const statusLabel = isMatch ? 'Primary lang' : isSecondary ? 'Secondary lang' : null

  const genre = item.primary_genre || '—'
  const language = item.language || '—'

  return (
    <article className="title-card">
      <div className="title-top">
        <div className="poster-swatch" style={{ background: color }}>
          <span className="poster-id">{item.movie_id}</span>
          <span className="poster-year">{item.release_year}</span>
        </div>
        <div className="title-detail">
          <div className="title-meta">
            <span>{language} · {genre}</span>
            {statusLabel && <span className="title-status">{statusLabel}</span>}
          </div>
          <div className="title-name">{item.title}</div>
          <p>{item.director} · {item.duration_min} min</p>
        </div>
      </div>
      <div className="card-foot">
        {personalized
          ? (item.why_recommended || 'Hybrid recommendation')
          : (item.why_recommended || `Popularity ${item.popularity_score}`)}
      </div>
    </article>
  )
}
