<script setup>
/*
  Same contract as StudentFields: `form` is the parent's reactive object,
  mutated in place through v-model on its properties.

  Only `name` is nullable=False on the Company model — the rest are optional
  and can be completed later from a company profile page.
*/
defineProps({
  form: { type: Object, required: true },
})
</script>

<template>
  <BRow class="g-2">
    <BCol md="6">
      <BFormGroup label="Company name" label-for="company-name">
        <BFormInput id="company-name" v-model="form.name" type="text" required />
      </BFormGroup>
    </BCol>

    <BCol md="6">
      <BFormGroup label="Industry" label-for="company-industry">
        <BFormInput
          id="company-industry"
          v-model="form.industry"
          type="text"
          placeholder="Optional"
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
      <BFormGroup label="HR contact name" label-for="company-hr-name">
        <BFormInput
          id="company-hr-name"
          v-model="form.hrContactName"
          type="text"
          placeholder="Optional"
        />
      </BFormGroup>
    </BCol>

    <BCol md="6">
      <BFormGroup label="HR contact email" label-for="company-hr-email">
        <BFormInput
          id="company-hr-email"
          v-model="form.hrContactEmail"
          type="email"
          placeholder="Optional"
        />
      </BFormGroup>
    </BCol>

    <BCol md="6">
      <BFormGroup label="Website" label-for="company-website">
        <BFormInput
          id="company-website"
          v-model="form.website"
          type="url"
          placeholder="https://example.com"
        />
      </BFormGroup>
    </BCol>
  </BRow>
</template>
