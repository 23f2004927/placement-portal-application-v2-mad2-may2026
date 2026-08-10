<script setup>
import { computed } from 'vue'
import { formatDate, formatDateTime } from '@/utils/dates'

/*
  Thin wrapper over BTable rather than a hand-rolled <table>: BTable already
  provides per-column slots, a busy state and an empty state, and using it keeps
  the "Bootstrap only" claim honest.

  The wrapper exists so views keep OUR vocabulary — `columns` / `rows` /
  `cell-<key>` — and so a BTable API change is one file to fix, not eleven.
*/
const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  rowKey: { type: String, default: 'id' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  emptyText: { type: String, default: 'Nothing to show yet.' },
  // Paging is presentational here: the parent owns the page number (it lives in
  // the route query) and this only reports which page was asked for.
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  perPage: { type: Number, default: 25 },
  sort: { type: String, default: '' },
  dir: { type: String, default: '' },
})

const emit = defineEmits(['update:page', 'update:sort'])
const slots = defineSlots()

/*
  Sorting is server-side, so this only reports intent. A column opts in with
  `sortable: true`; clicking cycles asc -> desc -> off, and "off" matters
  because the default ordering (newest first, say) is often the useful one.
*/
function toggleSort(key) {
  if (props.sort !== key) return emit('update:sort', { sort: key, dir: 'asc' })
  if (props.dir === 'asc') return emit('update:sort', { sort: key, dir: 'desc' })
  emit('update:sort', { sort: undefined, dir: undefined })
}

function arrow(key) {
  if (props.sort !== key) return ''
  return props.dir === 'desc' ? '↓' : '↑'
}

// A column marked `type: 'date'` or `'datetime'` is formatted here, so no view
// has to remember to do it and none can do it differently.
const FORMATTERS = { date: formatDate, datetime: formatDateTime }

function display(col, value) {
  const format = FORMATTERS[col.type]
  if (format) return format(value)
  return value ?? '—'
}

const pages = computed(() => Math.ceil(props.total / props.perPage) || 1)
const firstRow = computed(() => (props.page - 1) * props.perPage + 1)
const lastRow = computed(() => Math.min(props.page * props.perPage, props.total))

// `width` on a column becomes a header style; BTable has no width prop.
const fields = computed(() => {
  const mapped = props.columns.map((col) => ({
    key: col.key,
    label: col.label,
    sortable: col.sortable ?? false,
    thStyle: col.width ? { width: col.width } : undefined,
  }))

  if (slots.actions) {
    mapped.push({ key: '_actions', label: 'Actions', thClass: 'text-end', tdClass: 'text-end' })
  }

  return mapped
})
</script>

<template>
  <div class="table-wrap">
    <BAlert v-if="error" :model-value="true" variant="danger" class="mb-0">{{ error }}</BAlert>

    <BTable
      v-else
      :items="rows"
      :fields="fields"
      :busy="loading"
      :primary-key="rowKey"
      show-empty
      :empty-text="emptyText"
      hover
      responsive
      class="mb-0"
    >
      <!-- BTable's own sorting is client-side and would only reorder the
           current page, so headers are rendered here and reported upward. -->
      <template v-for="col in columns" :key="`h-${col.key}`" #[`head(${col.key})`]>
        <button
          v-if="col.sortable"
          type="button"
          class="th-sort"
          :class="{ 'is-on': sort === col.key }"
          @click="toggleSort(col.key)"
        >
          {{ col.label }}<span class="arrow">{{ arrow(col.key) }}</span>
        </button>
        <template v-else>{{ col.label }}</template>
      </template>

      <!-- Re-expose BTable's cell(key) slots under our own cell-key name.
           The fallback keeps a column working without any slot at all. -->
      <template v-for="col in columns" :key="col.key" #[`cell(${col.key})`]="{ value, item }">
        <slot :name="`cell-${col.key}`" :row="item" :value="value">
          {{ display(col, value) }}
        </slot>
      </template>

      <template v-if="slots.actions" #[`cell(_actions)`]="{ item }">
        <slot name="actions" :row="item" />
      </template>

      <template #table-busy>
        <div class="state-box">
          <BSpinner small />
          <span>Loading…</span>
        </div>
      </template>

      <template #empty>
        <div class="state-box">{{ emptyText }}</div>
      </template>
    </BTable>

    <div v-if="!error && total > perPage" class="table-foot">
      <span class="range">{{ firstRow }}–{{ lastRow }} of {{ total }}</span>
      <BPagination
        :model-value="page"
        :total-rows="total"
        :per-page="perPage"
        size="sm"
        class="mb-0"
        @update:model-value="emit('update:page', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.table-wrap {
  border: 1px solid var(--border);
  background: var(--surface);
}

.state-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 48px 16px;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.table-wrap :deep(.table) {
  margin-bottom: 0;
  font-size: 0.875rem;
}

.table-wrap :deep(.table > thead th) {
  border-bottom: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.table-wrap :deep(.table > :not(caption) > * > *) {
  padding: 12px 16px;
  background: transparent;
  border-bottom-color: var(--border);
}

.table-wrap :deep(.table > tbody > tr:last-child > *) {
  border-bottom: 0;
}

.th-sort {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0;
  border: 0;
  background: none;
  color: inherit;
  font: inherit;
  letter-spacing: inherit;
  text-transform: inherit;
  cursor: pointer;
}

.th-sort:hover {
  color: var(--text);
}

.th-sort.is-on {
  color: var(--primary);
}

.arrow {
  font-size: 0.75rem;
}

.table-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  border-top: 1px solid var(--border);
}

.range {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.table-foot :deep(.page-link) {
  border-radius: 0;
  color: var(--text-muted);
}

.table-foot :deep(.active > .page-link) {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}
</style>
