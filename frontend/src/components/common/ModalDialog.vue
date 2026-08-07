<script setup>
import { watch } from 'vue'

/*
  Hand-rolled rather than BModal, for the same reason PublicNavbar avoids
  BNavbar: bootstrap-vue-next's overlay APIs have shifted across versions, and
  this needs exactly one behaviour.
*/
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, required: true },
  confirmText: { type: String, default: 'Confirm' },
  confirmVariant: { type: String, default: 'primary' },
  busy: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'confirm'])

function close() {
  emit('update:modelValue', false)
}

function onKey(event) {
  if (event.key === 'Escape') close()
}

watch(
  () => props.modelValue,
  (open) => {
    document.body.style.overflow = open ? 'hidden' : ''
    if (open) window.addEventListener('keydown', onKey)
    else window.removeEventListener('keydown', onKey)
  },
)
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="backdrop" @click.self="close">
      <div class="panel" role="dialog" aria-modal="true">
        <header class="panel-head">
          <h2>{{ title }}</h2>
          <button type="button" class="close" aria-label="Close" @click="close">&times;</button>
        </header>

        <div class="panel-body">
          <slot />
        </div>

        <footer class="panel-foot">
          <BButton variant="outline-primary" size="sm" @click="close">Cancel</BButton>
          <BButton
            :variant="confirmVariant"
            size="sm"
            :disabled="busy || disabled"
            @click="emit('confirm')"
          >
            {{ busy ? 'Working…' : confirmText }}
          </BButton>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgb(27 26 23 / 45%);
}

.panel {
  width: 100%;
  max-width: 480px;
  max-height: 90dvh;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-strong);
  background: var(--surface);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.panel-head h2 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.close {
  background: none;
  border: 0;
  color: var(--text-muted);
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
}

.close:hover {
  color: var(--text);
}

.panel-body {
  padding: 20px;
  overflow-y: auto;
  font-size: 0.875rem;
}

.panel-foot {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 20px;
  border-top: 1px solid var(--border);
}
</style>
