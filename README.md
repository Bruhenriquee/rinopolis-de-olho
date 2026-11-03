# Rinópolis de Olho

O mapa dos moradores de Rinópolis-SP. A pessoa marca buraco, poste apagado, lixo ou esgoto no lugar exato, os vizinhos confirmam, e cada placa conta os dias até o conserto.

O site também mostra quem decide na cidade (prefeita, vice e os 9 vereadores), o plano de governo registrado no TSE, as contas da prefeitura e um pedido oficial pronto pra enviar.

No ar em **https://bruhenriquee.github.io/rinopolis-de-olho/**

## Como funciona

- As marcações ficam num banco de dados no **Supabase**. Os moradores só gravam pelas funções do banco, que conferem tudo (limite de 5 marcações por hora, aparelho bloqueado, foto só de quem marcou).
- Ninguém precisa de cadastro pra marcar. Cada aparelho tem um código secreto; o banco guarda só a versão embaralhada.
- As fotos e as frases só aparecem pra todos depois de aprovadas no **Painel** (aba Conferir).
- A equipe (dono e moderadores) entra com e-mail e senha pelo endereço do site com `#painel` no fim: https://bruhenriquee.github.io/rinopolis-de-olho/#painel. Não há link público pro login.

## Arquivos

- `index.html`: o site.
- `ruas.js`: as ruas da cidade, tiradas do OpenStreetMap.
- `config.js`: endereço e chave pública do Supabase, e-mail de contato, endereço do site e chave pública dos avisos (`vapid`).
- `supabase.sql`, `supabase-painel.sql`, `supabase-denuncias.sql`, `supabase-frases.sql` e `supabase-avisos.sql`: o banco. Rodar uma vez, nessa ordem, no SQL Editor do Supabase.
- `supabase/functions/avisar`: manda o aviso no celular de quem acompanha uma placa (veja **Avisos no celular**).
- `gerar_site.py`: monta a pasta `docs/`, que é o que o GitHub Pages publica.
- `gerar_previa.py`: gera `previa.png`, a imagem que aparece quando o link é mandado no WhatsApp.
- `manifest.webmanifest` e `sw.js`: deixam instalar o site na tela do celular, como um aplicativo.
- `gerar_icones.py`: gera os ícones do site instalado (`icone-192.png`, `icone-512.png`, `icone-maskable.png`, `apple-touch-icon.png`).

Depois de mudar qualquer coisa:

```
python gerar_site.py
git add -A && git commit -m "o que mudou" && git push
```

## Moderadores

1. No Painel, aba **Equipe**, adicione o e-mail da pessoa (só o dono faz isso).
2. No Supabase, em **Authentication → Users → Add user**, crie o login com o mesmo e-mail e marque **Auto Confirm User**.

## Avisos no celular

Quem acompanha uma placa pode receber aviso no celular quando ela for consertada ou a prefeitura responder. Só esses dois avisos.
No iPhone, só funciona com o site instalado na tela inicial.

Para ligar (uma vez só):

1. No Supabase, **SQL Editor**: cole `supabase-avisos.sql` e clique em Run.
2. **Edge Functions → Deploy a new function → Via Editor**: nome `avisar`, cole `supabase/functions/avisar/index.ts` e publique.
   Depois, nos detalhes da função, desligue **Verify JWT** (quem chama é o próprio banco; a função relê a placa e não confia no pedido).
3. **Edge Functions → Secrets**: crie `VAPID_PUBLICA` e `VAPID_PRIVADA` com as duas chaves dos avisos.
   A pública também fica em `config.js`. A privada **não vai para o GitHub**: guarde num lugar seguro, fora desta pasta.
   Se perder a privada, gere um par novo; quem já tinha pedido aviso precisa pedir de novo.

## Fontes

- Ruas: © colaboradores do [OpenStreetMap](https://www.openstreetmap.org/copyright), licença ODbL.
- Eleição e plano de governo: TSE.
- Contas: relatórios da prefeitura no Tesouro Nacional (Siconfi).

Projeto de moradores, sem partido.
