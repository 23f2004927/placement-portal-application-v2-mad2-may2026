import api from './api'

export async function fetchNotifications() {
  const res = await api.get('/notifications')
  return res.data // { items, unread }
}

export async function markAllRead() {
  const res = await api.post('/notifications/read')
  return res.data
}
