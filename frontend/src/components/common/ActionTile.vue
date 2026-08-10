<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

/*
  A queue, not a statistic. Separate from StatCard because the whole point is
  that it goes somewhere: the count is only useful next to the list that clears
  it, so the tile links to that list with the filter already applied.

  Zero is styled down rather than hidden — an empty queue is information, and a
  tile that disappears makes the row jump around between loads.
*/
const props = defineProps({
  label: { type: String, required: true },
  value: { type: Number, default: null },
  to: { type: Object, required: true },
  hint: { type: String, default: '' },
})

const isClear = computed(() => !props.value)
</script>

<template>
  <RouterLink :to="to" class="action-tile" :class="{ 'is-clear': isClear }">
    <span class="tile-label">{{ label }}</span>
    <span class="tile-value">{{ value ?? '—' }}</span>
    <span class="tile-hint">{{ isClear ? 'Nothing waiting' : hint || 'Review' }}</span>
  </RouterLink>
</template>

<style scoped>
.action-tile {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  text-decoration: none;
  transition:
    border-color 0.15s ease,
    background 0.15s ease;
}

.action-tile:hover {
  border-color: var(--primary);
  background: var(--primary-soft);
}

.tile-label {
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* Proportional figures: this is a standalone number, not a table column. */
.tile-value {
  font-size: 1.75rem;
  font-weight: 800;
  line-height: 1;
  color: var(--primary);
}

.is-clear .tile-value {
  color: var(--text-muted);
}

.tile-hint {
  color: var(--text-muted);
  font-size: 0.75rem;
}
</style>
