<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/common/DataTable.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import { useTableFilters } from '@/composables/useTableFilters'
import { useCapabilities } from '@/composables/useCapabilities'
import { fetchApplications, revokeApplication } from '@/services/applications'

const columns = [
  { key: 'studentName', label: 'Candidate' },
  { key: 'rollNumber', label: 'Roll no.', width: '130px' },
  { key: 'driveTitle', label: 'Role' },
  { key: 'companyName', label: 'Company' },
  { key: 'appliedAt', label: 'Applied', width: '130px' },
  { key: 'status', label: 'Status', width: '130px' },
]

const rows = ref([])
const loading = ref(false)
const error = ref('')
const capabilities = ref({})

const { apply, isFiltered } = useTableFilters({
  searchKeys: ['studentName', 'rollNumber', 'driveTitle', 'companyName'],
})
const visibleRows = computed(() => apply(rows.value))
const { can } = useCapabilities(capabilities)

const revoking = ref(null)
const busy = ref(false)

// Same GET the other two roles call — the backend scopes by claim, so admin
// gets every row unfiltered, including withdrawn ones.
async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchApplications()
    rows.value = data.items
    capabilities.value = data.capabilities
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load applications.'
  } finally {
    loading.value = false
  }
}

async function confirmRevoke() {
  busy.value = true
  try {
    await revokeApplication(revoking.value.id)
    revoking.value = null
    await load()
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not revoke that application.'
    revoking.value = null
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <DataTable
      :columns="columns"
      :rows="visibleRows"
      :loading="loading"
      :error="error"
      :empty-text="isFiltered ? 'No applications match the current filters.' : 'No applications yet.'"
    >
      <template #cell-status="{ value }">
        <StatusBadge :status="value" />
      </template>

      <template #actions="{ row }">
        <BButton variant="link" size="sm" class="text-danger"
          :disabled="!can('revoke', row)"
          @click="revoking = row"
        >
          Revoke
        </BButton>
      </template>
    </DataTable>

    <ModalDialog
      :model-value="!!revoking"
      title="Revoke this application?"
      confirm-text="Revoke"
      confirm-variant="danger"
      :busy="busy"
      @update:model-value="revoking = null"
      @confirm="confirmRevoke"
    >
      <p class="mb-0">
        <strong>{{ revoking?.studentName }}</strong>'s application to
        {{ revoking?.driveTitle }} will be withdrawn. The company will no longer see it, and the
        student cannot re-apply.
      </p>
    </ModalDialog>
  </div>
</template>

