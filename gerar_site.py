"""Gera a pasta docs/ (o site do GitHub Pages) a partir do index.html.

O index.html é escrito para o Claude, que coloca o cabeçalho da página sozinho.
Aqui a gente coloca esse cabeçalho (doctype, viewport, ícone, prévia do WhatsApp)
e copia os arquivos que o site usa. Rode depois de cada mudança:

    python gerar_site.py
"""
import pathlib
import re
import shutil

PASTA = pathlib.Path(__file__).parent
DOCS = PASTA / 'docs'

TITULO = 'Rinópolis de Olho'
DESCRICAO = 'O mapa dos moradores de Rinópolis-SP: marque buracos, luz apagada, lixo e esgoto, e acompanhe os dias até o conserto.'
ICONE = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E"
         "%3Crect x='8.5' y='8.5' width='31' height='31' rx='4' transform='rotate(45 24 24)' fill='%23f6c21a'/%3E"
         "%3Cpath d='M13.5 24c3-4.6 6.5-6.9 10.5-6.9s7.5 2.3 10.5 6.9c-3 4.6-6.5 6.9-10.5 6.9s-7.5-2.3-10.5-6.9z' "
         "fill='%23ece9df' stroke='%2317150e' stroke-width='2.2'/%3E%3Ccircle cx='24' cy='24' r='4.4' fill='%2317150e'/%3E%3C/svg%3E")

corpo = (PASTA / 'index.html').read_text(encoding='utf-8')
# tira do corpo o que vai para o cabeçalho
corpo = re.sub(r'^\s*<meta charset="utf-8">\s*', '', corpo)
corpo = re.sub(r'<title>.*?</title>\s*', '', corpo, count=1)
corpo = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\s*', '', corpo, count=1)

cabeca = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{TITULO}</title>
<meta name="description" content="{DESCRICAO}">
<meta property="og:title" content="{TITULO}">
<meta property="og:description" content="{DESCRICAO}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#1b1d20">
<link rel="icon" href="{ICONE}">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);color-scheme:dark}}body{{margin:0;font:14px system-ui,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
</head>
<body>
'''

DOCS.mkdir(exist_ok=True)
(DOCS / 'index.html').write_text(cabeca + corpo + '\n</body>\n</html>\n', encoding='utf-8')
for arquivo in ('ruas.js', 'config.js'):
    shutil.copy2(PASTA / arquivo, DOCS / arquivo)
(DOCS / '.nojekyll').write_text('', encoding='utf-8')
print('Site gerado em', DOCS)
