const CACHE_VERSION = "v3";
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const PRECACHE_URLS = [
  "/",
  "/static/css/styles.css",
  "/static/logo.png",
  "/static/manifest.webmanifest"
];
self.addEventListener("install", event => {
  event.waitUntil(caches.open(STATIC_CACHE).then(cache => cache.addAll(PRECACHE_URLS)));
});
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== STATIC_CACHE).map(k => caches.delete(k))))
  );
});
self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.method !== "GET") return;
  if (PRECACHE_URLS.some(u => req.url.includes(u.replace("/", "")))) {
    event.respondWith(caches.match(req).then(cached => cached || fetch(req)));
    return;
  }
  event.respondWith(
    fetch(req).then(res => {
      const clone = res.clone();
      caches.open(STATIC_CACHE).then(cache => cache.put(req, clone));
      return res;
    }).catch(() => caches.match(req))
  );
});
