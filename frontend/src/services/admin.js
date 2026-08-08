import api from './api'

export async function fetchCompanies() {
  const res = await api.get('/admin/companies')
  return res.data // { items, capabilities }
}

// Accepts { accountStatus } and/or { blackListed }.
export async function moderateCompany(id, payload) {
  const res = await api.patch(`/admin/companies/${id}`, payload)
  return res.data
}

export async function fetchStudents() {
  const res = await api.get('/admin/students')
  return res.data // { items, capabilities }
}

export async function moderateStudent(id, payload) {
  const res = await api.patch(`/admin/students/${id}`, payload)
  return res.data
}
