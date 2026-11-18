"""Troca um bloco que faltava (09, 11, S01–S08) pela gravação do Guilherme.

Uso: python3 trocar_audio.py <gravação bruta> <bloco>      ex.: trocar_audio.py ~/gravacao-14.wav 09

1. Limpa a gravação inteira com o mesmo tratamento dos outros blocos (limpar_gui.sh: ruído, EQ, de-esser, compressão,
   gate, sala pequena, -16 LUFS).
2. Transcreve com Whisper (tempo por palavra) e acha a ÚLTIMA leitura do texto do bloco (se ele repetiu, vale a última).
3. Corta essa leitura com as mesmas folgas do cortar_gui.py e aperta pausas internas longas (sem acelerar a voz).
4. Grava video/public/media/narr_gui/b<bloco>.wav (fora do Git) e o tempo por palavra em video/src/v3/palavras_gui.json.
   Se já existir um b<bloco>.wav, o antigo é guardado como b<bloco>_antes_N.wav (nada é apagado).

Depois:
- blocos 09 e 11: rodar pipeline/montar_timeline_v3.py (o bloco sai de [REGRAVAR] e as cenas se reposicionam pelas palavras dele);
- S01–S08: nada a fazer no código; hooks.tsx põe o hook falado antes do Short na próxima renderização.
Nunca TTS: só gravação dele.
"""
import difflib, json, os, re, subprocess, sys, unicodedata
import numpy as np, soundfile as sf

AQUI = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(os.path.join(AQUI, "..", ".."))
NARR = os.environ.get("TROCAR_NARR") or os.path.join(EP, "video", "public", "media", "narr_gui")  # TROCAR_* só para teste
PAL = os.environ.get("TROCAR_PAL") or os.path.join(EP, "video", "src", "v3", "palavras_gui.json")
if os.environ.get("TROCAR_TEXTO"): TEXTOS_EXTRA = {"TESTE": os.environ["TROCAR_TEXTO"]}
else: TEXTOS_EXTRA = {}
TEXTOS = {  # roteiro (COBERTURA_NARRACAO.md)
    "09": "O retorno não estava em cada hora assistida. Estava em outro lugar.",
    "11": "Ter a série não bastava. Ela precisava que você não parasse de assistir.",
    "S01": "O CEO da Netflix disse que ela compete com o seu sono.",
    "S02": "Esse botão é apertado cento e trinta e seis milhões de vezes por dia.",
    "S03": "Você dá cinco estrelas para um filme e assiste outro. A Netflix percebeu.",
    "S04": "Todo chefe da Netflix precisa responder uma pergunta sobre você.",
    "S05": "Em muitos países, a Netflix nem escreve o próprio nome.",
    "S06": "Em 2015, um candidato fez propaganda no intervalo de um debate na CNN. Ele não existe.",
    "S07": "A Netflix proibiu dividir a senha. Muita gente disse que ia cancelar.",
    "S08": "A Netflix abriu uma casa onde você entra nas séries.",
}
TEXTOS.update(TEXTOS_EXTRA)
PROMPT = "Netflix, Reed Hastings, HBO, CNN, Brand by Izoton."
SR = 48000


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", w)


def transcrever(x16):
    from faster_whisper import WhisperModel
    m = WhisperModel("medium", compute_type="int8", cpu_threads=4)
    segs, _ = m.transcribe(x16, language="pt", word_timestamps=True, initial_prompt=PROMPT, vad_filter=False, condition_on_previous_text=False)
    return [[round(p.start, 2), round(p.end, 2), p.word.strip()] for s in segs for p in s.words]


def x16_de(arq):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32)


def main():
    bruto, bloco = sys.argv[1], sys.argv[2].upper().replace("B", "")
    if bloco not in TEXTOS: sys.exit(f"bloco {bloco} não está na lista: {', '.join(TEXTOS)}")
    alvo = [norm(w) for w in TEXTOS[bloco].split()]
    limpo = os.path.join("/tmp", f"trocar_{bloco}_limpo.wav")
    subprocess.run(["bash", os.path.join(AQUI, "limpar_gui.sh"), bruto, limpo], check=True)
    pal = transcrever(x16_de(limpo))
    ws = [norm(p[2]) for p in pal]
    # última leitura: janela que mais casa com o texto, procurando de trás para frente
    melhor, ini_w, fim_w = 0.0, 0, len(pal) - 1
    n = len(alvo)
    for i in range(len(ws) - 1, -1, -1):
        jan = ws[i:i + n + 3]
        r = difflib.SequenceMatcher(None, alvo, jan, autojunk=False).ratio()
        if r > melhor + 0.05 or (r >= 0.8 and r >= melhor - 0.02 and melhor < 0.8):
            melhor, ini_w = r, i
            bl = difflib.SequenceMatcher(None, alvo, jan, autojunk=False).get_matching_blocks()
            fim_w = i + max(b.b + b.size for b in bl if b.size) - 1
        if melhor >= 0.9: break
    if melhor < 0.6: sys.exit(f"não achei o texto do bloco {bloco} na gravação (melhor casamento {melhor:.2f}). Confira o arquivo.")
    x, sr = sf.read(limpo); assert sr == SR
    a = max(0, pal[ini_w][0] - 0.07); b = min(len(x) / SR, pal[fim_w][1] + 0.14)
    trecho = pal[ini_w:fim_w + 1]
    # pausas internas maiores que 0,6 s (0,75 s depois de ponto) viram esse limite
    pedacos, t = [], a
    for p, q in zip(trecho, trecho[1:]):
        lim = 0.75 if p[2].endswith((".", "?", "!")) else 0.6
        if q[0] - p[1] > lim:
            meio = p[1] + lim / 2
            pedacos.append((t, meio)); t = q[0] - lim / 2
    pedacos.append((t, b))
    y = np.concatenate([x[int(s * SR):int(e * SR)] for s, e in pedacos])
    fade = int(0.01 * SR); y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
    os.makedirs(NARR, exist_ok=True)
    dest = os.path.join(NARR, f"b{bloco}.wav")
    if os.path.exists(dest):
        k = 1
        while os.path.exists(os.path.join(NARR, f"b{bloco}_antes_{k}.wav")): k += 1
        os.rename(dest, os.path.join(NARR, f"b{bloco}_antes_{k}.wav"))
    sf.write(dest, y, SR, subtype="PCM_24")
    # tempo por palavra no bloco cortado
    palb = transcrever(x16_de(dest))
    d = json.load(open(PAL))
    d[bloco] = {"dur": round(len(y) / SR, 2), "palavras": palb}
    json.dump(d, open(PAL, "w"), ensure_ascii=False)
    print(f"ok: {dest} ({len(y) / SR:.2f} s, casamento {melhor:.2f})")
    print("transcrição:", " ".join(p[2] for p in palb))
    print("roteiro:    ", TEXTOS[bloco])
    if bloco in ("09", "11"):
        print("próximo passo: rodar pipeline/montar_timeline_v3.py e renderizar o episódio de novo.")
    else:
        print("próximo passo: renderizar o Short de novo (hooks.tsx já põe o hook antes).")


if __name__ == "__main__":
    main()
