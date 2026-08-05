import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import { useAuth } from '@/stores/auth'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },

    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    { path: '/login',  name: 'login',  component: LoginView,  meta: { guestOnly: true } },
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
