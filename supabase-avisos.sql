-- Rinópolis de Olho: aviso no celular quando consertarem ou a prefeitura responder uma placa que a pessoa acompanha.
-- Rode depois dos outros arquivos .sql, no SQL Editor do Supabase. Pode rodar de novo sem problema.
-- O aviso sai pela função "avisar" (supabase/functions/avisar), que o próprio banco chama.

create extension if not exists pg_net with schema extensions;

-- quem pediu aviso de cada placa. "endpoint" é o endereço de aviso que o navegador cria; não identifica a pessoa.
-- "avisado" é o último estado da placa que esse celular já recebeu ('feito' ou a resposta da prefeitura)
create table if not exists public.avisos (
  endpoint text not null check (char_length(endpoint) <= 800 and endpoint ~ '^https://(fcm\.googleapis\.com|updates\.push\.services\.mozilla\.com|web\.push\.apple\.com|[a-z0-9.-]+\.notify\.windows\.com)/'),
  p256dh text not null check (char_length(p256dh) <= 200),
  auth text not null check (char_length(auth) <= 100),
  reclamacao uuid not null references public.reclamacoes(id) on delete cascade,
  autor text not null,
  avisado text not null default '',
  criado timestamptz not null default now(),
  primary key (endpoint, reclamacao)
);
-- sem regra de leitura: pelo site ninguém lê esta tabela; só as funções abaixo e a função "avisar"
alter table public.avisos enable row level security;

create or replace function public.estado_aviso(r public.reclamacoes) returns text
language sql stable set search_path = public as $$
  select case when r.resolvido is not null then 'feito' else coalesce(r.resposta ->> 'status', '') end;
$$;

-- o celular passa a receber aviso destas placas (já começa sabendo o estado de agora)
create or replace function public.quero_aviso(p_endpoint text, p_p256dh text, p_auth text, p_ids uuid[], p_segredo text) returns void
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo);
begin
  perform public.checar_bloqueio(h);
  if coalesce(array_length(p_ids, 1), 0) > 100
     or (select count(*) from public.avisos where endpoint = p_endpoint) >= 200 then
    raise exception 'placas demais';
  end if;
  insert into public.avisos (endpoint, p256dh, auth, reclamacao, autor, avisado)
    select p_endpoint, p_p256dh, p_auth, r.id, h, public.estado_aviso(r) from public.reclamacoes r where r.id = any(p_ids)
  on conflict (endpoint, reclamacao) do update set p256dh = excluded.p256dh, auth = excluded.auth, autor = excluded.autor;
end $$;

-- para de avisar de uma placa (ou de todas, sem p_id)
create or replace function public.nao_quero_aviso(p_endpoint text, p_id uuid default null) returns void
language sql security definer set search_path = public as $$
  delete from public.avisos where endpoint = p_endpoint and (p_id is null or reclamacao = p_id);
$$;

grant execute on function public.quero_aviso, public.nao_quero_aviso to anon, authenticated;

-- quando a placa é consertada ou a prefeitura responde, chama a função "avisar"
create or replace function public.disparar_aviso() returns trigger
language plpgsql security definer set search_path = public as $$
declare antes text := public.estado_aviso(old); agora text := public.estado_aviso(new);
begin
  if agora = '' or agora = antes or antes = 'feito' then return null; end if;
  -- quem disse "já consertaram", ou quem fechou a própria placa, já sabe: não recebe o aviso
  if agora = 'feito' then
    update public.avisos a set avisado = 'feito' where a.reclamacao = new.id and (
      exists (select 1 from public.apoios p where p.reclamacao = new.id and p.autor = a.autor and p.tipo = 'ok')
      or (a.autor = new.autor and auth.jwt() ->> 'email' is null
          and (select count(*) from public.apoios p where p.reclamacao = new.id and p.tipo = 'ok') < 2));
  end if;
  perform net.http_post(url := 'https://ajrxqmnctrmdfvtrkejz.supabase.co/functions/v1/avisar',
                        body := jsonb_build_object('id', new.id));
  return null;
end $$;
drop trigger if exists disparar_aviso on public.reclamacoes;
create trigger disparar_aviso after update of resolvido, resposta on public.reclamacoes
  for each row execute function public.disparar_aviso();
