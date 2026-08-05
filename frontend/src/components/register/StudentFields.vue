<script setup>
import { branches, yearsOfStudy } from '@/config/branches'

/*
  `form` is the parent's reactive object, passed by reference.
  Writing `v-model="form.name"` mutates a PROPERTY of the prop, which is fine —
  parent and child share the same proxy, so no emit is needed.
  Reassigning `form` itself would break that link and Vue would warn.
*/
defineProps({
  form: { type: Object, required: true },
})
</script>

<template>
  <BRow class="g-2">
    <BCol md="6">
      <BFormGroup label="Full name" label-for="student-name">
        <BFormInput id="student-name" v-model="form.name" type="text" required />
      </BFormGroup>
    </BCol>

    <BCol md="6">
      <BFormGroup label="Email" label-for="student-email">
        <BFormInput id="student-email" v-model="form.email" type="email" required />
      </BFormGroup>
    </BCol>

    <BCol md="4">
      <!-- Column is String(10); pattern keeps the browser from sending anything else. -->
      <BFormGroup label="Phone number" label-for="student-phone">
        <BFormInput
          id="student-phone"
          v-model="form.phoneNumber"
          type="tel"
          pattern="[0-9]{10}"
          maxlength="10"
          placeholder="10 digits"
          required
        />
      </BFormGroup>
    </BCol>

    <BCol md="4">
      <BFormGroup label="Roll number" label-for="student-roll">
        <BFormInput id="student-roll" v-model="form.rollNumber" type="text" required />
      </BFormGroup>
    </BCol>

    <BCol md="4">
      <BFormGroup label="Branch" label-for="student-branch">
        <BFormSelect
          id="student-branch"
          v-model="form.branch"
          :options="branches"
          required
        >
          <template #first>
            <BFormSelectOption :value="''" disabled>Select a branch</BFormSelectOption>
          </template>
        </BFormSelect>
      </BFormGroup>
    </BCol>

    <BCol md="4">
      <BFormGroup label="Year of study" label-for="student-year">
        <BFormSelect
          id="student-year"
          v-model="form.yearStudy"
          :options="yearsOfStudy"
          required
        >
          <template #first>
            <BFormSelectOption :value="''" disabled>Select</BFormSelectOption>
          </template>
        </BFormSelect>
      </BFormGroup>
    </BCol>

    <BCol md="4">
      <BFormGroup label="Graduation year" label-for="student-grad">
        <BFormInput
          id="student-grad"
          v-model="form.gradeYear"
          type="number"
          min="2000"
          max="2100"
          step="1"
          placeholder="2027"
          required
        />
      </BFormGroup>
    </BCol>

    <BCol md="4">
      <BFormGroup label="CGPA" label-for="student-cgpa">
        <BFormInput
          id="student-cgpa"
          v-model="form.cgpa"
          type="number"
          min="0"
          max="10"
          step="0.01"
          placeholder="8.50"
          required
        />
      </BFormGroup>
    </BCol>
  </BRow>
</template>
