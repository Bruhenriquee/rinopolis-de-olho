# LGPD Audit Status

**Projeto**: Rinópolis de Olho (mapa colaborativo de problemas urbanos de Rinópolis-SP)
**Cenário**: B — sistema em produção (retrofit)
**Início**: 07/11/2026
**Última atualização**: 07/11/2026
**Encarregado**: pendente (ATPP: dispensado pela Res. 2/2022 Art. 11, desde que haja canal de contato funcionando)

## Pipeline atual
- [x] L0 — Setup `.lgpd/`
- [x] L1 — Gap analysis (`discovery.md`, `gaps.md`) — ⏸ aguardando aprovação
- [ ] L2 — Mapa de dados (lgpd-data-mapping)
- [ ] L3 — Base legal (lgpd-legal-basis)
- [ ] L4 — Operadores (lgpd-vendor-audit)
- [ ] L5 — Retenção (lgpd-retention-erasure)
- [ ] L6 — Anonimização (não se aplica: não há analytics)
- [ ] L7 — Direitos do titular (lgpd-dsar)
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
- `supabase-pedidos.sql` + formulário "Falar com a equipe" (canal do titular, gap 1) — código pronto, falta rodar o SQL e publicar

## Gaps abertos
Críticos: gap 2 resolvido; gap 1 com código pronto, falta rodar o SQL e publicar. Mais 5 altos e 5 médios. Ver `.lgpd/gaps.md`.

## Próximo passo
Rodar `supabase-pedidos.sql` no Supabase, publicar o site e confirmar a revogação da chave do INC-2026-001. Depois: base legal (gap 4) e "apagar minha marcação" (gap 5).
