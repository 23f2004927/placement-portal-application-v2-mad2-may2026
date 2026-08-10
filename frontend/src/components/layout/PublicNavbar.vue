<script setup>
import { useAuth } from '@/stores/auth'
import InstallButton from '@/components/common/InstallButton.vue'

/*
  Public-facing top bar.

  The nav items don't navigate — they drive which panel the landing page shows.
  So this component owns no state: the parent passes the currently active key
  down, and this emits intent back up.
    - `select`  → user committed to a section (click)
    - `preview` → user is hovering a section; null means "hover ended"
*/
const props = defineProps({
  active: { type: String, default: 'home' },
})

const emit = defineEmits(['select', 'preview'])

const auth = useAuth()

const items = [
  { key: 'home', label: 'Home' },
  { key: 'stats', label: 'Placements' },
  { key: 'about', label: 'About' },
  { key: 'contact', label: 'Contact' },
]

</script>

<template>
  <header class="site-nav">
    <div class="site-nav-inner">
      <button type="button" class="brand" @click="emit('select', 'home')">
        Placement<span class="brand-accent">Portal</span>
      </button>

      <nav class="nav-items" @mouseleave="emit('preview', null)">
        <InstallButton />
        <button
          v-for="item in items"
          :key="item.key"
          type="button"
          class="nav-btn"
          :class="{ 'is-active': props.active === item.key }"
          @mouseenter="emit('preview', item.key)"
          @click="emit('select', item.key)"
        >
          {{ item.label }}
        </button>

        <button
          v-if="!auth.isAuthenticated"
          type="button"
          class="nav-btn"
          :class="{ 'is-active': props.active === 'signin' }"
          @mouseenter="emit('preview', 'signin')"
          @click="emit('select', 'signin')"
        >
          Sign in
        </button>

        <BButton v-else :to="auth.homeRoute" variant="primary" size="sm">Dashboard</BButton>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.site-nav {
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  flex-shrink: 0;
}

.site-nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 0 32px;
  min-height: 64px;
}

/* Brand */

.brand {
  background: none;
  border: 0;
  padding: 0;
  color: var(--text);
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  cursor: pointer;
}

.brand-accent {
  color: var(--primary);
  margin-left: 6px;
}

/* Nav items */

.nav-items {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-btn {
  background: none;
  border: 0;
  border-bottom: 2px solid transparent;
  padding: 8px 14px;
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  cursor: pointer;
  transition:
    color 0.15s ease,
    border-color 0.15s ease;
}

.nav-btn:hover {
  color: var(--text);
}

.nav-btn.is-active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

@media (max-width: 575px) {
  .site-nav-inner {
    flex-direction: column;
    gap: 8px;
    padding: 12px 16px;
  }

  .nav-btn {
    padding: 6px 8px;
    font-size: 0.75rem;
  }
}
</style>
