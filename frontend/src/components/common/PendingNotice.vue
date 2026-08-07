<script setup>
/*
  Marks a view whose backend endpoint does not exist yet. Grep for
  <PendingNotice to find every screen still waiting to be wired.
*/
defineProps({
  endpoint: { type: String, required: true },
})
</script>

<template>
  <div class="pending">
    <strong>Not wired yet</strong>
    <span>Waiting on <code>{{ endpoint }}</code></span>
  </div>
</template>

<style scoped>
.pending {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin-bottom: 24px;
  border: 1px dashed var(--border-strong);
  background: var(--surface-alt);
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.pending strong {
  color: var(--text);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

code {
  color: var(--primary);
}
</style>
