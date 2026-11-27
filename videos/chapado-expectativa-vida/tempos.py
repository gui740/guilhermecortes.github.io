"""Ajusta a duração das cenas à narração e gera as legendas (3-4 palavras) sincronizadas com a voz.
Saída: narracao_tempos.js (lido pelo index.html, sobrescreve CENAS) e out/tempos.json (usado pelo audio.py)."""
import json, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
NARR = os.path.join(HERE, "out", "narr")
T = 0.9   # TRANSICAO (igual ao config.js)
cfg = subprocess.run(["node", "-e", "const c=require('./config.js');console.log(JSON.stringify(c.CENAS))"],
                     cwd=HERE, capture_output=True, text=True, check=True).stdout
cenas = json.loads(cfg)
lines = json.load(open(os.path.join(HERE, "narracao.json")))
words = json.load(open(os.path.join(NARR, "words.json")))

def dur_wav(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)

NUMEROS = [("mil novecentos e quarenta", "1940"), ("quarenta e cinco", "45"), ("dois mil e dez", "2010"),
    ("setenta e quatro anos e meio", "74,5 ANOS"), ("setenta e seis vírgula seis", "76,6"), ("dois mil e vinte e um", "2021"),
    ("setenta e dois vírgula oito", "72,8"), ("dois mil e vinte e quatro", "2024"), ("setenta e três vírgula três", "73,3"),
    ("cinquenta e oito", "58"), ("setenta e quatro por cento", "74%"), ("três", "3")]
ovr, t0, out = {}, 0.0, []
for i, c in enumerate(cenas):
    k = f"n{i:02d}"
    sp = dur_wav(os.path.join(NARR, k + ".wav"))
    pre = T if i > 0 else 0.0
    cs = 0.4 if i == 0 else pre + 0.25                       # quando a fala começa (relógio da cena)
    last = i == len(cenas) - 1
    need = (cs + sp + 0.35 + T) if i == 0 else (cs + sp + 0.35 if not last else cs + sp + 1.4 - pre)
    dur = round(max(c["dur"], need), 2)
    # números falados viram algarismos na legenda (o tempo é o da primeira palavra)
    ws = [dict(w) for w in words[k]]
    orig = lines[i]["text"].split()
    if len(orig) == len(ws):                       # recupera a pontuação do texto original
        for w, o in zip(ws, orig):
            w["w"] = o
    toks, j = [], 0
    norm = lambda x: re.sub(r"[^\wÀ-ú]", "", x).lower()
    while j < len(ws):
        hit = None
        for frase, rep in NUMEROS:
            fw = frase.split()
            if [norm(x["w"]) for x in ws[j:j + len(fw)]] == fw:
                hit = (len(fw), rep); break
        if hit:
            n, rep = hit
            tail = re.sub(r"^[\wÀ-ú]+", "", ws[j + n - 1]["w"])      # mantém a pontuação final
            toks.append({"w": rep + tail, "t": ws[j]["t"]}); j += n
        else:
            toks.append(ws[j]); j += 1
    # legendas: blocos de até 4 palavras / 22 letras
    legs, cur = [], []
    for w in toks:
        if cur and (len(cur) >= 4 or sum(len(x["w"]) + 1 for x in cur) + len(w["w"]) > 22 or re.search(r"[.?!:…]$", cur[-1]["w"])):
            legs.append(cur); cur = []
        cur.append(w)
    if cur:
        legs.append(cur)
    limpa = lambda x: re.sub(r"[.,:;]+$", "", x)      # tira vírgula/ponto final, mantém ? ! ...
    leg = [[round(cs + ch[0]["t"], 2), " ".join(limpa(x["w"]) if not x["w"].endswith("...") else x["w"] for x in ch).upper()] for ch in legs]
    if c["id"] == "cena2":
        leg = []          # a vinheta já mostra o nome do canal
    pal = [[re.sub(r"[^\wÀ-ú]", "", w["w"]).lower(), round(cs + w["t"], 2)] for w in words[k]]
    ovr[c["id"]] = {"dur": dur, "legendas": leg, "palavras": pal}
    real = t0 - pre + cs
    out.append({"id": c["id"], "wav": os.path.join(NARR, k + ".wav"), "start": round(real, 3), "t0": round(t0, 3), "pre": pre, "dur": dur})
    t0 += dur
open(os.path.join(HERE, "narracao_tempos.js"), "w").write(
    "// GERADO por tempos.py a partir da narração — não edite à mão\nconst TEMPOS_NARRACAO = " + json.dumps(ovr, ensure_ascii=False, indent=1) +
    ";\nCENAS.forEach((c) => TEMPOS_NARRACAO[c.id] && Object.assign(c, TEMPOS_NARRACAO[c.id]));\n")
json.dump({"cenas": out, "total": round(t0, 3)}, open(os.path.join(HERE, "out", "tempos.json"), "w"), indent=1)
for o in out:
    print(f'{o["id"]}  início {o["t0"]:6.2f}s  dur {o["dur"]:5.2f}s  fala em {o["start"]:6.2f}s')
print("total", round(t0, 2), "s")
