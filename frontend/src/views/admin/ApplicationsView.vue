<script setup>
import { ref } from 'vue'
import DataTable from '@/components/common/DataTable.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import { useServerTable } from '@/composables/useServerTable'
import { useCapabilities } from '@/composables/useCapabilities'
import { fetchApplications, revokeApplication } from '@/services/applications'

const columns = [
  { key: 'studentName', label: 'Candidate' , sortable: true },
  { key: 'rollNumber', label: 'Roll no.', width: '130px' , sortable: true },
  { key: 'driveTitle', label: 'Role' , sortable: true },
  { key: 'companyName', label: 'Company' , sortable: true },
  { key: 'appliedAt', label: 'Applied', width: '130px' , sortable: true , type: 'date' },
  { key: 'status', label: 'Status', width: '130px' , sortable: true },
]

const { rows, capabilities, total, page, perPage, loading, error, isFiltered, sortKey, sortDir, load, setPage, setSort } =
  useServerTable(fetchApplications)

const { can } = useCapabilities(capabilities)

const revoking = ref(null)
const busy = ref(false)

// Same GET the other two roles call — the backend scopes by claim, so admin
// gets every row unfiltered, including withdrawn ones.

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

</script>

<template>
  <div>
    <DataTable
      :columns="columns"
      :rows="rows"
      :loading="loading"
      :error="error"
      :total="total"
      :page="page"
      :per-page="perPage"
      :empty-text="isFiltered ? 'No applications match the current filters.' : 'No applications yet.'"
      :sort="sortKey"
      :dir="sortDir"
      @update:page="setPage"
      @update:sort="setSort"
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

