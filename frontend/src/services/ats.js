import api from './api'

export async function screenResume(driveId, resumeText) {
  const res = await api.post('/ats/screen', { driveId, resumeText })
  return res.data // { driveTitle, score, matched, missing }
}
