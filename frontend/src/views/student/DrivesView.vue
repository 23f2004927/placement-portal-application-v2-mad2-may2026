<script setup>
import { ref } from 'vue'
import DataTable from '@/components/common/DataTable.vue'
import ModalDialog from '@/components/common/ModalDialog.vue'
import { useServerTable } from '@/composables/useServerTable'
import { applyToDrive } from '@/services/applications'
import { fetchDrives } from '@/services/drives'

const columns = [
  { key: 'title', label: 'Role' , sortable: true },
  { key: 'companyName', label: 'Company' , sortable: true },
  { key: 'jobType', label: 'Type', width: '130px' , sortable: true },
  { key: 'minCgpa', label: 'Min CGPA', width: '100px' , sortable: true },
  { key: 'salary', label: 'Salary', width: '110px' , sortable: true },
  { key: 'applicationDeadline', label: 'Closes', width: '140px' , sortable: true , type: 'date' },
  { key: 'eligible', label: 'Match', width: '150px' },
]

const { rows, capabilities, total, page, perPage, loading, error, isFiltered, sortKey, sortDir, load, setPage, setSort } =
  useServerTable(fetchDrives)

const applying = ref(null)

const busy = ref(false)


/*
  `alreadyApplied` comes from the drives serializer — the UniqueConstraint on
  (studentId, driveId) is what actually prevents a duplicate, this only stops
  the pointless request. A revoked application keeps its row, so re-applying
  after a withdrawal fails here too.
*/
async function confirmApply() {
  busy.value = true
  try {
    await applyToDrive(applying.value.id)
    applying.value = null
    await load()
  } catch (err) {
    error.value = err.response?.data?.message ?? 'Could not submit that application.'
    applying.value = null
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
      :empty-text="isFiltered ? 'No drives match the current filters.' : 'No open drives right now.'"
      :sort="sortKey"
      :dir="sortDir"
      @update:page="setPage"
      @update:sort="setSort"
    >
      <template #cell-skillsRequired="{ value }">
        <span v-for="skill in value ?? []" :key="skill" class="skill">{{ skill }}</span>
      </template>

      <!-- Advisory, not a gate: the company sets these criteria as a preference
           and Apply stays enabled either way. -->
      <template #cell-eligible="{ row }">
        <BBadge v-if="row.eligible" variant="success" class="match">Meets criteria</BBadge>
        <BBadge
          v-else
          variant="secondary"
          class="match"
          :title="row.ineligibleReasons.join(' · ')"
        >
          {{ row.ineligibleReasons.join(' · ') }}
        </BBadge>
      </template>

      <template #actions="{ row }">
        <BButton variant="link" size="sm"
          :disabled="row.alreadyApplied"
          @click="applying = row"
        >
          {{ row.alreadyApplied ? 'Applied' : 'Apply' }}
        </BButton>
      </template>
    </DataTable>

    <ModalDialog
      :model-value="!!applying"
      title="Apply to this drive?"
      confirm-text="Apply"
      :busy="busy"
      @update:model-value="applying = null"
      @confirm="confirmApply"
    >
      <p class="mb-2">
        <strong>{{ applying?.title }}</strong> at {{ applying?.companyName }}
      </p>
      <BAlert
        v-if="applying && !applying.eligible"
        :model-value="true"
        variant="secondary"
        class="mb-2 below"
      >
        You are outside this drive's stated criteria ({{ applying.ineligibleReasons.join(' · ') }}).
        You can still apply — the company decides.
      </BAlert>

      <p class="muted mb-0">
        Your profile is shared with the company. You can withdraw while the application is still
        being reviewed.
      </p>
    </ModalDialog>
  </div>
</template>

<style scoped>
.skill {
  display: inline-block;
  margin-right: 4px;
  padding: 1px 6px;
  border: 1px solid var(--border);
  font-size: 0.6875rem;
}

.muted {
  color: var(--text-muted);
}

.match {
  padding: 4px 8px;
  font-size: 0.6875rem;
  font-weight: 600;
  white-space: normal;
  text-align: left;
}

.below {
  font-size: 0.8125rem;
}

</style>
