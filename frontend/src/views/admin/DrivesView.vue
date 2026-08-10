<script setup>
import { ref } from 'vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { useServerTable } from '@/composables/useServerTable'
import { useCapabilities } from '@/composables/useCapabilities'
import { fetchDrives, updateDrive } from '@/services/drives'

const columns = [
  { key: 'title', label: 'Role' , sortable: true },
  { key: 'companyName', label: 'Company' , sortable: true },
  { key: 'jobType', label: 'Type', width: '140px' , sortable: true },
  { key: 'applicationDeadline', label: 'Deadline', width: '150px' , sortable: true , type: 'date' },
  { key: 'status', label: 'Status', width: '130px' , sortable: true },
]

const { rows, capabilities, total, page, perPage, loading, error, isFiltered, sortKey, sortDir, load, setPage, setSort } =
  useServerTable(fetchDrives)

const { can } = useCapabilities(capabilities)

const moderating = ref(null)
const busy = ref(false)


// DriveStatus has no REJECTED member: rejection maps to CLOSED, so the posting
// stays on record but no student can apply to it.
async function moderate(approved) {
  busy.value = true
  try {
    await updateDrive(moderating.value.row.id, { status: approved ? 'approved' : 'closed' })
    moderating.value = null
    await load()
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not update that drive.'
    moderating.value = null
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
      :empty-text="isFiltered ? 'No drives match the current filters.' : 'No drives posted yet.'"
      :sort="sortKey"
      :dir="sortDir"
      @update:page="setPage"
      @update:sort="setSort"
    >
      <template #cell-status="{ value }">
        <StatusBadge :status="value" />
      </template>

      <template #actions="{ row }">
        <BButton variant="link" size="sm"
          :disabled="!can('approve', row)"
          @click="moderating = { row, approve: true }"
        >
          Approve
        </BButton>
        <BButton variant="link" size="sm" class="text-danger"
          :disabled="!can('reject', row)"
          @click="moderating = { row, approve: false }"
        >
          Reject
        </BButton>
      </template>
    </DataTable>

    <ModalDialog
      :model-value="!!moderating"
      :title="moderating?.approve ? 'Approve this drive?' : 'Reject this drive?'"
      :confirm-text="moderating?.approve ? 'Approve' : 'Reject'"
      :confirm-variant="moderating?.approve ? 'primary' : 'danger'"
      :busy="busy"
      @update:model-value="moderating = null"
      @confirm="moderate(moderating.approve)"
    >
      <p class="mb-0">
        <strong>{{ moderating?.row.title }}</strong> by {{ moderating?.row.companyName }}
        <span v-if="moderating?.approve"> will become visible to eligible students.</span>
        <span v-else> will be closed. It stays on record but no student can apply.</span>
      </p>
    </ModalDialog>
  </div>
</template>

