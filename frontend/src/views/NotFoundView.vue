<script setup>
import { useAuth } from '@/stores/auth'

const auth = useAuth()
</script>

<template>
  <div class="notfound">
    <h1>404</h1>
    <p>That page doesn't exist.</p>
    <BButton :to="auth.isAuthenticated ? auth.homeRoute : '/'" variant="primary">
      {{ auth.isAuthenticated ? 'Back to dashboard' : 'Back to home' }}
    </BButton>
  </div>
</template>

<style scoped>
.notfound {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: var(--bg);
}

h1 {
  margin: 0;
  font-size: 4rem;
  font-weight: 800;
  color: var(--primary);
}

p {
  color: var(--text-muted);
  margin-bottom: 16px;
}
</style>
