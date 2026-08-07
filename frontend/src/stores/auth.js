import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

const ROLE_HOME = {
  admin: '/admin',
  company: '/company',
  student: '/student',
}

export const useAuth = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const role = ref(localStorage.getItem('role'))
  const userName = ref(localStorage.getItem('userName'))
  const isAuthenticated = computed(() => !!token.value)

  // Single source of truth for "where does this user belong": read by the router
  // guard, the 403 interceptor, LoginView and PublicNavbar.
  const homeRoute = computed(() => ROLE_HOME[role.value] ?? '/login')

  function setSession(newToken, newRole, newUserName) {
    token.value = newToken
    role.value = newRole
    userName.value = newUserName
    localStorage.setItem('token', newToken)
    localStorage.setItem('role', newRole)
    localStorage.setItem('userName', newUserName)
  }

  function logout() {
    token.value = null
    role.value = null
    userName.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('userName')
  }

  return { token, role, userName, isAuthenticated, homeRoute, setSession, logout }
})
