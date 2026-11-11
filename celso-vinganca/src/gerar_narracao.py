"""Gera a narração com o TTS do Gemini (Google AI Studio).

Uso:
  export GEMINI_API_KEY=...        # sua chave do AI Studio (NÃO commitar)
  python3 src/gerar_narracao.py [--voz Algenib] [--modelo gemini-3.8-flash-tts]

Gera uma fala por vez e salva:
  assets/narracao_gancho.wav   -> "E se o Celso resolvesse se vingar?" (gancho do início)
  assets/narracao.wav          -> as 9 falas do roteiro com pausas entre elas
  assets/narracao_marcas.txt   -> segundo exato em que cada fala começa no WAV
  assets/narracao_falas/NN.wav -> cada fala separada (para conferir/refazer)
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T  # noqa: E402

API = 'https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent'
SR_TTS = 24000

# Os modelos TTS mais novos leem em voz alta qualquer instrução de estilo junto do texto,
# então mandamos só o texto: o timbre vem da voz escolhida e o ritmo, da pontuação.
ESTILO = ESTILO_GANCHO = ESTILO_FIM = ''


def tts(text, style, voice, model, key, tries=6):
    body = {
        'contents': [{'parts': [{'text': style + text}]}],
        'generationConfig': {
            'responseModalities': ['AUDIO'],
            'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice}}},
        },
    }
    for k in range(tries):
        req = urllib.request.Request(API % model, data=json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            part = d['candidates'][0]['content']['parts'][0]['inlineData']
            pcm = np.frombuffer(base64.b64decode(part['data']), '<i2').astype(np.float32) / 32768
            limite = len(text) / 5.0 + 4.0          # fala absurda de longa = leu algo a mais
            if len(pcm) / SR_TTS > limite:
                print('  duração suspeita (%.1fs), refazendo' % (len(pcm) / SR_TTS))
                time.sleep(8)
                continue
            time.sleep(7)                          # respeita o limite por minuto da cota gratuita
            return pcm
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError) as e:
            msg = e.read().decode()[:300] if isinstance(e, urllib.error.HTTPError) else str(e)
            print('  tentativa %d falhou: %s' % (k + 1, msg))
            time.sleep(15 * (k + 1))
    raise SystemExit('TTS falhou: ' + text)


def trim(x, thr=0.01, pad=0.08):
    idx = np.nonzero(np.abs(x) > thr)[0]
    if not len(idx):
        return x
    a = max(0, idx[0] - int(pad * SR_TTS))
    b = min(len(x), idx[-1] + int(pad * 2 * SR_TTS))
    return x[a:b]


def save(path, x, sr=SR_TTS):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


ESTILO_25 = ('Say in Brazilian Portuguese, like a human horror storyteller telling a tale at night: '
             'deep, calm, slow and mysterious voice, slightly ironic, with long pauses between sentences '
             'and at the ellipses, whispering the last line: ')
ESTILO_25_GANCHO = ('Say in Brazilian Portuguese, in a deep, intriguing, almost whispered horror narrator '
                    'voice, full of suspense: ')


def main_um_pedido(args, key):
    """Roteiro inteiro em 1 pedido (voz idêntica em todas as falas, gasta pouca cota).
    O render separa as 9 falas pelas pausas."""
    print('gancho:', T.HOOK_LINE)
    g = trim(tts(T.HOOK_LINE, ESTILO_25_GANCHO, args.voz, args.modelo, key))
    save(os.path.join(T.ASSETS, 'narracao_gancho.wav'), g)
    texto = '\n\n'.join(l[2] for l in T.LINES)
    print('roteiro inteiro (%d caracteres)' % len(texto))
    x = trim(tts(texto, ESTILO_25, args.voz, args.modelo, key))
    full = np.concatenate([np.zeros(int(0.3 * SR_TTS), np.float32), x])
    save(os.path.join(T.ASSETS, 'narracao.wav'), full)
    m = os.path.join(T.ASSETS, 'narracao_marcas.txt')
    if os.path.exists(m):
        os.remove(m)
    print('ok: narracao.wav %.1fs, gancho %.1fs (voz %s, modelo %s)' % (
        len(full) / SR_TTS, len(g) / SR_TTS, args.voz, args.modelo))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--voz', default='Algenib')
    ap.add_argument('--modelo', default='gemini-2.5-flash-preview-tts')
    ap.add_argument('--fala-por-fala', action='store_true',
                    help='1 pedido por fala (gasta 10 pedidos da cota diária)')
    args = ap.parse_args()
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        raise SystemExit('defina GEMINI_API_KEY')
    if not args.fala_por_fala:
        return main_um_pedido(args, key)
    d = os.path.join(T.ASSETS, 'narracao_falas')
    os.makedirs(d, exist_ok=True)

    print('gancho:', T.HOOK_LINE)
    g = trim(tts(T.HOOK_LINE, ESTILO_GANCHO, args.voz, args.modelo, key))
    save(os.path.join(T.ASSETS, 'narracao_gancho.wav'), g)

    gap = np.zeros(int(0.9 * SR_TTS), np.float32)
    parts, marks, t = [np.zeros(int(0.3 * SR_TTS), np.float32)], [], 0.3
    for i, (_, _, txt) in enumerate(T.LINES):
        style = ESTILO_FIM if i == len(T.LINES) - 1 else ESTILO
        print('fala %d: %s' % (i + 1, txt))
        x = trim(tts(txt, style, args.voz, args.modelo, key))
        save(os.path.join(d, '%02d.wav' % (i + 1)), x)
        marks.append(t)
        parts += [x, gap]
        t += (len(x) + len(gap)) / SR_TTS
    full = np.concatenate(parts)
    save(os.path.join(T.ASSETS, 'narracao.wav'), full)
    with open(os.path.join(T.ASSETS, 'narracao_marcas.txt'), 'w') as f:
        f.write('\n'.join('%.3f' % m for m in marks) + '\n')
    print('ok: narracao.wav %.1fs (voz %s, modelo %s)' % (len(full) / SR_TTS, args.voz, args.modelo))


if __name__ == '__main__':
    main()
