<script setup>
import { ref, reactive, computed } from 'vue'
import DataTable from '@/components/common/DataTable.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import { useServerTable } from '@/composables/useServerTable'
import { useCapabilities } from '@/composables/useCapabilities'
import {
  fetchApplications,
  updateApplication,
  issueOfferLetter,
  downloadOfferLetter,
} from '@/services/applications'
import { openResume } from '@/services/profile'
import { useExport } from '@/composables/useExport'

const columns = [
  { key: 'studentName', label: 'Candidate' , sortable: true },
  { key: 'rollNumber', label: 'Roll no.', width: '130px' , sortable: true },
  { key: 'branch', label: 'Branch', width: '150px' },
  { key: 'cgpa', label: 'CGPA', width: '80px' , sortable: true },
  { key: 'driveTitle', label: 'Drive' , sortable: true },
  { key: 'belowCriteria', label: 'Match', width: '150px' },
  { key: 'interviewScheduledAt', label: 'Interview', width: '150px' , sortable: true , type: 'datetime' },
  { key: 'status', label: 'Status', width: '130px' , sortable: true },
]

const { rows, capabilities, total, page, perPage, loading, error, isFiltered, sortKey, sortDir, load, setPage, setSort } =
  useServerTable(fetchApplications)

const { can, optionsFor } = useCapabilities(capabilities)
const { exporting, message: exportMsg, run: exportCsv } = useExport()

const editing = ref(null)
const offering = ref(null)
const busy = ref(false)
const draft = reactive({ status: '', feedback: '', interviewScheduledAt: '' })
const joiningDate = ref('')


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

function openOffer(row) {
  offering.value = row
  joiningDate.value = ''
}

async function confirmOffer() {
  busy.value = true
  try {
    await issueOfferLetter(offering.value.id, joiningDate.value || null)
    offering.value = null
    await load()
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not issue that offer letter.'
    offering.value = null
  } finally {
    busy.value = false
  }
}

async function download(row) {
  try {
    await downloadOfferLetter(row.id)
  } catch {
    error.value = 'Could not download that offer letter.'
  }
}

// The endpoint re-checks that this candidate applied to one of our drives, so a
// disabled button here is a convenience, not the control.
async function resume(row) {
  try {
    await openResume(row.studentId)
  } catch {
    error.value = 'Could not open that resume.'
  }
}

</script>

<template>
  <div>
    <div class="view-toolbar">
      <span v-if="exportMsg" class="export-msg">{{ exportMsg }}</span>
      <BButton variant="outline-primary" size="sm" :disabled="exporting" @click="exportCsv">
        {{ exporting ? 'Working…' : 'Export CSV' }}
      </BButton>
    </div>

    <DataTable
      :columns="columns"
      :rows="rows"
      :loading="loading"
      :error="error"
      :total="total"
      :page="page"
      :per-page="perPage"
      :empty-text="isFiltered ? 'No applicants match the current filters.' : 'No applications received yet.'"
      :sort="sortKey"
      :dir="sortDir"
      @update:page="setPage"
      @update:sort="setSort"
    >
      <template #cell-status="{ value }">
        <StatusBadge :status="value" />
      </template>

      <!-- Students may apply outside the advertised criteria, so say which ones
           did rather than letting it pass unnoticed. -->
      <template #cell-belowCriteria="{ row }">
        <BBadge v-if="row.belowCriteria" variant="secondary" class="match">
          {{ row.criteriaMissed.join(' · ') }}
        </BBadge>
        <span v-else class="text-muted">—</span>
      </template>

      <template #actions="{ row }">
        <BButton variant="link" size="sm"
          :disabled="!can('setStatus', row)"
          @click="openStatus(row)"
        >
          Update
        </BButton>
        <BButton
          variant="link"
          size="sm"
          :disabled="!row.resumeUploadedAt"
          @click="resume(row)"
        >
          Resume
        </BButton>
        <BButton
          v-if="row.offerLetterIssuedAt"
          variant="link"
          size="sm"
          @click="download(row)"
        >
          Offer letter
        </BButton>
        <BButton
          v-else
          variant="link"
          size="sm"
          :disabled="!can('issueOfferLetter', row)"
          @click="openOffer(row)"
        >
          Issue offer
        </BButton>
      </template>
    </DataTable>

    <ModalDialog
      :model-value="!!offering"
      title="Issue offer letter"
      confirm-text="Issue"
      :busy="busy"
      @update:model-value="offering = null"
      @confirm="confirmOffer"
    >
      <p class="candidate">
        {{ offering?.studentName }} — <span class="muted">{{ offering?.driveTitle }}</span>
      </p>

      <p class="muted mb-3">
        The letter copies the drive's title, type, location and salary as they stand now. Later
        edits to the drive will not change it.
      </p>

      <BFormGroup label="Joining date" label-for="offer-joining" description="Optional">
        <BFormInput id="offer-joining" v-model="joiningDate" type="date" />
      </BFormGroup>
    </ModalDialog>

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

.match {
  padding: 4px 8px;
  font-size: 0.6875rem;
  font-weight: 600;
  white-space: normal;
  text-align: left;
}

.view-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 16px;
}

.export-msg {
  color: var(--text-muted);
  font-size: 0.8125rem;
}

</style>
