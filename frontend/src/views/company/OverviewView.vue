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
    const [s, a] = await Promise.all([fetchStats('company'), fetchAnalytics('company')])
    stats.value = s
    analytics.value = a
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load the dashboard totals.'
  }
})

// Queues — live from /api/company/stats, each linking to the filtered list.
const queues = computed(() => [
  {
    label: 'New applications',
    value: stats.value?.toReview,
    hint: 'Not yet reviewed',
    to: { name: 'company-applicants', query: { status: 'applied' } },
  },
  {
    label: 'Interviews this week',
    value: stats.value?.interviewsThisWeek,
    hint: 'Next 7 days',
    to: { name: 'company-applicants', query: { status: 'interview' } },
  },
  {
    label: 'Offers awaiting reply',
    value: stats.value?.offersAwaiting,
    hint: 'With the candidate',
    to: { name: 'company-applicants', query: { status: 'offer' } },
  },
  {
    label: 'Drives awaiting approval',
    value: stats.value?.drivesPending,
    hint: 'With the placement office',
    to: { name: 'company-drives', query: { status: 'pending' } },
  },
])

const cards = computed(() => [
  { label: 'Drives posted', value: stats.value?.drives, hint: 'Approved and pending' },
  { label: 'Applications', value: stats.value?.applications, hint: 'Across all drives' },
  { label: 'Shortlisted', value: stats.value?.shortlisted },
  { label: 'Offers made', value: stats.value?.offers },
])

/*
  Rates are single numbers, so they are tiles rather than charts.
  Shortlist and interview conversion are deliberately absent — a rejected
  application does not record how far it got, so those rates cannot be computed
  without inventing them.
*/
const conversion = computed(() => analytics.value?.conversion ?? {})
const criteria = computed(() => analytics.value?.belowCriteria ?? { total: 0, below: 0 })

const pct = (v) => (v === null || v === undefined ? '—' : `${v}%`)

const rates = computed(() => [
  {
    label: 'Offer rate',
    value: pct(conversion.value.offerRate),
    hint: 'Applications that reached an offer',
  },
  {
    label: 'Acceptance rate',
    value: pct(conversion.value.acceptanceRate),
    hint: 'Offers accepted vs declined',
  },
  {
    label: 'Placement rate',
    value: pct(conversion.value.placementRate),
    hint: 'Applications ending in a placement',
  },
  {
    label: 'Below your criteria',
    value: criteria.value.total
      ? `${Math.round((criteria.value.below / criteria.value.total) * 100)}%`
      : '—',
    hint: `${criteria.value.below} of ${criteria.value.total} applicants`,
  },
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

const outcomeLabels = computed(() => (analytics.value?.offerOutcomes ?? []).map((o) => o.outcome))
const outcomeSeries = computed(() => [
  { label: 'Offers', data: (analytics.value?.offerOutcomes ?? []).map((o) => o.count) },
])

const branchLabels = computed(() =>
  (analytics.value?.applicantBranches ?? []).map((b) => b.branch),
)
const branchSeries = computed(() => [
  { label: 'Applicants', data: (analytics.value?.applicantBranches ?? []).map((b) => b.count) },
])

const cgpaLabels = computed(() => (analytics.value?.applicantCgpa ?? []).map((b) => b.band))
const cgpaSeries = computed(() => [
  { label: 'Applicants', data: (analytics.value?.applicantCgpa ?? []).map((b) => b.count) },
])
</script>

<template>
  <div>
    <BAlert v-if="error" :model-value="true" variant="danger">{{ error }}</BAlert>

    <p class="section-label">Needs attention</p>
    <div class="stat-grid">
      <ActionTile v-for="q in queues" :key="q.label" v-bind="q" />
    </div>

    <p class="section-label">Your totals</p>
    <div class="stat-grid">
      <StatCard v-for="c in cards" :key="c.label" v-bind="c" />
    </div>

    <p class="section-label">Conversion</p>
    <div class="stat-grid">
      <StatCard v-for="r in rates" :key="r.label" v-bind="r" />
    </div>

    <div class="chart-grid">
      <ChartCard
        class="span-2"
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

      <ChartCard
        title="Offer outcomes"
        subtitle="How candidates responded to your offers"
        horizontal
        :labels="outcomeLabels"
        :series="outcomeSeries"
      />

      <ChartCard
        title="Applicants by branch"
        subtitle="Top branches, remainder grouped as other"
        horizontal
        :labels="branchLabels"
        :series="branchSeries"
      />

      <ChartCard
        title="Applicant CGPA"
        subtitle="How your applicants are distributed"
        :labels="cgpaLabels"
        :series="cgpaSeries"
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
  margin-top: 24px;
}

.span-2 {
  grid-column: 1 / -1;
}
</style>
