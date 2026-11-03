-- Rinópolis de Olho: tira do alcance do público as funções internas do banco (alertas do Security Advisor).
-- Rode por último, no SQL Editor. Pode rodar de novo sem problema. O site continua igual.
-- As funções que os moradores usam (marcar, confirmar, denunciar, pedir aviso...) continuam abertas de propósito:
-- é por elas que o site funciona sem cadastro, e cada uma confere o pedido antes de gravar.

-- pg_net (usado pelos avisos) vai para o lugar certo das extensões
drop extension if exists pg_net;
create extension pg_net with schema extensions;
alter function public.estado_aviso(public.reclamacoes) set search_path = public;

-- funções internas: só o próprio banco chama (histórico, gatilhos, bloqueio)
revoke execute on function public.anotar(text, text), public.h_reclamacoes(), public.h_fotos(), public.h_equipe(),
  public.disparar_aviso(), public.checar_bloqueio(text), public.estado_aviso(public.reclamacoes)
  from public, anon, authenticated;

-- funções da equipe: só quem entrou com e-mail e senha (e elas ainda conferem se é da equipe)
revoke execute on function public.is_admin(), public.is_dono(), public.aprovar_frase(uuid), public.recusar_frase(uuid),
  public.manter_placa(uuid) from public, anon;
grant execute on function public.is_admin(), public.is_dono(), public.aprovar_frase(uuid), public.recusar_frase(uuid),
  public.manter_placa(uuid) to authenticated;
