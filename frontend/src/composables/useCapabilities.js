import { computed, unref } from 'vue'

/*
  Reads the `capabilities` block the list endpoints return:

    { revoke:    { allowedFrom: ['applied', 'shortlisted'] },
      setStatus: { options: [...], allowedFrom: [...] } }

  The block is advertised once per response, not per row — `can()` compares a
  row's current status against `allowedFrom` locally.

  This is a UI hint. Every action endpoint re-checks role, ownership and status
  server-side, because a client can call it without ever reading this.
*/
export function useCapabilities(source) {
  const capabilities = computed(() => unref(source) ?? {})

  function can(action, row) {
    const rule = capabilities.value[action]
    if (!rule) return false
    if (!rule.allowedFrom) return true
    return rule.allowedFrom.includes(row?.status)
  }

  function optionsFor(action) {
    return capabilities.value[action]?.options ?? []
  }

  return { capabilities, can, optionsFor }
}
