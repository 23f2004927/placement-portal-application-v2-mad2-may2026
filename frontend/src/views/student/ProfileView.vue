<script setup>
import { reactive, ref, onMounted } from 'vue'
import StudentFields from '@/components/register/StudentFields.vue'
import { fetchStudentProfile, saveStudentProfile } from '@/services/profile'
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
const resume = ref('')
const fieldErrors = reactive({})
const errorMsg = ref('')
const savedMsg = ref('')
const saving = ref(false)

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
    resume.value = data.resume ?? ''
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
    await saveStudentProfile({ ...editable, links, resume: resume.value })
    savedMsg.value = 'Profile updated.'
  } catch (err) {
    errorMsg.value = err.response?.data?.message ?? 'Could not save your profile.'
    Object.assign(fieldErrors, err.response?.data?.errors ?? {})
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <BForm class="profile-form" @submit.prevent="handleSubmit">
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
        <BCol md="12">
          <BFormGroup label="Resume URL" label-for="resume" description="Link to a hosted PDF">
            <BFormInput id="resume" v-model="resume" type="url" placeholder="https://" />
          </BFormGroup>
        </BCol>
      </BRow>

      <div class="form-actions">
        <BButton type="submit" variant="primary" size="sm" :disabled="saving">
          {{ saving ? 'Saving…' : 'Save changes' }}
        </BButton>
      </div>
    </BForm>
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
</style>
