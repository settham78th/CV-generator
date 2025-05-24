// Service Worker for CV Optimizer Pro PWA
const CACHE_NAME = 'cv-optimizer-v1.0.0';
const STATIC_CACHE = 'cv-optimizer-static-v1.0.0';
const DYNAMIC_CACHE = 'cv-optimizer-dynamic-v1.0.0';

// Files to cache for offline functionality
const STATIC_FILES = [
  '/',
  '/static/css/custom.css',
  '/static/js/main.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// Install event - cache static files
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Service Worker: Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .catch(err => {
        console.log('Service Worker: Cache failed', err);
      })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== STATIC_CACHE && cache !== DYNAMIC_CACHE) {
            console.log('Service Worker: Clearing old cache', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  const { request } = event;
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Handle API requests differently
  if (request.url.includes('/api/') || request.url.includes('/upload-cv') || request.url.includes('/process-cv')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Cache successful API responses for short time
          if (response.ok && request.url.includes('/upload-cv')) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // For offline, return cached response if available
          return caches.match(request).then(cachedResponse => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // Return offline page for API requests
            return new Response(
              JSON.stringify({
                success: false,
                message: 'Aplikacja jest obecnie offline. Sprawdź połączenie z internetem.'
              }),
              {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
              }
            );
          });
        })
    );
    return;
  }

  // Handle static files with cache-first strategy
  event.respondWith(
    caches.match(request)
      .then(cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }
        
        return fetch(request)
          .then(response => {
            // Cache successful responses
            if (response.ok) {
              const responseClone = response.clone();
              caches.open(DYNAMIC_CACHE).then(cache => {
                cache.put(request, responseClone);
              });
            }
            return response;
          })
          .catch(() => {
            // Return offline page for navigation requests
            if (request.destination === 'document') {
              return caches.match('/').then(cachedHome => {
                return cachedHome || new Response(
                  `<!DOCTYPE html>
                   <html>
                   <head>
                     <title>CV Optimizer Pro - Offline</title>
                     <meta charset="UTF-8">
                     <meta name="viewport" content="width=device-width, initial-scale=1.0">
                     <style>
                       body { font-family: Inter, sans-serif; text-align: center; padding: 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
                       .offline-message { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto; }
                       h1 { color: #667eea; margin-bottom: 1rem; }
                       p { color: #666; margin-bottom: 1.5rem; }
                       .retry-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 24px; border-radius: 12px; cursor: pointer; }
                     </style>
                   </head>
                   <body>
                     <div class="offline-message">
                       <h1>🚀 CV Optimizer Pro</h1>
                       <h2>Jesteś offline</h2>
                       <p>Sprawdź połączenie z internetem i spróbuj ponownie.</p>
                       <button class="retry-btn" onclick="window.location.reload()">Spróbuj ponownie</button>
                     </div>
                   </body>
                   </html>`,
                  { headers: { 'Content-Type': 'text/html' } }
                );
              });
            }
            return new Response('Offline', { status: 503 });
          });
      })
  );
});

// Background sync for failed uploads
self.addEventListener('sync', event => {
  if (event.tag === 'cv-upload-retry') {
    event.waitUntil(retryFailedUploads());
  }
});

// Push notification handling
self.addEventListener('push', event => {
  if (!event.data) return;

  const data = event.data.json();
  const options = {
    body: data.body || 'Twoje CV zostało przetworzone!',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: data.data || {},
    actions: [
      {
        action: 'view',
        title: 'Zobacz wyniki',
        icon: '/static/icons/view-icon.png'
      },
      {
        action: 'close',
        title: 'Zamknij',
        icon: '/static/icons/close-icon.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'CV Optimizer Pro', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Helper function to retry failed uploads
async function retryFailedUploads() {
  // Implementation for retrying failed CV uploads
  console.log('Service Worker: Retrying failed uploads...');
}

// Update notification for new version
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});