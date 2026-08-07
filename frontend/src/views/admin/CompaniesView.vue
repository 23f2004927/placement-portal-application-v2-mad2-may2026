<script setup>
import { ref, computed } from 'vue'
import PendingNotice from '@/components/common/PendingNotice.vue'
import DataTable from '@/components/common/DataTable.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { useTableFilters } from '@/composables/useTableFilters'

const columns = [
  { key: 'name', label: 'Company' },
  { key: 'industry', label: 'Industry', width: '160px' },
  { key: 'location', label: 'Location', width: '150px' },
  { key: 'hrContactEmail', label: 'HR contact' },
  { key: 'accountStatus', label: 'Status', width: '130px' },
]

const rows = ref([])
const loading = ref(false)
const error = ref('')

const { apply, isFiltered } = useTableFilters({
  searchKeys: ['name', 'industry', 'location', 'hrContactEmail'],
  statusKey: 'accountStatus',
})
const visibleRows = computed(() => apply(rows.value))

/*
  TODO (together): approve / reject writes User.accountStatus via
  PATCH /api/admin/companies/<id>/status, plus the blacklist toggle.
*/
</script>

<template>
  <div>
    <PendingNotice endpoint="GET /api/admin/companies" />

    <DataTable
      :columns="columns"
      :rows="visibleRows"
      :loading="loading"
      :error="error"
      :empty-text="isFiltered ? 'No companies match the current filters.' : 'No companies registered yet.'"
    >
      <template #cell-accountStatus="{ value }">
        <StatusBadge :status="value" />
      </template>
    </DataTable>
  </div>
</template>
