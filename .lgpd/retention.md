# Prazos de guarda e eliminação — Rinópolis de Olho

**Versão**: v1 · **Data**: 09/11/2026 · Gap 6 do `gaps.md`
Base: LGPD Art. 15 e 16 (fim do tratamento), Art. 6º, III (necessidade), Art. 18, VI (eliminação).
Regime ATPP. Isto é análise técnica, não parecer jurídico.

## Ideia em uma frase
Cada dado fica guardado só pelo tempo em que serve pra alguma coisa. Depois sai sozinho, toda semana, por uma rotina do banco (`limpar_antigos()` em `supabase-retencao.sql`). O conteúdo do mapa (as placas) não tem apagamento automático — é o registro público do que foi pedido e do que foi resolvido.

## O que é dado pessoal aqui
Nenhum nome, CPF, telefone ou e-mail de morador. O que mais se aproxima de "pessoal":
- **autor** = código embaralhado do aparelho (hash). Não diz quem é a pessoa.
- **endpoint** do aviso no celular (push).
- **e-mail da equipe** (só quem modera).
- **foto** e **frase** escritas pelo morador (podem, por acaso, trazer algo pessoal — por isso passam por moderação antes de aparecer).

## Tabela de prazos

| O quê (tabela) | Por que guardar | Prazo | Depois | Automático? |
|---|---|---|---|---|
| **reclamacoes** (as placas) | é o conteúdo do mapa; mostra o problema e, se resolvido, o histórico | enquanto o problema existe; resolvidas ficam como histórico | revisão manual (sem apagar sozinho) | não |
| **apoios** ("eu também vi" / "consertaram") | contar quantos confirmam | enquanto a placa existir | somem junto com a placa | sim (cascata) |
| **fotos_publicas** / **textos_escondidos** | foto aprovada e texto escondido ligados à placa | enquanto a placa existir | somem junto com a placa | sim (cascata) |
| **fotos_pendentes** (foto esperando moderação) | moderar antes de publicar | 90 dias | apaga | **sim** |
| **textos_pendentes** (frase esperando moderação) | moderar antes de publicar | 90 dias | apaga | **sim** |
| **denuncias** (denúncia de placa) | decidir sobre a placa; defesa contra abuso | 1 ano | apaga | **sim** |
| **avisos** (push no celular) | avisar quando a placa muda | sai 30 dias depois de a placa ser resolvida, ou com mais de 1 ano | apaga | **sim** |
| **bloqueios** (aparelho bloqueado) | impedir abuso de quem foi bloqueado | revisar a cada 2 anos | tirar quem não faz mais sentido manter | não (revisão manual) |
| **historico** (ações da equipe) | responsabilização (Art. 6º, X) e prova em incidente | 5 anos | apaga | **sim** |
| **admins** (e-mail da equipe) | login de quem modera | enquanto a pessoa estiver na equipe | tirar quando sair | não |
| **localStorage** (`rdo-*` no navegador) | guardar o código do aparelho e preferências no próprio celular | fica no aparelho do morador; ele controla | sai quando ele limpa o navegador | — |

## Por que esses números
- **90 dias (moderação pendente):** se ninguém moderou em 3 meses, a foto/frase não vai ser publicada; segurar mais só acumula dado à toa.
- **1 ano (denúncias):** tempo folgado pra decidir sobre a placa e ver se há abuso repetido. O resultado da decisão (placa escondida ou mantida) fica registrado em outras tabelas.
- **30 dias / 1 ano (avisos):** quando a placa é resolvida, o aviso já cumpriu o papel; e endereço de push velho costuma nem funcionar mais.
- **2 anos (bloqueios):** bloqueio é punição; rever de tempos em tempos evita manter bloqueio eterno sem motivo. Não dá pra automatizar "rever", então é uma tarefa no calendário.
- **5 anos (histórico):** alinhado ao prazo de guarda de registro de incidente (Res. CD/ANPD nº 15/2024, Art. 10) e à prescrição comum.

## Retenção legal obrigatória
Não há. O projeto não tem nota fiscal, contrato de trabalho nem relação bancária ligada a esses dados. Por isso o apagamento pode ser direto (hard delete), sem fase de "bloqueio e guarda".

## Como acontece
`supabase-retencao.sql` cria a função `limpar_antigos()` e a agenda para rodar **toda segunda, 4h** (pg_cron). Cada passagem conta quantas linhas apagou e grava uma linha no `historico` (`acao = 'limpeza automatica'`). Para rodar na mão a qualquer momento: `select public.limpar_antigos();` no SQL Editor do Supabase.

## Pedido de exclusão pelo titular (Art. 18, VI)
Já existe o botão **"Apagar minha marcação"** (gap 5), que apaga a placa e tudo ligado a ela (cascata), provando a autoria pelo código do aparelho. Para pedir a exclusão de outros dados, o canal **"Falar com a equipe"** (gap 1).

## Reflexo na política de privacidade
A política de 31/10/2026 diz que os dados ficam "enquanto forem úteis". Na **v2** (gap 9), trocar por: *"Cada informação é guardada pelo prazo descrito na nossa tabela de prazos de guarda e depois apagada automaticamente; as placas do mapa ficam como histórico público."* — e resumir os prazos principais.

## Tarefa no calendário
- **A cada 2 anos** (próxima: nov/2028): revisar a tabela `bloqueios` e tirar os que não fazem mais sentido.
