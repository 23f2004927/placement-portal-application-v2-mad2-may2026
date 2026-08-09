<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import { fetchNotifications, markAllRead } from '@/services/notifications'

/*
  Where the Celery jobs become visible. The scheduled reminder writes a
  Notification row; this reads it. Polls every 30s so a job that fires while the
  tab is open shows up without a refresh.
*/
const POLL_MS = 30000

const items = ref([])
const unread = ref(0)
const open = ref(false)
const busy = ref(false)
let timer = null

async function load() {
  try {
    const data = await fetchNotifications()
    items.value = data.items
    unread.value = data.unread
  } catch {
    /* the bell must never break the page it sits in */
  }
}

async function readAll() {
  busy.value = true
  try {
    await markAllRead()
    await load()
    open.value = false
  } finally {
    busy.value = false
  }
}

function when(iso) {
  return iso ? new Date(iso).toLocaleString() : ''
}

onMounted(() => {
  load()
  timer = setInterval(load, POLL_MS)
})

onUnmounted(() => clearInterval(timer))
</script>

<template>
  <div class="bell-wrap">
    <button type="button" class="bell" title="Notifications" @click="open = true">
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
        <path
          d="M6 9a6 6 0 1 1 12 0c0 5 2 6 2 6H4s2-1 2-6M10 20a2 2 0 0 0 4 0"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="square"
        />
      </svg>
      <BBadge v-if="unread" variant="danger" class="count">{{ unread }}</BBadge>
    </button>

    <ModalDialog
      :model-value="open"
      title="Notifications"
      confirm-text="Mark all read"
      :busy="busy"
      :disabled="!unread"
      @update:model-value="open = false"
      @confirm="readAll"
    >
      <p v-if="!items.length" class="empty mb-0">Nothing yet.</p>

      <ul v-else class="feed">
        <li v-for="n in items" :key="n.id" class="item" :class="{ 'is-unread': !n.read }">
          <p class="item-title">{{ n.title }}</p>
          <p v-if="n.body" class="item-body">{{ n.body }}</p>
          <p class="item-when">{{ when(n.createdAt) }}</p>
        </li>
      </ul>
    </ModalDialog>
  </div>
</template>

<style scoped>
.bell-wrap {
  position: relative;
}

.bell {
  position: relative;
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  cursor: pointer;
}

.bell:hover {
  color: var(--text);
  border-color: var(--border-strong);
}

.count {
  position: absolute;
  top: -7px;
  right: -7px;
  padding: 2px 5px;
  font-size: 0.625rem;
  border-radius: var(--radius);
}

.empty {
  color: var(--text-muted);
}

.feed {
  margin: 0;
  padding: 0;
  list-style: none;
}

.item {
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.item:last-child {
  border-bottom: 0;
}

.item-title {
  margin: 0 0 2px;
  font-weight: 700;
}

.is-unread .item-title::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  margin-right: 8px;
  vertical-align: middle;
  background: var(--primary);
}

.item-body {
  margin: 0;
  color: var(--text-muted);
}

.item-when {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 0.6875rem;
}
</style>
