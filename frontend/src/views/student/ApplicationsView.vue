<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/common/DataTable.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import { useTableFilters } from '@/composables/useTableFilters'
import { useCapabilities } from '@/composables/useCapabilities'
import { fetchApplications, revokeApplication } from '@/services/applications'

const columns = [
  { key: 'driveTitle', label: 'Role' },
  { key: 'companyName', label: 'Company' },
  { key: 'appliedAt', label: 'Applied', width: '130px' },
  { key: 'interviewScheduledAt', label: 'Interview', width: '150px' },
  { key: 'status', label: 'Status', width: '130px' },
]

const rows = ref([])
const loading = ref(false)
const error = ref('')
const capabilities = ref({})

const { apply, isFiltered } = useTableFilters({ searchKeys: ['driveTitle', 'companyName'] })
const visibleRows = computed(() => apply(rows.value))
const { can } = useCapabilities(capabilities)

const withdrawing = ref(null)
const viewing = ref(null)
const busy = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchApplications()
    rows.value = data.items
    capabilities.value = data.capabilities
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load your applications.'
  } finally {
    loading.value = false
  }
}

async function confirmWithdraw() {
  busy.value = true
  try {
    await revokeApplication(withdrawing.value.id)
    withdrawing.value = null
    await load()
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not withdraw that application.'
    withdrawing.value = null
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
      :empty-text="isFiltered ? 'No applications match the current filters.' : 'You haven\'t applied to anything yet.'"
    >
      <template #cell-status="{ value }">
        <StatusBadge :status="value" />
      </template>

      <template #actions="{ row }">
        <BButton variant="link" size="sm" :disabled="!row.feedback" @click="viewing = row">
          Feedback
        </BButton>
        <BButton variant="link" size="sm" class="text-danger"
          :disabled="!can('revoke', row)"
          @click="withdrawing = row"
        >
          Withdraw
        </BButton>
      </template>
    </DataTable>

    <ModalDialog
      :model-value="!!withdrawing"
      title="Withdraw this application?"
      confirm-text="Withdraw"
      confirm-variant="danger"
      :busy="busy"
      @update:model-value="withdrawing = null"
      @confirm="confirmWithdraw"
    >
      <p class="mb-0">
        You are withdrawing from <strong>{{ withdrawing?.driveTitle }}</strong> at
        {{ withdrawing?.companyName }}. You will not be able to apply to it again.
      </p>
    </ModalDialog>

    <ModalDialog
      :model-value="!!viewing"
      title="Feedback"
      confirm-text="Close"
      @update:model-value="viewing = null"
      @confirm="viewing = null"
    >
      <p class="muted mb-2">{{ viewing?.companyName }} — {{ viewing?.driveTitle }}</p>
      <p class="mb-0">{{ viewing?.feedback }}</p>
    </ModalDialog>
  </div>
</template>

<style scoped>
.muted {
  color: var(--text-muted);
  font-size: 0.8125rem;
}

</style>
