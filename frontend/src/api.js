/**
 * StreamGlass — all API calls go through this module.
 * Vite proxies /api/* → http://127.0.0.1:8000 in dev.
 * In production, /api/* is handled by the Vercel Python function.
 */

const BASE = ''  // same origin — Vite proxy handles it in dev

async function get(path) {
  const res = await fetch(BASE + path)
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`)
  return res.json()
}

async function post(path, body) {
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `API ${path} → ${res.status}`)
  }
  return res.json()
}

export const api = {
  health: () => get('/api/health'),
  dbMetrics: () => get('/api/db/metrics'),
  dbUsers: () => get('/api/db/users'),
  dbMovies: () => get('/api/db/movies'),
  dbWatchHistory: () => get('/api/db/watch_history'),

  courseworkDmgt: () => get('/api/coursework/dmgt'),
  courseworkAdsa: () => get('/api/coursework/adsa'),

  popularFeed: (limit = 6) => get(`/api/recommendations/popular?limit=${limit}`),
  personalizedFeed: (userId, k = 5, alpha = 0.6, limit = 6) =>
    get(`/api/recommendations/personalized/${userId}?k=${k}&alpha=${alpha}&limit=${limit}`),

  userProfile: (userId) => get(`/api/users/${userId}/profile`),

  recordInteraction: (userId, movieId, watchPct, rating) =>
    post('/api/interactions', {
      user_id: userId,
      movie_id: movieId,
      watch_percentage: watchPct,
      rating,
    }),

  modelSimilarity: (movieA, movieB) =>
    get(`/api/model/similarity?movie_a=${movieA}&movie_b=${movieB}`),
  modelNetwork: () => get('/api/model/network'),

  analyticsPartitions: () => get('/api/analytics/partitions'),
  analyticsCentrality: () => get('/api/analytics/centrality'),
  analyticsMatrix: () => get('/api/analytics/matrix'),
}
