"""Gera as imagens do Instagram: logo do perfil e os 3 posts fixados.

    python gerar_insta.py

Monta cada imagem como uma página (com as letras, os ícones e as ruas de verdade do site) e tira
a foto com o Chrome sem janela. Sai tudo na pasta insta/.
"""
import pathlib
import shutil
import subprocess

PASTA = pathlib.Path(__file__).parent
SAIDA = PASTA / 'insta'
PAGINAS = SAIDA / '_paginas'
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

ICONE = {
    'buraco': '<ellipse cx="12" cy="14.5" rx="8.5" ry="4.5"/><path d="M7.5 13.5l2.5 1.6 2-2.2 2.2 2.1 2.3-1.4"/>',
    'luz': '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.8 10.6c.6.6.8 1.4.8 2.4h6c0-1 .2-1.8.8-2.4A6 6 0 0 0 12 3z"/><path d="M3 3l18 18"/>',
    'lixo': '<path d="M4 7h16M10 7V4h4v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/>',
    'agua': '<path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11z"/><path d="M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5"/>',
    'mato': '<path d="M3 20h18M7 20c0-5-2-8-3.5-9.5M12 20V5M17 20c0-5 2-8 3.5-9.5M9.5 20c0-4-.8-6-2.2-7.5M14.5 20c0-4 .8-6 2.2-7.5"/>',
    'outro': '<path d="M12 7v7M12 17.2v.3"/><circle cx="12" cy="12" r="9.5"/>',
}
NOMES = {'buraco': 'Buraco', 'luz': 'Luz apagada', 'lixo': 'Lixo', 'agua': 'Esgoto', 'mato': 'Mato alto', 'outro': 'Outro'}

LOGO = '''<svg class="logo" viewBox="0 0 48 48">
  <rect x="8.5" y="8.5" width="31" height="31" rx="4" transform="rotate(45 24 24)" fill="#f6c21a"/>
  <rect x="11.5" y="11.5" width="25" height="25" rx="2.5" transform="rotate(45 24 24)" fill="none" stroke="#17150e" stroke-width="2"/>
  <path d="M13.5 24c3-4.6 6.5-6.9 10.5-6.9s7.5 2.3 10.5 6.9c-3 4.6-6.5 6.9-10.5 6.9s-7.5-2.3-10.5-6.9z" fill="#ece9df" stroke="#17150e" stroke-width="2.2" stroke-linejoin="round"/>
  <circle cx="24" cy="24" r="4.4" fill="#17150e"/>
  <circle cx="25.6" cy="22.5" r="1.3" fill="#ece9df"/>
</svg>'''

BASE = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Barlow+Condensed:wght@600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0}
html,body{width:@W@px;height:@H@px;overflow:hidden;background:@FUNDO@}
body{font-family:"Atkinson Hyperlegible",sans-serif;color:#ece9df;position:relative}
canvas{position:absolute;left:0;top:0}
.veu{position:absolute;inset:0}
.m{position:absolute;inset:0;padding:88px;display:flex;flex-direction:column}
.marca{display:flex;align-items:center;gap:16px}
.marca .logo{width:58px;height:58px}
.marca b{font-family:"Barlow Condensed";font-weight:700;font-size:30px;letter-spacing:.14em;text-transform:uppercase}
.marca b span{color:#f6c21a}
.txt{margin-top:auto}
.eti{font-family:"Barlow Condensed";font-weight:600;font-size:28px;letter-spacing:.22em;text-transform:uppercase;color:#f6c21a}
h1{font-family:"Barlow Condensed";font-weight:800;text-transform:uppercase;line-height:.92;margin-top:18px}
h1 em{font-style:normal;color:#f6c21a}
.sub{font-size:32px;line-height:1.45;color:#b9b6ab;margin-top:30px;max-width:860px}
.pe{display:flex;justify-content:space-between;align-items:flex-end;border-top:1px solid #33373d;padding-top:30px;margin-top:46px}
.pe b{font-family:"Barlow Condensed";font-weight:700;font-size:34px;letter-spacing:.12em;text-transform:uppercase;color:#f6c21a}
.pe span{font-size:24px;color:#8f949b;text-align:right;line-height:1.4}
.solto{position:absolute}
.pino{position:relative;display:grid;place-items:center}
.pino::before{content:"";position:absolute;inset:15%;background:#f6c21a;border-radius:6px;transform:rotate(45deg);outline:4px solid #17150e;outline-offset:-10px;box-shadow:0 10px 24px rgba(0,0,0,.5)}
.pino.velho::before{background:#ef5a3c}
.pino.feito::before{background:#43b27e}
.pino svg{position:relative;width:44%;height:44%;color:#17150e}
.dias{position:absolute;top:92%;left:50%;transform:translateX(-50%);background:#17150e;color:#f6c21a;font-family:"Barlow Condensed";font-weight:800;font-size:30px;line-height:1;padding:6px 10px;border-radius:5px;white-space:nowrap}
.velho .dias{color:#ef5a3c}.feito .dias{color:#43b27e}
@CSS@
</style></head><body>@CORPO@</body></html>'''

# o mapa de verdade de Rinópolis (ruas.js), desenhado no alto da imagem
MAPA = '''<canvas id="c" width="1080" height="1350"></canvas>
<div class="veu" style="background:linear-gradient(180deg,rgba(23,25,28,.1) 0%,rgba(23,25,28,.2) @A@%,rgba(23,25,28,.95) @B@%,#17191c @C@%)"></div>
<script src="ruas.js"></script>
<script>
const M = window.MAPA, g = document.getElementById('c').getContext('2d'), KX = Math.cos(M.lat0*Math.PI/180);
let minx=1e9,maxx=-1e9,miny=1e9,maxy=-1e9; const ruas=[];
for (const [ni,k,f] of M.ruas) { const l=[]; for (let j=0;j<f.length;j+=2) { const x=f[j+1]*KX, y=-f[j]; l.push([x,y]);
  if (k===2) { minx=Math.min(minx,x);maxx=Math.max(maxx,x);miny=Math.min(miny,y);maxy=Math.max(maxy,y); } } ruas.push([k,l]); }
const cx=(minx+maxx)/2, cy=(miny+maxy)/2, esc=@ZOOM@/(maxx-minx);
g.lineCap='round'; g.lineJoin='round';
for (const [k,l] of ruas) { g.beginPath(); l.forEach(([x,y],i) => { const X=540+(x-cx)*esc, Y=@CY@+(y-cy)*esc; i?g.lineTo(X,Y):g.moveTo(X,Y); });
  g.strokeStyle = k<=1 ? '#565a61' : '#3a3e45'; g.lineWidth = k<=1 ? 8 : 5; g.stroke(); }
</script>'''


def mapa(centro_y=470, zoom=1180, veu=(20, 38, 60, 72)):
    a, b, c, d = veu
    return (MAPA.replace('@CY@', str(centro_y)).replace('@ZOOM@', str(zoom))
            .replace('@A@', str(b)).replace('@B@', str(c)).replace('@C@', str(d)))


def icone(k, largura=2.4):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{largura}" stroke-linecap="round" stroke-linejoin="round">{ICONE[k]}</svg>'


def pino(tipo, estado='', dias='', tam=150):
    rot = f'<span class="dias">{dias}</span>' if dias else ''
    return f'<div class="pino {estado}" style="width:{tam}px;height:{tam}px">{icone(tipo)}{rot}</div>'


def pagina(nome, corpo, css='', w=1080, h=1350, fundo='#17191c'):
    PAGINAS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PASTA / 'ruas.js', PAGINAS / 'ruas.js')
    arq = PAGINAS / (nome + '.html')
    arq.write_text(BASE.replace('@W@', str(w)).replace('@H@', str(h)).replace('@FUNDO@', fundo)
                   .replace('@CSS@', css).replace('@CORPO@', corpo), encoding='utf-8')
    png = SAIDA / (nome + '.png')
    args = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
            f'--window-size={w},{h}', '--virtual-time-budget=8000', f'--screenshot={png}', arq.as_uri()]
    if fundo == 'transparent':
        args.insert(1, '--default-background-color=00000000')
    subprocess.run(args, check=True, capture_output=True, timeout=120)
    print('ok', png.name)


MARCA = f'<div class="marca">{LOGO}<b>Rinópolis <span>de Olho</span></b></div>'
RODAPE = '<div class="pe"><b>Link na bio →</b><span>Projeto independente de moradores<br>Sem vínculo partidário</span></div>'

# ---------- logos ----------
pagina('logo-perfil', f'<div style="position:absolute;inset:0;display:grid;place-items:center">{LOGO}</div>',
       '.logo{width:880px;height:880px}', 1080, 1080, '#1b1d20')
pagina('logo-sem-fundo', f'<div style="position:absolute;inset:0;display:grid;place-items:center">{LOGO}</div>',
       '.logo{width:1000px;height:1000px}', 1080, 1080, 'transparent')
pagina('logo-com-nome', f'''<div style="position:absolute;inset:0;display:flex;align-items:center;padding:0 60px">
  <div class="marca">{LOGO}<span><small>RINÓPOLIS · SP</small><strong>DE OLHO</strong></span></div></div>''',
       '.marca{gap:40px}.marca .logo{width:300px;height:300px}'
       '.marca small{display:block;font-family:"Barlow Condensed";font-weight:700;font-size:62px;letter-spacing:.2em;color:#f6c21a;line-height:1}'
       '.marca strong{display:block;font-family:"Barlow Condensed";font-weight:800;font-size:170px;line-height:.9}', 1200, 420, 'transparent')

# ---------- os 3 posts fixados: um painel só, cortado em 3 ----------
# No perfil os 3 ficam lado a lado e a mesma rua atravessa os três; sozinho, cada um continua completo.
# Formato 3:4 (1080x1440), o mesmo da grade do perfil: nada é cortado e a rua emenda certinho.
L, A = 1080, 1440
RUA_Y, RUA_H = 520, 150          # faixa da rua (topo e altura)


def placa(x, tipo, estado, rotulo, tam=170):
    """Placa de rua fincada na calçada de cima, com o poste descendo até o asfalto."""
    poste = RUA_Y - 330
    return (f'<div class="poste" style="left:{x - 7}px;top:{poste + tam // 2}px;height:{RUA_Y - poste - tam // 2}px"></div>'
            f'<div class="solto" style="left:{x - tam // 2}px;top:{poste - tam // 2 + 40}px">{pino(tipo, estado, rotulo, tam)}</div>')


def painel(n, eti, titulo, tam_titulo, corpo):
    marcas = ''.join(f'<i class="{"on" if k == n else ""}"></i>' for k in (1, 2, 3))
    return f'''<div class="m" style="left:{(n - 1) * L}px;width:{L}px">{MARCA}<div class="txt">
  <div class="eti">{eti}</div>
  <h1 style="font-size:{tam_titulo}px">{titulo}</h1>
  {corpo}
  <div class="pe"><b>Link na bio →</b><span class="seq">{marcas}</span></div></div></div>'''


passos = [
    'Toque em <b>Marcar problema</b> e arraste o mapa até o alfinete ficar no lugar.',
    'Escolha o tipo e, se quiser, mande uma <b>foto</b>.',
    'Os vizinhos <b>confirmam</b>, e a placa conta os dias até o conserto.',
]
itens = [
    'Seu nome <b>não aparece</b> no mapa.',
    'Fotos e frases são <b>conferidas</b> antes de publicar.',
    'Os números das contas vêm de <b>fontes oficiais</b>.',
    '<b>Não apoiamos nem atacamos</b> nenhum político.',
]
lista = ''.join(f'<li><span class="num">{i}</span><p>{t}</p></li>' for i, t in enumerate(passos, 1))
cuidados = ''.join(f'<li><span class="ok"></span><p>{t}</p></li>' for t in itens)

MAPA_LARGO = f'''<canvas id="c" width="{3 * L}" height="{A}"></canvas>
<script src="ruas.js"></script>
<script>
const M = window.MAPA, g = document.getElementById('c').getContext('2d'), KX = Math.cos(M.lat0*Math.PI/180);
let minx=1e9,maxx=-1e9,miny=1e9,maxy=-1e9; const ruas=[];
for (const [ni,k,f] of M.ruas) {{ const l=[]; for (let j=0;j<f.length;j+=2) {{ const x=f[j+1]*KX, y=-f[j]; l.push([x,y]);
  if (k===2) {{ minx=Math.min(minx,x);maxx=Math.max(maxx,x);miny=Math.min(miny,y);maxy=Math.max(maxy,y); }} }} ruas.push([k,l]); }}
const cx=(minx+maxx)/2, cy=(miny+maxy)/2, esc=2600/(maxx-minx);
g.lineCap='round'; g.lineJoin='round';
for (const [k,l] of ruas) {{ g.beginPath(); l.forEach(([x,y],i) => {{ const X={3 * L // 2}+(x-cx)*esc, Y=420+(y-cy)*esc; i?g.lineTo(X,Y):g.moveTo(X,Y); }});
  g.strokeStyle = k<=1 ? '#4a4e55' : '#33373d'; g.lineWidth = k<=1 ? 8 : 5; g.stroke(); }}
</script>
<div class="veu" style="background:linear-gradient(180deg,rgba(23,25,28,.35) 0%,rgba(23,25,28,.15) 25%,rgba(23,25,28,.9) 50%,#17191c 58%)"></div>
<div class="rua"><i class="meio"></i></div>'''

pagina('_painel', MAPA_LARGO
       + placa(560, 'buraco', 'velho', '52 DIAS', 190) + placa(860, 'luz', 'velho', '38 DIAS', 120)
       + placa(1640, 'buraco', '', 'HOJE', 190)
       + placa(2700, 'buraco', 'feito', 'CONSERTADO', 190) + placa(2380, 'luz', 'feito', 'OK', 120)
       + painel(1, 'O mapa dos moradores de Rinópolis', 'Se ninguém marca,<br><em>ninguém conserta.</em>', 112,
                '<p class="sub">Buraco, poste apagado, lixo, esgoto. Marque pelo celular e acompanhe os dias até o conserto.</p>')
       + painel(2, 'Como funciona', 'Marque em<br><em>3 passos.</em>', 112, f'<ol class="passos">{lista}</ol>')
       + painel(3, 'Como cuidamos', 'Sem partido.<br><em>Sem patrão.</em>', 112,
                f'<ul class="cuid">{cuidados}</ul>'),
       '.m{top:0;bottom:0;right:auto;padding:88px 88px 80px}'
       '.txt{margin-top:0;position:absolute;left:88px;right:88px;top:725px;bottom:80px}'
       '.txt .pe{position:absolute;left:0;right:0;bottom:0;margin:0}'
       f'.rua{{position:absolute;left:0;right:0;top:{RUA_Y}px;height:{RUA_H}px;background:#26292d;border-top:6px solid #3c4148;border-bottom:6px solid #3c4148}}'
       '.rua .meio{position:absolute;left:0;right:0;top:50%;height:10px;margin-top:-5px;background:repeating-linear-gradient(90deg,#f6c21a 0 70px,transparent 70px 120px)}'
       '.poste{position:absolute;width:14px;background:linear-gradient(90deg,#8f949b,#5d6168);border-radius:3px}'
       '.dias{font-size:34px}'
       '.sub{font-size:34px}'
       '.seq{display:flex;gap:14px}.seq i{width:22px;height:22px;transform:rotate(45deg);border:3px solid #f6c21a;border-radius:3px}.seq i.on{background:#f6c21a}'
       '.passos{list-style:none;padding:0;margin-top:32px;display:flex;flex-direction:column;gap:18px}'
       '.passos li{display:grid;grid-template-columns:72px 1fr;gap:26px;align-items:center}'
       '.num{width:68px;height:68px;display:grid;place-items:center;font-family:"Barlow Condensed";font-weight:800;font-size:40px;color:#17150e;position:relative;isolation:isolate}'
       '.num::before{content:"";position:absolute;inset:7px;background:#f6c21a;transform:rotate(45deg);border-radius:5px;z-index:-1}'
       '.passos p{font-size:31px;line-height:1.35;color:#b9b6ab}.passos b{color:#ece9df}'
       '.cuid{list-style:none;padding:0;margin-top:36px;display:flex;flex-direction:column;gap:20px}'
       '.cuid li{display:grid;grid-template-columns:56px 1fr;gap:22px;align-items:center}'
       '.ok{width:50px;height:50px;position:relative}'
       '.ok::before{content:"";position:absolute;inset:7px;background:#43b27e;transform:rotate(45deg);border-radius:4px}'
       '.ok::after{content:"";position:absolute;left:17px;top:12px;width:11px;height:19px;border:solid #17150e;border-width:0 5px 5px 0;transform:rotate(45deg)}'
       '.cuid p{font-size:31px;line-height:1.35;color:#b9b6ab}.cuid b{color:#ece9df}',
       3 * L, A)

from PIL import Image
inteiro = Image.open(SAIDA / '_painel.png').convert('RGB')
for k, nome in enumerate(('post-1-chamada', 'post-2-como-funciona', 'post-3-sem-partido')):
    inteiro.crop((k * L, 0, (k + 1) * L, A)).save(SAIDA / (nome + '.png'))
    print('ok', nome + '.png')
# o painel inteiro fica salvo pra conferir como o perfil vai ficar
inteiro.resize((3 * L // 2, A // 2)).save(SAIDA / 'perfil-previa.jpg', quality=88)
(SAIDA / '_painel.png').unlink()

shutil.rmtree(PAGINAS, ignore_errors=True)
print('Imagens em', SAIDA)
