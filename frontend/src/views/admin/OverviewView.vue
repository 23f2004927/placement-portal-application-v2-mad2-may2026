<script setup>
import { ref, computed, onMounted } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import ActionTile from '@/components/common/ActionTile.vue'
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

const outcomeLabels = computed(() => (analytics.value?.offerOutcomes ?? []).map((o) => o.outcome))
const outcomeSeries = computed(() => [
  { label: 'Offers', data: (analytics.value?.offerOutcomes ?? []).map((o) => o.count) },
])

const branchLabels = computed(() =>
  (analytics.value?.placementsByBranch ?? []).map((b) => b.branch),
)
const branchSeries = computed(() => [
  { label: 'Students placed', data: (analytics.value?.placementsByBranch ?? []).map((b) => b.count) },
])

const cards = computed(() => [
  { label: 'Students', value: stats.value?.students },
  { label: 'Companies', value: stats.value?.companies },
  { label: 'Drives', value: stats.value?.drives },
  { label: 'Applications', value: stats.value?.applications },
  { label: 'Placed', value: stats.value?.placed },
])

/*
  Queues, not statistics. Each links to the list that clears it, with the filter
  already in the route query — the same query params the topbar FilterBar reads,
  so arriving via a tile leaves the filter control showing the right value.
*/
const queues = computed(() => [
  {
    label: 'Companies to review',
    value: stats.value?.pendingCompanies,
    hint: 'Approve or reject',
    to: { name: 'admin-companies', query: { status: 'pending' } },
  },
  {
    label: 'Drives to review',
    value: stats.value?.pendingDrives,
    hint: 'Approve before students see them',
    to: { name: 'admin-drives', query: { status: 'pending' } },
  },
  {
    label: 'Offers awaiting reply',
    value: stats.value?.offersAwaiting,
    hint: 'With the student',
    to: { name: 'admin-applications', query: { status: 'offer' } },
  },
  {
    label: 'Interviews this week',
    value: stats.value?.interviewsThisWeek,
    hint: 'Next 7 days',
    to: { name: 'admin-applications', query: { status: 'interview' } },
  },
])
</script>

<template>
  <div>
    <BAlert v-if="error" :model-value="true" variant="danger">{{ error }}</BAlert>

    <p class="section-label">Needs attention</p>
    <div class="stat-grid">
      <ActionTile v-for="q in queues" :key="q.label" v-bind="q" />
    </div>

    <p class="section-label">Portal totals</p>
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

      <ChartCard
        title="Offer outcomes"
        subtitle="What students did with the offers made to them"
        horizontal
        :labels="outcomeLabels"
        :series="outcomeSeries"
      />

      <ChartCard
        title="Placements by branch"
        subtitle="Top branches, remainder grouped as other"
        horizontal
        :labels="branchLabels"
        :series="branchSeries"
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

.section-label {
  margin: 0 0 8px;
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.section-label:not(:first-child) {
  margin-top: 24px;
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
