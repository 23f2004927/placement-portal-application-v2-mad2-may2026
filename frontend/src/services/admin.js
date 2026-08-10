import api from './api'

export async function fetchCompanies(params) {
  const res = await api.get('/admin/companies', { params })
  return res.data // { items, capabilities }
}

// Accepts { accountStatus } and/or { blackListed }.
export async function moderateCompany(id, payload) {
  const res = await api.patch(`/admin/companies/${id}`, payload)
  return res.data
}

// The student-facing recruiter directory. A different endpoint from the admin
// register above, not the same one filtered — it carries no account status.
export async function fetchCompanyDirectory(params) {
  const res = await api.get('/companies', { params })
  return res.data
}

export async function fetchStudents(params) {
  const res = await api.get('/admin/students', { params })
  return res.data // { items, capabilities }
}

export async function moderateStudent(id, payload) {
  const res = await api.patch(`/admin/students/${id}`, payload)
  return res.data
}
