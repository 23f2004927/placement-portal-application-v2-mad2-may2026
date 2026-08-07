import { computed } from 'vue'
import { useRoute } from 'vue-router'

/*
  The topbar writes filters into the route query; every table reads them back
  from there. The URL is the single source of truth, so a filtered view is
  shareable, survives a refresh, and needs no shared store between the layout
  and the routed child.

  `apply` filters client-side for now. Once the endpoints exist these become
  query params on the request — admin search in particular has to be
  server-side, since the client must never receive rows it then hides.
*/
export function useTableFilters({ searchKeys = [], statusKey = 'status' } = {}) {
  const route = useRoute()

  const search = computed(() => String(route.query.search ?? '').trim().toLowerCase())
  const status = computed(() => String(route.query.status ?? ''))

  function apply(rows) {
    return rows.filter((row) => {
      if (status.value && row[statusKey] !== status.value) return false
      if (!search.value) return true
      return searchKeys.some((key) => String(row[key] ?? '').toLowerCase().includes(search.value))
    })
  }

  const isFiltered = computed(() => !!search.value || !!status.value)

  return { search, status, isFiltered, apply }
}
