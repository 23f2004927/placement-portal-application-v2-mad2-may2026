<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { filtersByRoute } from '@/config/filters'

const route = useRoute()
const router = useRouter()

const config = computed(() => filtersByRoute[route.name] ?? null)

const searchText = ref(String(route.query.search ?? ''))
// Each control is a computed straight onto the route query, so a filter set by
// a link (an admin queue tile, say) shows up selected here with no syncing.
function queryModel(key) {
  return computed({
    get: () => String(route.query[key] ?? ''),
    set: (value) => setQuery({ [key]: value || undefined, page: undefined }),
  })
}

const status = queryModel('status')
const applied = queryModel('applied')
const maxCgpa = queryModel('maxCgpa')

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

const isFiltered = computed(() =>
  ['search', 'status', 'applied', 'maxCgpa'].some((key) => !!route.query[key]),
)
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

    <BFormSelect v-if="config.applied" v-model="applied" size="sm" class="filter-select">
      <BFormSelectOption value="">Applied or not</BFormSelectOption>
      <BFormSelectOption v-for="opt in config.applied" :key="opt.value" :value="opt.value">
        {{ opt.text }}
      </BFormSelectOption>
    </BFormSelect>

    <BFormInput
      v-if="config.maxCgpa"
      v-model="maxCgpa"
      size="sm"
      type="number"
      min="0"
      max="10"
      step="0.1"
      :placeholder="config.maxCgpa"
      class="filter-number"
    />

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

.filter-number {
  max-width: 130px;
}

.filter-select {
  max-width: 180px;
}

@media (max-width: 767px) {
  .filter-search,
  .filter-number,
  .filter-select {
    max-width: none;
  }
}
</style>
