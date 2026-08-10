<script setup>
import { ref, computed, onMounted } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import ChartCard from '@/components/common/ChartCard.vue'
import { fetchStats } from '@/services/stats'
import { fetchAnalytics } from '@/services/analytics'

const stats = ref(null)
const analytics = ref(null)
const error = ref('')

onMounted(async () => {
  try {
    const [s, a] = await Promise.all([fetchStats('company'), fetchAnalytics('company')])
    stats.value = s
    analytics.value = a
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load the dashboard totals.'
  }
})

const cards = computed(() => [
  { label: 'Drives posted', value: stats.value?.drives, hint: 'Approved and pending' },
  { label: 'Applications', value: stats.value?.applications, hint: 'Across all drives' },
  { label: 'Shortlisted', value: stats.value?.shortlisted },
  { label: 'Offers made', value: stats.value?.offers },
])

const monthLabels = computed(() => analytics.value?.months ?? [])

const trendSeries = computed(() => [
  { label: 'Applications', data: analytics.value?.applications ?? [] },
  { label: 'Placements', data: analytics.value?.placements ?? [] },
])

const funnelLabels = computed(() => (analytics.value?.funnel ?? []).map((f) => f.stage))
const funnelSeries = computed(() => [
  { label: 'Candidates', data: (analytics.value?.funnel ?? []).map((f) => f.count) },
])
</script>

<template>
  <div>
    <BAlert v-if="error" :model-value="true" variant="danger">{{ error }}</BAlert>

    <div class="stat-grid">
      <StatCard v-for="c in cards" :key="c.label" v-bind="c" />
    </div>

    <div class="chart-grid">
      <ChartCard
        title="Hiring activity"
        subtitle="Applications received and candidates placed, last 6 months"
        type="line"
        :labels="monthLabels"
        :series="trendSeries"
      />

      <ChartCard
        title="Candidate funnel"
        subtitle="Where your applicants currently stand"
        horizontal
        :labels="funnelLabels"
        :series="funnelSeries"
      />
    </div>
  </div>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
  margin-top: 16px;
}
</style>
