# Gap Analysis e Plano de Remediação — 07/11/2026

Regime considerado: **ATPP** (Res. CD/ANPD nº 2/2022), sem fins lucrativos, sem dados sensíveis.
Isto é análise técnica, não parecer jurídico: os itens marcados ⚖ pedem conversa com um advogado de proteção de dados.

## Resumo
- 2 gaps críticos
- 5 gaps altos
- 5 gaps médios
- 2 gaps baixos

## Tabela

| # | Item | Status | Evidência | Severidade | Norma |
|---|---|---|---|---|---|
| 1 | Canal de contato do titular funcionando | 🟢 FEITO (07/11) — e-mail retirado; canal "Falar com a equipe" no site, resposta pelo painel | `contato@rinopolisdeolho.com.br` — domínio não existe (sem DNS/MX). Pedidos de acesso, exclusão e denúncia por e-mail não chegam a ninguém | **crítica** | Art. 18 e 19; Art. 41 §1º; Res. 2/2022 Art. 11 (ATPP precisa de canal mesmo sem Encarregado) |
| 2 | Registro de incidentes + roteiro | 🟢 FEITO (07/11) — `incidents/runbook.md`, `log.md`, `templates/`; INC-2026-001 aguarda confirmar revogação da chave | Nenhum roteiro nem registro | **crítica** | Art. 48; Res. 15/2024 Arts. 6º, 9º e 10 (registrar TODO incidente por 5 anos) |
| 3 | Identificação do controlador | 🟡 YELLOW ⚖ | Política diz só "a equipe que mantém o mapa"; sem nome de pessoa nem de associação | alta | Art. 9º, III; Art. 5º, VI |
| 4 | Base legal das confirmações, denúncias, código do aparelho e push | 🟢 FEITO (07/11) — `legal-basis.md` com 10 atividades + 2 testes de legítimo interesse; política, seção 4, atualizada | Política cita só consentimento (Art. 7º, I) via caixa marcada ao **marcar**; confirmar e denunciar não têm caixa ("ao confirmar você concorda" não é consentimento livre e inequívoco) | alta | Art. 7º, I e IX; Art. 8º; Art. 10 (legítimo interesse exige teste documentado) |
| 5 | Exclusão pelo próprio titular | 🟢 FEITO (07/11) — botão "Apagar minha marcação" na placa, só no aparelho que marcou (`supabase-apagar-minha.sql`) | Só a equipe apaga placas; o autor não consegue apagar a sua, e pedido por e-mail não tem como provar autoria (qualquer um pode pedir para apagar a placa dos outros) | alta | Art. 18, VI e IX; Art. 6º, V (qualidade) |
| 6 | Retenção definida | 🟡 YELLOW | "Enquanto forem úteis"; histórico, bloqueios e pedidos de aviso sem prazo | alta | Art. 15 e 16; Art. 6º, III (necessidade) |
| 7 | Transferência internacional | 🟡 YELLOW ⚖ | Política cita Art. 33 sem dizer qual hipótese; nenhum dos serviços (Supabase, GitHub, Google, Cloudflare) tem Cláusulas-Padrão brasileiras | alta | Arts. 33–36; Res. 19/2024 |
| 8 | ROPA (registro de operações) | 🟡 YELLOW | Não existe. O `discovery.md` já serve de base | média | Art. 37; Res. 2/2022 Art. 9º (ATPP pode usar modelo simplificado) |
| 9 | Transparência sobre operadores | 🟡 YELLOW | Hospedagem descrita como "um serviço de hospedagem", sem nome; não cita que o Supabase também registra IP | média | Art. 9º, V |
| 10 | Google Fonts | 🟡 YELLOW | Toda visita manda o IP ao Google só para baixar as letras | média | Art. 6º, III (necessidade); Art. 33 |
| 11 | Avaliação ECA Digital | 🟡 YELLOW | Não há registro da avaliação. Site sem contas, sem anúncios e sem perfilamento, não direcionado a menores: risco baixo, mas a conclusão precisa estar escrita | média | Lei 15.211/2025 (vigente desde 17/03/2026) |
| 12 | Avaliação de alto risco (RIPD) | 🟡 YELLOW | Não há registro. Pela Res. 2/2022 Art. 4º não parece alto risco (cidade de ~9 mil habitantes, sem dados sensíveis, sem decisão automatizada), mas a conclusão precisa estar escrita | média | Art. 38; Res. 2/2022 Art. 4º |
| 13 | Segurança técnica | 🟢 GREEN | RLS em todas as tabelas, escrita só por funções validadas, limite por hora, bloqueio, HTTPS, Security Advisor sem erros | — | Art. 46 |
| 14 | Minimização e fotos | 🟢 GREEN | Sem nome/CPF/e-mail de morador; hash do aparelho; EXIF removido; moderação prévia | — | Art. 6º, III; Art. 46 §2º |
| 15 | Registro das ações da equipe | 🟢 GREEN | Tabela `historico` gravada por gatilho do banco | baixa | Art. 6º, X |
| 16 | Política de privacidade publicada | 🟢 GREEN (com ajustes dos itens 3, 4, 6, 7, 9) | Versão de 31/10/2026 no site | baixa | Art. 9º |

## Ações imediatas (esta semana)
1. **Fazer o canal de contato funcionar** (gap 1) — trocar `config.js > contato` por um e-mail que já existe e você lê (pode ser um Gmail só do projeto), até o domínio estar no ar. 10 minutos.
2. **Roteiro e registro de incidentes** (gap 2) — `.lgpd/incidents/runbook.md` + `log.md`. Skill: lgpd-incident-response.

## Próximas 2 semanas
3. **Base legal revisada** (gap 4) — consentimento para marcar, foto, frase e push; legítimo interesse documentado para o código do aparelho, confirmações e denúncias (antifraude). Skill: lgpd-legal-basis.
4. **"Apagar minha marcação" no próprio site** (gap 5) — o aparelho que marcou prova a autoria pelo código. Skill: lgpd-dsar.
5. **Prazos de retenção** (gap 6) — por exemplo: denúncias até a decisão (já é assim), pedidos de aviso 1 ano sem uso, histórico 5 anos, bloqueios revisados a cada 2 anos. Skill: lgpd-retention-erasure.
6. **Google Fonts dentro do site** (gap 10) — baixar as duas fontes e servir junto com as páginas. Tira um operador e uma transferência.

## Próximo mês
7. **Identificação do controlador** (gap 3) ⚖ — decidir se aparece o nome de uma pessoa responsável ou se vira associação com CNPJ. Conversar com advogado.
8. **Transferência internacional** (gap 7) ⚖ — escolher a hipótese do Art. 33 e escrever na política; ver a região do projeto no Supabase (Project Settings → General → Region): se for São Paulo (sa-east-1), o banco fica no Brasil. Skill: lgpd-international-transfer.
9. **Política v2** com os ajustes acima (gaps 3, 4, 6, 7, 9). Skill: lgpd-privacy-policy. ⏸ revisão humana antes de publicar.

## Backlog
10. ROPA simplificado (gap 8) — lgpd-ropa.
11. Registro das avaliações ECA Digital e de alto risco (gaps 11 e 12) — lgpd-eca-digital-minors, lgpd-ripd.
