import {
  applicationStatuses,
  companyVisibleStatuses,
  driveStatuses,
  accountStatuses,
} from '@/config/enums'

/*
  Which filters the topbar shows, keyed by route name. A route absent from this
  map gets no filter bar. Once the API is wired these become query params rather
  than a client-side pass.
*/
export const filtersByRoute = {
  'company-drives': {
    search: 'Search title or skill',
    status: driveStatuses,
  },
  'company-applicants': {
    search: 'Search candidate or drive',
    status: companyVisibleStatuses,
  },

  'student-drives': {
    search: 'Search role, company or skill',
    applied: [
      { value: 'no', text: 'Not applied yet' },
      { value: 'yes', text: 'Already applied' },
    ],
    maxCgpa: 'Max CGPA asked',
  },
  'student-applications': {
    search: 'Search role or company',
    status: applicationStatuses,
  },
  'student-companies': {
    search: 'Search name, industry or location',
  },

  'admin-companies': {
    search: 'Search name or industry',
    status: accountStatuses,
  },
  'admin-drives': {
    search: 'Search role, company or skill',
    status: driveStatuses,
  },
  'admin-students': {
    search: 'Search name, roll or contact',
  },
  'admin-applications': {
    search: 'Search candidate, role or company',
    status: applicationStatuses,
  },
}
