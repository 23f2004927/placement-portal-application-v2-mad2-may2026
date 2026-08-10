/*
  The API sends full ISO strings. A table cell wants a date, not a timestamp —
  "2026-08-13T15:57:23.454394" is noise in a 130px column.
*/
const DATE = { day: '2-digit', month: 'short', year: 'numeric' }
const DATE_TIME = { ...DATE, hour: '2-digit', minute: '2-digit' }

export function formatDate(iso) {
  if (!iso) return '—'
  const value = new Date(iso)
  return Number.isNaN(value.getTime()) ? '—' : value.toLocaleDateString('en-GB', DATE)
}

// For the one case where the time is the point: a scheduled interview.
export function formatDateTime(iso) {
  if (!iso) return '—'
  const value = new Date(iso)
  return Number.isNaN(value.getTime()) ? '—' : value.toLocaleString('en-GB', DATE_TIME)
}
