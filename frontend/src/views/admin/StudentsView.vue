<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/common/DataTable.vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import { useTableFilters } from '@/composables/useTableFilters'
import { useCapabilities } from '@/composables/useCapabilities'
import { fetchStudents, moderateStudent } from '@/services/admin'

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'rollNumber', label: 'Roll no.', width: '130px' },
  { key: 'branch', label: 'Branch', width: '170px' },
  { key: 'yearStudy', label: 'Year', width: '80px' },
  { key: 'cgpa', label: 'CGPA', width: '90px' },
  { key: 'email', label: 'Email' },
  { key: 'blackListed', label: 'Access', width: '120px' },
]

const rows = ref([])
const loading = ref(false)
const error = ref('')
const capabilities = ref({})

const { apply, isFiltered } = useTableFilters({
  searchKeys: ['name', 'rollNumber', 'email', 'phoneNumber', 'branch'],
})
const visibleRows = computed(() => apply(rows.value))
const { can } = useCapabilities(capabilities, 'accountStatus')

const pending = ref(null)
const busy = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchStudents()
    rows.value = data.items
    capabilities.value = data.capabilities
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load students.'
  } finally {
    loading.value = false
  }
}

async function confirm() {
  busy.value = true
  try {
    await moderateStudent(pending.value.id, { blackListed: !pending.value.blackListed })
    pending.value = null
    await load()
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not update that student.'
    pending.value = null
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
      :empty-text="isFiltered ? 'No students match the current filters.' : 'No students registered yet.'"
    >
      <template #cell-blackListed="{ value }">
        <BBadge v-if="value" variant="danger" class="access-badge">Blacklisted</BBadge>
        <span v-else class="text-muted">—</span>
      </template>

      <template #actions="{ row }">
        <BButton
          variant="link"
          size="sm"
          :class="row.blackListed ? '' : 'text-danger'"
          :disabled="!can('blacklist', row)"
          @click="pending = row"
        >
          {{ row.blackListed ? 'Restore' : 'Blacklist' }}
        </BButton>
      </template>
    </DataTable>

    <ModalDialog
      :model-value="!!pending"
      :title="pending?.blackListed ? 'Restore access?' : 'Blacklist this student?'"
      :confirm-text="pending?.blackListed ? 'Restore' : 'Blacklist'"
      :confirm-variant="pending?.blackListed ? 'primary' : 'danger'"
      :busy="busy"
      @update:model-value="pending = null"
      @confirm="confirm"
    >
      <p class="mb-0">
        <strong>{{ pending?.name }}</strong> ({{ pending?.rollNumber }})
        {{ pending?.blackListed
          ? 'will be able to sign in again.'
          : 'will be blocked from signing in. Existing applications are left untouched.' }}
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
