<script setup>
import { computed } from 'vue'

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
})

const slots = defineSlots()

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
      <!-- Re-expose BTable's cell(key) slots under our own cell-key name.
           The fallback keeps a column working without any slot at all. -->
      <template v-for="col in columns" :key="col.key" #[`cell(${col.key})`]="{ value, item }">
        <slot :name="`cell-${col.key}`" :row="item" :value="value">
          {{ value ?? '—' }}
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
</style>
