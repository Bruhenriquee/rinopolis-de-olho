"""Gera a narração com a voz Kokoro (português) e o arquivo de tempos de cada cena.

    python gerar_voz.py      (com o Python do venv em _ferramentas)

Sai em _audio/voz.wav e tempos.js. Para usar a voz da ElevenLabs, rode voz_elevenlabs.py no lugar deste.
"""
import numpy as np
import sherpa_onnx

from montar_voz import PASTA, frases, montar

MODELO = PASTA / '_ferramentas' / 'kokoro-multi-lang-v1_0'
VOZ = 42            # pf_dora, português do Brasil
VELOCIDADE = 1.0

kokoro = sherpa_onnx.OfflineTtsKokoroModelConfig(
    model=str(MODELO / 'model.onnx'), voices=str(MODELO / 'voices.bin'), tokens=str(MODELO / 'tokens.txt'),
    data_dir=str(MODELO / 'espeak-ng-data'), dict_dir=str(MODELO / 'dict'),
    lexicon=f"{MODELO / 'lexicon-us-en.txt'},{MODELO / 'lexicon-zh.txt'}", lang='pt-br')
tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(kokoro=kokoro, num_threads=4)))

sons, taxa = [], 24000
for _, lista in frases():
    for f in lista:
        a = tts.generate(f, sid=VOZ, speed=VELOCIDADE)
        sons.append(np.array(a.samples, dtype=np.float32)); taxa = a.sample_rate
montar(sons, taxa)
