<script setup>
import { ref, shallowRef, onMounted, onUnmounted, watch } from 'vue'
import Chart from 'chart.js/auto'

/*
  One wrapper for every chart in the app, so the styling decisions are made once.

  Every chart also has a table view. A canvas is a picture — a screen reader
  cannot read it, and neither can anyone who needs the exact number — so the
  toggle is not decoration, it is how the data stays reachable.
*/
const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  type: { type: String, default: 'bar' },        // 'bar' | 'line'
  horizontal: { type: Boolean, default: false },
  labels: { type: Array, default: () => [] },
  // [{ label, data }] — one entry per series.
  series: { type: Array, default: () => [] },
  height: { type: Number, default: 260 },
})

// Series 1 is the app's own accent. Series 2 is validated against it for
// colour-vision deficiency (ΔE 28 protan) rather than picked by eye.
const COLOURS = ['#5551c6', '#eb6834']

const INK_MUTED = '#6d6a62'
const GRID = '#e6e3dc'

const canvas = ref(null)
const showTable = ref(false)
// shallowRef: Chart holds a big mutable instance that must not be made reactive.
const chart = shallowRef(null)

function config() {
  const multi = props.series.length > 1

  return {
    type: props.type,
    data: {
      labels: props.labels,
      datasets: props.series.map((s, i) => ({
        label: s.label,
        data: s.data,
        backgroundColor: COLOURS[i % COLOURS.length],
        borderColor: COLOURS[i % COLOURS.length],
        borderWidth: props.type === 'line' ? 2 : 0,
        // Square corners: the whole theme has --radius: 0.
        borderRadius: 0,
        // Thin marks — a bar that fills its slot reads as a solid block.
        barPercentage: 0.6,
        categoryPercentage: 0.7,
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0,
        fill: false,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: props.horizontal ? 'y' : 'x',
      // Bigger hit area than the mark itself, and one tooltip for the whole
      // category rather than making the user land on a 4px point.
      interaction: { mode: 'index', intersect: false },
      plugins: {
        // A legend earns its place only when there is more than one series;
        // with one, the card title already names it.
        legend: {
          display: multi,
          position: 'bottom',
          labels: { boxWidth: 10, boxHeight: 10, color: INK_MUTED, font: { size: 11 } },
        },
        tooltip: {
          backgroundColor: '#1b1a17',
          padding: 10,
          cornerRadius: 0,
          displayColors: multi,
        },
      },
      // Gridlines run perpendicular to the bars, so which axis carries them
      // flips with `horizontal`. Solid hairlines, never dashed. `border` rather
      // than the v3 `grid.drawBorder`, which Chart.js 4 removed.
      scales: {
        x: {
          grid: { display: props.horizontal, color: GRID },
          border: { display: false },
          ticks: { color: INK_MUTED, font: { size: 11 } },
        },
        y: {
          beginAtZero: true,
          grid: { display: !props.horizontal, color: GRID },
          border: { display: false },
          ticks: { color: INK_MUTED, font: { size: 11 }, precision: 0 },
        },
      },
    },
  }
}

function render() {
  if (chart.value) {
    chart.value.destroy()
    chart.value = null
  }
  if (canvas.value) chart.value = new Chart(canvas.value, config())
}

onMounted(render)
// Chart.js does not track Vue reactivity; a data change means a re-render.
watch(() => [props.labels, props.series], render, { deep: true })
onUnmounted(() => chart.value?.destroy())
</script>

<template>
  <section class="chart-card">
    <header class="chart-head">
      <div>
        <h3 class="chart-title">{{ title }}</h3>
        <p v-if="subtitle" class="chart-sub">{{ subtitle }}</p>
      </div>
      <BButton variant="link" size="sm" @click="showTable = !showTable">
        {{ showTable ? 'Chart' : 'Table' }}
      </BButton>
    </header>

    <div v-show="!showTable" class="chart-body" :style="{ height: `${height}px` }">
      <canvas ref="canvas" />
    </div>

    <div v-if="showTable" class="chart-table">
      <table class="table table-sm mb-0">
        <thead>
          <tr>
            <th></th>
            <th v-for="s in series" :key="s.label" class="num">{{ s.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(label, i) in labels" :key="label">
            <td>{{ label }}</td>
            <td v-for="s in series" :key="s.label" class="num">{{ s.data[i] ?? 0 }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.chart-card {
  padding: 20px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.chart-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.chart-title {
  margin: 0;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.chart-sub {
  margin: 2px 0 0;
  color: var(--text-muted);
  font-size: 0.75rem;
}

.chart-body {
  position: relative;
}

.chart-table {
  overflow-x: auto;
  font-size: 0.8125rem;
}

/* tabular-nums here, where digits align down a column — but never on the big
   standalone stat-card numbers, where equal-width digits read as loose. */
.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
</style>
