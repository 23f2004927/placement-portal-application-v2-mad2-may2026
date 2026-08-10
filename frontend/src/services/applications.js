import api from './api'

// One endpoint, scoped three ways by JWT claim — the caller never says who it is.
export async function fetchApplications(params) {
  const res = await api.get('/applications', { params })
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

// decision is 'accept' (-> placed) or 'decline' (-> declined).
export async function respondToOffer(id, decision) {
  const res = await api.post(`/applications/${id}/respond`, { decision })
  return res.data
}

export async function updateApplication(id, payload) {
  const res = await api.patch(`/applications/${id}`, payload)
  return res.data
}

export async function issueOfferLetter(id, joiningDate) {
  const res = await api.post(`/applications/${id}/offer-letter`, { joiningDate })
  return res.data
}

/*
  Fetched as a blob rather than linked directly: the endpoint needs the
  Authorization header, and a plain <a href> cannot send one.
*/
export async function downloadOfferLetter(id) {
  const res = await api.get(`/applications/${id}/offer-letter`, { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const link = document.createElement('a')
  link.href = url
  link.download = `offer-letter-${id}.html`
  link.click()
  URL.revokeObjectURL(url)
}
