-- Rinópolis de Olho: canal "Falar com a equipe" (direitos do titular, LGPD Art. 18, e contestação de placas).
-- Substitui o e-mail de contato. O morador manda o pedido pelo site, sem dar nome nem e-mail; a equipe responde
-- pelo painel e a resposta aparece no mesmo aparelho. Rode no SQL Editor depois dos outros. Pode rodar de novo.

create table if not exists public.pedidos (
  id bigserial primary key,
  criado timestamptz not null default now(),
  tipo text not null check (tipo in ('acesso','correcao','exclusao','revogacao','contestacao','outro')),
  mensagem text not null check (char_length(mensagem) between 3 and 1000),
  contato text check (char_length(contato) <= 120),
  autor text not null,
  resposta text check (char_length(resposta) <= 1000),
  respondido timestamptz
);
-- só a equipe lê e responde; o morador só envia e lê os próprios, pelas funções abaixo
alter table public.pedidos enable row level security;
drop policy if exists "quem cuida" on public.pedidos;
create policy "quem cuida" on public.pedidos for all to authenticated using (public.is_admin()) with check (public.is_admin());

-- envia um pedido (até 5 por dia por aparelho). Aparelho bloqueado também pode: pedir os próprios direitos não se bloqueia.
create or replace function public.enviar_pedido(p_tipo text, p_mensagem text, p_contato text, p_segredo text) returns bigint
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo); novo bigint;
begin
  if (select count(*) from public.pedidos where autor = h and criado > now() - interval '1 day') >= 5 then
    raise exception 'limite de 5 pedidos por dia';
  end if;
  insert into public.pedidos (tipo, mensagem, contato, autor)
  values (p_tipo, left(trim(p_mensagem), 1000), nullif(left(trim(p_contato), 120), ''), h)
  returning id into novo;
  return novo;
end $$;

-- os pedidos deste aparelho, com a resposta da equipe
create or replace function public.meus_pedidos(p_segredo text)
returns table (id bigint, criado timestamptz, tipo text, mensagem text, resposta text, respondido timestamptz)
language sql security definer set search_path = public as $$
  select id, criado, tipo, mensagem, resposta, respondido from public.pedidos
  where autor = public.codigo(p_segredo) order by criado desc limit 20;
$$;

grant execute on function public.enviar_pedido, public.meus_pedidos to anon, authenticated;

-- a resposta da equipe entra no histórico
create or replace function public.h_pedidos() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.resposta is distinct from old.resposta and new.resposta is not null then
    perform public.anotar('respondeu pedido', new.tipo || ' · nº ' || new.id);
  end if;
  return null;
end $$;
revoke execute on function public.h_pedidos() from public, anon, authenticated;
drop trigger if exists h_pedidos on public.pedidos;
create trigger h_pedidos after update of resposta on public.pedidos for each row execute function public.h_pedidos();
