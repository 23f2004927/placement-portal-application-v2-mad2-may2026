/*
  Service worker — hand-written rather than a Vite PWA plugin, to keep the
  dependency list inside the permitted stack and the behaviour readable.

  Deliberately conservative:
    - the app shell is cached so "Add to Home Screen" opens instantly offline
    - /api/ is NEVER cached. Placement data is per-user and authorised; a
      cached API response could be shown to the wrong account after a logout.
*/

const CACHE = 'ppa-shell-v1'
const SHELL = ['/', '/index.html', '/manifest.webmanifest', '/icon-192.png', '/icon-512.png']

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)))
  self.skipWaiting()
})

// Drop caches from older versions, otherwise a stale shell survives a deploy.
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))),
  )
  self.clients.claim()
})

self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  if (request.method !== 'GET') return
  if (url.origin !== self.location.origin) return
  if (url.pathname.startsWith('/api/')) return

  // Navigations: try the network, fall back to the cached shell when offline.
  if (request.mode === 'navigate') {
    event.respondWith(fetch(request).catch(() => caches.match('/index.html')))
    return
  }

  // Static assets: serve from cache, and fill the cache on first use.
  event.respondWith(
    caches.match(request).then(
      (hit) =>
        hit ||
        fetch(request).then((response) => {
          const copy = response.clone()
          caches.open(CACHE).then((c) => c.put(request, copy))
          return response
        }),
    ),
  )
})
