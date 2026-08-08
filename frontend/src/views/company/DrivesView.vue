<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/common/DataTable.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import { useTableFilters } from '@/composables/useTableFilters'
import { useCapabilities } from '@/composables/useCapabilities'
import { fetchDrives, updateDrive } from '@/services/drives'
import { useAuth } from '@/stores/auth'

const auth = useAuth()

const columns = [
  { key: 'title', label: 'Title' },
  { key: 'jobType', label: 'Type', width: '140px' },
  { key: 'numOpenings', label: 'Openings', width: '110px' },
  { key: 'applicationCount', label: 'Applicants', width: '110px' },
  { key: 'applicationDeadline', label: 'Deadline', width: '150px' },
  { key: 'status', label: 'Status', width: '130px' },
]

const rows = ref([])
const loading = ref(false)
const error = ref('')
const capabilities = ref({})

const { apply, isFiltered } = useTableFilters({ searchKeys: ['title', 'jobType'] })
const visibleRows = computed(() => apply(rows.value))
const { can } = useCapabilities(capabilities)

const closing = ref(null)
const busy = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchDrives()
    rows.value = data.items
    capabilities.value = data.capabilities
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load your drives.'
  } finally {
    loading.value = false
  }
}

async function confirmClose() {
  busy.value = true
  try {
    await updateDrive(closing.value.id, { status: 'closed' })
    closing.value = null
    await load()
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not close that drive.'
    closing.value = null
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <!-- Say why the button is dead, rather than letting the route guard bounce
         them back here with no explanation. -->
    <BAlert v-if="!auth.isApproved" :model-value="true" variant="secondary" class="pending-note">
      Your account is awaiting approval by the placement office. You can look
      around, but you cannot post a drive until it is approved.
    </BAlert>

    <div class="view-toolbar">
      <BButton
        :to="auth.isApproved ? { name: 'company-drive-new' } : undefined"
        :disabled="!auth.isApproved"
        variant="primary"
        size="sm"
      >
        New drive
      </BButton>
    </div>

    <DataTable
      :columns="columns"
      :rows="visibleRows"
      :loading="loading"
      :error="error"
      :empty-text="isFiltered ? 'No drives match the current filters.' : 'You haven\'t posted a drive yet.'"
    >
      <template #cell-status="{ value }">
        <StatusBadge :status="value" />
      </template>

      <template #actions="{ row }">
        <BButton variant="link" size="sm"
          :to="{ name: 'company-applicants', query: { search: row.title } }"
        >
          Applicants
        </BButton>
        <BButton variant="link" size="sm"
          v-if="can('edit', row)"
          :to="{ name: 'company-drive-edit', params: { id: row.id } }"
        >
          Edit
        </BButton>
        <BButton variant="link" size="sm" class="text-danger"
          :disabled="!can('close', row)"
          @click="closing = row"
        >
          Close
        </BButton>
      </template>
    </DataTable>

    <ModalDialog
      :model-value="!!closing"
      title="Close this drive?"
      confirm-text="Close drive"
      confirm-variant="danger"
      :busy="busy"
      @update:model-value="closing = null"
      @confirm="confirmClose"
    >
      <p class="mb-0">
        <strong>{{ closing?.title }}</strong> will stop accepting applications. Existing
        applications are unaffected.
      </p>
    </ModalDialog>
  </div>
</template>

<style scoped>
.view-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.pending-note {
  font-size: 0.8125rem;
}

</style>
