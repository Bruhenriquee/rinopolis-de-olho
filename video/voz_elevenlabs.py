"""Usa a narração gravada na ElevenLabs no lugar da voz Kokoro.

    python voz_elevenlabs.py      (com o Python do venv em _ferramentas, que tem o Whisper)

Coloque em video/_audio/elevenlabs/ a narração inteira num arquivo só (o texto corrido do roteiro),
ou um arquivo por cena, 1.mp3 a 8.mp3 (pode ser .wav ou .m4a). Com o arquivo único, as frases são
separadas reconhecendo as palavras; com um por cena, pelas pausas mais longas da fala.
Sai em _audio/voz.wav e tempos.js, como gerar_voz.py.
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
if len(arquivos) not in (1, len(cenas)):
    sys.exit(f'Achei {len(arquivos)} arquivos em {pasta}: ponha a narração inteira num arquivo só, ou um por cena (1 a {len(cenas)}).')


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


def por_palavras(som, arq):
    """Narração inteira num arquivo só: acha onde cada frase começa reconhecendo as palavras (Whisper)
    e corta no meio do silêncio entre a última palavra de uma frase e a primeira da seguinte."""
    from faster_whisper import WhisperModel
    modelo = WhisperModel('small', device='cpu', compute_type='int8', download_root=str(PASTA / '_ferramentas' / 'whisper'))
    segs, _ = modelo.transcribe(str(arq), language='pt', word_timestamps=True)
    palavras = [(w.start, w.end) for s in segs for w in s.words]
    contagem = [len(f.split()) for _, lista in cenas for f in lista]
    if len(palavras) != sum(contagem):
        sys.exit(f'A voz tem {len(palavras)} palavras e o roteiro {sum(contagem)}: confira se o texto foi lido inteiro, sem trocar palavras.')
    cortes, k = [0], 0
    for n in contagem[:-1]:
        k += n
        cortes.append(int((palavras[k - 1][1] + palavras[k][0]) / 2 * TAXA))
    tempos, k = [], 0
    for i, n in enumerate(contagem):
        tempos.append([(a - cortes[i] / TAXA, b - cortes[i] / TAXA) for a, b in palavras[k:k + n]]); k += n
    return np.split(som, cortes[1:]), tempos


sons, palavras = [], None
if len(arquivos) == 1:
    sons, palavras = por_palavras(ler(arquivos[0]), arquivos[0])
else:
    for arq, (nome, lista) in zip(arquivos, cenas):
        sons += dividir(ler(arq), len(lista))
montar(sons, TAXA, palavras)
