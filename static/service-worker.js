if ('serviceWorker' in navigator) {
    navigator.serviceWorker
    .register('./service-worker.js')
    .then(function(registration) {
        console.log('Service Worker Registered!');
        return registration;
    })
    .catch(function(err) {
        console.error('Unable to register service worker.', err);
    });
  }
  const CACHE_NAME = 'static-cache';
  
  const FILES_TO_CACHE = [
    
  ];
  
  
  self.addEventListener('install', (evt) => {
      console.log('[ServiceWorker] Install');
      evt.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
          console.log('[ServiceWorker] Pre-caching offline page');
          return cache.addAll(FILES_TO_CACHE);
        })
      );
    
      self.skipWaiting();
    });
  
  
    self.addEventListener('activate', (evt) => {
      console.log('[ServiceWorker] Activate');
      evt.waitUntil(
        caches.keys().then((keyList) => {
          return Promise.all(keyList.map((key) => {
            if (key !== CACHE_NAME) {
              console.log('[ServiceWorker] Removing old cache', key);
              return caches.delete(key);
            }
          }));
        })
      );
      self.clients.claim();
    });
  
  //   self.addEventListener('fetch', function(event) {
  //     event.respondWith(fetch(event.request));
  //   });
  
  //   self.addEventListener('fetch', (evt) => {
  //   if (evt.request.mode !== 'navigate') {
  //     return;
  //   }
  //   evt.respondWith(fetch(evt.request).catch(() => {
  //       return caches.open(CACHE_NAME).then((cache) => {
  //         return cache.match('offline.html');
  //       });
  //     })
  //   );
  // });
  
  self.addEventListener('fetch', function(event) {
      event.respondWith(
        fetch(event.request).catch(function() {
          return caches.match(event.request);
        })
      );
    });
  