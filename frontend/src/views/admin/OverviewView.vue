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
    // Independent endpoints — request them together rather than in sequence.
    const [s, a] = await Promise.all([fetchStats('admin'), fetchAnalytics('admin')])
    stats.value = s
    analytics.value = a
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load the dashboard totals.'
  }
})

const monthLabels = computed(() => analytics.value?.months ?? [])

const trendSeries = computed(() => [
  { label: 'Applications', data: analytics.value?.applications ?? [] },
  { label: 'Placements', data: analytics.value?.placements ?? [] },
])

const funnelLabels = computed(() => (analytics.value?.funnel ?? []).map((f) => f.stage))
const funnelSeries = computed(() => [
  { label: 'Applications', data: (analytics.value?.funnel ?? []).map((f) => f.count) },
])

const skillLabels = computed(() => (analytics.value?.topSkills ?? []).map((s) => s.skill))
const skillSeries = computed(() => [
  { label: 'Drives asking', data: (analytics.value?.topSkills ?? []).map((s) => s.count) },
])

const cards = computed(() => [
  { label: 'Students', value: stats.value?.students },
  { label: 'Companies', value: stats.value?.companies },
  { label: 'Drives', value: stats.value?.drives },
  { label: 'Applications', value: stats.value?.applications },
  { label: 'Placed', value: stats.value?.placed },
  {
    label: 'Awaiting approval',
    value: stats.value?.pendingApprovals,
    hint: 'Companies and drives',
  },
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
        class="span-2"
        title="Placement trend"
        subtitle="Applications received and students placed, last 6 months"
        type="line"
        :labels="monthLabels"
        :series="trendSeries"
      />

      <ChartCard
        title="Application funnel"
        subtitle="Where applications currently stand"
        horizontal
        :labels="funnelLabels"
        :series="funnelSeries"
      />

      <ChartCard
        title="Skills in demand"
        subtitle="How many drives ask for each skill"
        horizontal
        :labels="skillLabels"
        :series="skillSeries"
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

/* The trend is the headline, so it gets the full width when there is room. */
.span-2 {
  grid-column: 1 / -1;
}
</style>
