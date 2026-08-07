<script setup>
import { reactive, ref, onMounted } from 'vue'
import CompanyFields from '@/components/register/CompanyFields.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { fetchCompanyProfile, saveCompanyProfile } from '@/services/profile'
import { useAuth } from '@/stores/auth'

const auth = useAuth()

const form = reactive({
  name: '',
  industry: '',
  location: '',
  hrContactName: '',
  hrContactEmail: '',
  website: '',
})

const accountStatus = ref('')
const fieldErrors = reactive({})
const errorMsg = ref('')
const savedMsg = ref('')
const saving = ref(false)

function clearFieldErrors() {
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
}

onMounted(async () => {
  try {
    const data = await fetchCompanyProfile()
    Object.assign(form, {
      name: data.name ?? '',
      industry: data.industry ?? '',
      location: data.location ?? '',
      hrContactName: data.hrContactName ?? '',
      hrContactEmail: data.hrContactEmail ?? '',
      website: data.website ?? '',
    })
    accountStatus.value = data.accountStatus ?? ''
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
    await saveCompanyProfile({ ...form })
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
      <BRow class="g-2 align-items-end">
        <BCol md="5">
          <BFormGroup label="Username">
            <BFormInput :model-value="auth.userName" disabled />
          </BFormGroup>
        </BCol>
        <BCol md="4">
          <BFormGroup label="Role">
            <BFormInput :model-value="auth.role" disabled />
          </BFormGroup>
        </BCol>
        <BCol md="3">
          <BFormGroup label="Approval">
            <StatusBadge :status="accountStatus || 'pending'" />
          </BFormGroup>
        </BCol>
      </BRow>

      <hr class="divider" />
      <p class="section-label">Company details</p>

      <CompanyFields :form="form" :errors="fieldErrors" />

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
