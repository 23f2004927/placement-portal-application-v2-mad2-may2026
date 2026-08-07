<script setup>
import { ref, computed } from 'vue'
import PendingNotice from '@/components/common/PendingNotice.vue'
import DataTable from '@/components/common/DataTable.vue'
import { useTableFilters } from '@/composables/useTableFilters'

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'rollNumber', label: 'Roll no.', width: '130px' },
  { key: 'branch', label: 'Branch', width: '170px' },
  { key: 'yearStudy', label: 'Year', width: '80px' },
  { key: 'cgpa', label: 'CGPA', width: '90px' },
  { key: 'email', label: 'Email' },
]

const rows = ref([])
const loading = ref(false)
const error = ref('')

const { apply, isFiltered } = useTableFilters({
  searchKeys: ['name', 'rollNumber', 'email', 'phoneNumber', 'branch'],
})
const visibleRows = computed(() => apply(rows.value))
</script>

<template>
  <div>
    <PendingNotice endpoint="GET /api/admin/students" />

    <DataTable
      :columns="columns"
      :rows="visibleRows"
      :loading="loading"
      :error="error"
      :empty-text="isFiltered ? 'No students match the current filters.' : 'No students registered yet.'"
    />
  </div>
</template>
