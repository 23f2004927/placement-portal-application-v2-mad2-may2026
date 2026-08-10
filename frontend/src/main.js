import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createBootstrap } from 'bootstrap-vue-next'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'
import './assets/main.css'

import App from './App.vue'
import router from './router'
import api from './services/api'
import { useAuth } from './stores/auth'
import { vTrim } from './directives/trim'

const app = createApp(App)

app.use(createPinia())
app.use(createBootstrap())
app.use(router)

// Used as v-trim on a <form>; see directives/trim.js for why it lives there
// and not on each input.
app.directive('trim', vTrim)

/*
  Registered here rather than in services/api.js: that module is imported by
  services/auth.js, which is imported by LoginView, which the router imports —
  so pulling the router into api.js would close an import cycle. Both objects
  already exist at this point, and Pinia is active.

  401/422 = the identity is no good  → clear the session.
  403     = valid session, wrong door → send them home, do NOT sign them out.
  /auth/* is exempt: a failed login is a form error, not a session problem.
*/
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const url = error.config?.url ?? ''

    if (!url.startsWith('/auth/')) {
      const auth = useAuth()
      if (status === 401 || status === 422) {
        auth.logout()
        router.push('/login')
      } else if (status === 403) {
        router.push(auth.homeRoute)
      }
    }

    return Promise.reject(error)
  },
)

/*
  PWA. Registered after load so it never competes with the first paint, and only
  in a production build — a service worker caching assets in front of Vite's dev
  server makes hot reload behave unpredictably.
*/
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      /* offline support is a bonus; never block the app on it */
    })
  })
}

app.mount('#app')
