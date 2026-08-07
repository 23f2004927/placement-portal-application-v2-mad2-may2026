import api from './api'

export const fetchStats = (role) => api.get(`/${role}/stats`).then((r) => r.data)
