/*
  `short` is rendered when the sidebar is collapsed, so it must stay unique
  within a role.
*/
export const navByRole = {
  company: [
    { to: { name: 'company-analytics' }, label: 'Overview', short: 'OV' },
    { to: { name: 'company-drives' }, label: 'Drives', short: 'DR' },
    { to: { name: 'company-applicants' }, label: 'Applicants', short: 'AP' },
    { to: { name: 'company-ats' }, label: 'Screener', short: 'SC' },
  ],

  student: [
    { to: { name: 'student-analytics' }, label: 'Overview', short: 'OV' },
    { to: { name: 'student-drives' }, label: 'Drives', short: 'DR' },
    { to: { name: 'student-applications' }, label: 'Applications', short: 'AP' },
    { to: { name: 'student-ats' }, label: 'Screener', short: 'SC' },
  ],

  admin: [
    { to: { name: 'admin-analytics' }, label: 'Overview', short: 'OV' },
    { to: { name: 'admin-companies' }, label: 'Companies', short: 'CO' },
    { to: { name: 'admin-drives' }, label: 'Drives', short: 'DR' },
    { to: { name: 'admin-students' }, label: 'Students', short: 'ST' },
    { to: { name: 'admin-applications' }, label: 'Applications', short: 'AP' },
  ],
}
