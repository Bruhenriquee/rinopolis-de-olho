"""Tira fotos da animação em alguns momentos e junta numa folha, para conferir as cenas.

    python folha_contato.py 2 5.5 9 ...
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

PASTA = pathlib.Path(__file__).parent
tempos = [float(x) for x in sys.argv[1:]] or [1, 3, 5.5, 9, 12, 15, 17, 19, 22, 24.5, 26, 29, 32, 34.5, 37, 40, 43, 46, 49, 53, 56, 59]
SAIDA = PASTA / '_quadros' / 'folha'
SAIDA.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    nav = p.chromium.launch(channel='chrome')
    pg = nav.new_page(viewport={'width': 1080, 'height': 1920})
    pg.goto((PASTA / 'cenas.html').as_uri())
    pg.wait_for_function('window.render && document.fonts.status === "loaded"')
    pg.wait_for_timeout(400)
    tiras = []
    for t in tempos:
        pg.evaluate(f'render({t})')
        arq = SAIDA / f'q_{t:05.1f}.jpg'
        pg.screenshot(path=str(arq), type='jpeg', quality=80)
        tiras.append(arq)
    nav.close()
# folha: miniaturas lado a lado, com o tempo embaixo
from PIL import Image, ImageDraw
L, A, COL = 270, 480, 6
folha = Image.new('RGB', (COL * (L + 6), ((len(tiras) + COL - 1) // COL) * (A + 30)), 'black')
for i, arq in enumerate(tiras):
    x, y = (i % COL) * (L + 6), (i // COL) * (A + 30)
    folha.paste(Image.open(arq).resize((L, A)), (x, y))
    ImageDraw.Draw(folha).text((x + 4, y + A + 6), arq.stem[2:] + 's', fill='white')
folha.save(SAIDA / 'folha.jpg', quality=80)
print(SAIDA / 'folha.jpg')
