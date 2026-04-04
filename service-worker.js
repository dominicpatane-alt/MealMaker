const CACHE_NAME = 'meal-maker-v2026-04-05e';
const STATIC_ASSETS = [
  './',
  './index.html',
  './PWA/manifest-v2.json',
  './Sprites/sanji-icon-192.png?v=3',
  './Sprites/sanji-icon-512.png?v=3',
  'https://unpkg.com/xlsx@0.18.5/dist/xlsx.full.min.js'
];
const LIVE_DATA_HOSTS = new Set(['script.google.com', 'opensheet.elk.sh']);

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(() => {
        console.log('Some assets failed to cache, continuing anyway');
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => Promise.all(
      cacheNames.map(cacheName => {
        if (cacheName !== CACHE_NAME) {
          return caches.delete(cacheName);
        }
        return Promise.resolve();
      })
    ))
  );
  self.clients.claim();
});

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', event => {
  const { request } = event;

  if (request.method !== 'GET') {
    return;
  }

  const requestUrl = new URL(request.url);
  const acceptsHtml = (request.headers.get('accept') || '').includes('text/html');
  const isNavigationRequest = request.mode === 'navigate' || acceptsHtml;
  const isVersionRequest = requestUrl.origin === self.location.origin && requestUrl.pathname.endsWith('/version.json');
  const isLiveDataRequest = LIVE_DATA_HOSTS.has(requestUrl.hostname);

  if (isLiveDataRequest) {
    event.respondWith(
      fetch(request, { cache: 'no-store' }).catch(() => fetch(request))
    );
    return;
  }

  if (isVersionRequest) {
    event.respondWith(
      fetch(request, { cache: 'no-store' }).catch(() => new Response(JSON.stringify({ version: CACHE_NAME }), {
        status: 200,
        headers: new Headers({
          'Content-Type': 'application/json'
        })
      }))
    );
    return;
  }

  if (isNavigationRequest) {
    event.respondWith(
      fetch(request, { cache: 'no-store' })
        .then(response => {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, responseClone));
          return response;
        })
        .catch(async () => {
          const cachedResponse = await caches.match(request);
          return cachedResponse || caches.match('./index.html') || new Response('Offline - please check internet connection', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
              'Content-Type': 'text/plain'
            })
          });
        })
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(cachedResponse => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(request).then(networkResponse => {
        const responseClone = networkResponse.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, responseClone));
        return networkResponse;
      });
    })
  );
});
