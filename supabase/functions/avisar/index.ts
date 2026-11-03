// Rinópolis de Olho: manda o aviso no celular de quem acompanha uma placa.
// O próprio banco chama esta função (supabase-avisos.sql) quando uma placa é consertada ou a prefeitura responde.
// Não confia no pedido: relê a placa e só avisa quem ainda não recebeu aquele estado.
// Segredos (Edge Functions → Secrets): VAPID_PUBLICA e VAPID_PRIVADA. SUPABASE_URL e a chave de serviço o Supabase já põe sozinho.
import webpush from 'npm:web-push@3.6.7';
import { createClient } from 'npm:@supabase/supabase-js@2.45.4';

const SITE = Deno.env.get('SITE_LINK') ?? 'https://bruhenriquee.github.io/rinopolis-de-olho/';
const TIPOS: Record<string, string> = { buraco: 'Buraco', luz: 'Luz apagada', lixo: 'Lixo ou entulho', agua: 'Esgoto', mato: 'Mato alto', outro: 'Problema' };
const RESPOSTAS: Record<string, string> = { vimos: 'a prefeitura viu', agendado: 'o conserto foi agendado', obra: 'está em obra' };

webpush.setVapidDetails('mailto:contato@rinopolisdeolho.com.br', Deno.env.get('VAPID_PUBLICA')!, Deno.env.get('VAPID_PRIVADA')!);
const db = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!);

Deno.serve(async (req) => {
  const { id } = await req.json().catch(() => ({}));
  if (typeof id !== 'string') return new Response('sem placa', { status: 400 });
  const { data: r } = await db.from('reclamacoes').select('id,tipo,rua,criado,resolvido,resposta').eq('id', id).maybeSingle();
  if (!r) return new Response('placa não existe', { status: 404 });
  const estado = r.resolvido ? 'feito' : (r.resposta?.status ?? '');
  if (!estado) return new Response('nada a avisar');

  // marca antes de mandar: se a função for chamada duas vezes, ninguém recebe o aviso repetido
  const { data: lista, error } = await db.from('avisos').update({ avisado: estado })
    .eq('reclamacao', id).neq('avisado', estado).select('endpoint,p256dh,auth');
  if (error) return new Response(error.message, { status: 500 });

  const oque = `${TIPOS[r.tipo] ?? 'Problema'} na ${r.rua || 'cidade'}`;
  const dias = Math.max(1, Math.round((Date.parse(r.resolvido ?? '') - Date.parse(r.criado)) / 864e5));
  const aviso = estado === 'feito'
    ? { titulo: 'Consertaram!', texto: `${oque}: consertado em ${dias} ${dias === 1 ? 'dia' : 'dias'}.` }
    : { titulo: 'A prefeitura respondeu', texto: `${oque}: ${RESPOSTAS[estado] ?? 'tem novidade'}.` };
  const corpo = JSON.stringify({ ...aviso, url: SITE + '#p-' + id, tag: 'placa-' + id });

  let enviados = 0;
  for (const a of lista ?? []) {
    try {
      await webpush.sendNotification({ endpoint: a.endpoint, keys: { p256dh: a.p256dh, auth: a.auth } }, corpo, { TTL: 7 * 86400 });
      enviados++;
    } catch (e) {
      const s = (e as { statusCode?: number }).statusCode;
      // o celular desligou os avisos ou apagou o site: esquece esse endereço
      if (s === 404 || s === 410) await db.from('avisos').delete().eq('endpoint', a.endpoint);
      else console.error(s, e);
    }
  }
  return new Response(`avisos enviados: ${enviados}`);
});
