<script setup>
import { ref, computed, onMounted } from 'vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { useTableFilters } from '@/composables/useTableFilters'
import { useCapabilities } from '@/composables/useCapabilities'
import { fetchDrives, updateDrive } from '@/services/drives'

const columns = [
  { key: 'title', label: 'Role' },
  { key: 'companyName', label: 'Company' },
  { key: 'jobType', label: 'Type', width: '140px' },
  { key: 'applicationDeadline', label: 'Deadline', width: '150px' },
  { key: 'status', label: 'Status', width: '130px' },
]

const rows = ref([])
const loading = ref(false)
const error = ref('')

const capabilities = ref({})
const { apply, isFiltered } = useTableFilters({ searchKeys: ['title', 'companyName', 'jobType'] })
const visibleRows = computed(() => apply(rows.value))
const { can } = useCapabilities(capabilities)

const moderating = ref(null)
const busy = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchDrives()
    rows.value = data.items
    capabilities.value = data.capabilities
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load drives.'
  } finally {
    loading.value = false
  }
}

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

onMounted(load)

</script>

<template>
  <div>

    <DataTable
      :columns="columns"
      :rows="visibleRows"
      :loading="loading"
      :error="error"
      :empty-text="isFiltered ? 'No drives match the current filters.' : 'No drives posted yet.'"
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

