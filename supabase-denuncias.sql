-- Rinópolis de Olho: denúncias de placas falsas, ofensivas ou repetidas.
-- Rode DEPOIS do supabase.sql e do supabase-painel.sql. Cole tudo no SQL Editor e clique em Run. Pode rodar de novo sem problema.

-- ---------- Denúncias: só a equipe lê ----------
create table if not exists public.denuncias (
  id bigserial primary key,
  reclamacao uuid not null references public.reclamacoes(id) on delete cascade,
  motivo text not null check (motivo in ('falsa','ofensiva','repetida','outro')),
  detalhe text check (char_length(detalhe) <= 200),
  autor text not null,
  criado timestamptz not null default now(),
  unique (reclamacao, autor)
);
alter table public.denuncias enable row level security;
drop policy if exists "quem cuida" on public.denuncias;
create policy "quem cuida" on public.denuncias for all to authenticated using (public.is_admin()) with check (public.is_admin());

-- texto tirado do ar depois de 3 denúncias de "ofensiva": fica guardado aqui até a equipe decidir
create table if not exists public.textos_escondidos (
  reclamacao uuid primary key references public.reclamacoes(id) on delete cascade,
  texto text not null,
  criado timestamptz not null default now()
);
alter table public.textos_escondidos enable row level security;
drop policy if exists "quem cuida" on public.textos_escondidos;
create policy "quem cuida" on public.textos_escondidos for all to authenticated using (public.is_admin()) with check (public.is_admin());

-- ---------- Morador denuncia (uma vez por placa, até 10 por hora) ----------
create or replace function public.denunciar(p_id uuid, p_motivo text, p_detalhe text, p_segredo text) returns void
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo); t text;
begin
  perform public.checar_bloqueio(h);
  if p_motivo not in ('falsa','ofensiva','repetida','outro') then raise exception 'motivo inválido'; end if;
  if not exists (select 1 from public.reclamacoes where id = p_id) then raise exception 'placa não existe'; end if;
  if exists (select 1 from public.reclamacoes where id = p_id and autor = h) then raise exception 'quem marcou não denuncia a própria placa'; end if;
  if (select count(*) from public.denuncias where autor = h and criado > now() - interval '1 hour') >= 10 then
    raise exception 'limite de 10 denúncias por hora';
  end if;
  insert into public.denuncias (reclamacao, motivo, detalhe, autor) values (p_id, p_motivo, nullif(left(p_detalhe,200),''), h)
  on conflict (reclamacao, autor) do update set motivo = excluded.motivo, detalhe = excluded.detalhe, criado = now();
  -- 3 pessoas dizendo que é ofensiva: a frase sai do ar na hora (a placa continua)
  if (select count(*) from public.denuncias where reclamacao = p_id and motivo = 'ofensiva') >= 3 then
    select texto into t from public.reclamacoes where id = p_id;
    if t is not null then
      insert into public.textos_escondidos (reclamacao, texto) values (p_id, t) on conflict (reclamacao) do nothing;
      update public.reclamacoes set texto = null where id = p_id;
    end if;
  end if;
end $$;
grant execute on function public.denunciar to anon, authenticated;

-- ---------- Equipe mantém a placa: limpa as denúncias e devolve a frase, se tinha saído ----------
create or replace function public.manter_placa(p_id uuid) returns void
language plpgsql security definer set search_path = public as $$
declare t text; d text;
begin
  if not public.is_admin() then raise exception 'só a equipe'; end if;
  select texto into t from public.textos_escondidos where reclamacao = p_id;
  if t is not null then update public.reclamacoes set texto = t where id = p_id; end if;
  delete from public.textos_escondidos where reclamacao = p_id;
  delete from public.denuncias where reclamacao = p_id;
  select tipo || ' · ' || coalesce(rua,'') into d from public.reclamacoes where id = p_id;
  perform public.anotar('manteve placa denunciada', d);
end $$;
grant execute on function public.manter_placa to authenticated;
