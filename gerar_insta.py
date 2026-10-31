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

# ---------- post 1: a chamada ----------
pagina('post-1-chamada', mapa() + f'''
<div class="solto" style="left:250px;top:250px">{pino('buraco', 'velho', '52 DIAS', 150)}</div>
<div class="solto" style="left:610px;top:380px">{pino('luz', '', '12 DIAS', 120)}</div>
<div class="solto" style="left:780px;top:170px">{pino('mato', 'feito', 'OK', 110)}</div>
<div class="m">{MARCA}<div class="txt">
  <div class="eti">O mapa dos moradores de Rinópolis</div>
  <h1 style="font-size:118px">Se ninguém marca,<br><em>ninguém conserta.</em></h1>
  <p class="sub">Buraco, poste apagado, lixo, esgoto. Marque pelo celular e acompanhe os dias até o conserto.</p>
  {RODAPE}</div></div>''')

# ---------- post 2: como funciona ----------
passos = [
    'Toque em <b>Marcar problema</b> e arraste o mapa até o alfinete ficar no lugar.',
    'Escolha o tipo e, se quiser, mande uma <b>foto</b>.',
    'Os vizinhos <b>confirmam</b>, e a placa conta os dias até o conserto.',
]
lista = ''.join(f'<li><span class="num">{i}</span><p>{t}</p></li>' for i, t in enumerate(passos, 1))
tipos = ''.join(f'<div class="tp">{pino(k, "", "", 92)}<span>{NOMES[k]}</span></div>' for k in ICONE)
pagina('post-2-como-funciona', mapa(330, 1300, (10, 18, 30, 38)) + f'''
<div class="m">{MARCA}
  <div class="tipos">{tipos}</div>
  <div class="txt">
  <div class="eti">Como funciona</div>
  <h1 style="font-size:104px">Marque em <em>3 passos</em></h1>
  <ol class="passos">{lista}</ol>
  {RODAPE}</div></div>''',
       '.tipos{display:grid;grid-template-columns:repeat(6,1fr);gap:4px;margin-top:240px}'
       '.tp{display:flex;flex-direction:column;align-items:center;gap:2px}.tp span{font-size:21px;color:#b9b6ab;text-align:center}'
       '.passos{list-style:none;padding:0;margin-top:40px;display:flex;flex-direction:column;gap:26px}'
       '.passos li{display:grid;grid-template-columns:72px 1fr;gap:26px;align-items:center}'
       '.num{width:68px;height:68px;display:grid;place-items:center;font-family:"Barlow Condensed";font-weight:800;font-size:40px;color:#17150e;position:relative;isolation:isolate}'
       '.num::before{content:"";position:absolute;inset:7px;background:#f6c21a;transform:rotate(45deg);border-radius:5px;z-index:-1}'
       '.passos p{font-size:32px;line-height:1.35;color:#b9b6ab}.passos b{color:#ece9df}')

# ---------- post 3: como cuidamos ----------
itens = [
    'Seu nome <b>não aparece</b> no mapa.',
    'Fotos e frases são <b>conferidas</b> antes de publicar.',
    'Os números das contas vêm de <b>fontes oficiais</b>.',
    '<b>Não apoiamos nem atacamos</b> nenhum político.',
]
cuidados = ''.join(f'<li><span class="ok"></span><p>{t}</p></li>' for t in itens)
pagina('post-3-sem-partido', mapa(380, 1180, (10, 22, 40, 50)) + f'''
<div class="m">{MARCA}<div class="txt">
  <div class="eti">Como cuidamos</div>
  <h1 style="font-size:124px">Sem partido.<br><em>Sem patrão.</em></h1>
  <ul class="cuid">{cuidados}</ul>
  <p class="nota">Termos de uso e política de privacidade no site.</p>
  {RODAPE}</div></div>''',
       '.cuid{list-style:none;padding:0;margin-top:40px;display:flex;flex-direction:column;gap:22px}'
       '.cuid li{display:grid;grid-template-columns:56px 1fr;gap:22px;align-items:center}'
       '.ok{width:50px;height:50px;position:relative}'
       '.ok::before{content:"";position:absolute;inset:7px;background:#43b27e;transform:rotate(45deg);border-radius:4px}'
       '.ok::after{content:"";position:absolute;left:17px;top:12px;width:11px;height:19px;border:solid #17150e;border-width:0 5px 5px 0;transform:rotate(45deg)}'
       '.cuid p{font-size:32px;line-height:1.35;color:#b9b6ab}.cuid b{color:#ece9df}'
       '.nota{font-size:24px;color:#8f949b;margin-top:30px}')

shutil.rmtree(PAGINAS, ignore_errors=True)
print('Imagens em', SAIDA)
