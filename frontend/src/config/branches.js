/*
  Mirrors the `Branch` enum in backend/app/models/student.py.

  `value` MUST match the Python enum's .value string exactly — the backend does
  Branch(payload["branch"]) and a mismatch raises rather than validating.
  If this list and the model ever drift, replace it with a GET /api/meta/branches
  endpoint so the enum stays the single source of truth.

  Shaped as { value, text } so it feeds <BFormSelect :options> directly.
*/

export const branches = [
  { value: 'computer', text: 'Computer' },
  { value: 'information_technology', text: 'Information Technology' },
  { value: 'electronics', text: 'Electronics' },
  { value: 'electronics_and_telecommunication', text: 'Electronics & Telecommunication' },
  { value: 'electrical', text: 'Electrical' },
  { value: 'mechanical', text: 'Mechanical' },
  { value: 'civil', text: 'Civil' },
  { value: 'chemical', text: 'Chemical' },
  { value: 'ai_ml', text: 'AI & ML' },
  { value: 'data_science', text: 'Data Science' },
  { value: 'robotics', text: 'Robotics' },
  { value: 'biomedical', text: 'Biomedical' },
  { value: 'aerospace', text: 'Aerospace' },
  { value: 'automobile', text: 'Automobile' },
  { value: 'industrial', text: 'Industrial' },
  { value: 'mining', text: 'Mining' },
  { value: 'metallurgy', text: 'Metallurgy' },
  { value: 'environmental', text: 'Environmental' },
]

/*
  ASSUMPTION — confirm before the backend lands:
    yearStudy  (String(3))  = current year of study, "1".."5"
    gradeYear  (Integer)    = expected year of graduation, e.g. 2027
*/
export const yearsOfStudy = [
  { value: '1', text: '1st Year' },
  { value: '2', text: '2nd Year' },
  { value: '3', text: '3rd Year' },
  { value: '4', text: '4th Year' },
  { value: '5', text: '5th Year' },
]
