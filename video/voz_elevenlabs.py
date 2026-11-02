"""Usa a narração gravada na ElevenLabs no lugar da voz Kokoro.

    python voz_elevenlabs.py

Coloque em video/_audio/elevenlabs/ um arquivo por cena, na ordem do roteiro-elevenlabs.md:
1.mp3 a 8.mp3 (pode ser .wav ou .m4a). Quando a cena tem mais de uma frase, o corte entre elas é feito
nas pausas mais longas da fala. Sai em _audio/voz.wav e tempos.js, como gerar_voz.py.
"""
import subprocess
import sys

import imageio_ffmpeg
import numpy as np

from montar_voz import PASTA, frases, montar

TAXA = 48000
pasta = PASTA / '_audio' / 'elevenlabs'
arquivos = sorted((p for p in pasta.glob('*') if p.suffix.lower() in ('.mp3', '.wav', '.m4a')), key=lambda p: int(''.join(c for c in p.stem if c.isdigit()) or 0))
cenas = frases()
if len(arquivos) != len(cenas):
    sys.exit(f'Achei {len(arquivos)} arquivos em {pasta}, mas o roteiro tem {len(cenas)} cenas (1 a {len(cenas)}).')


def ler(arq):
    bruto = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-loglevel', 'error', '-i', str(arq),
                            '-ac', '1', '-ar', str(TAXA), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(bruto, dtype=np.float32).copy()


def dividir(som, n):
    """Corta em n pedaços nas n-1 pausas mais longas (trechos de 20 ms abaixo de -40 dB)."""
    if n == 1:
        return [som]
    q = int(0.02 * TAXA)
    alto = np.sqrt(np.mean(som[:len(som) // q * q].reshape(-1, q) ** 2, axis=1)) > 0.01
    pausas, i = [], 0
    while i < len(alto):
        if not alto[i]:
            j = i
            while j < len(alto) and not alto[j]:
                j += 1
            if i > 0 and j < len(alto):          # só pausas no meio da fala
                pausas.append((j - i, (i + j) // 2 * q))
            i = j
        else:
            i += 1
    if len(pausas) < n - 1:
        sys.exit(f'Não achei {n - 1} pausas para separar as frases; grave com uma pausa clara entre elas.')
    cortes = sorted(c for _, c in sorted(pausas, reverse=True)[:n - 1])
    return np.split(som, cortes)


sons = []
for arq, (nome, lista) in zip(arquivos, cenas):
    sons += dividir(ler(arq), len(lista))
montar(sons, TAXA)
