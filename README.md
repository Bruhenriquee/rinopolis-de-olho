# Rinópolis de Olho

O mapa dos moradores de Rinópolis-SP. A pessoa marca buraco, poste apagado, lixo ou esgoto no lugar exato, os vizinhos confirmam, e cada placa conta os dias até o conserto.

O site também mostra quem decide na cidade (prefeita, vice e os 9 vereadores), o plano de governo registrado no TSE, as contas da prefeitura e um pedido oficial pronto pra enviar.

## Como está organizado

- `index.html`: o site.
- `ruas.js`: as ruas da cidade, tiradas do OpenStreetMap.
- `config.js`: e-mail de contato e endereço do site.
- `gerar_site.py`: monta a pasta `docs/`, que é o que o GitHub Pages publica.

Depois de mudar qualquer coisa, rode:

```
python gerar_site.py
```

## Situação

Por enquanto as marcações ficam guardadas só no aparelho de quem marcou. O próximo passo é ligar um banco de dados, pra elas aparecerem pra cidade toda.

## Fontes

- Ruas: © colaboradores do [OpenStreetMap](https://www.openstreetmap.org/copyright), licença ODbL.
- Eleição e plano de governo: TSE.
- Contas: relatórios da prefeitura no Tesouro Nacional (Siconfi).

Projeto de moradores, sem partido.
