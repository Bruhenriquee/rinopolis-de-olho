/* Rinópolis de Olho: permite instalar o site no celular.
   Sempre busca a versão nova na internet; o que fica guardado só aparece quando está sem sinal.
   Não guarda nada do banco de dados (outro endereço), só os arquivos do próprio site. */
const CACHE = 'rdo-v1';
const BASE = ['./', './ruas.js', './config.js', './icone-192.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  e.respondWith(
    fetch(e.request)
      .then(r => { const copia = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copia)); return r; })
      .catch(() => caches.match(e.request).then(r => r || caches.match('./')))
  );
});
