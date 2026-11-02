"""Junta as frases da narração numa faixa só e marca o tempo de cada cena e de cada frase.

Usado por gerar_voz.py (voz Kokoro) e por voz_elevenlabs.py (voz gravada na ElevenLabs).
O vídeo tem o tamanho da narração: nada de pausa longa entre as cenas.
"""
import json
import pathlib
import re

import numpy as np
import soundfile as sf

from roteiro import CENAS, ENDERECO

PASTA = pathlib.Path(__file__).parent
FOLGA = 1.1         # silêncio entre uma cena e a próxima (a animação da troca acontece aqui)
INICIO = 0.6        # silêncio antes da primeira frase
SOBRA_FIM = 3.2     # tempo da última cena depois que a voz termina


def frases():
    """[(cena, [frase, ...]), ...] na ordem do roteiro."""
    return [(nome, [f.strip() for f in re.findall(r'[^.?!:]+[.?!:]?', texto) if f.strip()]) for nome, texto in CENAS]


def aparar(som):
    """Corta o silêncio das pontas."""
    vivo = np.nonzero(np.abs(som) > 0.01)[0]
    return som[max(0, vivo[0] - 200):vivo[-1] + 800] if len(vivo) else som


def montar(sons, taxa):
    """sons: um áudio (numpy, mono) por frase, na ordem de frases(). Grava _audio/voz.wav e tempos.js."""
    blocos, k = [], 0
    for nome, lista in frases():
        partes = []
        for f in lista:
            partes.append((f, aparar(sons[k]), 0.38 if f[-1] in '?:' else 0.30)); k += 1
        blocos.append((nome, partes))
    pedacos, tempos, t = [np.zeros(int(INICIO * taxa), np.float32)], [], INICIO
    for i, (nome, partes) in enumerate(blocos):
        cena = {'nome': nome, 'inicio': round(t - (INICIO if i == 0 else FOLGA * 0.5), 3), 'frases': []}
        for f, som, pausa in partes:
            cena['frases'].append({'texto': f, 'inicio': round(t, 3), 'fim': round(t + len(som) / taxa, 3)})
            pedacos += [som.astype(np.float32), np.zeros(int(pausa * taxa), np.float32)]
            t += len(som) / taxa + pausa
        if i < len(blocos) - 1:
            pedacos.append(np.zeros(int(FOLGA * taxa), np.float32)); t += FOLGA
        tempos.append(cena)
    duracao = round(t + SOBRA_FIM, 2)
    for i, c in enumerate(tempos):
        c['fim'] = tempos[i + 1]['inicio'] if i + 1 < len(tempos) else duracao
    voz = np.concatenate(pedacos)
    voz = np.concatenate([voz, np.zeros(max(0, int(duracao * taxa) - len(voz)), np.float32)])[:int(duracao * taxa)]
    (PASTA / '_audio').mkdir(exist_ok=True)
    sf.write(PASTA / '_audio' / 'voz.wav', voz / max(1e-6, np.abs(voz).max()) * 0.9, taxa)
    (PASTA / 'tempos.js').write_text('window.TEMPOS = ' + json.dumps(tempos, ensure_ascii=False, indent=1) +
                                     ';\nwindow.ENDERECO = ' + json.dumps(ENDERECO) + ';\n', encoding='utf-8')
    print(f'vídeo de {duracao:.1f} s')
    for c in tempos:
        print(f"{c['inicio']:6.2f}-{c['fim']:6.2f} {c['nome']}")


def duracao():
    """Tamanho do vídeo, lido de tempos.js (fim da última cena)."""
    tempos = json.loads((PASTA / 'tempos.js').read_text(encoding='utf-8').split('window.TEMPOS = ')[1].split(';\nwindow.ENDERECO')[0])
    return tempos[-1]['fim']
