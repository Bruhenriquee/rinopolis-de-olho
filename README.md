# Rinópolis de Olho

O mapa dos moradores de Rinópolis-SP. A pessoa marca buraco, poste apagado, lixo ou esgoto no lugar exato, os vizinhos confirmam, e cada placa conta os dias até o conserto.

O site também mostra quem decide na cidade (prefeita, vice e os 9 vereadores), o plano de governo registrado no TSE, as contas da prefeitura e um pedido oficial pronto pra enviar.

No ar em **https://bruhenriquee.github.io/rinopolis-de-olho/**

## Como funciona

- As marcações ficam num banco de dados no **Supabase**. Os moradores só gravam pelas funções do banco, que conferem tudo (limite de 5 marcações por hora, aparelho bloqueado, foto só de quem marcou).
- Ninguém precisa de cadastro pra marcar. Cada aparelho tem um código secreto; o banco guarda só a versão embaralhada.
- As fotos só aparecem pra todos depois de aprovadas no **Painel**.
- A equipe (dono e moderadores) entra com e-mail e senha pelo endereço do site com `#painel` no fim: https://bruhenriquee.github.io/rinopolis-de-olho/#painel. Não há link público pro login.

## Arquivos

- `index.html`: o site.
- `ruas.js`: as ruas da cidade, tiradas do OpenStreetMap.
- `config.js`: endereço e chave pública do Supabase, e-mail de contato e endereço do site.
- `supabase.sql` e `supabase-painel.sql`: o banco. Rodar uma vez, nessa ordem, no SQL Editor do Supabase.
- `gerar_site.py`: monta a pasta `docs/`, que é o que o GitHub Pages publica.
- `gerar_previa.py`: gera `previa.png`, a imagem que aparece quando o link é mandado no WhatsApp.

Depois de mudar qualquer coisa:

```
python gerar_site.py
git add -A && git commit -m "o que mudou" && git push
```

## Moderadores

1. No Painel, aba **Equipe**, adicione o e-mail da pessoa (só o dono faz isso).
2. No Supabase, em **Authentication → Users → Add user**, crie o login com o mesmo e-mail e marque **Auto Confirm User**.

## Fontes

- Ruas: © colaboradores do [OpenStreetMap](https://www.openstreetmap.org/copyright), licença ODbL.
- Eleição e plano de governo: TSE.
- Contas: relatórios da prefeitura no Tesouro Nacional (Siconfi).

Projeto de moradores, sem partido.
