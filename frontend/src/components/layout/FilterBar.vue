<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { filtersByRoute } from '@/config/filters'

const route = useRoute()
const router = useRouter()

const config = computed(() => filtersByRoute[route.name] ?? null)

const searchText = ref(String(route.query.search ?? ''))
const status = computed({
  get: () => String(route.query.status ?? ''),
  set: (value) => setQuery({ status: value || undefined }),
})

// Navigating to another section must not carry the previous section's text.
watch(
  () => route.fullPath,
  () => {
    searchText.value = String(route.query.search ?? '')
  },
)

let debounce
watch(searchText, (value) => {
  clearTimeout(debounce)
  debounce = setTimeout(() => setQuery({ search: value.trim() || undefined }), 300)
})

function setQuery(patch) {
  router.replace({ query: { ...route.query, ...patch } })
}

function clearAll() {
  searchText.value = ''
  router.replace({ query: {} })
}

const isFiltered = computed(() => !!route.query.search || !!route.query.status)
</script>

<template>
  <div v-if="config" class="filter-bar">
    <BFormInput
      v-if="config.search"
      v-model="searchText"
      size="sm"
      type="search"
      :placeholder="config.search"
      class="filter-search"
    />

    <BFormSelect v-if="config.status" v-model="status" size="sm" class="filter-select">
      <BFormSelectOption value="">All statuses</BFormSelectOption>
      <BFormSelectOption v-for="opt in config.status" :key="opt.value" :value="opt.value">
        {{ opt.text }}
      </BFormSelectOption>
    </BFormSelect>

    <BButton v-if="isFiltered" size="sm" variant="outline-primary" @click="clearAll">Clear</BButton>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.filter-search {
  max-width: 320px;
}

.filter-select {
  max-width: 180px;
}

@media (max-width: 767px) {
  .filter-search,
  .filter-select {
    max-width: none;
  }
}
</style>
