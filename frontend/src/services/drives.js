import api from './api'

// One endpoint, scoped three ways by JWT claim.
export async function fetchDrives(params) {
  const res = await api.get('/drives', { params })
  return res.data // { items, capabilities }
}

export async function fetchDrive(id) {
  const res = await api.get(`/drives/${id}`)
  return res.data
}

export async function createDrive(payload) {
  const res = await api.post('/drives', payload)
  return res.data
}

export async function updateDrive(id, payload) {
  const res = await api.patch(`/drives/${id}`, payload)
  return res.data
}
