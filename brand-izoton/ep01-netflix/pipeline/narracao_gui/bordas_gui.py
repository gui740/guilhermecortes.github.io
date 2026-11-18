import json, re, difflib, sys
sys.path.insert(0, '..')
exec(open('../alinhar_gui.py').read().split("arquivos = {")[0])  # norm, toks, blocos, NUM
res = json.load(open('alinhamento.json'))
res['54'] = {'arquivo': '14', 'manual': True}
cache = {}
def pal_de(a):
    if a not in cache: cache[a] = json.load(open(f'trans/gravacao-{a}.medium.json'))
    return cache[a]
p14 = pal_de('14')
i54 = [i for i, p in enumerate(p14) if p[0] >= 71.5 and p[1] <= 75.5]
res['54'].update({'w0': i54[0], 'w1': i54[-1]})
EXCL = {'bloco', 'capitulo'}
for bid, r in res.items():
    if r.get('faltando'): continue
    pal = pal_de(r['arquivo'])
    raw = [norm(w) for w in blocos[bid].split()]
    ini_set, fim_set = set(raw[:8]), set(raw[-8:])
    w0, w1 = r['w0'], r['w1']
    for _ in range(7):
        if w0 == 0: break
        prev = pal[w0 - 1]; t = norm(prev[2])
        if pal[w0][0] - prev[1] > 0.5 or t in EXCL or not (t in ini_set or t.isdigit()): break
        w0 -= 1
    for _ in range(5):
        if w1 + 1 >= len(pal): break
        nx = pal[w1 + 1]; t = norm(nx[2])
        if nx[0] - pal[w1][1] > 0.5 or t in EXCL or not (t in fim_set or t.isdigit()): break
        w1 += 1
    r.update({'w0': w0, 'w1': w1, 'ini': pal[w0][0], 'fim': pal[w1][1], 'lido': ' '.join(p[2] for p in pal[w0:w1 + 1])})
# sem sobreposição dentro do mesmo arquivo
for a in set(r['arquivo'] for r in res.values()):
    bs = sorted([(r['w0'], k) for k, r in res.items() if r['arquivo'] == a and not r.get('faltando')])
    for (w0a, ka), (w0b, kb) in zip(bs, bs[1:]):
        if res[ka]['w1'] >= w0b:
            pal = pal_de(a); res[ka]['w1'] = w0b - 1; res[ka]['fim'] = pal[w0b - 1][1]
            res[ka]['lido'] = ' '.join(p[2] for p in pal[res[ka]['w0']:w0b])
def dif(bid, lido):
    A = [norm(w) for w in blocos[bid].split()]; B = [norm(w) for w in lido.split()]
    A = [x for x in A if x]; B = [x for x in B if x]
    out = []
    for op, a0, a1, b0, b1 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if op == 'equal': continue
        sa, sb = A[a0:a1], B[b0:b1]
        if all(x.isdigit() or x in NUM for x in sa + sb): continue  # número por extenso × algarismo
        out.append(f"{op}: '{' '.join(sa)}' → '{' '.join(sb)}'")
    return out
for bid in sorted(res, key=lambda k: (k.startswith('S'), k)):
    r = res[bid]
    if r.get('faltando'): print(bid, 'FALTA'); continue
    r['dif'] = dif(bid, r['lido'])
    print(bid, r['arquivo'], f"{r['ini']:.2f}-{r['fim']:.2f}", '|', r['lido'][:60], '||', '; '.join(r['dif']))
json.dump(res, open('alinhamento_final.json', 'w'), ensure_ascii=False, indent=1)
