<script setup>
import { computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '@/stores/auth'
import { navByRole } from '@/config/nav'

/*
  Collapsed is the resting state. Expansion is driven by :hover in CSS rather
  than a JS ref — no listeners, no flicker on fast pointer movement, and the
  transition stays interruptible. `pinned` is the only thing JS owns.
*/
defineProps({
  pinned: { type: Boolean, default: false },
})

const auth = useAuth()
const router = useRouter()

const items = computed(() => navByRole[auth.role] ?? [])
const profileRoute = computed(() => ({ name: `${auth.role}-profile` }))

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <aside class="sidebar" :class="{ 'is-pinned': pinned }">
    <RouterLink :to="auth.homeRoute" class="brand">
      <span class="rail-only">PP</span>
      <span class="wide-only">Placement<span class="brand-accent">Portal</span></span>
    </RouterLink>

    <nav class="side-nav">
      <RouterLink
        v-for="item in items"
        :key="item.label"
        :to="item.to"
        class="side-link"
        exact-active-class="is-exact"
        :title="item.label"
      >
        <span class="rail-only">{{ item.short }}</span>
        <span class="wide-only">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="side-foot">
      <RouterLink :to="profileRoute" class="role-chip" :title="`${auth.userName} — profile`">
        <span class="rail-only">{{ auth.role?.charAt(0) }}</span>
        <span class="wide-only">{{ auth.role }}</span>
      </RouterLink>

      <button type="button" class="signout" title="Sign out" @click="handleLogout">
        <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
          <path
            d="M10 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4M16 17l5-5-5-5M21 12H10"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="square"
          />
        </svg>
        <span class="wide-only">Sign out</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
/*
  Absolutely positioned so expanding floats over the content instead of
  reflowing it — the grid keeps reserving only the rail width.
*/
.sidebar {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 20;
  width: 64px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border);
  background: var(--surface);
  overflow: hidden;
  transition: width 0.18s ease;
}

.sidebar:hover,
.sidebar.is-pinned {
  width: 240px;
}

/* Visibility is the CSS half of the hover behaviour: both labels are always
   rendered, and width state decides which one is shown. */
.wide-only {
  display: none;
  white-space: nowrap;
}

.sidebar:hover .wide-only,
.sidebar.is-pinned .wide-only {
  display: inline;
}

.sidebar:hover .rail-only,
.sidebar.is-pinned .rail-only {
  display: none;
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  min-height: 64px;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  text-decoration: none;
  flex-shrink: 0;
}

.sidebar:hover .brand,
.sidebar.is-pinned .brand {
  justify-content: flex-start;
}

.brand .rail-only {
  color: var(--primary);
}

.brand-accent {
  color: var(--primary);
  margin-left: 6px;
}

.side-nav {
  display: flex;
  flex-direction: column;
  padding: 16px 0;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  min-height: 0;
}

.side-link {
  padding: 10px 0;
  border-left: 2px solid transparent;
  color: var(--text-muted);
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  text-decoration: none;
  text-align: center;
  transition:
    color 0.15s ease,
    border-color 0.15s ease,
    background 0.15s ease;
}

.sidebar:hover .side-link,
.sidebar.is-pinned .side-link {
  padding: 10px 20px;
  text-align: left;
}

.side-link:hover {
  color: var(--text);
  background: var(--bg);
}

/* router-link-active matches by prefix, so the index route would stay lit on
   every sibling page. Only the exact match is styled. */
.side-link.is-exact {
  color: var(--primary);
  border-left-color: var(--primary);
  background: var(--primary-soft);
}

.side-foot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}

.sidebar:hover .side-foot,
.sidebar.is-pinned .side-foot {
  flex-direction: row;
  justify-content: space-between;
  padding: 12px 16px;
}

.role-chip {
  display: inline-block;
  padding: 3px 8px;
  border: 1px solid var(--border-strong);
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-decoration: none;
  white-space: nowrap;
  transition:
    color 0.15s ease,
    border-color 0.15s ease;
}

.role-chip:hover {
  color: var(--primary);
  border-color: var(--primary);
  background: var(--primary-soft);
}

.signout {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: none;
  border: 0;
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: color 0.15s ease;
}

.signout:hover {
  color: var(--primary);
}

/*
  No hover on touch, and no room to float — the sidebar becomes a static
  horizontal strip and the rail/wide distinction is dropped.
*/
@media (max-width: 767px) {
  .sidebar,
  .sidebar:hover,
  .sidebar.is-pinned {
    position: static;
    grid-area: sidebar;
    width: auto;
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }

  .brand {
    display: none;
  }

  .rail-only,
  .sidebar:hover .rail-only,
  .sidebar.is-pinned .rail-only {
    display: none;
  }

  .wide-only,
  .sidebar .wide-only {
    display: inline;
  }

  .side-nav {
    flex-direction: row;
    padding: 0;
    overflow-x: auto;
  }

  .side-link,
  .sidebar:hover .side-link {
    padding: 12px 16px;
    border-left: 0;
    border-bottom: 2px solid transparent;
    white-space: nowrap;
  }

  .side-link.is-exact {
    border-left: 0;
    border-bottom-color: var(--primary);
  }

  .side-foot,
  .sidebar:hover .side-foot {
    flex-direction: row;
    justify-content: space-between;
    padding: 8px 16px;
  }
}
</style>
