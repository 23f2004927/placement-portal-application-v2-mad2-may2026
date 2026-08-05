<script setup>
import { useAuth } from '@/stores/auth'

import { useRouter } from 'vue-router'
const auth = useAuth()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="login-page">
    <BCard>
      <BButton @click="handleLogout">LOGOUT</BButton>
      <h2 class="text-center fw-bold text-uppercase mb-1">Logged In</h2>
      <p>you are {{ auth.userName }} : {{ auth.role }}</p>
    </BCard>
  </div>
</template>
