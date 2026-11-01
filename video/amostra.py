"""Renderiza só um trecho do vídeo, com o som, para aprovar o estilo antes do resto.

    python amostra.py 0 14
"""
import pathlib
import subprocess
import sys

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

PASTA = pathlib.Path(__file__).parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 60
a, b = float(sys.argv[1]), float(sys.argv[2])
saida = PASTA / f'amostra_{int(a)}-{int(b)}s.mp4'
ff = subprocess.Popen([FFMPEG, '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                       '-ss', str(a), '-t', str(b - a), '-i', str(PASTA / '_audio' / 'mix.wav'),
                       '-vf', 'scale=in_range=pc:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-crf', '19', '-color_range', 'tv',
                       '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', str(saida)], stdin=subprocess.PIPE)
with sync_playwright() as p:
    nav = p.chromium.launch(channel='chrome')
    pg = nav.new_page(viewport={'width': 1080, 'height': 1920})
    pg.goto((PASTA / 'cenas.html').as_uri())
    pg.wait_for_function('window.render && document.fonts.status === "loaded"')
    pg.wait_for_timeout(400)
    for q in range(int(a * FPS), int(b * FPS)):
        pg.evaluate(f'render({q / FPS})')
        ff.stdin.write(pg.screenshot(type='jpeg', quality=92))
    nav.close()
ff.stdin.close()
ff.wait()
print(saida)
