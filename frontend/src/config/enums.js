/*
  Mirrors the backend enums. Values MUST match each Python enum's `.value`
  exactly — the API compares against them directly.

  Same drift risk as config/branches.js: a GET /api/meta/enums endpoint is the
  proper long-term fix.
*/

export const applicationStatuses = [
  { value: 'applied', text: 'Applied' },
  { value: 'shortlisted', text: 'Shortlisted' },
  { value: 'interview', text: 'Interview' },
  { value: 'offer', text: 'Offer' },
  // 'rejected' is the company turning the student down; 'declined' is the
  // student turning the company down.
  { value: 'rejected', text: 'Rejected' },
  { value: 'declined', text: 'Declined' },
  { value: 'placed', text: 'Placed' },
  { value: 'revoked', text: 'Withdrawn' },
]

// Companies never receive withdrawn applications, so offering the filter would
// only ever return nothing. 'declined' stays — a company needs to see it.
export const companyVisibleStatuses = applicationStatuses.filter((s) => s.value !== 'revoked')

export const driveStatuses = [
  { value: 'pending', text: 'Pending' },
  { value: 'approved', text: 'Approved' },
  { value: 'closed', text: 'Closed' },
]

export const accountStatuses = [
  { value: 'pending', text: 'Pending' },
  { value: 'approved', text: 'Approved' },
  { value: 'rejected', text: 'Rejected' },
]

export const jobTypes = [
  { value: 'full_time', text: 'Full time' },
  { value: 'internship', text: 'Internship' },
  { value: 'ppo', text: 'PPO' },
]
