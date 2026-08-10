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
// Every query key that narrows the list. Keep in step with config/filters.js.
const FILTER_KEYS = ['search', 'status', 'applied', 'maxCgpa']

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

  const isFiltered = computed(() =>
    FILTER_KEYS.some((key) => !!route.query[key]),
  )

  /*
    Responses can arrive out of order — type quickly in search and an older
    request can answer after a newer one, leaving the table showing something
    the URL no longer asks for. Each load claims a ticket and only the newest
    one is allowed to write.
  */
  let ticket = 0

  async function load() {
    const mine = ++ticket
    loading.value = true
    error.value = ''
    try {
      const data = await fetcher({ ...route.query })
      if (mine !== ticket) return

      rows.value = data.items ?? []
      capabilities.value = data.capabilities ?? {}
      total.value = data.total ?? rows.value.length
      page.value = data.page ?? 1
      perPage.value = data.perPage ?? 25
    } catch (err) {
      if (mine !== ticket) return
      error.value = err.response?.data?.message ?? 'Could not load this list.'
      rows.value = []
    } finally {
      if (mine === ticket) loading.value = false
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

  /*
    Resetting to page 1 on a filter change is the job of whatever CHANGES the
    filter — FilterBar and setSort both drop `page` when they write.

    A watcher here cannot do it: its getter would have to return a fresh array
    of the filter values, Vue compares that by reference, so it fired on every
    query change including `page` itself — clicking page 2 immediately bounced
    back to page 1, with both requests racing.
  */
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
