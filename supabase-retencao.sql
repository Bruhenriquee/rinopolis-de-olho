-- ============================================================
-- Prazos de guarda (LGPD gap 6) — apaga sozinho o que já passou do prazo.
-- Rode este arquivo UMA vez no SQL Editor do Supabase.
-- Prazos explicados em .lgpd/retention.md
-- ============================================================

-- Limpa tudo que passou do prazo. Devolve um resumo do que apagou.
create or replace function public.limpar_antigos() returns text
language plpgsql security definer set search_path = public as $$
declare
  n_fotos int; n_textos int; n_denuncias int; n_avisos int; n_hist int;
  resumo text;
begin
  -- fotos esperando moderação há mais de 90 dias
  delete from public.fotos_pendentes where criado < now() - interval '90 days';
  get diagnostics n_fotos = row_count;

  -- frases esperando moderação há mais de 90 dias
  delete from public.textos_pendentes where criado < now() - interval '90 days';
  get diagnostics n_textos = row_count;

  -- denúncias com mais de 1 ano
  delete from public.denuncias where criado < now() - interval '1 year';
  get diagnostics n_denuncias = row_count;

  -- avisos de placa já resolvida há mais de 30 dias, ou avisos com mais de 1 ano
  delete from public.avisos a
   where a.criado < now() - interval '1 year'
      or exists (
        select 1 from public.reclamacoes r
         where r.id = a.reclamacao
           and r.resolvido is not null
           and r.resolvido < now() - interval '30 days'
      );
  get diagnostics n_avisos = row_count;

  -- histórico da equipe com mais de 5 anos
  delete from public.historico where quando < now() - interval '5 years';
  get diagnostics n_hist = row_count;

  resumo := format(
    'fotos %s, frases %s, denuncias %s, avisos %s, historico %s',
    n_fotos, n_textos, n_denuncias, n_avisos, n_hist
  );

  -- registra a limpeza no próprio histórico
  insert into public.historico (quem, acao, detalhe)
  values ('sistema', 'limpeza automatica', resumo);

  return resumo;
end $$;

-- Só a equipe (logada) pode chamar na mão; o cron roda como dono do banco.
revoke all on function public.limpar_antigos() from public, anon;
grant execute on function public.limpar_antigos() to authenticated;

-- ---------- Agendar toda segunda, 4h da manhã ----------
-- Precisa da extensão pg_cron (Supabase: Database → Extensions → pg_cron).
create extension if not exists pg_cron;

-- remove agendamento anterior com o mesmo nome, se houver
select cron.unschedule('limpar_antigos')
 where exists (select 1 from cron.job where jobname = 'limpar_antigos');

select cron.schedule('limpar_antigos', '0 4 * * 1', $$select public.limpar_antigos();$$);

-- Para rodar agora, na mão:  select public.limpar_antigos();
