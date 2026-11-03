-- Rinópolis de Olho: tira o alerta "Security Definer View" do Supabase (public.contagem).
-- Cole no SQL Editor e clique em Run. O site continua igual.
-- quantas confirmações cada placa tem (sem mostrar quem confirmou). A função conta; a visão só repassa
create or replace function public.contagem_apoios() returns table (reclamacao uuid, ve bigint, ok bigint)
language sql stable security definer set search_path = public as $$
  select reclamacao, count(*) filter (where tipo = 've'), count(*) filter (where tipo = 'ok')
  from public.apoios group by reclamacao;
$$;
create or replace view public.contagem with (security_invoker = true) as select * from public.contagem_apoios();
grant execute on function public.contagem_apoios to anon, authenticated;
grant select on public.contagem to anon, authenticated;
