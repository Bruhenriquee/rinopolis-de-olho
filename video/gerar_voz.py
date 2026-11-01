"""Gera a narração (voz Kokoro em português) e o arquivo de tempos de cada cena.

    python gerar_voz.py

Sai em _audio/voz.wav e tempos.js (início e fim de cada cena e de cada frase, em segundos).
"""
import json
import pathlib
import re

import numpy as np
import sherpa_onnx
import soundfile as sf

from roteiro import CENAS, ENDERECO

PASTA = pathlib.Path(__file__).parent
MODELO = PASTA / '_ferramentas' / 'kokoro-multi-lang-v1_0'
SAIDA = PASTA / '_audio'
DURACAO = 60.0      # duração total do vídeo
SOBRA_FIM = 3.2     # tempo da última cena depois que a voz termina
VOZ = 42            # pf_dora, português do Brasil
VELOCIDADE = 1.0

kokoro = sherpa_onnx.OfflineTtsKokoroModelConfig(
    model=str(MODELO / 'model.onnx'), voices=str(MODELO / 'voices.bin'), tokens=str(MODELO / 'tokens.txt'),
    data_dir=str(MODELO / 'espeak-ng-data'), dict_dir=str(MODELO / 'dict'),
    lexicon=f"{MODELO / 'lexicon-us-en.txt'},{MODELO / 'lexicon-zh.txt'}", lang='pt-br')
tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(kokoro=kokoro, num_threads=4)))


def falar(texto):
    a = tts.generate(texto, sid=VOZ, speed=VELOCIDADE)
    som = np.array(a.samples, dtype=np.float32)
    # corta o silêncio que o modelo deixa nas pontas
    vivo = np.nonzero(np.abs(som) > 0.01)[0]
    return (som[max(0, vivo[0] - 200):vivo[-1] + 800] if len(vivo) else som), a.sample_rate


# cada cena vira frases curtas; a pausa depende da pontuação
blocos = []
for nome, texto in CENAS:
    frases = [f.strip() for f in re.findall(r'[^.?!:]+[.?!:]?', texto) if f.strip()]
    partes = []
    for f in frases:
        som, taxa = falar(f)
        partes.append((f, som, 0.38 if f[-1] in '?:' else 0.30))
    blocos.append((nome, partes))

voz_total = sum(len(s) / taxa + p for _, partes in blocos for _, s, p in partes)
folga = max(0.35, (DURACAO - SOBRA_FIM - 0.6 - voz_total) / (len(blocos) - 1))

pedacos, tempos, t = [np.zeros(int(0.6 * taxa), np.float32)], [], 0.6
for i, (nome, partes) in enumerate(blocos):
    cena = {'nome': nome, 'inicio': round(t - (0.6 if i == 0 else folga * 0.5), 3), 'frases': []}
    for f, som, pausa in partes:
        cena['frases'].append({'texto': f, 'inicio': round(t, 3), 'fim': round(t + len(som) / taxa, 3)})
        pedacos += [som, np.zeros(int(pausa * taxa), np.float32)]
        t += len(som) / taxa + pausa
    if i < len(blocos) - 1:
        pedacos.append(np.zeros(int(folga * taxa), np.float32)); t += folga
    tempos.append(cena)
for i, c in enumerate(tempos):
    c['fim'] = tempos[i + 1]['inicio'] if i + 1 < len(tempos) else DURACAO

SAIDA.mkdir(exist_ok=True)
voz = np.concatenate(pedacos)
voz = np.concatenate([voz, np.zeros(max(0, int(DURACAO * taxa) - len(voz)), np.float32)])[:int(DURACAO * taxa)]
sf.write(SAIDA / 'voz.wav', voz / max(1e-6, np.abs(voz).max()) * 0.9, taxa)
(PASTA / 'tempos.js').write_text('window.TEMPOS = ' + json.dumps(tempos, ensure_ascii=False, indent=1) +
                                 ';\nwindow.ENDERECO = ' + json.dumps(ENDERECO) + ';\n', encoding='utf-8')
print(f'voz {voz_total:.1f}s, folga entre cenas {folga:.2f}s')
for c in tempos:
    print(f"{c['inicio']:6.2f}-{c['fim']:6.2f} {c['nome']}")
