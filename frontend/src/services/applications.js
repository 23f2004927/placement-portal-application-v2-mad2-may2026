import api from './api'

// One endpoint, scoped three ways by JWT claim — the caller never says who it is.
export async function fetchApplications() {
  const res = await api.get('/applications')
  return res.data // { items, capabilities }
}

export async function applyToDrive(driveId) {
  const res = await api.post('/applications', { driveId })
  return res.data
}

export async function revokeApplication(id) {
  const res = await api.post(`/applications/${id}/revoke`)
  return res.data
}

export async function updateApplication(id, payload) {
  const res = await api.patch(`/applications/${id}`, payload)
  return res.data
}
