<script setup>
import { ref, computed, onMounted } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import { fetchStats } from '@/services/stats'

const stats = ref(null)
const error = ref('')

onMounted(async () => {
  try {
    stats.value = await fetchStats('student')
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load the dashboard totals.'
  }
})

const cards = computed(() => [
  { label: 'Open drives', value: stats.value?.openDrives, hint: 'You are eligible for' },
  { label: 'Applications', value: stats.value?.applications },
  { label: 'Shortlisted', value: stats.value?.shortlisted },
  { label: 'Interviews', value: stats.value?.interviews, hint: 'Scheduled' },
])
</script>

<template>
  <div>
    <BAlert v-if="error" :model-value="true" variant="danger">{{ error }}</BAlert>

    <div class="stat-grid">
      <StatCard v-for="c in cards" :key="c.label" v-bind="c" />
    </div>
  </div>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
</style>
