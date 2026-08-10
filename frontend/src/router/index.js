import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import LandingView from '@/views/LandingView.vue'
import DashboardLayout from '@/components/layout/DashboardLayout.vue'
import { useAuth } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: LandingView },
    { path: '/login', name: 'login', component: LoginView, meta: { guestOnly: true } },
    {
      path: '/register/:role?',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guestOnly: true },
    },

    {
      path: '/company',
      component: DashboardLayout,
      meta: { requiresAuth: true, role: 'company' },
      children: [
        {
          path: '',
          name: 'company-analytics',
          component: () => import('@/views/company/OverviewView.vue'),
          meta: { title: 'Overview', subtitle: 'Your hiring activity at a glance' },
        },
        {
          path: 'drives',
          name: 'company-drives',
          component: () => import('@/views/company/DrivesView.vue'),
          meta: { title: 'Drives', subtitle: 'Roles you have posted' },
        },
        {
          path: 'applicants',
          name: 'company-applicants',
          component: () => import('@/views/company/ApplicantsView.vue'),
          meta: { title: 'Applicants', subtitle: 'Candidates who applied to your drives' },
        },
        {
          path: 'drives/new',
          name: 'company-drive-new',
          component: () => import('@/views/company/DriveFormView.vue'),
          // requiresApproved keeps a company awaiting review out of the form.
          // Cosmetic: POST /api/drives carries role_required(approved=True).
          meta: {
            title: 'New drive',
            subtitle: 'Post a role for students to apply to',
            requiresApproved: true,
          },
        },
        {
          path: 'drives/:id/edit',
          name: 'company-drive-edit',
          component: () => import('@/views/company/DriveFormView.vue'),
          meta: {
            title: 'Edit drive',
            subtitle: 'Update this posting',
            requiresApproved: true,
          },
        },
        {
          path: 'screener',
          name: 'company-ats',
          component: () => import('@/views/shared/AtsView.vue'),
          meta: { title: 'Resume screener', subtitle: 'Match a resume against a drive' },
        },
        {
          path: 'profile',
          name: 'company-profile',
          component: () => import('@/views/company/ProfileView.vue'),
          meta: { title: 'Profile', subtitle: 'Your account details' },
        },
      ],
    },

    {
      path: '/student',
      component: DashboardLayout,
      meta: { requiresAuth: true, role: 'student' },
      children: [
        {
          path: '',
          name: 'student-analytics',
          component: () => import('@/views/student/OverviewView.vue'),
          meta: { title: 'Overview', subtitle: 'Where your applications stand' },
        },
        {
          path: 'drives',
          name: 'student-drives',
          component: () => import('@/views/student/DrivesView.vue'),
          meta: { title: 'Drives', subtitle: 'Open roles you are eligible for' },
        },
        {
          path: 'applications',
          name: 'student-applications',
          component: () => import('@/views/student/ApplicationsView.vue'),
          meta: { title: 'Applications', subtitle: 'Everything you have applied to' },
        },
        {
          path: 'screener',
          name: 'student-ats',
          component: () => import('@/views/shared/AtsView.vue'),
          meta: { title: 'Resume screener', subtitle: 'Check your resume against a drive' },
        },
        {
          path: 'profile',
          name: 'student-profile',
          component: () => import('@/views/student/ProfileView.vue'),
          meta: { title: 'Profile', subtitle: 'Your account details' },
        },
      ],
    },

    {
      path: '/admin',
      component: DashboardLayout,
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        {
          path: '',
          name: 'admin-analytics',
          component: () => import('@/views/admin/OverviewView.vue'),
          meta: { title: 'Overview', subtitle: 'Portal-wide totals' },
        },
        {
          path: 'companies',
          name: 'admin-companies',
          component: () => import('@/views/admin/CompaniesView.vue'),
          meta: { title: 'Companies', subtitle: 'Approve registrations and manage accounts' },
        },
        {
          path: 'drives',
          name: 'admin-drives',
          component: () => import('@/views/admin/DrivesView.vue'),
          meta: { title: 'Drives', subtitle: 'Approve postings before students see them' },
        },
        {
          path: 'students',
          name: 'admin-students',
          component: () => import('@/views/admin/StudentsView.vue'),
          meta: { title: 'Students', subtitle: 'Registered candidates' },
        },
        {
          path: 'applications',
          name: 'admin-applications',
          component: () => import('@/views/admin/ApplicationsView.vue'),
          meta: { title: 'Applications', subtitle: 'Every application in the portal' },
        },
        {
          path: 'profile',
          name: 'admin-profile',
          component: () => import('@/views/admin/ProfileView.vue'),
          meta: { title: 'Profile', subtitle: 'Your account details' },
        },
      ],
    },

    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuth() // must be INSIDE the guard — Pinia isn't active at module scope

  // A tampered or unrecognised role would make homeRoute resolve to /login, which
  // is guestOnly, which redirects back to homeRoute. Clearing the session first
  // breaks that loop.
  if (auth.isAuthenticated && auth.homeRoute === '/login') {
    auth.logout()
    return '/login'
  }

  if (to.meta.guestOnly && auth.isAuthenticated) return auth.homeRoute

  if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login'

  if (to.meta.role && auth.role !== to.meta.role) return auth.homeRoute

  // Synchronous on purpose. Gating on an awaited fetch inside the component
  // would let the view mount and render before the answer arrived.
  if (to.meta.requiresApproved && !auth.isApproved) return auth.homeRoute
})

export default router
