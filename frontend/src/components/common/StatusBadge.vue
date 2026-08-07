<script setup>
import { computed } from 'vue'

/*
  BBadge with a Bootstrap variant, rather than a hand-rolled chip.
  Tone is grouped by meaning, not by enum, so the same colour language reads
  consistently across ApplicationStatus, DriveStatus and AccountStatus.
*/
const VARIANTS = {
  applied: 'secondary',
  pending: 'secondary',
  reviewed: 'primary',
  shortlisted: 'primary',
  interview: 'primary',
  offer: 'success',
  approved: 'success',
  placed: 'success',
  rejected: 'danger',
  revoked: 'light',
  closed: 'light',
}

// 'revoked' is the enum value; 'withdrawn' is what a person calls it.
const LABELS = { revoked: 'withdrawn' }

const props = defineProps({
  status: { type: String, default: '' },
})

const variant = computed(() => VARIANTS[props.status] ?? 'secondary')
const label = computed(() => LABELS[props.status] ?? props.status.replace(/_/g, ' '))
</script>

<template>
  <BBadge :variant="variant" class="status-badge">{{ label }}</BBadge>
</template>

<style scoped>
.status-badge {
  padding: 4px 10px;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  white-space: nowrap;
}
</style>
