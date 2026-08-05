<script setup>
import { computed, ref } from 'vue'
import PublicNavbar from '@/components/layout/PublicNavbar.vue';
import { site } from '@/config/site'

// Static content — the landing page fetches nothing.
// Kept as data so the markup stays one v-for instead of three near-identical blocks.
const features = [
  {
    title: 'Students',
    body: 'Build a profile once, browse every open drive, and track each application from applied to offer.',
  },
  {
    title: 'Companies',
    body: 'Post placement drives, set eligibility criteria, and review applicants from a single dashboard.',
  },
  {
    title: 'Admin',
    body: 'Approve company registrations, oversee drives, and keep the platform clean with full moderation control.',
  },
]

const contacts = [
  { label: 'Email', value: 'placements@example.edu' },
  { label: 'Phone', value: '+91 00000 00000' },
  { label: 'Office', value: 'Placement Cell, Block C, Room 204' },
  { label: 'Hours', value: 'Monday to Friday, 09:00 – 17:00' },
]

/*
  Two separate pieces of state, one derived view of them:
    pinned  — the section the user clicked; survives until they click another
    preview — the section they're hovering; null when the pointer leaves the nav
  `active` prefers the hover so the panel responds instantly, then falls back to
  the pinned section once hovering stops. One computed keeps that rule in one place.
*/
const pinned = ref('home')
const preview = ref(null)
const active = computed(() => preview.value ?? pinned.value)

function handleSelect(key) {
  pinned.value = key
  preview.value = null
}
</script>

<template>
  <div class="landing">
    <PublicNavbar
      :active="active"
      @select="handleSelect"
      @preview="preview = $event"
    />

    <div class="landing-body">
      <!-- Left: constant, never reacts to the nav -->
      <aside class="brand-panel">
        <p class="eyebrow">Campus Recruitment</p>
        <p class="brand-title">Placement<br />Portal</p>
      </aside>

      <!-- Right: swaps with the nav selection -->
      <section class="panel">
        <Transition name="panel-fade" mode="out-in">
          <div :key="active" class="panel-inner">
            <!-- Home -->
            <template v-if="active === 'home'">
              <p class="eyebrow">Campus Recruitment</p>
              <h1 class="panel-title">Run the entire placement cycle in one place.</h1>
              <p class="panel-body">
                Students, recruiters and administrators working from a single record of
                every drive, applicant and outcome.
              </p>
              <div class="cta-row">
                <BButton to="/register/student" variant="primary">Register as Student</BButton>
                <BButton to="/register/company" variant="outline-primary">Register as Company</BButton>
              </div>
            </template>

            <!-- About -->
            <template v-else-if="active === 'about'">
              <p class="eyebrow">About</p>
              <h1 class="panel-title">Built for three roles.</h1>
              <p class="panel-body">
                The portal replaces scattered spreadsheets and mail threads. Students apply
                once against a verified profile, companies see only eligible candidates, and
                administrators keep oversight without sitting in the middle of every exchange.
              </p>
              <dl class="detail-list">
                <div v-for="feature in features" :key="feature.title" class="detail-row">
                  <dt>{{ feature.title }}</dt>
                  <dd>{{ feature.body }}</dd>
                </div>
              </dl>
            </template>

            <!-- Contact -->
            <template v-else-if="active === 'contact'">
              <p class="eyebrow">Contact</p>
              <h1 class="panel-title">Talk to the placement cell.</h1>
              <p class="panel-body">
                Account issues, drive eligibility and company onboarding are all handled here.
              </p>
              <dl class="detail-list">
                <div v-for="contact in contacts" :key="contact.label" class="detail-row">
                  <dt>{{ contact.label }}</dt>
                  <dd>{{ contact.value }}</dd>
                </div>
              </dl>
            </template>

            <!-- Sign in -->
            <template v-else>
              <p class="eyebrow">Sign in</p>
              <h1 class="panel-title">Welcome back.</h1>
              <p class="panel-body">
                Use the credentials issued when your account was approved.
              </p>
              <div class="cta-row">
                <BButton to="/login" variant="primary">Continue to sign in</BButton>
              </div>
              <p class="panel-note">
                No account yet?
                <RouterLink to="/register/student">Register as Student</RouterLink>
                or
                <RouterLink to="/register/company">Register as Company</RouterLink>.
              </p>
            </template>
          </div>
        </Transition>
      </section>
    </div>

    <footer class="site-footer">
      <p class="footer-meta">{{ site.footerMeta.join(' · ') }}</p>
      <nav class="footer-links">
        <!-- External URLs, so plain anchors — RouterLink would try to route them. -->
        <a
          v-for="link in site.footerLinks"
          :key="link.label"
          :href="link.url"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ link.label }}
        </a>
      </nav>
    </footer>
  </div>
</template>

<style scoped>
/* Shell — exactly one viewport tall, never scrolls the document */

.landing {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.landing-body {
  flex: 1;
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  /* Without this a grid child refuses to shrink, and the page scrolls again. */
  min-height: 0;
}

/* Left panel */

.panel {
  display: flex;
  align-items: center;
  padding: 48px 56px;
  /* Overflow is contained here rather than on the document. */
  overflow-y: auto;
}

.panel-inner {
  width: 100%;
  max-width: 34rem;
}

.eyebrow {
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 20px;
}

.panel-title {
  font-size: clamp(2rem, 3.6vw, 3rem);
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -0.02em;
  margin-bottom: 20px;
}

.panel-body {
  max-width: 46ch;
  color: var(--text-muted);
  font-size: 1.0625rem;
  line-height: 1.65;
  margin-bottom: 0;
}

.panel-note {
  margin: 20px 0 0;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.panel-note a {
  color: var(--primary);
  font-weight: 600;
}

/* Definition lists — used by both About and Contact */

.detail-list {
  margin: 28px 0 0;
  border-top: 1px solid var(--border);
}

.detail-row {
  display: grid;
  grid-template-columns: 8rem 1fr;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}

.detail-row dt {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text);
}

.detail-row dd {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.55;
}

/* Buttons */

.cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 32px;
}

/* Left panel — constant */

.brand-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 56px;
  background: var(--surface-alt);
  border-right: 1px solid var(--border);
}

.brand-title {
  font-size: clamp(2.5rem, 6vw, 5rem);
  font-weight: 800;
  line-height: 0.95;
  letter-spacing: -0.03em;
  text-transform: uppercase;
  margin: 0;
}

/* Footer — sits outside the scrollable body, so it never moves */

.site-footer {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 14px 32px;
  border-top: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.footer-meta {
  margin: 0;
  letter-spacing: 0.02em;
}

.footer-links {
  display: flex;
  gap: 20px;
}

.footer-links a {
  color: var(--text-muted);
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-size: 0.75rem;
  text-decoration: none;
}

.footer-links a:hover {
  color: var(--primary);
}

/* Panel swap */

.panel-fade-enter-active,
.panel-fade-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.panel-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.panel-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* Below md the brand panel is dropped rather than stacked — stacking would
   reintroduce a scroll, which is the one thing this layout must not do. */
@media (max-width: 767px) {
  .landing-body {
    grid-template-columns: 1fr;
  }

  .brand-panel {
    display: none;
  }

  .panel {
    padding: 32px 24px;
  }

  .site-footer {
    justify-content: center;
    padding: 12px 16px;
  }
}
</style>
