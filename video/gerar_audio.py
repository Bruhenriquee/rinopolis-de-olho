"""Faz a trilha (sintetizada aqui mesmo, sem direitos autorais) e mistura com a narração.

    python gerar_audio.py

Lê _audio/voz.wav e tempos.js; sai em _audio/mix.wav.
"""
import json
import pathlib

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

PASTA = pathlib.Path(__file__).parent
TAXA = 48000
DURACAO = 60.0
BPM = 92

voz, tv = sf.read(PASTA / '_audio' / 'voz.wav', dtype='float32')
if tv != TAXA:
    voz = np.interp(np.arange(int(len(voz) * TAXA / tv)) * tv / TAXA, np.arange(len(voz)), voz).astype(np.float32)
tempos = json.loads((PASTA / 'tempos.js').read_text(encoding='utf-8').split('window.TEMPOS = ')[1].split(';\nwindow.ENDERECO')[0])

n = int(DURACAO * TAXA)
t = np.arange(n) / TAXA
beat = 60 / BPM
musica = np.zeros(n, np.float32)
hz = lambda nota: 440 * 2 ** ((nota - 69) / 12)

# acordes: Lá menor, Fá, Dó, Sol (2 compassos cada), em loop
ACORDES = [[57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]]
compasso = 4 * beat
for k in range(int(DURACAO / (2 * compasso)) + 1):
    notas = ACORDES[k % 4]
    a = int(k * 2 * compasso * TAXA); b = min(n, int((k + 1) * 2 * compasso * TAXA) + int(.4 * TAXA))
    if a >= n: break
    tt = np.arange(b - a) / TAXA
    env = np.minimum(1, tt / .6) * np.minimum(1, (len(tt) / TAXA - tt) / .6)
    pad = sum(np.sin(2 * np.pi * hz(m) * tt) + .4 * np.sin(2 * np.pi * hz(m) * 2.003 * tt) for m in notas)
    musica[a:b] += (.05 * env * pad).astype(np.float32)
    # baixo: a fundamental uma oitava abaixo, a cada tempo
    for j in range(8):
        s = a + int(j * beat * TAXA); e = min(n, s + int(beat * TAXA))
        if s >= n: break
        u = np.arange(e - s) / TAXA
        musica[s:e] += (.11 * np.exp(-u * 3.2) * np.sin(2 * np.pi * hz(notas[0] - 12) * u)).astype(np.float32)
    # dedilhado suave em colcheias
    for j in range(16):
        s = a + int(j * beat / 2 * TAXA); e = min(n, s + int(.5 * TAXA))
        if s >= n: break
        u = np.arange(e - s) / TAXA
        m = notas[[0, 1, 2, 1][j % 4]] + 12
        musica[s:e] += (.035 * np.exp(-u * 7) * np.sin(2 * np.pi * hz(m) * u)).astype(np.float32)
# chimbal bem leve no contratempo
ruido = np.random.default_rng(3).standard_normal(int(.05 * TAXA)).astype(np.float32)
ruido = sosfilt(butter(4, 7000, 'hp', fs=TAXA, output='sos'), ruido).astype(np.float32)
for j in range(int(DURACAO / beat)):
    s = int((j + .5) * beat * TAXA)
    if s + len(ruido) < n: musica[s:s + len(ruido)] += .03 * ruido * np.exp(-np.arange(len(ruido)) / TAXA * 60)
musica = sosfilt(butter(2, 9000, 'lp', fs=TAXA, output='sos'), musica).astype(np.float32)

# whoosh suave na troca de cena
for c in tempos[1:]:
    s = int((c['inicio'] - .35) * TAXA); L = int(.7 * TAXA)
    if s < 0 or s + L > n: continue
    w = np.random.default_rng(int(s)).standard_normal(L).astype(np.float32)
    w = sosfilt(butter(2, [400, 3000], 'bp', fs=TAXA, output='sos'), w).astype(np.float32)
    musica[s:s + L] += .05 * w * np.sin(np.linspace(0, np.pi, L)) ** 2

# abaixa a trilha quando a voz fala (ducking) e sobe no fim
env = np.abs(voz[:n]) if len(voz) >= n else np.pad(np.abs(voz), (0, n - len(voz)))
janela = int(.25 * TAXA)
env = np.convolve(env, np.ones(janela) / janela, 'same')
duck = 1 - .6 * np.clip(env / .02, 0, 1)
duck = np.convolve(duck, np.ones(int(.15 * TAXA)) / int(.15 * TAXA), 'same')
entrada = np.clip(t / 1.0, 0, 1); saida = np.clip((DURACAO - t) / 2.5, 0, 1)
musica *= duck * entrada * saida

# um pouco de sala na voz
v = np.pad(voz, (0, max(0, n - len(voz))))[:n]
sala = np.zeros(n, np.float32)
for atraso, g in [(.023, .18), (.041, .12), (.067, .08)]:
    d = int(atraso * TAXA); sala[d:] += g * v[:-d]
v = v + sosfilt(butter(2, 4000, 'lp', fs=TAXA, output='sos'), sala).astype(np.float32)

mix = .85 * v + .9 * musica
mix /= max(1e-6, np.abs(mix).max()) / .9
sf.write(PASTA / '_audio' / 'mix.wav', mix.astype(np.float32), TAXA)
print('ok', PASTA / '_audio' / 'mix.wav')
