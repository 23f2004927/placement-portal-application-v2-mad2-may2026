import api from './api'

// role is 'admin' or 'company' — same shape either way, scoped server-side.
export async function fetchAnalytics(role) {
  const res = await api.get(`/${role}/analytics`)
  return res.data
}

// No auth header needed, but going through `api` keeps the base URL in one place.
export async function fetchPublicStats() {
  const res = await api.get('/public/stats')
  return res.data
}
