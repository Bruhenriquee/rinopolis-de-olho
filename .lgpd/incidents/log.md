# Registro de incidentes — Rinópolis de Olho

Todo incidente entra aqui, avisado à ANPD ou não, e fica guardado por **5 anos** (Res. CD/ANPD nº 15/2024, Art. 10).

---

## INC-2026-001 — chave secreta do Supabase exposta em conversa

- **Quando**: fim de outubro de 2026 (data exata a confirmar)
- **O que houve**: a chave secreta (`sb_secret_…`) do projeto Supabase foi colada numa conversa com o assistente de IA.
  Quem tem essa chave consegue ler e apagar tudo no banco, passando por cima das regras de segurança.
- **Dados que poderiam ser afetados**: todas as tabelas (marcações, fotos, denúncias, pedidos de aviso, e-mails da equipe).
- **Acesso indevido conhecido**: nenhum.
- **Medida**: na época, a orientação foi revogar a chave e gerar outra.
  **PENDENTE — confirmar no Supabase (Project Settings → API Keys) que a chave antiga foi revogada.**
- **Teste do Art. 5º**: A (dano relevante) = não, sem sinal de acesso indevido · B = poderia envolver login da equipe.
  **Decisão: não notificar a ANPD**, só registrar.
- **Guarda deste registro até**: 31/10/2031

---

## Modelo (copie para cada incidente novo)

```
## INC-AAAA-NNN — título curto

- **Quando aconteceu**:
- **Quando soube que afetou dados pessoais** (conta o prazo):
- **O que houve**:
- **Dados afetados**:
- **Pessoas afetadas** (quantas; tem criança, adolescente ou idoso?):
- **Causa**:
- **Medidas tomadas** (o quê e quando):
- **Teste do Art. 5º**: A = sim/não (por quê) · B = sim/não (qual item)
- **Decisão**: notificar / não notificar
- **ANPD**: data e protocolo (se notificou)
- **Pessoas afetadas avisadas**: como e quando (se notificou)
- **Complemento à ANPD** (até 20 dias úteis):
- **Correção definitiva**:
- **Guarda deste registro até**: (data + 5 anos)
```
