<script setup>
import { ref, computed, watch } from 'vue'

/*
  A one-at-a-time slide switcher, used so the landing panel never scrolls.

  Hand-rolled rather than BCarousel for one specific reason: **only the active
  slide is rendered**. Bootstrap's carousel keeps every slide in the DOM and
  hides the inactive ones, and a <canvas> inside a `display: none` parent
  measures 0x0 — Chart.js would size to nothing and stay blank when you slid to
  it. Mounting one slide at a time sidesteps that entirely, and ChartCard
  already destroys its chart on unmount.
*/
const props = defineProps({
  items: { type: Array, required: true },
  label: { type: String, default: 'slide' },
})

const index = ref(0)

// If the list shrinks (fewer charts after a reload) the old index could point
// past the end and render nothing.
watch(
  () => props.items.length,
  (len) => {
    if (index.value >= len) index.value = 0
  },
)

const current = computed(() => props.items[index.value])
const many = computed(() => props.items.length > 1)

function go(step) {
  const len = props.items.length
  index.value = (index.value + step + len) % len
}
</script>

<template>
  <div class="carousel">
    <div class="slide">
      <slot :item="current" :index="index" />
    </div>

    <div v-if="many" class="controls">
      <button type="button" class="arrow" :aria-label="`Previous ${label}`" @click="go(-1)">
        &lsaquo;
      </button>

      <div class="dots">
        <button
          v-for="(item, i) in items"
          :key="i"
          type="button"
          class="dot"
          :class="{ 'is-on': i === index }"
          :aria-label="`${label} ${i + 1}`"
          :aria-current="i === index"
          @click="index = i"
        />
      </div>

      <button type="button" class="arrow" :aria-label="`Next ${label}`" @click="go(1)">
        &rsaquo;
      </button>
    </div>
  </div>
</template>

<style scoped>
.carousel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}

.slide {
  min-height: 0;
}

.controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.arrow {
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  padding: 0;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
}

.arrow:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.dots {
  display: flex;
  gap: 6px;
}

.dot {
  width: 7px;
  height: 7px;
  padding: 0;
  border: 1px solid var(--border-strong);
  background: transparent;
  cursor: pointer;
}

.dot.is-on {
  background: var(--primary);
  border-color: var(--primary);
}
</style>
