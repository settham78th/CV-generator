const CACHE_NAME = 'cv-optimizer-pro-v1';
const urlsToCache = [
  '/',
  '/static/css/custom.css',
  '/static/css/modern-premium.css',
  '/static/js/main.js',
  '/static/js/clean-main.js',
  '/static/js/modern-enhanced.js',
  '/manifest.json',
  '/offline',
  // Add commonly used Bootstrap and Font Awesome from CDN
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// Install event
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Return cached version or fetch from network
        if (response) {
          return response;
        }
        
        return fetch(event.request).then(function(response) {
          // Check if we received a valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response
          var responseToCache = response.clone();

          caches.open(CACHE_NAME)
            .then(function(cache) {
              cache.put(event.request, responseToCache);
            });

          return response;
        }).catch(function() {
          // If both cache and network fail, show offline page
          if (event.request.destination === 'document') {
            return caches.match('/offline');
          }
        });
      })
  );
});

// Activate event
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Background sync for form submissions
self.addEventListener('sync', function(event) {
  if (event.tag === 'cv-upload') {
    event.waitUntil(retryFailedUploads());
  }
});

async function retryFailedUploads() {
  const db = await openDB();
  const tx = db.transaction(['uploads'], 'readonly');
  const store = tx.objectStore('uploads');
  const uploads = await store.getAll();
  
  for (const upload of uploads) {
    try {
      const response = await fetch('/upload-cv', {
        method: 'POST',
        body: upload.formData
      });
      
      if (response.ok) {
        // Remove from indexedDB after successful upload
        const deleteTx = db.transaction(['uploads'], 'readwrite');
        const deleteStore = deleteTx.objectStore('uploads');
        await deleteStore.delete(upload.id);
      }
    } catch (error) {
      console.log('Retry failed:', error);
    }
  }
}

// Push notification handler
self.addEventListener('push', function(event) {
  const options = {
    body: event.data ? event.data.text() : 'CV analysis complete!',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-96x96.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'explore',
        title: 'View Results',
        icon: '/static/icons/icon-96x96.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/icons/icon-96x96.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('CV Optimizer Pro', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', function(event) {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});