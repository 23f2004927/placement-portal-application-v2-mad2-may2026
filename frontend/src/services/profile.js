import api from './api'

// Two endpoints rather than one branching on role — the role is in the URL, so
// it can never be spoofed from the body.
export const fetchStudentProfile = () => api.get('/student/profile').then((r) => r.data)
export const saveStudentProfile = (payload) =>
  api.patch('/student/profile', payload).then((r) => r.data)

export const fetchCompanyProfile = () => api.get('/company/profile').then((r) => r.data)
export const saveCompanyProfile = (payload) =>
  api.patch('/company/profile', payload).then((r) => r.data)
