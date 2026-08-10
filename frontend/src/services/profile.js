import api from './api'

// Two endpoints rather than one branching on role — the role is in the URL, so
// it can never be spoofed from the body.
export const fetchStudentProfile = () => api.get('/student/profile').then((r) => r.data)
export const saveStudentProfile = (payload) =>
  api.patch('/student/profile', payload).then((r) => r.data)

/*
  FormData, and deliberately no Content-Type header: the browser has to write
  the multipart boundary itself, and setting the header by hand strips it, which
  leaves Flask seeing an empty form.
*/
export function uploadResume(file) {
  const body = new FormData()
  body.append('file', file)
  return api.post('/student/resume', body).then((r) => r.data)
}

export const deleteResume = () => api.delete('/student/resume').then((r) => r.data)

/*
  Fetched as a blob for the same reason the offer letter is: the endpoint needs
  the Authorization header and a plain <a href> cannot send one. Opened rather
  than downloaded — the response is inline PDF, so it lands in the browser's
  viewer instead of piling up in Downloads.

  The object URL is not revoked: the new tab is still reading from it.
*/
export async function openResume(studentId) {
  const res = await api.get(`/students/${studentId}/resume`, { responseType: 'blob' })
  window.open(URL.createObjectURL(res.data), '_blank')
}

export const fetchCompanyProfile = () => api.get('/company/profile').then((r) => r.data)
export const saveCompanyProfile = (payload) =>
  api.patch('/company/profile', payload).then((r) => r.data)
