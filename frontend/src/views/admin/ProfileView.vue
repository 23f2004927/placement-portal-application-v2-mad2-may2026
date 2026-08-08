<script setup>
import { ref, onMounted } from 'vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { fetchMe } from '@/services/auth'

const me = ref({ userName: '', role: '', accountStatus: '' })
const errorMsg = ref('')

onMounted(async () => {
  try {
    me.value = await fetchMe()
  } catch (err) {
    errorMsg.value = err.response?.data?.message ?? 'Could not load your account.'
  }
})
</script>

<template>
  <div>
    <div class="profile-form">
      <BAlert v-if="errorMsg" :model-value="true" variant="danger">{{ errorMsg }}</BAlert>

      <p class="section-label">Account</p>
      <BRow class="g-2 align-items-end">
        <BCol md="5">
          <BFormGroup label="Username">
            <BFormInput :model-value="me.userName" disabled />
          </BFormGroup>
        </BCol>
        <BCol md="4">
          <BFormGroup label="Role">
            <BFormInput :model-value="me.role" disabled />
          </BFormGroup>
        </BCol>
        <BCol md="3">
          <BFormGroup label="Approval">
            <StatusBadge :status="me.accountStatus || 'approved'" />
          </BFormGroup>
        </BCol>
      </BRow>

      <hr class="divider" />
      <p class="note">
        Administrator accounts are provisioned during setup, so there is nothing here to edit.
      </p>
    </div>
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

.note {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.8125rem;
}
</style>
