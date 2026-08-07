<script setup>
import { ref, watch } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import Sidebar from '@/components/layout/Sidebar.vue'
import FilterBar from '@/components/layout/FilterBar.vue'

const route = useRoute()


const pinned = ref(localStorage.getItem('sidebarPinned') === '1')

watch(pinned, (value) => localStorage.setItem('sidebarPinned', value ? '1' : '0'))
</script>

<template>
  <div class="dashboard" :class="{ 'is-pinned': pinned }">
    <Sidebar :pinned="pinned" />
    <header class="topbar">
      <button
        type="button"
        class="pin"
        :class="{ 'is-on': pinned }"
        :title="pinned ? 'Unpin sidebar' : 'Keep sidebar open'"
        :aria-pressed="pinned"
        @click="pinned = !pinned"
      >
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <path
            d="M3 6h18M3 12h18M3 18h18"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="square"
          />
        </svg>
      </button>

      <div class="page-id">
        <h1 class="page-title">{{ route.meta.title }}</h1>
        <p v-if="route.meta.subtitle" class="page-subtitle">{{ route.meta.subtitle }}</p>
      </div>

      <FilterBar />
    </header>

    <main class="dash-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>

.dashboard {
  position: relative;
  --rail-w: 64px;
  height: 100dvh;
  display: grid;
  grid-template-columns: var(--rail-w) 1fr;
  grid-template-rows: 64px 1fr;
  grid-template-areas:
    '. topbar'
    '. main';
  background: var(--bg);
  transition: grid-template-columns 0.18s ease;
}

.dashboard.is-pinned {
  --rail-w: 240px;
}

.topbar {
  grid-area: topbar;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 24px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}

.pin {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  background: none;
  border: 1px solid transparent;
  color: var(--text-muted);
  cursor: pointer;
  flex-shrink: 0;
  transition:
    color 0.15s ease,
    border-color 0.15s ease,
    background 0.15s ease;
}

.pin:hover {
  color: var(--primary);
  border-color: var(--border);
}

.pin.is-on {
  color: var(--primary);
  border-color: var(--primary);
  background: var(--primary-soft);
}

.page-id {
  min-width: 0;
  flex-shrink: 0;
  padding-right: 12px;
  border-right: 1px solid var(--border);
}

.page-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  white-space: nowrap;
}

.page-subtitle {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* min-height: 0 — grid children default to auto and refuse to shrink below
   their content, which would push the page past 100dvh and add a document scroll. */
.dash-main {
  grid-area: main;
  overflow-y: auto;
  min-height: 0;
  padding: 32px;
}

@media (max-width: 767px) {
  .dashboard,
  .dashboard.is-pinned {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr;
    grid-template-areas:
      'topbar'
      'sidebar'
      'main';
  }

  .topbar {
    flex-wrap: wrap;
    padding: 8px 16px;
  }

  .pin,
  .page-subtitle {
    display: none;
  }

  .page-id {
    border-right: 0;
    padding-right: 0;
  }

  .dash-main {
    padding: 16px;
  }
}
</style>
