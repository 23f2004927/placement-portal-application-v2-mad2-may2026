<script setup>
import { reactive, computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { branches } from '@/config/branches'
import { jobTypes } from '@/config/enums'
import { createDrive, fetchDrive, updateDrive } from '@/services/drives'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  title: '',
  description: '',
  jobType: '',
  branch: '',
  minCgpa: '',
  eligibleYear: '',
  skillsRequired: '',
  experienceRequired: '',
  salary: '',
  benefits: '',
  numOpenings: '',
  applicationDeadline: '',
})

const submitting = ref(false)
const errorMsg = ref('')
const fieldErrors = reactive({})

const stateOf = (key) => (fieldErrors[key] ? false : null)

/*
  `skillsRequired` is a comma-separated input here and a JSON array on the
  model; a blank `branch` means "open to all". The backend re-coerces both, so
  this is convenience, not validation.
*/
function buildPayload() {
  return {
    ...form,
    branch: form.branch || null,
    skillsRequired: form.skillsRequired
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean),
  }
}
// A company awaiting approval never reaches this view: meta.requiresApproved on
// both drive-form routes turns it away in the router guard, before mount.
onMounted(async () => {
  if (!isEdit.value) return
  try {
    const drive = await fetchDrive(route.params.id)
    Object.assign(form, {
      ...drive,
      description: drive.description ?? '',
      jobType: drive.jobType ?? '',
      branch: drive.branch ?? '',
      minCgpa: drive.minCgpa ?? '',
      eligibleYear: drive.eligibleYear ?? '',
      salary: drive.salary ?? '',
      benefits: drive.benefits ?? '',
      experienceRequired: drive.experienceRequired ?? '',
      numOpenings: drive.numOpenings ?? '',
      skillsRequired: (drive.skillsRequired ?? []).join(', '),
      // datetime-local wants "YYYY-MM-DDTHH:mm"; the API sends full ISO.
      applicationDeadline: drive.applicationDeadline?.slice(0, 16) ?? '',
    })
  } catch (err) {
    errorMsg.value = err.response?.data?.message ?? 'Could not load that drive.'
  }
})

async function handleSubmit() {
  errorMsg.value = ''
  submitting.value = true
  try {
    if (isEdit.value) await updateDrive(route.params.id, buildPayload())
    else await createDrive(buildPayload())
    router.push({ name: 'company-drives' })
  } catch (err) {
    errorMsg.value = err.response?.data?.message ?? 'Could not save this drive.'
    Object.assign(fieldErrors, err.response?.data?.errors ?? {})
  } finally {
    submitting.value = false
  }
}

function cancel() {
  router.push({ name: 'company-drives' })
}
</script>

<template>
  <div>
    <BForm v-trim class="drive-form" @submit.prevent="handleSubmit">
      <BAlert v-if="errorMsg" :model-value="true" variant="danger">{{ errorMsg }}</BAlert>

      <BRow class="g-2">
        <BCol md="8">
          <BFormGroup label="Title" label-for="drive-title" :state="stateOf('title')" :invalid-feedback="fieldErrors.title">
            <BFormInput id="drive-title" v-model="form.title" :state="stateOf('title')" required />
          </BFormGroup>
        </BCol>

        <BCol md="4">
          <BFormGroup label="Job type" label-for="drive-type">
            <BFormSelect id="drive-type" v-model="form.jobType" :options="jobTypes" required>
              <template #first>
                <BFormSelectOption :value="''" disabled>Select a type</BFormSelectOption>
              </template>
            </BFormSelect>
          </BFormGroup>
        </BCol>

        <BCol md="12">
          <BFormGroup label="Description" label-for="drive-desc">
            <BFormTextarea id="drive-desc" v-model="form.description" rows="4" />
          </BFormGroup>
        </BCol>
      </BRow>

      <hr class="divider" />
      <p class="section-label">Eligibility</p>

      <BRow class="g-2">
        <BCol md="4">
          <BFormGroup label="Branch" label-for="drive-branch" description="Leave blank for all branches">
            <BFormSelect id="drive-branch" v-model="form.branch" :options="branches">
              <template #first>
                <BFormSelectOption :value="''">All branches</BFormSelectOption>
              </template>
            </BFormSelect>
          </BFormGroup>
        </BCol>

        <BCol md="4">
          <BFormGroup label="Minimum CGPA" label-for="drive-cgpa">
            <BFormInput id="drive-cgpa" v-model="form.minCgpa" type="number" min="0" max="10" step="0.01" />
          </BFormGroup>
        </BCol>

        <BCol md="4">
          <BFormGroup label="Eligible graduation year" label-for="drive-year">
            <BFormInput id="drive-year" v-model="form.eligibleYear" type="number" min="2000" max="2100" step="1" />
          </BFormGroup>
        </BCol>

        <BCol md="8">
          <BFormGroup label="Skills required" label-for="drive-skills" description="Comma separated">
            <BFormInput id="drive-skills" v-model="form.skillsRequired" placeholder="python, sql, react" />
          </BFormGroup>
        </BCol>

        <BCol md="4">
          <BFormGroup label="Experience" label-for="drive-experience" description="Stated, not filtered on">
            <BFormInput id="drive-experience" v-model="form.experienceRequired" placeholder="0–1 years" />
          </BFormGroup>
        </BCol>
      </BRow>

      <hr class="divider" />
      <p class="section-label">Offer</p>

      <BRow class="g-2">
        <BCol md="4">
          <BFormGroup label="Salary" label-for="drive-salary">
            <BFormInput id="drive-salary" v-model="form.salary" type="number" min="0" step="1000" />
          </BFormGroup>
        </BCol>

        <BCol md="4">
          <BFormGroup label="Openings" label-for="drive-openings">
            <BFormInput id="drive-openings" v-model="form.numOpenings" type="number" min="1" step="1" />
          </BFormGroup>
        </BCol>

        <BCol md="4">
          <BFormGroup label="Application deadline" label-for="drive-deadline">
            <BFormInput id="drive-deadline" v-model="form.applicationDeadline" type="datetime-local" />
          </BFormGroup>
        </BCol>

        <BCol md="12">
          <BFormGroup label="Benefits" label-for="drive-benefits" description="Optional">
            <BFormTextarea
              id="drive-benefits"
              v-model="form.benefits"
              rows="2"
              placeholder="Health cover, relocation support, learning budget…"
            />
          </BFormGroup>
        </BCol>
      </BRow>

      <div class="form-actions">
        <BButton variant="outline-primary" size="sm" @click="cancel">Cancel</BButton>
        <BButton type="submit" variant="primary" size="sm" :disabled="submitting">
          {{ isEdit ? 'Save changes' : 'Create drive' }}
        </BButton>
      </div>
    </BForm>
  </div>
</template>

<style scoped>
.drive-form {
  max-width: 860px;
  padding: 24px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.divider {
  border: 0;
  border-top: 1px solid var(--border);
  opacity: 1;
  margin: 20px 0 12px;
}

.section-label {
  margin: 0 0 8px;
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 24px;
}
</style>
