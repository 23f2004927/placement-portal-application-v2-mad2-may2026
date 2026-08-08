import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchMe } from '@/services/auth'

const ROLE_HOME = {
  admin: '/admin',
  company: '/company',
  student: '/student',
}

export const useAuth = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const role = ref(localStorage.getItem('role'))
  const userName = ref(localStorage.getItem('userName'))
  const accountStatus = ref(localStorage.getItem('accountStatus'))
  const isAuthenticated = computed(() => !!token.value)

  // Single source of truth for "where does this user belong": read by the router
  // guard, the 403 interceptor, LoginView and PublicNavbar.
  const homeRoute = computed(() => ROLE_HOME[role.value] ?? '/login')

  // Drives the requiresApproved route guard and the pending banner. A UI hint
  // only — like `role` it lives in localStorage and is therefore editable, so
  // every write endpoint re-reads the real value from the database.
  const isApproved = computed(() => accountStatus.value === 'approved')

  function setSession(newToken, newRole, newUserName, newAccountStatus) {
    token.value = newToken
    role.value = newRole
    userName.value = newUserName
    accountStatus.value = newAccountStatus
    localStorage.setItem('token', newToken)
    localStorage.setItem('role', newRole)
    localStorage.setItem('userName', newUserName)
    localStorage.setItem('accountStatus', newAccountStatus)
  }

  /*
    Pulls fresh role and accountStatus from the server, because JWT claims are
    frozen at issue time. Failures are swallowed on purpose: a dead session is
    already handled by the 401 interceptor, and any other error should leave the
    cached values alone rather than log the user out.
  */
  async function refresh() {
    try {
      const me = await fetchMe()
      role.value = me.role
      accountStatus.value = me.accountStatus
      localStorage.setItem('role', me.role)
      localStorage.setItem('accountStatus', me.accountStatus)
    } catch {
      /* keep whatever was cached at login */
    }
  }

  function logout() {
    token.value = null
    role.value = null
    userName.value = null
    accountStatus.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('userName')
    localStorage.removeItem('accountStatus')
  }

  return {
    token,
    role,
    userName,
    accountStatus,
    isAuthenticated,
    isApproved,
    homeRoute,
    setSession,
    refresh,
    logout,
  }
})
