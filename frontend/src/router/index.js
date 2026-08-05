import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import { useAuth } from '@/stores/auth'
import LandingView from '@/views/LandingView.vue'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: LandingView,
    },
    { path: '/login', name: 'login', component: LoginView, meta: { guestOnly: true } },
    {
      path: '/register/:role?',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guestOnly: true },
    },
    { path: '/logged', name: 'logged', component: () => import('../views/LoggedView.vue'), meta: { requiresAuth: true } },
  ],
})

router.beforeEach((to) => {
  const auth = useAuth()          // ← must be INSIDE the guard

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return '/logged'              // already logged in → bounce off /login
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/login'               // not logged in → bounce to login
  }
})
export default router
