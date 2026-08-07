<script setup>
import PendingNotice from '@/components/common/PendingNotice.vue'
import { useAuth } from '@/stores/auth'

const auth = useAuth()
</script>

<template>
  <div>
    <PendingNotice endpoint="GET /api/auth/me" />

    <div class="profile-card">
      <div class="field">
        <span class="field-label">Username</span>
        <span class="field-value">{{ auth.userName }}</span>
      </div>
      <div class="field">
        <span class="field-label">Role</span>
        <span class="field-value">{{ auth.role }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-card {
  max-width: 480px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.field {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
}

.field:last-child {
  border-bottom: 0;
}

.field-label {
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.field-value {
  font-size: 0.875rem;
  font-weight: 600;
}
</style>
