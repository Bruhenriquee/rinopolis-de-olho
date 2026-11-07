-- Rinópolis de Olho: quem marcou pode apagar a própria placa (LGPD Art. 18, VI e IX), sem pedir à equipe.
-- A prova de autoria é o código do aparelho: só apaga se a placa foi marcada por ele.
-- Confirmações, fotos, frases, denúncias e pedidos de aviso da placa saem junto (on delete cascade).
-- Rode no SQL Editor. Pode rodar de novo sem problema.

create or replace function public.apagar_minha_placa(p_id uuid, p_segredo text) returns boolean
language plpgsql security definer set search_path = public as $$
declare h text := public.codigo(p_segredo);
begin
  delete from public.reclamacoes where id = p_id and autor = h;
  return found;
end $$;
grant execute on function public.apagar_minha_placa to anon, authenticated;
