# Discovery LGPD — Rinópolis de Olho

**Data**: 07/11/2026 · **Método**: leitura do código (`index.html`, `config.js`, `sw.js`, `supabase*.sql`, `supabase/functions/avisar`) e da Política de Privacidade e Termos publicados no site (versão de 31/10/2026).

## Quem é quem

| Papel | Quem | Observação |
|---|---|---|
| Controlador (Art. 5º, VI) | "A equipe que mantém o mapa" — projeto independente de moradores, sem CNPJ | **Não identificado** por nome na política |
| Regime | Provável **Agente de Tratamento de Pequeno Porte** (Res. CD/ANPD nº 2/2022): ente despersonalizado / pessoa natural, sem fins lucrativos | Prazos em dobro para titular (30 dias) e incidente (6 dias úteis); Encarregado dispensado se houver canal de comunicação (Art. 11) |
| Encarregado (Art. 41) | Não designado | Canal publicado: `contato@rinopolisdeolho.com.br` — **o domínio não existe hoje (DNS sem registro A e MX)** |

## Tratamentos encontrados

| # | Atividade | Dados | Titular | Onde | Público? |
|---|---|---|---|---|---|
| 1 | Marcar problema | tipo, lat/lon, rua, ponto de referência, data/hora, frase (opcional), foto (opcional, EXIF removido no aparelho), hash do código do aparelho | morador | Supabase `reclamacoes`, `fotos_pendentes`/`fotos_publicas`, `textos_pendentes` | sim (sem autor); frase e foto só após moderação |
| 2 | Confirmar ("eu também vi" / "já consertaram") | hash do aparelho, placa, tipo, data | morador | `apoios` (só contagem é pública, via `contagem`) | só a contagem |
| 3 | Denunciar placa | motivo, detalhe livre, hash, data | morador | `denuncias`, `textos_escondidos` | não |
| 4 | Aviso no celular (push) | endpoint do navegador + chaves, placas acompanhadas, hash | morador | `avisos` (sem leitura pública) + serviços de push (Google, Apple, Mozilla, Microsoft) | não |
| 5 | Moderação | e-mail e senha (hash) da equipe; histórico de ações com e-mail | equipe | Supabase Auth, `admins`, `historico` | não |
| 6 | Bloqueio de aparelho | hash do aparelho, motivo | morador | `bloqueios` | não |
| 7 | Agentes públicos | nome, partido, votos dos eleitos; plano de governo | prefeita, vice, vereadores | fixo no `index.html` (fonte TSE) | sim |
| 8 | Armazenamento local | código do aparelho (`rdo-segredo`), marcações, preferências (18 chaves `rdo-*`) | morador | `localStorage` do navegador | não |
| 9 | Acesso ao site | endereço IP | visitante | logs da hospedagem, Supabase, Google Fonts, cdnjs, jsDelivr | não |
| 10 | Localização "Estou aqui" | posição do aparelho, só ao tocar, usada para posicionar a marcação | morador | navegador → vira lat/lon da placa | sim (como local do problema) |

Sem cookies de rastreamento, sem publicidade, sem analytics (conferido no código).

## Operadores e transferências internacionais

| Serviço | Recebe | País |
|---|---|---|
| Supabase, Inc. (banco, Auth, Edge Function) | todos os dados de 1–6 | EUA (empresa); região do projeto **a confirmar** no painel |
| Hospedagem das páginas (GitHub Pages / GitHub, Inc.) | IP de quem acessa | EUA |
| Google Fonts (Google LLC) | IP | EUA |
| cdnjs (Cloudflare) e jsDelivr | IP | EUA / global |
| Serviços de push (Google FCM, Apple, Mozilla, Microsoft) | endpoint + texto do aviso | EUA |

## Pontos fortes já existentes

- Política de Privacidade e Termos publicados, com data de versão, lista de dados, operadores, finalidade, base legal, direitos e prazo de 15 dias.
- Minimização: sem nome, CPF, telefone ou e-mail de morador; código do aparelho só como hash SHA-256.
- Fotos com metadados removidos e moderação prévia de foto e frase (rostos, placas de carro, nomes recusados).
- Escrita no banco só por funções que validam cada pedido; RLS em todas as tabelas; limite de 5 marcações/hora; bloqueio de aparelho.
- Histórico das ações da equipe gravado pelo próprio banco (Art. 6º, X — responsabilização).
- Security Advisor do Supabase sem erros (corrigido em 03/11/2026).
