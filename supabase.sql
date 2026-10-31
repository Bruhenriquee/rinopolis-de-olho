-- Rinópolis de Olho: banco de dados no Supabase.
-- Cole tudo no "SQL Editor" do Supabase, troque o e-mail na ÚLTIMA linha pelo seu e clique em Run.
-- Pode rodar de novo sem problema: ele não apaga marcações já feitas.

create extension if not exists pgcrypto with schema extensions;

-- ---------- Tabelas ----------

-- quem cuida do mapa (pode aprovar fotos, marcar consertado, responder e apagar)
create table if not exists public.admins (
  email text primary key
);

-- as placas do mapa. "autor" é um código embaralhado do aparelho de quem marcou; não identifica a pessoa
create table if not exists public.reclamacoes (
  id uuid primary key default gen_random_uuid(),
  criado timestamptz not null default now(),
  tipo text not null check (tipo in ('buraco','luz','lixo','agua','mato','outro')),
  lat double precision not null check (lat between -21.80 and -21.66),
  lon double precision not null check (lon between -50.80 and -50.64),
  rua text check (char_length(rua) <= 120),
  perto text check (char_length(perto) <= 160),
  texto text check (char_length(texto) <= 160),
  tem_foto boolean not null default false,
  tem_foto_depois boolean not null default false,
  autor text not null,
  visto timestamptz,
  resolvido timestamptz,
  resposta jsonb
);

-- "eu também vi" (ve) e "já consertaram" (ok): um por aparelho em cada placa
create table if not exists public.apoios (
  reclamacao uuid not null references public.reclamacoes(id) on delete cascade,
  autor text not null,
  tipo text not null check (tipo in ('ve','ok')),
  criado timestamptz not null default now(),
  primary key (reclamacao, autor)
);

-- fotos esperando conferência: só quem cuida do mapa vê
create table if not exists public.fotos_pendentes (
  chave text primary key,
  reclamacao uuid not null references public.reclamacoes(id) on delete cascade,
  tipo text not null check (tipo in ('antes','depois')),
  foto text not null check (char_length(foto) <= 200000 and foto like 'data:image/jpeg;base64,%'),
  autor text not null,
  criado timestamptz not null default now()
);

-- fotos aprovadas: todo mundo vê
create table if not exists public.fotos_publicas (
  chave text primary key,
  reclamacao uuid not null references public.reclamacoes(id) on delete cascade,
  foto text not null
);

-- ---------- Quem pode o quê ----------

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.admins where lower(email) = lower(auth.jwt() ->> 'email'));
$$;

alter table public.admins enable row level security;
alter table public.reclamacoes enable row level security;
alter table public.apoios enable row level security;
alter table public.fotos_pendentes enable row level security;
alter table public.fotos_publicas enable row level security;

drop policy if exists "todos leem" on public.reclamacoes;
create policy "todos leem" on public.reclamacoes for select using (true);
drop policy if exists "todos leem" on public.fotos_publicas;
create policy "todos leem" on public.fotos_publicas for select using (true);

drop policy if exists "quem cuida" on public.reclamacoes;
create policy "quem cuida" on public.reclamacoes for all to authenticated using (public.is_admin()) with check (public.is_admin());
drop policy if exists "quem cuida" on public.apoios;
create policy "quem cuida" on public.apoios for all to authenticated using (public.is_admin()) with check (public.is_admin());
drop policy if exists "quem cuida" on public.fotos_pendentes;
create policy "quem cuida" on public.fotos_pendentes for all to authenticated using (public.is_admin()) with check (public.is_admin());
drop policy if exists "quem cuida" on public.fotos_publicas;
create policy "quem cuida" on public.fotos_publicas for all to authenticated using (public.is_admin()) with check (public.is_admin());

-- quantas confirmações cada placa tem (sem mostrar quem confirmou)
create or replace view public.contagem as
  select reclamacao,
         count(*) filter (where tipo = 've') as ve,
         count(*) filter (where tipo = 'ok') as ok
  from public.apoios group by reclamacao;
grant select on public.contagem to anon, authenticated;

-- ---------- O que os moradores podem fazer (sempre por estas funções) ----------

create or replace function public.codigo(p_segredo text) returns text
language plpgsql immutable set search_path = public, extensions as $$
begin
  if p_segredo is null or char_length(p_segredo) not between 20 and 80 then
    raise exception 'código do aparelho inválido';
  end if;
  return encode(extensions.digest(p_segredo, 'sha256'), 'hex');
end $$;

create or replace function public.criar_reclamacao(p_tipo text, p_lat double precision, p_lon double precision,
  p_rua text, p_perto text, p_texto text, p_tem_foto boolean, p_segredo text) returns uuid
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo); novo uuid;
begin
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

create or replace function public.ainda_esta(p_id uuid) returns void
language sql security definer set search_path = public as $$
  update public.reclamacoes set visto = now() where id = p_id and resolvido is null;
$$;

-- quem marcou fecha na hora; outra pessoa conta como "já consertaram" (com 2, fecha)
create or replace function public.confirmar_conserto(p_id uuid, p_segredo text) returns boolean
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo);
begin
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

create or replace function public.meus_votos(p_segredo text) returns table (reclamacao uuid, tipo text)
language sql security definer set search_path = public as $$
  select reclamacao, tipo from public.apoios where autor = public.codigo(p_segredo);
$$;

create or replace function public.sou_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select public.is_admin();
$$;

grant execute on function public.criar_reclamacao, public.apoiar, public.ainda_esta, public.confirmar_conserto,
  public.enviar_foto, public.meus_votos, public.sou_admin to anon, authenticated;

-- ---------- Troque pelo SEU e-mail (o mesmo que você vai usar pra entrar no painel) ----------
insert into public.admins (email) values ('SEU_EMAIL_AQUI') on conflict do nothing;
