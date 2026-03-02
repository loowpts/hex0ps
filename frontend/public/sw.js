/**
 * Service Worker — кэширование и оффлайн режим.
 *
 * Стратегии:
 * - Статика React: cache-first (всегда)
 * - GET /api/tasks/ и /api/tasks/{id}/: stale-while-revalidate, TTL 5 минут
 * - GET /api/notes/: offline-first (мгновенный кэш)
 * - GET /api/analytics/me/: stale-while-revalidate, TTL 1 час
 */

const STATIC_CACHE = 'hexops-static-v1'
const API_CACHE = 'hexops-api-v1'

const STATIC_ASSETS = [
  '/',
  '/index.html',
]

// TTL в секундах
const CACHE_TTL = {
  tasks: 5 * 60,       // 5 минут
  notes: 0,            // offline-first (без TTL)
  analytics: 60 * 60,  // 1 час
}

// ─── Install ─────────────────────────────────────────────────────────────────

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS))
  )
  self.skipWaiting()
})

// ─── Activate ────────────────────────────────────────────────────────────────

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== STATIC_CACHE && k !== API_CACHE)
          .map((k) => caches.delete(k))
      )
    )
  )
  self.clients.claim()
})

// ─── Helpers ─────────────────────────────────────────────────────────────────

function isExpired(response, ttl) {
  if (!ttl) return false
  const dateHeader = response.headers.get('sw-cached-at')
  if (!dateHeader) return false
  const cachedAt = parseInt(dateHeader, 10)
  return Date.now() - cachedAt > ttl * 1000
}

async function fetchAndCache(request, cacheName, ttl) {
  const response = await fetch(request)
  if (response.ok && request.method === 'GET') {
    const cache = await caches.open(cacheName)
    // Добавляем заголовок времени кэширования
    const headers = new Headers(response.headers)
    headers.set('sw-cached-at', String(Date.now()))
    const cachedResponse = new Response(await response.clone().arrayBuffer(), {
      status: response.status,
      statusText: response.statusText,
      headers,
    })
    cache.put(request, cachedResponse)
  }
  return response
}

// ─── Fetch ───────────────────────────────────────────────────────────────────

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)

  // Только GET запросы
  if (event.request.method !== 'GET') return

  // Статика (HTML, JS, CSS, images)
  if (!url.pathname.startsWith('/api/')) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        if (cached) return cached
        return fetch(event.request).then((response) => {
          if (response.ok) {
            caches.open(STATIC_CACHE).then((cache) => cache.put(event.request, response.clone()))
          }
          return response
        }).catch(() => caches.match('/index.html'))
      })
    )
    return
  }

  // /api/notes/ — offline-first
  if (url.pathname.startsWith('/api/notes/')) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        const networkFetch = fetchAndCache(event.request, API_CACHE, CACHE_TTL.notes)
        return cached || networkFetch
      })
    )
    return
  }

  // /api/tasks/ — stale-while-revalidate, TTL 5 минут
  if (
    url.pathname.startsWith('/api/tasks/') ||
    url.pathname === '/api/tasks/'
  ) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        const networkFetch = fetchAndCache(event.request, API_CACHE, CACHE_TTL.tasks)
        if (cached && !isExpired(cached, CACHE_TTL.tasks)) {
          return cached
        }
        return networkFetch.catch(() => cached || new Response('{}', { status: 503 }))
      })
    )
    return
  }

  // /api/analytics/me/ — stale-while-revalidate, TTL 1 час
  if (url.pathname.startsWith('/api/analytics/')) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        const networkFetch = fetchAndCache(event.request, API_CACHE, CACHE_TTL.analytics)
        if (cached && !isExpired(cached, CACHE_TTL.analytics)) {
          return cached
        }
        return networkFetch.catch(() => cached || new Response('{}', { status: 503 }))
      })
    )
    return
  }
})
