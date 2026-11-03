/* Rinópolis de Olho: permite instalar o site no celular.
   Sempre busca a versão nova na internet; o que fica guardado só aparece quando está sem sinal.
   Não guarda nada do banco de dados (outro endereço), só os arquivos do próprio site. */
const CACHE = 'rdo-v2';
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

/* aviso no celular (consertaram, prefeitura respondeu): chega mesmo com o site fechado */
self.addEventListener('push', e => {
  let d = {}; try { d = e.data ? e.data.json() : {}; } catch (err) {}
  e.waitUntil(self.registration.showNotification(d.titulo || 'Rinópolis de Olho', {
    body: d.texto || 'Tem novidade numa placa que você acompanha.', icon: './icone-192.png', badge: './icone-192.png',
    tag: d.tag, data: {url: d.url || './'}
  }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = new URL(e.notification.data.url, self.registration.scope).href;
  e.waitUntil(clients.matchAll({type: 'window', includeUncontrolled: true}).then(abertos => {
    const aba = abertos.find(c => c.url.startsWith(self.registration.scope));
    return aba ? aba.navigate(url).then(c => c && c.focus()) : clients.openWindow(url);
  }));
});
