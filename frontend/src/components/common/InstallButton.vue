<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

/*
  "Add to Home Screen", made explicit.

  Chrome and Edge fire `beforeinstallprompt` when the page qualifies as
  installable (manifest + service worker + https or localhost). Calling
  preventDefault() suppresses the browser's own mini-banner so we can offer the
  prompt from a button the user can actually find.

  iOS Safari never fires this event — installing there is Share → Add to Home
  Screen — so the button simply stays hidden rather than lying about being
  available.
*/
const deferred = ref(null)
const installed = ref(false)

function capture(event) {
  event.preventDefault()
  deferred.value = event
}

function onInstalled() {
  installed.value = true
  deferred.value = null
}

async function install() {
  if (!deferred.value) return
  deferred.value.prompt()
  await deferred.value.userChoice
  // The event is single-use: once prompted it cannot be replayed.
  deferred.value = null
}

onMounted(() => {
  window.addEventListener('beforeinstallprompt', capture)
  window.addEventListener('appinstalled', onInstalled)
})

onUnmounted(() => {
  window.removeEventListener('beforeinstallprompt', capture)
  window.removeEventListener('appinstalled', onInstalled)
})
</script>

<template>
  <BButton v-if="deferred && !installed" variant="outline-primary" size="sm" @click="install">
    Install app
  </BButton>
</template>
