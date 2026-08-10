/*
  v-trim — put it on a <form>, not on each input.

  The problem it solves: HTML5 `required` rejects "" but happily accepts "   ".
  A space-only value then passes the browser, reaches the API, and satisfies a
  NOT NULL column while colliding on a unique index later.

  `v-model.trim` is not the fix — it trims the model but leaves the spaces in
  the DOM, so the field the user is looking at still says something different
  from what was sent.

  This trims on blur (focusout bubbles; blur does not), then re-dispatches an
  input event so v-model picks the change up. Passwords are skipped: leading or
  trailing spaces there are deliberate characters, not typing slips.
*/
export const vTrim = {
  mounted(el) {
    el.addEventListener('focusout', (event) => {
      const field = event.target
      if (!(field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement)) return
      if (field.type === 'password') return

      const trimmed = field.value.trim()
      if (trimmed === field.value) return

      field.value = trimmed
      field.dispatchEvent(new Event('input', { bubbles: true }))
    })
  },
}
