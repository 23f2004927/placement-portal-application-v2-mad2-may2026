import api from './api'

export async function login(userName, password) {
  const res = await api.post('/auth/login', { userName, password })
  return res.data   // { access_token, role, userName }
}

/*
  Two endpoints rather than one, because the two paths differ in ways that make a
  merged handler awkward: different validation, different child table, and
  different landing state — students land APPROVED, companies land PENDING.

  The SPA still exposes them behind a single /register route; the URL structure of
  the frontend has no obligation to mirror the API's.
*/
export async function registerStudent(payload) {
  const res = await api.post('/auth/register/student', payload)
  return res.data
}

export async function registerCompany(payload) {
  const res = await api.post('/auth/register/company', payload)
  return res.data
}
