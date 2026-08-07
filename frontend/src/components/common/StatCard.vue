<script setup>
// BCard, so theme.css's global .card rules apply here for free.
defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: null },
  hint: { type: String, default: '' },
})
</script>

<template>
  <BCard class="stat-card" body-class="stat-body">
    <span class="stat-label">{{ label }}</span>
    <span class="stat-value">{{ value ?? '—' }}</span>
    <span v-if="hint" class="stat-hint">{{ hint }}</span>
  </BCard>
</template>

<style scoped>
.stat-card :deep(.stat-body) {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px;
}

.stat-label {
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 800;
  line-height: 1;
}

.stat-hint {
  color: var(--text-muted);
  font-size: 0.75rem;
}
</style>
