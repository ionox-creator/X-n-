// Capital Auditor Service Worker — ALWAYS FRESH
// Every URL open fetches the latest version from the server.
// Cache is ONLY used as offline fallback — never served by default.

const CACHE_NAME = 'capital-auditor-v4';

self.addEventListener('install', (event) => {
  // Don't pre-cache anything — let it load fresh
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // Delete ALL old caches on activation
  event.waitUntil(
    caches.keys().then((names) => Promise.all(names.map((n) => caches.delete(n))))
  );
  self.clients.claim();
  // Tell all clients to reload so they get fresh content
  self.clients.matchAll().then((clients) => {
    clients.forEach((client) => client.postMessage({ type: 'FORCE_RELOAD' }));
  });
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // API calls — never cache, always pass through
  if (url.pathname.startsWith('/api/')) return;

  // For ALL requests: try network first, cache only as offline backup
  event.respondWith(
    fetch(event.request, { cache: 'no-store' })
      .then((response) => {
        if (response && response.status === 200) {
          // Update cache in background (for offline use later)
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone)).catch(() => {});
        }
        return response;
      })
      .catch(() => {
        // OFFLINE — only then serve from cache
        return caches.match(event.request).then((cached) => {
          if (cached) return cached;
          // Last resort: try serving the main page
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }
          return new Response('Offline', { status: 503 });
        });
      })
  );
});
