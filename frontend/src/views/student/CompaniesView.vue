<script setup>
import DataTable from '@/components/common/DataTable.vue'
import { useServerTable } from '@/composables/useServerTable'
import { fetchCompanyDirectory } from '@/services/admin'

// No status column and no actions: the directory only lists approved companies,
// so an account state would be the same word on every row.
const columns = [
  { key: 'name', label: 'Company', sortable: true },
  { key: 'industry', label: 'Industry', width: '200px', sortable: true },
  { key: 'location', label: 'Location', width: '180px', sortable: true },
  { key: 'openDrives', label: 'Open drives', width: '130px', sortable: true },
  { key: 'website', label: 'Website' },
]

const { rows, total, page, perPage, loading, error, isFiltered, sortKey, sortDir, setPage, setSort } =
  useServerTable(fetchCompanyDirectory)
</script>

<template>
  <DataTable
    :columns="columns"
    :rows="rows"
    :loading="loading"
    :error="error"
    :total="total"
    :page="page"
    :per-page="perPage"
    :empty-text="isFiltered ? 'No companies match the current filters.' : 'No companies recruiting yet.'"
    :sort="sortKey"
    :dir="sortDir"
    @update:page="setPage"
    @update:sort="setSort"
  >
    <!-- The count links into the drive list pre-filtered by this company's
         name, which works because drive search already covers Company.name. -->
    <template #cell-openDrives="{ row, value }">
      <RouterLink
        v-if="value"
        :to="{ name: 'student-drives', query: { search: row.name } }"
        class="count"
      >
        {{ value }}
      </RouterLink>
      <span v-else class="text-muted">—</span>
    </template>

    <!-- rel="noreferrer" because these are third-party URLs the company typed. -->
    <template #cell-website="{ value }">
      <a v-if="value" :href="value" target="_blank" rel="noopener noreferrer">{{ value }}</a>
      <span v-else class="text-muted">—</span>
    </template>
  </DataTable>
</template>

<style scoped>
.count {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
}
</style>
