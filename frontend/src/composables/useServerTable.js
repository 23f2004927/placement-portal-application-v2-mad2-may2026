import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

/*
  Replaces useTableFilters. The filters already live in the route query, so the
  whole of "refetch when the user filters" is a watcher on route.query — the
  server does the filtering and paging, and the browser never receives rows it
  would only hide.

  `fetcher` takes the query params and returns
  { items, capabilities, page, perPage, total }.
*/
export function useServerTable(fetcher) {
  const route = useRoute()
  const router = useRouter()

  const rows = ref([])
  const capabilities = ref({})
  const total = ref(0)
  const page = ref(1)
  const perPage = ref(25)
  const loading = ref(false)
  const error = ref('')

  const isFiltered = computed(() => !!route.query.search || !!route.query.status)

  async function load() {
    loading.value = true
    error.value = ''
    try {
      const data = await fetcher({ ...route.query })
      rows.value = data.items ?? []
      capabilities.value = data.capabilities ?? {}
      total.value = data.total ?? rows.value.length
      page.value = data.page ?? 1
      perPage.value = data.perPage ?? 25
    } catch (err) {
      error.value = err.response?.data?.message ?? 'Could not load this list.'
      rows.value = []
    } finally {
      loading.value = false
    }
  }

  const sortKey = computed(() => String(route.query.sort ?? ''))
  const sortDir = computed(() => String(route.query.dir ?? ''))

  function setPage(next) {
    router.replace({ query: { ...route.query, page: next > 1 ? next : undefined } })
  }

  // Re-sorting resets to page 1 — page 4 of one ordering has nothing to do with
  // page 4 of another.
  function setSort({ sort, dir }) {
    router.replace({ query: { ...route.query, sort, dir, page: undefined } })
  }

  // Any filter change should send the user back to page 1 — page 4 of an
  // unfiltered list is usually past the end of a filtered one.
  watch(
    () => [route.query.search, route.query.status, route.query.applied, route.query.maxCgpa],
    () => {
      if (Number(route.query.page ?? 1) !== 1) setPage(1)
    },
  )

  watch(() => route.query, load, { immediate: true, deep: true })

  return {
    rows,
    capabilities,
    total,
    page,
    perPage,
    loading,
    error,
    isFiltered,
    sortKey,
    sortDir,
    load,
    setPage,
    setSort,
  }
}
