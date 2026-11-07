# Bases Legais por Atividade de Tratamento — Rinópolis de Olho

**Última atualização**: 07/11/2026
Nenhuma atividade trata dado sensível (Art. 5º, II), então todas usam o Art. 7º.
Retenção marcada "gap 6" ainda será definida em `.lgpd/retention.md`.

---

## 1. Marcar um problema (placa, frase e foto opcionais)
- **Finalidade**: mostrar o problema no mapa, contar os dias até o conserto e montar o pedido à prefeitura.
- **Dados**: tipo, local (lat/lon), rua, ponto de referência, data/hora, frase e foto (opcionais), hash do código do aparelho.
- **Base legal**: Art. 7º, I — **consentimento**.
- **Justificativa**: a pessoa decide publicar algo; a caixa "concordo" é marcada por ela antes do envio
  (fica lembrada no aparelho depois da primeira vez). Frase e foto são escolhas à parte, dentro do mesmo envio.
- **Revogação**: sim — pedido "Apagar minha marcação" (Falar com a equipe) e, depois do gap 5, botão na própria placa.
- **Retenção**: gap 6.

## 2. Confirmar ("eu também vi" / "já consertaram")
- **Finalidade**: mostrar quantas pessoas viram o problema e fechar a placa quando 2 pessoas dizem que consertaram.
- **Dados**: hash do aparelho, placa, tipo da confirmação, data.
- **Base legal**: Art. 7º, IX — **legítimo interesse** (LIA A, abaixo).
- **Justificativa**: não há caixa de concordância, e não precisa: o dado é mínimo (só o hash), o público vê apenas
  a contagem, e é a forma de impedir que uma pessoa confirme a mesma placa várias vezes. Consentimento por "ao confirmar
  você concorda" não seria válido (Art. 8º).
- **Oposição**: tocar de novo desfaz a confirmação e apaga o registro.
- **Retenção**: enquanto a placa existir (apaga junto com ela).

## 3. Denunciar uma placa
- **Finalidade**: tirar do ar conteúdo falso, ofensivo ou repetido, protegendo outras pessoas.
- **Dados**: motivo, detalhe livre (opcional), hash do aparelho, data.
- **Base legal**: Art. 7º, IX — **legítimo interesse** (LIA A).
- **Retenção**: até a equipe decidir manter ou apagar a placa (já é assim).

## 4. Aviso no celular (push)
- **Finalidade**: avisar quem acompanha uma placa quando ela for consertada ou a prefeitura responder.
- **Dados**: endereço de aviso do navegador e suas chaves, placas acompanhadas, hash do aparelho.
- **Base legal**: Art. 7º, I — **consentimento** (botão "Quero o aviso" + permissão do próprio navegador).
- **Revogação**: desligar as notificações do site ou deixar de acompanhar a placa; endereços que o navegador cancela
  são apagados sozinhos no próximo envio.
- **Retenção**: gap 6.

## 5. Localização "Estou aqui"
- **Finalidade**: posicionar a marcação no lugar onde a pessoa está.
- **Dados**: posição do aparelho, usada uma vez e não guardada como tal (vira o local do problema).
- **Base legal**: Art. 7º, I — **consentimento** (o toque no botão + a permissão do navegador).

## 6. Código do aparelho e dados guardados no navegador
- **Finalidade**: uma confirmação por aparelho, lembrar o que a pessoa marcou e acompanha, e preferências da tela.
- **Dados**: código aleatório (no banco só o hash SHA-256), marcações e preferências no `localStorage`.
- **Base legal**: Art. 7º, IX — **legítimo interesse** (LIA A). É o que faz o site funcionar sem cadastro.
- **Oposição**: limpar os dados do site no navegador.

## 7. Falar com a equipe (pedidos dos moradores)
- **Finalidade**: receber e responder pedidos de direitos do titular e contestações de placas.
- **Dados**: assunto, mensagem, contato (opcional), hash do aparelho, data, resposta.
- **Base legal**: Art. 7º, II — **obrigação legal** (atender os direitos do Art. 18 em 15 dias, Art. 19) para pedidos de
  dados; Art. 7º, IX — **legítimo interesse** (LIA A) para contestações e outros assuntos.
- **Retenção**: até 1 ano depois da resposta (publicado na política em 07/11/2026).

## 8. Moderação, histórico da equipe e bloqueio de aparelhos
- **Finalidade**: login de quem modera, registro de cada ação (responsabilização) e bloqueio de quem abusa.
- **Dados**: e-mail e senha cifrada da equipe; ação, e-mail, data e hora; hash do aparelho bloqueado e motivo.
- **Base legal**: Art. 7º, IX — **legítimo interesse** (LIA B).
- **Retenção**: gap 6 (sugestão: histórico 5 anos; bloqueio revisto a cada 2 anos).

## 9. Eleitos e plano de governo
- **Finalidade**: informação e controle social.
- **Dados**: nome de urna, nome civil, partido, votos; plano de governo da chapa eleita.
- **Base legal**: Art. 7º, §§ 3º e 4º — dados tornados **manifestamente públicos pelos titulares** no registro de
  candidatura e divulgados pela Justiça Eleitoral, usados na mesma finalidade de interesse público.
- **Cuidado**: sem juízo de valor (já é regra do projeto); atualizar quando mudar o mandato.

## 10. Endereço IP ao abrir o site
- **Finalidade**: entregar as páginas e proteger contra abuso.
- **Dados**: IP, navegador, hora (registros dos serviços de hospedagem, banco e arquivos).
- **Base legal**: Art. 7º, IX — **legítimo interesse** (LIA B). Os registros são dos operadores; o projeto não os usa
  para identificar ninguém.

---

## LIA A — proteção e funcionamento do mapa sem cadastro (atividades 2, 3, 6 e 7)
Art. 10 LGPD, em 3 testes:
1. **Finalidade legítima** — manter um mapa confiável (sem votos repetidos, sem conteúdo ofensivo) sem exigir nome
   nem e-mail de ninguém. Atende o Art. 10, I (apoio às atividades do controlador) e II (proteção do titular e de terceiros).
2. **Necessidade** — usa só um hash de código aleatório, que não identifica a pessoa; sem ele, seria preciso cadastro,
   o que trataria **mais** dados. Detalhe de denúncia é opcional e limitado a 200 caracteres.
3. **Balanceamento** — o morador espera esse controle (está na política); o público vê só contagens; há como desfazer
   (tocar de novo) ou apagar tudo (limpar dados do site). Risco baixo para o titular.
**Conclusão**: legítimo interesse válido. Transparência: política, seção 4 (Art. 10, § 2º).

## LIA B — segurança e responsabilização (atividades 8 e 10)
1. **Finalidade legítima** — saber quem fez cada ação na moderação e impedir abuso (Art. 6º, X; Art. 46).
2. **Necessidade** — e-mail só da equipe; bloqueio só por hash; IP só nos registros técnicos dos operadores.
3. **Balanceamento** — a equipe sabe que suas ações são registradas (está na política); moradores bloqueados ainda
   podem fazer pedidos de direitos (o canal não é bloqueado).
**Conclusão**: legítimo interesse válido.
