"""Gera os ícones do site instalado no celular (a placa amarela com o olho).

    python gerar_icones.py

Cria icone-192.png, icone-512.png, icone-maskable.png (com margem, pro Android recortar)
e apple-touch-icon.png (iPhone).
"""
import pathlib

from PIL import Image, ImageDraw

PASTA = pathlib.Path(__file__).parent
ASFALTO, PLACA, ESCURO, TINTA = (27, 29, 32), (246, 194, 26), (23, 21, 14), (236, 233, 223)


def olho(d, cx, cy, r):
    """Olho em forma de amêndoa, como o do logo do site."""
    pts = []
    for i in range(41):
        t = i / 40
        x = cx - r + 2 * r * t
        y = cy - r * 0.62 * (1 - (2 * t - 1) ** 2) ** 0.9
        pts.append((x, y))
    for i in range(41):
        t = 1 - i / 40
        x = cx - r + 2 * r * t
        y = cy + r * 0.62 * (1 - (2 * t - 1) ** 2) ** 0.9
        pts.append((x, y))
    d.polygon(pts, fill=TINTA, outline=ESCURO, width=max(2, int(r * 0.09)))
    p = r * 0.38
    d.ellipse([cx - p, cy - p, cx + p, cy + p], fill=ESCURO)
    b = r * 0.12
    d.ellipse([cx + p * 0.25 - b, cy - p * 0.4 - b, cx + p * 0.25 + b, cy - p * 0.4 + b], fill=TINTA)


def icone(tam, margem):
    """Desenha em 4x e reduz, pra borda sair lisa."""
    S = tam * 4
    img = Image.new('RGB', (S, S), ASFALTO)
    d = ImageDraw.Draw(img)
    c = S / 2
    r = S / 2 * (1 - margem)
    d.polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], fill=PLACA)
    ri = r * 0.84
    d.polygon([(c, c - ri), (c + ri, c), (c, c + ri), (c - ri, c)], outline=ESCURO, width=int(S * 0.018))
    olho(d, c, c, r * 0.5)
    return img.resize((tam, tam), Image.LANCZOS)


icone(192, 0.06).save(PASTA / 'icone-192.png')
icone(512, 0.06).save(PASTA / 'icone-512.png')
icone(512, 0.24).save(PASTA / 'icone-maskable.png')
icone(180, 0.10).save(PASTA / 'apple-touch-icon.png')
print('Ícones gerados em', PASTA)
