<script setup>

const props = defineProps({
 form:   { type: Object, required: true },
 errors: { type: Object, default: () => ({}) },
})
const stateOf = (key) => (props.errors[key] ? false : null)

</script>

<template>
  <BRow class="g-2">
    <BCol md="6">
      <BFormGroup label="Company name" label-for="company-name" :state="stateOf('name')" :invalid-feedback="errors.name">
        <BFormInput id="company-name" v-model="form.name" type="text" :state="stateOf('name')" required />
      </BFormGroup>
    </BCol>

    <BCol md="6">
      <BFormGroup label="Industry" label-for="company-industry" :state="stateOf('industry')" :invalid-feedback="errors.industry" required>
        <BFormInput
          id="company-industry"
          v-model="form.industry"
          type="text"
          placeholder="electronics"
          required
          :state="stateOf('industry')"
        />
      </BFormGroup>
    </BCol>

    <BCol md="6">
      <BFormGroup label="Location" label-for="company-location">
        <BFormInput
          id="company-location"
          v-model="form.location"
          type="text"
          placeholder="Optional"

        />
      </BFormGroup>
    </BCol>

    <BCol md="6">
      <BFormGroup label="HR contact name" label-for="company-hr-name"  :state="stateOf('hrContactName')" :invalid-feedback="errors.hrContactName">
        <BFormInput
          id="company-hr-name"
          v-model="form.hrContactName"
          type="text"
          placeholder="Hr"
          required
          label-for="company-hr-email" :state="stateOf('hrContactName')"
        />
      </BFormGroup>
    </BCol>

    <BCol md="6">
      <BFormGroup label="HR contact email" label-for="company-hr-email" :state="stateOf('hrContactEmail')" :invalid-feedback="errors.hrContactEmail">
        <BFormInput
          id="company-hr-email"
          v-model="form.hrContactEmail"
          type="email"
          placeholder="Work email"
          :state="stateOf('hrContactEmail')"
          required
        />
      </BFormGroup>
    </BCol>

    <BCol md="6">
      <BFormGroup label="Website" label-for="company-website" :state="stateOf('website')" :invalid-feedback="errors.website">
        <BFormInput
          id="company-website"
          v-model="form.website"
          type="url"
          placeholder="https://example.com"
          :state="stateOf('website')"
          required
        />
      </BFormGroup>
    </BCol>
  </BRow>
</template>
