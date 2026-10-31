"""Gera as imagens do Instagram: logo do perfil e os 3 posts fixados.

    python gerar_insta.py

Monta cada imagem como uma página (com as letras e os ícones do site) e tira a foto com o
Chrome sem janela. Sai tudo na pasta insta/.
"""
import pathlib
import subprocess

PASTA = pathlib.Path(__file__).parent
SAIDA = PASTA / 'insta'
FONTES = SAIDA / '_paginas'
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


def icone(k, largura=2.4):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{largura}" stroke-linecap="round" stroke-linejoin="round">{ICONE[k]}</svg>'


LOGO = '''<svg class="logo" viewBox="0 0 48 48">
  <rect x="8.5" y="8.5" width="31" height="31" rx="4" transform="rotate(45 24 24)" fill="#f6c21a"/>
  <rect x="11.5" y="11.5" width="25" height="25" rx="2.5" transform="rotate(45 24 24)" fill="none" stroke="#17150e" stroke-width="2"/>
  <path d="M13.5 24c3-4.6 6.5-6.9 10.5-6.9s7.5 2.3 10.5 6.9c-3 4.6-6.5 6.9-10.5 6.9s-7.5-2.3-10.5-6.9z" fill="#ece9df" stroke="#17150e" stroke-width="2.2" stroke-linejoin="round"/>
  <circle cx="24" cy="24" r="4.4" fill="#17150e"/>
  <circle cx="25.6" cy="22.5" r="1.3" fill="#ece9df"/>
</svg>'''

# ruas ao fundo, inclinadas como no mapa da cidade
RUAS = '''<svg class="ruas" viewBox="0 0 1080 1350" preserveAspectRatio="none">
  <g stroke="#2c3036" stroke-width="10" fill="none" stroke-linecap="round">
    <path d="M-100 260L1180 -120"/><path d="M-100 520L1180 140"/><path d="M-100 780L1180 400"/><path d="M-100 1040L1180 660"/><path d="M-100 1300L1180 920"/><path d="M-100 1560L1180 1180"/>
    <path d="M90 -50L360 1400"/><path d="M420 -50L690 1400"/><path d="M750 -50L1020 1400"/>
  </g>
  <path d="M-100 1150L1180 330" stroke="#34383e" stroke-width="22" fill="none"/>
</svg>'''

BASE = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Barlow+Condensed:wght@600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0}
html,body{width:%(w)dpx;height:%(h)dpx;overflow:hidden;background:%(fundo)s}
body{font-family:"Atkinson Hyperlegible",sans-serif;color:#ece9df;position:relative}
.ruas{position:absolute;inset:0;width:100%%;height:100%%}
.placa-txt{font-family:"Barlow Condensed",sans-serif;font-weight:800;text-transform:uppercase;line-height:.95;letter-spacing:.005em}
.topo{position:absolute;left:0;right:0;top:0;height:18px;background:#f6c21a}
.marca{display:flex;align-items:center;gap:18px}
.marca .logo{width:86px;height:86px}
.marca small{display:block;font-family:"Barlow Condensed";font-weight:700;font-size:26px;letter-spacing:.2em;color:#f6c21a;line-height:1}
.marca strong{display:block;font-family:"Barlow Condensed";font-weight:800;font-size:52px;line-height:.9;letter-spacing:.01em}
.miolo{position:absolute;inset:18px 0 0 0;padding:70px 76px 64px;display:flex;flex-direction:column}
.eti{font-family:"Barlow Condensed";font-weight:700;font-size:34px;letter-spacing:.16em;text-transform:uppercase;color:#f6c21a}
.rodape{margin-top:auto;display:flex;align-items:center;justify-content:space-between;gap:24px}
.bio{background:#f6c21a;color:#17150e;font-family:"Barlow Condensed";font-weight:800;font-size:40px;letter-spacing:.04em;padding:16px 30px;border-radius:999px;white-space:nowrap}
.semp{font-size:24px;color:#b9b6ab;line-height:1.3;text-align:right}
.pino{position:relative;display:grid;place-items:center}
.pino::before{content:"";position:absolute;inset:15%%;background:#f6c21a;border-radius:6px;transform:rotate(45deg);outline:4px solid #17150e;outline-offset:-10px;box-shadow:0 10px 24px rgba(0,0,0,.55)}
.pino.velho::before{background:#ef5a3c}
.pino.feito::before{background:#43b27e}
.pino svg{position:relative;width:44%%;height:44%%;color:#17150e}
.dias{position:absolute;top:92%%;left:50%%;transform:translateX(-50%%);background:#17150e;color:#f6c21a;font-family:"Barlow Condensed";font-weight:800;font-size:34px;line-height:1;padding:6px 10px;border-radius:6px;white-space:nowrap}
.velho .dias{color:#ef5a3c}.feito .dias{color:#43b27e}
%(css)s
</style></head><body>%(corpo)s</body></html>'''


def pagina(nome, corpo, css='', w=1080, h=1350, fundo='#1b1d20'):
    FONTES.mkdir(parents=True, exist_ok=True)
    arq = FONTES / (nome + '.html')
    arq.write_text(BASE % {'w': w, 'h': h, 'corpo': corpo, 'css': css, 'fundo': fundo}, encoding='utf-8')
    png = SAIDA / (nome + '.png')
    args = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
            f'--window-size={w},{h}', '--virtual-time-budget=8000', f'--screenshot={png}', arq.as_uri()]
    if fundo == 'transparent':
        args.insert(1, '--default-background-color=00000000')
    subprocess.run(args, check=True, capture_output=True, timeout=120)
    print('ok', png.name)


def pino(tipo, estado='', dias='', tam=150):
    rot = f'<span class="dias">{dias}</span>' if dias else ''
    return f'<div class="pino {estado}" style="width:{tam}px;height:{tam}px">{icone(tipo)}{rot}</div>'


MARCA = f'<div class="marca">{LOGO}<span><small>RINÓPOLIS · SP</small><strong>DE OLHO</strong></span></div>'
RODAPE = '<div class="rodape"><span class="bio">LINK NA BIO</span><span class="semp">Projeto independente de moradores.<br>Sem partido.</span></div>'

# ---------- logos ----------
pagina('logo-perfil', f'<div style="position:absolute;inset:0;display:grid;place-items:center">{LOGO}</div>',
       '.logo{width:880px;height:880px}', 1080, 1080)
pagina('logo-sem-fundo', f'<div style="position:absolute;inset:0;display:grid;place-items:center">{LOGO}</div>',
       '.logo{width:1000px;height:1000px}', 1080, 1080, 'transparent')
pagina('logo-com-nome', f'<div style="position:absolute;inset:0;display:flex;align-items:center;padding:0 60px">{MARCA}</div>',
       '.marca{gap:40px}.marca .logo{width:300px;height:300px}.marca small{font-size:62px}.marca strong{font-size:170px}', 1200, 420, 'transparent')

# ---------- post 1: a chamada ----------
pagina('post-1-chamada', RUAS + '<div class="topo"></div><div class="miolo">' + MARCA + f'''
  <div class="cena">
    <div style="left:120px;top:40px">{pino('buraco', 'velho', '52 DIAS', 200)}</div>
    <div style="left:500px;top:100px">{pino('luz', '', '12 DIAS', 150)}</div>
    <div style="left:770px;top:10px">{pino('mato', 'feito', 'OK', 140)}</div>
  </div>
  <h1 class="placa-txt t1">Buraco, poste apagado, lixo, esgoto.</h1>
  <h1 class="placa-txt t2">Se ninguém marca, ninguém conserta.</h1>
  <p class="sub">O mapa dos moradores de Rinópolis. Marque o problema pelo celular, sem cadastro, e acompanhe os dias até o conserto.</p>
''' + RODAPE + '</div>',
       '.cena{position:relative;height:330px;margin:30px 0 40px}.cena>div{position:absolute}'
       '.t1{font-size:96px;margin-top:20px}.t2{font-size:96px;color:#f6c21a;margin-top:14px}'
       '.sub{font-size:32px;line-height:1.35;color:#d6d3c9;margin-top:30px;max-width:900px}')

# ---------- post 2: como funciona ----------
passos = [
    ('Toque em <b>Marcar problema</b> e arraste o mapa até o alfinete ficar no lugar.', 'buraco'),
    ('Escolha o tipo e, se quiser, mande uma <b>foto</b>.', 'lixo'),
    ('Os vizinhos <b>confirmam</b>, e a placa conta os dias até o conserto.', 'luz'),
]
lista = ''.join(f'<li><span class="num placa-txt">{i}</span><p>{t}</p></li>' for i, (t, _) in enumerate(passos, 1))
tipos = ''.join(f'<div class="tp">{pino(k, "", "", 120)}<span>{NOMES[k]}</span></div>' for k in ICONE)
pagina('post-2-como-funciona', RUAS + '<div class="topo"></div><div class="miolo">' + MARCA + f'''
  <span class="eti" style="margin-top:64px">Como funciona</span>
  <h1 class="placa-txt titulo">Marque em 3 passos</h1>
  <ol class="passos">{lista}</ol>
  <div class="tipos">{tipos}</div>
''' + RODAPE + '</div>',
       '.titulo{font-size:120px;margin-top:12px}'
       '.passos{list-style:none;padding:0;margin-top:46px;display:flex;flex-direction:column;gap:34px}'
       '.passos li{display:grid;grid-template-columns:96px 1fr;gap:30px;align-items:center}'
       '.num{width:92px;height:92px;display:grid;place-items:center;font-size:56px;color:#17150e;position:relative;isolation:isolate}'
       '.num::before{content:"";position:absolute;inset:8px;background:#f6c21a;transform:rotate(45deg);border-radius:6px;z-index:-1}'
       '.passos p{font-size:40px;line-height:1.25;color:#d6d3c9}.passos b{color:#ece9df}'
       '.tipos{display:grid;grid-template-columns:repeat(6,1fr);gap:6px;margin-top:56px}'
       '.tp{display:flex;flex-direction:column;align-items:center;gap:4px}.tp span{font-size:23px;color:#b9b6ab;text-align:center}')

# ---------- post 3: como cuidamos ----------
itens = [
    'Seu nome <b>não aparece</b> no mapa.',
    'Fotos e frases são <b>conferidas</b> antes de publicar.',
    'Os números das contas vêm de <b>fontes oficiais</b>.',
    '<b>Não apoiamos nem atacamos</b> nenhum político.',
]
cuidados = ''.join(f'<li><span class="ok"></span><p>{t}</p></li>' for t in itens)
pagina('post-3-sem-partido', RUAS + '<div class="topo"></div><div class="miolo">' + MARCA + f'''
  <span class="eti" style="margin-top:64px">Como cuidamos</span>
  <h1 class="placa-txt titulo">Sem partido.<br><span style="color:#f6c21a">Sem patrão.</span></h1>
  <ul class="cuid">{cuidados}</ul>
  <p class="nota">Termos de uso e política de privacidade no site.</p>
''' + RODAPE + '</div>',
       '.titulo{font-size:140px;margin-top:12px}'
       '.cuid{list-style:none;padding:0;margin-top:56px;display:flex;flex-direction:column;gap:30px}'
       '.cuid li{display:grid;grid-template-columns:70px 1fr;gap:26px;align-items:center}'
       '.ok{width:62px;height:62px;position:relative}'
       '.ok::before{content:"";position:absolute;inset:8px;background:#43b27e;transform:rotate(45deg);border-radius:5px}'
       '.ok::after{content:"";position:absolute;left:21px;top:16px;width:14px;height:24px;border:solid #17150e;border-width:0 6px 6px 0;transform:rotate(45deg)}'
       '.cuid p{font-size:40px;line-height:1.25;color:#d6d3c9}.cuid b{color:#ece9df}'
       '.nota{font-size:28px;color:#8f949b;margin-top:44px}')
print('Imagens em', SAIDA)
