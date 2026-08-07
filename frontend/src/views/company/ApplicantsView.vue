<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import DataTable from '@/components/common/DataTable.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import { useTableFilters } from '@/composables/useTableFilters'
import { useCapabilities } from '@/composables/useCapabilities'
import { fetchApplications, updateApplication } from '@/services/applications'

const columns = [
  { key: 'studentName', label: 'Candidate' },
  { key: 'rollNumber', label: 'Roll no.', width: '130px' },
  { key: 'branch', label: 'Branch', width: '150px' },
  { key: 'cgpa', label: 'CGPA', width: '80px' },
  { key: 'driveTitle', label: 'Drive' },
  { key: 'interviewScheduledAt', label: 'Interview', width: '150px' },
  { key: 'status', label: 'Status', width: '130px' },
]

const rows = ref([])
const loading = ref(false)
const error = ref('')
const capabilities = ref({})

const { apply, isFiltered } = useTableFilters({
  searchKeys: ['studentName', 'rollNumber', 'driveTitle', 'branch'],
})
const visibleRows = computed(() => apply(rows.value))
const { can, optionsFor } = useCapabilities(capabilities)

const editing = ref(null)
const busy = ref(false)
const draft = reactive({ status: '', feedback: '', interviewScheduledAt: '' })

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchApplications()
    rows.value = data.items
    capabilities.value = data.capabilities
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not load applicants.'
  } finally {
    loading.value = false
  }
}

function openStatus(row) {
  editing.value = row
  draft.status = row.status
  draft.feedback = row.feedback ?? ''
  // datetime-local wants "YYYY-MM-DDTHH:mm"; the API sends full ISO with seconds.
  draft.interviewScheduledAt = row.interviewScheduledAt?.slice(0, 16) ?? ''
}

async function save() {
  busy.value = true
  try {
    await updateApplication(editing.value.id, {
      status: draft.status,
      feedback: draft.feedback,
      interviewScheduledAt: draft.status === 'interview' ? draft.interviewScheduledAt : null,
    })
    editing.value = null
    await load()
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not update that application.'
    editing.value = null
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
      :empty-text="isFiltered ? 'No applicants match the current filters.' : 'No applications received yet.'"
    >
      <template #cell-status="{ value }">
        <StatusBadge :status="value" />
      </template>

      <template #actions="{ row }">
        <BButton variant="link" size="sm"
          :disabled="!can('setStatus', row)"
          @click="openStatus(row)"
        >
          Update
        </BButton>
      </template>
    </DataTable>

    <ModalDialog
      :model-value="!!editing"
      title="Update application"
      confirm-text="Save"
      :busy="busy"
      :disabled="!draft.status"
      @update:model-value="editing = null"
      @confirm="save"
    >
      <p class="candidate">
        {{ editing?.studentName }} — <span class="muted">{{ editing?.driveTitle }}</span>
      </p>

      <BFormGroup label="Status" label-for="app-status" class="mb-3">
        <BFormSelect id="app-status" v-model="draft.status">
          <BFormSelectOption v-for="opt in optionsFor('setStatus')" :key="opt" :value="opt">
            {{ opt }}
          </BFormSelectOption>
        </BFormSelect>
      </BFormGroup>

      <BFormGroup
        v-if="draft.status === 'interview'"
        label="Interview date"
        label-for="app-interview"
        class="mb-3"
      >
        <BFormInput id="app-interview" v-model="draft.interviewScheduledAt" type="datetime-local" />
      </BFormGroup>

      <BFormGroup label="Feedback" label-for="app-feedback" description="Shared with the candidate">
        <BFormTextarea id="app-feedback" v-model="draft.feedback" rows="3" />
      </BFormGroup>
    </ModalDialog>
  </div>
</template>

<style scoped>
.candidate {
  margin-bottom: 16px;
  font-weight: 600;
}

.muted {
  color: var(--text-muted);
  font-weight: 400;
}

</style>
