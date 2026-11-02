"""Renderiza cenas.html quadro a quadro (60 por segundo) e junta com a narração e a trilha.

    python render.py

O tamanho vem de tempos.js. Divide o vídeo em 4 partes que rodam ao mesmo tempo; uma parte já pronta não é refeita.
Sai em rinopolis-de-olho.mp4.
"""
import pathlib
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import imageio_ffmpeg

PASTA = pathlib.Path(__file__).parent
QUADROS = PASTA / '_quadros'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 60
from montar_voz import duracao
DURACAO = duracao()   # o tamanho da narração (tempos.js)
PARTES = 4


def parte(i):
    from playwright.sync_api import sync_playwright
    total = int(DURACAO * FPS)
    a, b = total * i // PARTES, total * (i + 1) // PARTES
    saida = QUADROS / f'parte_{i}.mp4'
    if (QUADROS / f'parte_{i}.done').exists():
        return saida
    ff = subprocess.Popen([FFMPEG, '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg',
                           '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', str(saida)],
                          stdin=subprocess.PIPE)
    with sync_playwright() as p:
        nav = p.chromium.launch(channel='chrome')
        pg = nav.new_page(viewport={'width': 1080, 'height': 1920})
        pg.goto((PASTA / 'cenas.html').as_uri())
        pg.wait_for_function('window.render && document.fonts.status === "loaded"')
        pg.wait_for_timeout(400)
        for q in range(a, b):
            pg.evaluate(f'render({q / FPS})')
            ff.stdin.write(pg.screenshot(type='jpeg', quality=92))
        nav.close()
    ff.stdin.close()
    ff.wait()
    (QUADROS / f'parte_{i}.done').touch()
    print('parte', i, 'pronta', flush=True)
    return saida


if __name__ == '__main__':
    QUADROS.mkdir(exist_ok=True)
    with ProcessPoolExecutor(PARTES) as ex:
        partes = list(ex.map(parte, range(PARTES)))
    lista = QUADROS / 'partes.txt'
    lista.write_text(''.join(f"file '{p.as_posix()}'\n" for p in partes), encoding='utf-8')
    imagem = QUADROS / 'imagem.mp4'
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(lista), '-c', 'copy', str(imagem)], check=True)
    if '--sem-audio' in sys.argv:
        sys.exit()
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', str(imagem), '-i', str(PASTA / '_audio' / 'mix.wav'),
                    '-filter:a', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-vf', 'scale=in_range=pc:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-crf', '20', '-preset', 'medium',
                    '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000',
                    '-shortest', '-movflags', '+faststart', str(PASTA / 'rinopolis-de-olho.mp4')], check=True)
    print(PASTA / 'rinopolis-de-olho.mp4')
