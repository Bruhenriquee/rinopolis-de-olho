-- Rinópolis de Olho: painel completo (moderadores, histórico e bloqueio de aparelhos).
-- Rode DEPOIS do supabase.sql. Cole tudo no SQL Editor e clique em Run. Pode rodar de novo sem problema.

-- ---------- Moderadores ----------
-- quem já estava na lista vira "dono"; quem você adicionar pelo painel entra como "moderador"
alter table public.admins add column if not exists papel text not null default 'moderador' check (papel in ('dono','moderador'));
alter table public.admins add column if not exists criado timestamptz not null default now();
update public.admins set papel = 'dono' where papel = 'moderador' and criado <= now() and not exists (select 1 from public.admins where papel = 'dono');

create or replace function public.is_dono() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.admins where lower(email) = lower(auth.jwt() ->> 'email') and papel = 'dono');
$$;

create or replace function public.meu_papel() returns text
language sql stable security definer set search_path = public as $$
  select papel from public.admins where lower(email) = lower(auth.jwt() ->> 'email');
$$;
grant execute on function public.meu_papel to anon, authenticated;

drop policy if exists "equipe ve" on public.admins;
create policy "equipe ve" on public.admins for select to authenticated using (public.is_admin());
drop policy if exists "dono adiciona" on public.admins;
create policy "dono adiciona" on public.admins for insert to authenticated with check (public.is_dono() and papel = 'moderador');
drop policy if exists "dono remove" on public.admins;
create policy "dono remove" on public.admins for delete to authenticated using (public.is_dono() and papel = 'moderador');

-- ---------- Aparelhos bloqueados ----------
create table if not exists public.bloqueios (
  autor text primary key,
  motivo text check (char_length(motivo) <= 200),
  criado timestamptz not null default now()
);
alter table public.bloqueios enable row level security;
drop policy if exists "quem cuida" on public.bloqueios;
create policy "quem cuida" on public.bloqueios for all to authenticated using (public.is_admin()) with check (public.is_admin());

create or replace function public.checar_bloqueio(h text) returns void
language plpgsql stable security definer set search_path = public as $$
begin
  if exists (select 1 from public.bloqueios where autor = h) then
    raise exception 'aparelho bloqueado';
  end if;
end $$;

-- as funções dos moradores passam a recusar aparelho bloqueado
create or replace function public.criar_reclamacao(p_tipo text, p_lat double precision, p_lon double precision,
  p_rua text, p_perto text, p_texto text, p_tem_foto boolean, p_segredo text) returns uuid
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo); novo uuid;
begin
  perform public.checar_bloqueio(h);
  if (select count(*) from public.reclamacoes where autor = h and criado > now() - interval '1 hour') >= 5 then
    raise exception 'limite de 5 marcações por hora';
  end if;
  insert into public.reclamacoes (tipo, lat, lon, rua, perto, texto, tem_foto, autor)
  values (p_tipo, p_lat, p_lon, left(p_rua,120), left(p_perto,160), nullif(left(p_texto,160),''), coalesce(p_tem_foto,false), h)
  returning id into novo;
  return novo;
end $$;

create or replace function public.apoiar(p_id uuid, p_segredo text, p_tipo text) returns text
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo); atual text; resultado text;
begin
  perform public.checar_bloqueio(h);
  if p_tipo not in ('ve','ok') then raise exception 'tipo inválido'; end if;
  if exists (select 1 from public.reclamacoes where id = p_id and autor = h) and p_tipo = 've' then
    raise exception 'quem marcou não confirma a própria placa';
  end if;
  select tipo into atual from public.apoios where reclamacao = p_id and autor = h;
  if atual = p_tipo then
    delete from public.apoios where reclamacao = p_id and autor = h;
    resultado := '';
  else
    insert into public.apoios (reclamacao, autor, tipo) values (p_id, h, p_tipo)
    on conflict (reclamacao, autor) do update set tipo = excluded.tipo, criado = now();
    resultado := p_tipo;
  end if;
  if resultado = 've' then
    update public.reclamacoes set visto = now() where id = p_id;
  end if;
  if (select count(*) from public.apoios where reclamacao = p_id and tipo = 'ok') >= 2 then
    update public.reclamacoes set resolvido = now() where id = p_id and resolvido is null;
  end if;
  return resultado;
end $$;

create or replace function public.confirmar_conserto(p_id uuid, p_segredo text) returns boolean
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo);
begin
  perform public.checar_bloqueio(h);
  if exists (select 1 from public.reclamacoes where id = p_id and autor = h) then
    update public.reclamacoes set resolvido = now() where id = p_id and resolvido is null;
    return true;
  end if;
  insert into public.apoios (reclamacao, autor, tipo) values (p_id, h, 'ok')
  on conflict (reclamacao, autor) do update set tipo = 'ok', criado = now();
  if (select count(*) from public.apoios where reclamacao = p_id and tipo = 'ok') >= 2 then
    update public.reclamacoes set resolvido = now() where id = p_id and resolvido is null;
  end if;
  return false;
end $$;

create or replace function public.enviar_foto(p_id uuid, p_tipo text, p_foto text, p_segredo text) returns void
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo); k text;
begin
  perform public.checar_bloqueio(h);
  if p_tipo = 'antes' then
    if not exists (select 1 from public.reclamacoes where id = p_id and autor = h) then
      raise exception 'só quem marcou manda a foto do problema';
    end if;
    k := p_id::text;
  elsif p_tipo = 'depois' then
    k := p_id::text || '_d';
  else
    raise exception 'tipo inválido';
  end if;
  insert into public.fotos_pendentes (chave, reclamacao, tipo, foto, autor) values (k, p_id, p_tipo, p_foto, h)
  on conflict (chave) do update set foto = excluded.foto, autor = excluded.autor, criado = now();
  if p_tipo = 'antes' then
    update public.reclamacoes set tem_foto = true where id = p_id;
  else
    update public.reclamacoes set tem_foto_depois = true where id = p_id;
  end if;
end $$;

-- ---------- Histórico: o banco anota sozinho tudo o que a equipe faz ----------
create table if not exists public.historico (
  id bigserial primary key,
  quando timestamptz not null default now(),
  quem text not null,
  acao text not null,
  detalhe text
);
alter table public.historico enable row level security;
drop policy if exists "equipe ve" on public.historico;
create policy "equipe ve" on public.historico for select to authenticated using (public.is_admin());

create or replace function public.anotar(p_acao text, p_detalhe text) returns void
language sql security definer set search_path = public as $$
  insert into public.historico (quem, acao, detalhe) values (coalesce(auth.jwt() ->> 'email', '?'), p_acao, p_detalhe);
$$;

create or replace function public.h_reclamacoes() returns trigger
language plpgsql security definer set search_path = public as $$
declare d text;
begin
  if not public.is_admin() then return null; end if;
  if tg_op = 'DELETE' then
    perform public.anotar('apagou placa', old.tipo || ' · ' || coalesce(old.rua,''));
    return null;
  end if;
  d := new.tipo || ' · ' || coalesce(new.rua,'');
  if old.resolvido is null and new.resolvido is not null then perform public.anotar('marcou consertado', d); end if;
  if old.resolvido is not null and new.resolvido is null then perform public.anotar('reabriu placa', d); end if;
  if new.resposta is distinct from old.resposta then
    perform public.anotar(case when new.resposta is null then 'tirou resposta' else 'respondeu: ' || coalesce(new.resposta ->> 'status','') end, d);
  end if;
  return null;
end $$;
drop trigger if exists h_reclamacoes on public.reclamacoes;
create trigger h_reclamacoes after update or delete on public.reclamacoes for each row execute function public.h_reclamacoes();

create or replace function public.h_fotos() returns trigger
language plpgsql security definer set search_path = public as $$
declare d text;
begin
  if not public.is_admin() then return null; end if;
  if tg_table_name = 'fotos_publicas' and tg_op = 'INSERT' then
    select r.tipo || ' · ' || coalesce(r.rua,'') into d from public.reclamacoes r where r.id = new.reclamacao;
    perform public.anotar('aprovou foto', d);
  elsif tg_table_name = 'fotos_pendentes' and tg_op = 'DELETE'
        and not exists (select 1 from public.fotos_publicas where chave = old.chave) then
    select r.tipo || ' · ' || coalesce(r.rua,'') into d from public.reclamacoes r where r.id = old.reclamacao;
    perform public.anotar('recusou foto', d);
  end if;
  return null;
end $$;
drop trigger if exists h_fotos_publicas on public.fotos_publicas;
create trigger h_fotos_publicas after insert on public.fotos_publicas for each row execute function public.h_fotos();
drop trigger if exists h_fotos_pendentes on public.fotos_pendentes;
create trigger h_fotos_pendentes after delete on public.fotos_pendentes for each row execute function public.h_fotos();

create or replace function public.h_equipe() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_table_name = 'admins' then
    if tg_op = 'INSERT' then perform public.anotar('adicionou moderador', new.email);
    else perform public.anotar('removeu moderador', old.email); end if;
  else
    if tg_op = 'INSERT' then perform public.anotar('bloqueou aparelho', coalesce(new.motivo,''));
    else perform public.anotar('desbloqueou aparelho', coalesce(old.motivo,'')); end if;
  end if;
  return null;
end $$;
drop trigger if exists h_admins on public.admins;
create trigger h_admins after insert or delete on public.admins for each row execute function public.h_equipe();
drop trigger if exists h_bloqueios on public.bloqueios;
create trigger h_bloqueios after insert or delete on public.bloqueios for each row execute function public.h_equipe();
