<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/common/DataTable.vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { useTableFilters } from '@/composables/useTableFilters'
import { useCapabilities } from '@/composables/useCapabilities'
import { fetchCompanies, moderateCompany } from '@/services/admin'

const columns = [
  { key: 'name', label: 'Company' },
  { key: 'industry', label: 'Industry', width: '160px' },
  { key: 'location', label: 'Location', width: '150px' },
  { key: 'hrContactEmail', label: 'HR contact' },
  { key: 'accountStatus', label: 'Status', width: '130px' },
  { key: 'blackListed', label: 'Access', width: '120px' },
]

const rows = ref([])
const loading = ref(false)
const error = ref('')
const capabilities = ref({})

const { apply, isFiltered } = useTableFilters({
  searchKeys: ['name', 'industry', 'location', 'hrContactEmail'],
  statusKey: 'accountStatus',
})
const visibleRows = computed(() => apply(rows.value))
const { can } = useCapabilities(capabilities, 'accountStatus')

const pending = ref(null)
const busy = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchCompanies()
    rows.value = data.items
    capabilities.value = data.capabilities
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load companies.'
  } finally {
    loading.value = false
  }
}

async function confirm() {
  busy.value = true
  try {
    await moderateCompany(pending.value.row.id, pending.value.payload)
    pending.value = null
    await load()
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not update that company.'
    pending.value = null
  } finally {
    busy.value = false
  }
}

function ask(row, payload, title, confirmText, variant, body) {
  pending.value = { row, payload, title, confirmText, variant, body }
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
      :empty-text="isFiltered ? 'No companies match the current filters.' : 'No companies registered yet.'"
    >
      <template #cell-accountStatus="{ value }">
        <StatusBadge :status="value" />
      </template>

      <template #cell-blackListed="{ value }">
        <BBadge v-if="value" variant="danger" class="access-badge">Blacklisted</BBadge>
        <span v-else class="text-muted">—</span>
      </template>

      <template #actions="{ row }">
        <BButton
          variant="link"
          size="sm"
          :disabled="!can('setAccountStatus', row)"
          @click="ask(row, { accountStatus: 'approved' }, 'Approve this company?', 'Approve', 'primary',
                       'It will be able to sign in and post drives.')"
        >
          Approve
        </BButton>
        <BButton
          variant="link"
          size="sm"
          class="text-danger"
          :disabled="!can('setAccountStatus', row)"
          @click="ask(row, { accountStatus: 'rejected' }, 'Reject this company?', 'Reject', 'danger',
                       'It will no longer be able to sign in. This decision cannot be reversed.')"
        >
          Reject
        </BButton>
        <BButton
          variant="link"
          size="sm"
          :class="row.blackListed ? '' : 'text-danger'"
          :disabled="!can('blacklist', row)"
          @click="ask(row, { blackListed: !row.blackListed },
                       row.blackListed ? 'Restore access?' : 'Blacklist this company?',
                       row.blackListed ? 'Restore' : 'Blacklist',
                       row.blackListed ? 'primary' : 'danger',
                       row.blackListed
                         ? 'It will be able to sign in again.'
                         : 'It will be signed out of new sessions and blocked from posting.')"
        >
          {{ row.blackListed ? 'Restore' : 'Blacklist' }}
        </BButton>
      </template>
    </DataTable>

    <ModalDialog
      :model-value="!!pending"
      :title="pending?.title"
      :confirm-text="pending?.confirmText"
      :confirm-variant="pending?.variant"
      :busy="busy"
      @update:model-value="pending = null"
      @confirm="confirm"
    >
      <p class="mb-0">
        <strong>{{ pending?.row.name }}</strong> — {{ pending?.body }}
      </p>
    </ModalDialog>
  </div>
</template>

<style scoped>
.access-badge {
  padding: 4px 10px;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
</style>
