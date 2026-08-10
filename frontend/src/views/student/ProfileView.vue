<script setup>
import { reactive, ref, onMounted } from 'vue'
import StudentFields from '@/components/register/StudentFields.vue'
import {
  fetchStudentProfile,
  saveStudentProfile,
  uploadResume,
  deleteResume,
  openResume,
} from '@/services/profile'
import { formatDate } from '@/utils/dates'
import { useAuth } from '@/stores/auth'

const auth = useAuth()

// Same field component the registration form uses — one definition of what a
// student record looks like, so the two screens cannot drift.
const form = reactive({
  name: '',
  email: '',
  phoneNumber: '',
  rollNumber: '',
  branch: '',
  yearStudy: '',
  gradeYear: '',
  cgpa: '',
})

const links = reactive({ github: '', linkedin: '', portfolio: '' })
const fieldErrors = reactive({})
const errorMsg = ref('')
const savedMsg = ref('')
const saving = ref(false)

// The resume is its own request, so it carries its own state rather than
// riding on the form's — an upload failing must not read as "profile not saved".
const studentId = ref(null)
const resumeUploadedAt = ref(null)
const resumeFile = ref(null)
const resumeBusy = ref(false)
const resumeError = ref('')

function clearFieldErrors() {
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
}

onMounted(async () => {
  try {
    const data = await fetchStudentProfile()
    Object.assign(form, {
      name: data.name ?? '',
      email: data.email ?? '',
      phoneNumber: data.phoneNumber ?? '',
      rollNumber: data.rollNumber ?? '',
      branch: data.branch ?? '',
      yearStudy: data.yearStudy ?? '',
      gradeYear: data.gradeYear ?? '',
      cgpa: data.cgpa ?? '',
    })
    Object.assign(links, { github: '', linkedin: '', portfolio: '', ...(data.links ?? {}) })
    studentId.value = data.id
    resumeUploadedAt.value = data.resumeUploadedAt
  } catch (err) {
    errorMsg.value = err.response?.data?.message ?? 'Could not load your profile.'
  }
})

async function handleSubmit() {
  errorMsg.value = ''
  savedMsg.value = ''
  clearFieldErrors()
  saving.value = true
  try {
    // rollNumber is read-only server-side, so it is not sent.
    const { rollNumber, ...editable } = form
    await saveStudentProfile({ ...editable, links })
    savedMsg.value = 'Profile updated.'
  } catch (err) {
    errorMsg.value = err.response?.data?.message ?? 'Could not save your profile.'
    Object.assign(fieldErrors, err.response?.data?.errors ?? {})
  } finally {
    saving.value = false
  }
}

// BFormFile gives a File or null; the picker is cleared after either action so
// the same file can be chosen again if the first attempt was rejected.
async function submitResume() {
  if (!resumeFile.value) return
  resumeError.value = ''
  resumeBusy.value = true
  try {
    const data = await uploadResume(resumeFile.value)
    resumeUploadedAt.value = data.resumeUploadedAt
    resumeFile.value = null
  } catch (err) {
    resumeError.value = err.response?.data?.message ?? 'Could not upload that file.'
  } finally {
    resumeBusy.value = false
  }
}

async function removeResume() {
  resumeError.value = ''
  resumeBusy.value = true
  try {
    await deleteResume()
    resumeUploadedAt.value = null
    resumeFile.value = null
  } catch (err) {
    resumeError.value = err.response?.data?.message ?? 'Could not remove your resume.'
  } finally {
    resumeBusy.value = false
  }
}

async function viewResume() {
  resumeError.value = ''
  try {
    await openResume(studentId.value)
  } catch {
    resumeError.value = 'Could not open your resume.'
  }
}
</script>

<template>
  <div>
    <BForm v-trim class="profile-form" @submit.prevent="handleSubmit">
      <BAlert v-if="errorMsg" :model-value="true" variant="danger">{{ errorMsg }}</BAlert>
      <BAlert v-if="savedMsg" :model-value="true" variant="success">{{ savedMsg }}</BAlert>

      <p class="section-label">Account</p>
      <BRow class="g-2">
        <BCol md="6">
          <BFormGroup label="Username">
            <BFormInput :model-value="auth.userName" disabled />
          </BFormGroup>
        </BCol>
        <BCol md="6">
          <BFormGroup label="Roll number" description="Set by the institute — not editable">
            <BFormInput :model-value="form.rollNumber" disabled />
          </BFormGroup>
        </BCol>
      </BRow>

      <hr class="divider" />
      <p class="section-label">Details</p>

      <StudentFields :form="form" :errors="fieldErrors" />

      <hr class="divider" />
      <p class="section-label">Portfolio</p>

      <BRow class="g-2">
        <BCol md="4">
          <BFormGroup label="GitHub" label-for="link-github">
            <BFormInput id="link-github" v-model="links.github" type="url" placeholder="https://" />
          </BFormGroup>
        </BCol>
        <BCol md="4">
          <BFormGroup label="LinkedIn" label-for="link-linkedin">
            <BFormInput id="link-linkedin" v-model="links.linkedin" type="url" placeholder="https://" />
          </BFormGroup>
        </BCol>
        <BCol md="4">
          <BFormGroup label="Portfolio" label-for="link-portfolio">
            <BFormInput id="link-portfolio" v-model="links.portfolio" type="url" placeholder="https://" />
          </BFormGroup>
        </BCol>
      </BRow>

      <div class="form-actions">
        <BButton type="submit" variant="primary" size="sm" :disabled="saving">
          {{ saving ? 'Saving…' : 'Save changes' }}
        </BButton>
      </div>
    </BForm>

    <!-- Outside the form on purpose: uploading is its own request, not part of
         "Save changes", so it must not be submitted with the rest. -->
    <section class="profile-form resume-card">
      <p class="section-label">Resume</p>

      <BAlert v-if="resumeError" :model-value="true" variant="danger">{{ resumeError }}</BAlert>

      <div class="resume-state">
        <span v-if="resumeUploadedAt">Uploaded {{ formatDate(resumeUploadedAt) }}</span>
        <span v-else class="muted">No resume uploaded</span>

        <template v-if="resumeUploadedAt">
          <BButton variant="link" size="sm" @click="viewResume">View</BButton>
          <BButton variant="link" size="sm" :disabled="resumeBusy" @click="removeResume">
            Remove
          </BButton>
        </template>
      </div>

      <div class="resume-pick">
        <BFormFile
          v-model="resumeFile"
          accept="application/pdf"
          size="sm"
          :placeholder="resumeUploadedAt ? 'Choose a PDF to replace it…' : 'Choose a PDF…'"
        />
        <BButton
          variant="primary"
          size="sm"
          :disabled="!resumeFile || resumeBusy"
          @click="submitResume"
        >
          {{ resumeBusy ? 'Uploading…' : 'Upload' }}
        </BButton>
      </div>

      <p class="hint">PDF only, up to 2 MB. Companies you have applied to can open it.</p>
    </section>
  </div>
</template>

<style scoped>
.profile-form {
  max-width: 900px;
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
  margin-top: 24px;
}

.resume-card {
  margin-top: 16px;
}

.resume-state {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 0.875rem;
}

.resume-pick {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 480px;
}

.muted {
  color: var(--text-muted);
}

.hint {
  margin: 10px 0 0;
  color: var(--text-muted);
  font-size: 0.75rem;
}
</style>
