import api from './api'
export async function login(userName, password) {
  const res = await api.post('/auth/login', { userName, password })
  return res.data   // { access_token, role }
}
