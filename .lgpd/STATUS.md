# LGPD Audit Status

**Projeto**: Rinópolis de Olho (mapa colaborativo de problemas urbanos de Rinópolis-SP)
**Cenário**: B — sistema em produção (retrofit)
**Início**: 07/11/2026
**Última atualização**: 09/11/2026
**Encarregado**: pendente (ATPP: dispensado pela Res. 2/2022 Art. 11, desde que haja canal de contato funcionando)

## Pipeline atual
- [x] L0 — Setup `.lgpd/`
- [x] L1 — Gap analysis (`discovery.md`, `gaps.md`) — ⏸ aguardando aprovação
- [ ] L2 — Mapa de dados (lgpd-data-mapping)
- [x] L3 — Base legal: `legal-basis.md` (07/11/2026) — 4 por consentimento, 1 por obrigação legal, o resto por legítimo interesse com teste escrito
- [ ] L4 — Operadores (lgpd-vendor-audit)
- [x] L5 — Retenção: prazos em `retention.md` + limpeza automática `supabase-retencao.sql` (09/11/2026)
- [ ] L6 — Anonimização (não se aplica: não há analytics)
- [x] L7 — Direitos do titular: "Falar com a equipe" + "Apagar minha marcação" (07/11/2026)
- [x] L8 — Incidentes: roteiro, registro e modelos em `incidents/` (07/11/2026)
- [ ] L9 — Política de privacidade v2 (lgpd-privacy-policy) ⏸
- [ ] L10 — ECA Digital (avaliação por escrito)
- [ ] L11 — RIPD (avaliação de alto risco por escrito) ⏸
- [ ] L12 — Encarregado / canal
- [ ] L13 — Relatório final

## Artefatos gerados
- `.lgpd/discovery.md` — v1, 07/11/2026
- `.lgpd/gaps.md` — v1, 07/11/2026
- `.lgpd/incidents/` — runbook, log (INC-2026-001), modelos ANPD e titular — 07/11/2026
- `supabase-pedidos.sql` + formulário "Falar com a equipe" (canal do titular, gap 1) — publicado 07/11/2026
- `.lgpd/legal-basis.md` — v1, 07/11/2026 (com os testes de legítimo interesse A e B)
- `supabase-apagar-minha.sql` + botão "Apagar minha marcação" (gap 5) — publicado 07/11/2026
- `.lgpd/retention.md` — v1, 09/11/2026 (prazos de guarda, gap 6)
- `supabase-retencao.sql` — função `limpar_antigos()` + agendamento semanal (pg_cron), gap 6 — **falta rodar no Supabase**

## Gaps abertos
Críticos e altos de código resolvidos (1, 2, 4, 5, 6). Abertos: 3 e 7 (pedem advogado) e os médios. Ver `.lgpd/gaps.md`.

## Próximo passo
Google Fonts no próprio site (gap 10). Com advogado: gaps 3 (quem aparece como responsável) e 7 (transferência internacional).
Pendência do gap 6: rodar `supabase-retencao.sql` no SQL Editor do Supabase (habilitar pg_cron antes).
