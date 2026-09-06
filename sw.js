const CACHE_NAME = "tjpe-2026-pwa-v1.0.1";

const PRECACHE_ASSETS = [
  "./",
  "./index.html",
  "./cronograma_interativo_tjpe_2026.html",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-192.png",
  "./icons/icon-maskable-512.png",
  "./icons/favicon.png",
  "./icons/favicon-32.png",
  "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"
];

// Instalação: Pré-cache dos ativos vitais
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[Service Worker] Pré-cacheando ativos da aplicação offline...");
      return cache.addAll(PRECACHE_ASSETS).catch((err) => {
        console.warn("[Service Worker] Aviso: alguns recursos externos podem não ter sido pré-cacheados imediatamente:", err);
      });
    }).then(() => self.skipWaiting())
  );
});

// Ativação: Limpeza de caches obsoletos
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log("[Service Worker] Removendo cache obsoleto:", cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Interceptação de Requisições: Stale-While-Revalidate com Fallback Offline
self.addEventListener("fetch", (event) => {
  // Ignorar esquemas não-HTTP(S) como chrome-extension ou file
  if (!event.request.url.startsWith("http")) return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Retorna imediatamente o cache e atualiza em segundo plano (Stale-While-Revalidate)
        fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, networkResponse);
            });
          }
        }).catch(() => {
          // Offline, ignora erro de fetch em segundo plano
        });
        return cachedResponse;
      }

      // Se não estava no cache, tenta a rede
      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== "basic") {
          return networkResponse;
        }

        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });

        return networkResponse;
      }).catch(() => {
        // Fallback offline se for requisição de navegação
        if (event.request.mode === "navigate") {
          return caches.match("./index.html");
        }
      });
    })
  );
});
