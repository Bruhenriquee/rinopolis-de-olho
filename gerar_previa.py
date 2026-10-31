"""Gera previa.png (1200x630): a imagem que aparece quando o link do site é mandado no WhatsApp.

    python gerar_previa.py
"""
import math
import pathlib
import random

from PIL import Image, ImageDraw, ImageFont

PASTA = pathlib.Path(__file__).parent
W, H = 1200, 630
ASFALTO, RUA, RUA_FORTE = (27, 29, 32), (60, 64, 70), (110, 106, 96)
PLACA, ESCURO, TINTA, TINTA2, ALERTA = (246, 194, 26), (23, 21, 14), (236, 233, 223), (185, 182, 171), (239, 90, 60)


def fonte(tamanho, estilo='Bold Condensed'):
    try:
        f = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', tamanho)
        f.set_variation_by_name(estilo)
        return f
    except Exception:
        return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', tamanho)


def losango(d, cx, cy, r, cor, contorno=None, largura=0):
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    d.polygon(pts, fill=cor, outline=contorno, width=largura)


img = Image.new('RGB', (W, H), ASFALTO)
d = ImageDraw.Draw(img)

# ruas ao fundo, inclinadas como no mapa da cidade
random.seed(7)
ang = math.radians(-33)
for i in range(-14, 22):
    off = i * 58
    x0, y0 = -200 + off * math.cos(ang + math.pi / 2), off * math.sin(ang + math.pi / 2)
    d.line([(x0, y0), (x0 + 2000 * math.cos(ang), y0 + 2000 * math.sin(ang))], fill=RUA, width=4)
    x0, y0 = off * 1.2, -100
    d.line([(x0, y0), (x0 + 1500 * math.cos(ang + 1.2), y0 + 1500 * math.sin(ang + 1.2))], fill=RUA, width=4)
d.line([(-50, 620), (1250, -180)], fill=RUA_FORTE, width=12)

# véu escuro à esquerda pra o texto ler bem
veu = Image.new('L', (W, H), 0)
dv = ImageDraw.Draw(veu)
for x in range(W):
    dv.line([(x, 0), (x, H)], fill=int(235 * max(0.0, 1 - x / 820)))
img.paste(Image.new('RGB', (W, H), ASFALTO), (0, 0), veu)
d = ImageDraw.Draw(img)

# placas no mapa
for cx, cy, cor in [(905, 205, PLACA), (1035, 395, ALERTA), (820, 470, PLACA)]:
    losango(d, cx, cy, 46, cor)
    losango(d, cx, cy, 36, None, ESCURO, 4)
    d.ellipse([cx - 16, cy - 8, cx + 16, cy + 10], outline=ESCURO, width=5)

# logo: placa amarela com olho
cx, cy, r = 120, 150, 62
losango(d, cx, cy, r, PLACA)
losango(d, cx, cy, r - 12, None, ESCURO, 4)
d.ellipse([cx - 34, cy - 18, cx + 34, cy + 18], fill=TINTA, outline=ESCURO, width=5)
d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=ESCURO)

d.text((205, 104), 'RINÓPOLIS', font=fonte(34), fill=PLACA)
d.text((200, 132), 'DE OLHO', font=fonte(104), fill=TINTA)
d.text((70, 300), 'Viu um buraco, um poste apagado,', font=fonte(46, 'SemiBold Condensed'), fill=TINTA)
d.text((70, 352), 'lixo ou esgoto? Marque no mapa.', font=fonte(46, 'SemiBold Condensed'), fill=TINTA)
d.text((70, 430), 'Cada placa conta os dias até o conserto.', font=fonte(34, 'Condensed'), fill=TINTA2)
d.rectangle([70, 520, 470, 572], fill=PLACA)
d.text((92, 527), 'MARCAR UM PROBLEMA', font=fonte(34), fill=ESCURO)
d.text((70, 592), 'O mapa dos moradores · sem partido', font=fonte(24, 'Condensed'), fill=TINTA2)

img.save(PASTA / 'previa.png', optimize=True)
print('previa.png gerada')
