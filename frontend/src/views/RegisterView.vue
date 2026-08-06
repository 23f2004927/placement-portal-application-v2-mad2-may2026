<script setup>
import { computed, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import StudentFields from '@/components/register/StudentFields.vue'
import CompanyFields from '@/components/register/CompanyFields.vue'
import { markRaw } from 'vue'
import { registerCompany, registerStudent } from '@/services/auth'

const route = useRoute()
const router = useRouter()
const credentials  = reactive({ userName: '', password: '', confirmPassword: '' })
const studentForm  = reactive({ name: '', email: '', phoneNumber: '', rollNumber: '',
                                branch: '', yearStudy: '', gradeYear: '', cgpa: '' })
const companyForm  = reactive({ name: '', industry: '', location: '',
  hrContactName: '', hrContactEmail: '', website: ''
})

const role = computed(() =>
  route.params.role === 'company' ? 'company' : 'student'   // anything else falls back
)

function setRole(next) {
  router.replace({ name: 'register', params: { role: next } })
}

// Writable computed so v-model on the toggle drives the URL rather than local state.
// `replace` (not `push`) keeps toggling out of the history stack.
const selectedRole = computed({
  get: () => role.value,
  set: (next) => setRole(next),
})

const roleOptions = [
  { value: 'student', text: 'Student' },
  { value: 'company', text: 'Company' },
]

const fieldComponents = { student: markRaw(StudentFields), company: markRaw(CompanyFields) }
const activeFields = computed(() => fieldComponents[role.value])
const activeForm   = computed(() => role.value === 'student' ? studentForm : companyForm)

const errorMsg = ref('')
const submitting = ref(false)
const fieldErrors = reactive({})
// Frozen at submit time so toggling the role afterwards can't rewrite the message.
const submittedRole = ref(null)

function clearFieldErrors() {
  Object.keys(fieldErrors).forEach(k => delete fieldErrors[k])
}

async function handleSubmit() {
  errorMsg.value = ''
  clearFieldErrors()
  // The one rule HTML5 validation cannot express.
  if (credentials.password !== credentials.confirmPassword) {
    fieldErrors.confirmPassword = 'Passwords do not match.'
    return
  }

  // confirmPassword is a UI concern — never sent.
  const payload = {
    userName: credentials.userName,
    password: credentials.password,
    ...activeForm.value,
  }

  submitting.value = true
  try {
    if (role.value === 'student') {
      await registerStudent(payload)
    } else {
      await registerCompany(payload)
    }
    submittedRole.value = role.value
  } catch (err) {
    const body = err.response?.data
    errorMsg.value = body?.message ?? 'Registration failed. Please try again.'
    Object.assign(fieldErrors, body?.errors ?? {})
  } finally {
    submitting.value = false
  }
}


</script>

<template>
  <div class="register-page">
    <BCard class="register-card">
      <!-- Success state replaces the form entirely -->
      <template v-if="submittedRole">
        <h2 class="text-center fw-bold text-uppercase mb-3">Registration received</h2>

        <p v-if="submittedRole === 'student'" class="text-center subtitle mb-4">
          Your student account is active. You can sign in straight away.
        </p>
        <p v-else class="text-center subtitle mb-4">
          Your company registration is pending administrator approval. You will be able
          to sign in once it has been reviewed.
        </p>

        <BButton to="/login" variant="primary" class="w-100">Go to sign in</BButton>
      </template>

      <!-- Form -->
      <template v-else>
        <h2 class="text-center fw-bold text-uppercase mb-1">Create an account</h2>
        <p class="text-center subtitle mb-3">Choose the account type you need.</p>

        <BFormRadioGroup
          v-model="selectedRole"
          :options="roleOptions"
          buttons
          button-variant="outline-primary"
          class="role-toggle mb-3"
        />

        <BForm @submit.prevent="handleSubmit">
          <BAlert v-if="errorMsg" :model-value="true" variant="danger">{{ errorMsg }}</BAlert>

          <!-- Shared account credentials -->
          <BRow class="g-2">
            <BCol md="4">
              <BFormGroup label="Username" label-for="username" :invalid-feedback="fieldErrors.userName" :state="fieldErrors.userName ? false : null" >
                <BFormInput id="username" v-model="credentials.userName" type="text" :state="fieldErrors.userName ? false : null"  required />
              </BFormGroup>
            </BCol>

            <BCol md="4">
              <BFormGroup label="Password" label-for="password">
                <BFormInput
                  id="password"
                  v-model="credentials.password"
                  type="password"
                  minlength="8"
                  required
                />
              </BFormGroup>
            </BCol>

            <BCol md="4">
              <BFormGroup label="Confirm password" label-for="confirm-password" :state="fieldErrors.confirmPassword ? false : null" :invalid-feedback="fieldErrors.confirmPassword">
                <BFormInput
                  id="confirm-password"
                  v-model="credentials.confirmPassword"
                  type="password"
                  minlength="8"
                  :state="fieldErrors.confirmPassword ? false : null"
                  required
                />
              </BFormGroup>
            </BCol>
          </BRow>

          <hr class="divider" />

          <!-- Role-specific fields: swapped by <component :is>, bound by shared reference -->
          <component :is="activeFields" :form="activeForm" :errors="fieldErrors" />

          <BButton
            type="submit"
            variant="primary"
            class="w-100 mt-3"
            :disabled="submitting"
          >
            {{ submitting ? 'Creating account…' : 'Create account' }}
          </BButton>

          <p class="text-center subtitle signin-row mb-0">
            Already have an account?
            <RouterLink to="/login" class="signin-link">Sign in</RouterLink>
          </p>
        </BForm>
      </template>
    </BCard>
  </div>
</template>

<style scoped>
/*
  Fixed to one viewport: the document never scrolls. If the form is taller than
  the screen (short laptop, phone) the CARD scrolls internally instead — the page
  frame stays put rather than the whole layout sliding away.
*/
.register-page {
  height: 100dvh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px 16px;
  background: var(--bg);
  overflow: hidden;
}

.register-card {
  width: 100%;
  max-width: 880px;
  max-height: 100%;
  overflow-y: auto;
  padding: 28px 32px;
}

/* BCard adds its own .card-body padding on top of the card's; zero it so the
   padding above is the only one in play. */
.register-card :deep(.card-body) {
  padding: 0;
}

/* Compact the form controls — 11 fields have to fit without scrolling. */
.register-card :deep(.form-label) {
  margin-bottom: 3px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-muted);
}

.register-card :deep(.form-control),
.register-card :deep(.form-select) {
  padding: 7px 12px;
  font-size: 0.9375rem;
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* BFormRadioGroup renders its buttons inside a child component, so the
   .btn rules can only be reached with :deep(). */
.role-toggle {
  display: flex;
  width: 100%;
}

.role-toggle :deep(.btn) {
  flex: 1;
}

.divider {
  border: 0;
  border-top: 1px solid var(--border);
  opacity: 1;
  margin: 16px 0;
}

.signin-row {
  margin-top: 14px;
}

.signin-link {
  color: var(--primary);
  font-weight: 600;
}
</style>
