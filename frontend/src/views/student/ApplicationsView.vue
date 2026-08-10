<script setup>
import { ref } from 'vue'
import DataTable from '@/components/common/DataTable.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import { useServerTable } from '@/composables/useServerTable'
import { useCapabilities } from '@/composables/useCapabilities'
import {
  fetchApplications,
  revokeApplication,
  respondToOffer,
  downloadOfferLetter,
} from '@/services/applications'
import { startExport, exportState, downloadExport } from '@/services/exports'

const columns = [
  { key: 'driveTitle', label: 'Role' , sortable: true },
  { key: 'companyName', label: 'Company' , sortable: true },
  { key: 'appliedAt', label: 'Applied', width: '130px' , sortable: true , type: 'date' },
  { key: 'interviewScheduledAt', label: 'Interview', width: '150px' , sortable: true , type: 'datetime' },
  { key: 'status', label: 'Status', width: '130px' , sortable: true },
]

const { rows, capabilities, total, page, perPage, loading, error, isFiltered, sortKey, sortDir, load, setPage, setSort } =
  useServerTable(fetchApplications)

const { can } = useCapabilities(capabilities)

const withdrawing = ref(null)
const viewing = ref(null)
const busy = ref(false)


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

/*
  Accepting is what makes a student PLACED — the company cannot set that status
  at all, so this is the only route to it.
*/
const responding = ref(null)

async function confirmResponse() {
  busy.value = true
  try {
    await respondToOffer(responding.value.row.id, responding.value.decision)
    responding.value = null
    await load()
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not record that response.'
    responding.value = null
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

/*
  The export is a Celery job, so the POST only returns a task id. We poll until
  the worker reports SUCCESS, then fetch the file. Requires a running worker —
  without one this stays "Working…" forever, which is the honest behaviour.
*/
const exporting = ref(false)
const exportMsg = ref('')

async function exportCsv() {
  exporting.value = true
  exportMsg.value = 'Preparing your export…'
  try {
    const { taskId } = await startExport()

    for (let attempt = 0; attempt < 20; attempt++) {
      await new Promise((r) => setTimeout(r, 1000))
      const { state } = await exportState(taskId)

      if (state === 'SUCCESS') {
        await downloadExport(taskId)
        exportMsg.value = 'Export downloaded.'
        return
      }
      if (state === 'FAILURE') {
        exportMsg.value = 'The export failed.'
        return
      }
    }
    exportMsg.value = 'Still working — is the Celery worker running?'
  } catch (err) {
    exportMsg.value = err.response?.data?.message ?? 'Could not start the export.'
  } finally {
    exporting.value = false
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
      :empty-text="isFiltered ? 'No applications match the current filters.' : 'You haven\'t applied to anything yet.'"
      :sort="sortKey"
      :dir="sortDir"
      @update:page="setPage"
      @update:sort="setSort"
    >
      <template #cell-status="{ value }">
        <StatusBadge :status="value" />
      </template>

      <template #actions="{ row }">
        <BButton
          v-if="can('respondToOffer', row)"
          variant="link"
          size="sm"
          @click="responding = { row, decision: 'accept' }"
        >
          Accept
        </BButton>
        <BButton
          v-if="can('respondToOffer', row)"
          variant="link"
          size="sm"
          class="text-danger"
          @click="responding = { row, decision: 'decline' }"
        >
          Decline
        </BButton>

        <BButton variant="link" size="sm" :disabled="!row.feedback" @click="viewing = row">
          Feedback
        </BButton>
        <BButton
          variant="link"
          size="sm"
          :disabled="!row.offerLetterIssuedAt"
          @click="download(row)"
        >
          Offer letter
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
      :model-value="!!responding"
      :title="responding?.decision === 'accept' ? 'Accept this offer?' : 'Decline this offer?'"
      :confirm-text="responding?.decision === 'accept' ? 'Accept offer' : 'Decline offer'"
      :confirm-variant="responding?.decision === 'accept' ? 'primary' : 'danger'"
      :busy="busy"
      @update:model-value="responding = null"
      @confirm="confirmResponse"
    >
      <p class="mb-2">
        <strong>{{ responding?.row.driveTitle }}</strong> at {{ responding?.row.companyName }}
      </p>
      <p class="muted mb-0">
        {{
          responding?.decision === 'accept'
            ? 'You will be recorded as placed for this role. Your other applications stay open — withdraw any you no longer want.'
            : 'The company will see that you turned this offer down. This cannot be undone.'
        }}
      </p>
    </ModalDialog>

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
