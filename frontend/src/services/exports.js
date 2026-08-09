import api from './api'

// 202 Accepted — the CSV does not exist yet, only a task id.
export async function startExport() {
  const res = await api.post('/exports/applications')
  return res.data // { taskId }
}

export async function exportState(taskId) {
  const res = await api.get(`/exports/${taskId}`)
  return res.data // { state, rows? }
}

export async function downloadExport(taskId) {
  const res = await api.get(`/exports/${taskId}/file`, { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const link = document.createElement('a')
  link.href = url
  link.download = 'my-applications.csv'
  link.click()
  URL.revokeObjectURL(url)
}
