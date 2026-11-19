"""Troca vários blocos de uma vez a partir de UMA gravação com rótulos falados ("um", "dois"... ou o nome do bloco) antes de cada frase.

Uso: python3 trocar_lote.py <gravação bruta> <bloco1,bloco2,...>    ex.: trocar_lote.py frases.mp4 09,11,S01,S02,S03,S04,S05,S06,S07,S08

1. Limpa a gravação inteira com o mesmo tratamento dos outros blocos (limpar_gui.sh).
2. Transcreve com Whisper (tempo por palavra). Cada rótulo falado (uma palavra só, numa linha própria, seguida de pausa) separa as frases;
   a frase N vai para o bloco N da lista, na ordem.
3. Corta cada frase com as mesmas folgas do cortar_gui.py (−0,07 / +0,14 s) e aperta pausas internas longas (sem acelerar a voz).
4. Casa o nível com os blocos vizinhos já gravados (blocos do episódio) ou com a mediana dos blocos (hooks dos Shorts).
5. Grava video/public/media/narr_gui/b<bloco>.wav (o antigo, se houver, vira b<bloco>_antes_N.wav) e o tempo por palavra em palavras_gui.json.
Imprime a transcrição de cada frase ao lado do roteiro, para conferência. Nunca TTS.
"""
import difflib, json, os, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trocar_audio import AQUI, NARR, PAL, TEXTOS, SR, norm, transcrever, x16_de

ROTULOS = {"um", "dois", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze", "bloco"}


def lufs(arq):
    out = subprocess.run(["ffmpeg", "-nostats", "-i", arq, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    lin = [l for l in out.splitlines() if l.strip().startswith("I:")]
    return float(lin[-1].split()[1])


def eh_rotulo(w):
    n = norm(w)
    return n.isdigit() or n in ROTULOS or (n.startswith("s0") and len(n) == 3)


def main():
    bruto, blocos = sys.argv[1], sys.argv[2].upper().replace("B", "").split(",")
    for b in blocos:
        if b not in TEXTOS: sys.exit(f"bloco {b} não está na lista: {', '.join(TEXTOS)}")
    limpo = "/tmp/trocar_lote_limpo.wav"
    subprocess.run(["bash", os.path.join(AQUI, "limpar_gui.sh"), bruto, limpo], check=True)
    pal = transcrever(x16_de(limpo))
    # frases: sequências de palavras entre rótulos
    frases, cur = [], []
    for p in pal:
        if eh_rotulo(p[2]) and (not cur or p[0] - cur[-1][1] > 0.6):
            if cur: frases.append(cur)
            cur = []
        else:
            cur.append(p)
    if cur: frases.append(cur)
    if len(frases) != len(blocos):
        print(f"atenção: {len(frases)} frases na gravação e {len(blocos)} blocos pedidos; casando pela ordem até onde der")
    x, sr = sf.read(limpo); assert sr == SR
    d = json.load(open(PAL))
    viz = []
    for k in sorted(d):
        f = os.path.join(NARR, f"b{k}.wav")
        if k.isdigit() and os.path.exists(f): viz.append((k, f))
    mediana = float(np.median([lufs(f) for _, f in viz])) if viz else -16.0
    relatorio = []
    for b, trecho in zip(blocos, frases):
        alvo = [norm(w) for w in TEXTOS[b].split()]
        lido = [norm(p[2]) for p in trecho]
        casa = difflib.SequenceMatcher(None, alvo, lido, autojunk=False).ratio()
        a = max(0, trecho[0][0] - 0.07); fim = min(len(x) / SR, trecho[-1][1] + 0.14)
        pedacos, t = [], a
        for p, q in zip(trecho, trecho[1:]):
            lim = 0.75 if p[2].endswith((".", "?", "!", ",")) else 0.6
            if q[0] - p[1] > lim:
                meio = p[1] + lim / 2
                pedacos.append((t, meio)); t = q[0] - lim / 2
        pedacos.append((t, fim))
        y = np.concatenate([x[int(s * SR):int(e * SR)] for s, e in pedacos])
        fade = int(0.01 * SR); y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
        # nível: blocos do episódio casam com os vizinhos gravados; hooks casam com a mediana
        if b.isdigit():
            n = int(b); ref = [f for k, f in viz if k.isdigit() and abs(int(k) - n) == 1] or [f for _, f in viz]
            nivel = float(np.mean([lufs(f) for f in ref]))
        else:
            nivel = mediana
        tmp = f"/tmp/trocar_lote_{b}.wav"; sf.write(tmp, y, SR, subtype="PCM_24")
        y = y * 10 ** ((nivel - lufs(tmp)) / 20)
        y = np.clip(y, -0.89, 0.89)
        os.makedirs(NARR, exist_ok=True)
        dest = os.path.join(NARR, f"b{b}.wav")
        if os.path.exists(dest):
            k = 1
            while os.path.exists(os.path.join(NARR, f"b{b}_antes_{k}.wav")): k += 1
            os.rename(dest, os.path.join(NARR, f"b{b}_antes_{k}.wav"))
        sf.write(dest, y, SR, subtype="PCM_24")
        palb = transcrever(x16_de(dest))
        d[b] = {"dur": round(len(y) / SR, 2), "palavras": palb}
        relatorio.append({"bloco": b, "de": round(trecho[0][0], 2), "ate": round(trecho[-1][1], 2), "dur": round(len(y) / SR, 2),
                          "lufs": round(lufs(dest), 1), "nivel_alvo": round(nivel, 1), "casamento": round(casa, 2),
                          "lido": " ".join(p[2] for p in palb), "roteiro": TEXTOS[b]})
        print(f"{b}: {trecho[0][0]:.2f}–{trecho[-1][1]:.2f} s → {len(y) / SR:.2f} s, casamento {casa:.2f}")
        print("   lido:   ", relatorio[-1]["lido"]); print("   roteiro:", TEXTOS[b])
    json.dump(d, open(PAL, "w"), ensure_ascii=False)
    json.dump(relatorio, open("/tmp/trocar_lote_relatorio.json", "w"), ensure_ascii=False, indent=1)
    print("relatório: /tmp/trocar_lote_relatorio.json")


if __name__ == "__main__":
    main()
