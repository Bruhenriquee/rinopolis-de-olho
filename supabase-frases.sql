-- Rinópolis de Olho: a frase que o morador escreve só aparece depois que a equipe aprova (como as fotos).
-- Rode DEPOIS do supabase.sql e do supabase-painel.sql. Cole tudo no SQL Editor e clique em Run. Pode rodar de novo sem problema.

-- ---------- Frases esperando conferência: só a equipe vê ----------
create table if not exists public.textos_pendentes (
  reclamacao uuid primary key references public.reclamacoes(id) on delete cascade,
  texto text not null check (char_length(texto) <= 160),
  criado timestamptz not null default now()
);
alter table public.textos_pendentes enable row level security;
drop policy if exists "quem cuida" on public.textos_pendentes;
create policy "quem cuida" on public.textos_pendentes for all to authenticated using (public.is_admin()) with check (public.is_admin());

-- ---------- Marcar: a placa entra na hora; a frase vai pra conferência ----------
create or replace function public.criar_reclamacao(p_tipo text, p_lat double precision, p_lon double precision,
  p_rua text, p_perto text, p_texto text, p_tem_foto boolean, p_segredo text) returns uuid
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo); novo uuid; t text := nullif(btrim(left(p_texto,160)),'');
begin
  perform public.checar_bloqueio(h);
  if (select count(*) from public.reclamacoes where autor = h and criado > now() - interval '1 hour') >= 5 then
    raise exception 'limite de 5 marcações por hora';
  end if;
  insert into public.reclamacoes (tipo, lat, lon, rua, perto, texto, tem_foto, autor)
  values (p_tipo, p_lat, p_lon, left(p_rua,120), left(p_perto,160), null, coalesce(p_tem_foto,false), h)
  returning id into novo;
  if t is not null then
    insert into public.textos_pendentes (reclamacao, texto) values (novo, t);
  end if;
  return novo;
end $$;

-- ---------- Equipe aprova ou recusa a frase ----------
create or replace function public.aprovar_frase(p_id uuid) returns void
language plpgsql security definer set search_path = public as $$
declare t text; d text;
begin
  if not public.is_admin() then raise exception 'só a equipe'; end if;
  select texto into t from public.textos_pendentes where reclamacao = p_id;
  if t is null then return; end if;
  update public.reclamacoes set texto = t where id = p_id;
  delete from public.textos_pendentes where reclamacao = p_id;
  select tipo || ' · ' || coalesce(rua,'') into d from public.reclamacoes where id = p_id;
  perform public.anotar('aprovou frase', d);
end $$;

create or replace function public.recusar_frase(p_id uuid) returns void
language plpgsql security definer set search_path = public as $$
declare d text;
begin
  if not public.is_admin() then raise exception 'só a equipe'; end if;
  delete from public.textos_pendentes where reclamacao = p_id;
  select tipo || ' · ' || coalesce(rua,'') into d from public.reclamacoes where id = p_id;
  perform public.anotar('recusou frase', d);
end $$;
grant execute on function public.aprovar_frase, public.recusar_frase to authenticated;
