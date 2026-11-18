import json, sys, numpy as np, soundfile as sf
OUT = sys.argv[1]
al = json.load(open('alinhamento_final.json'))
rot = json.load(open('blocos_roteiro.json'))
SR = 48000; FR = int(0.01 * SR)
cache = {}
def aud(a):
    if a not in cache: cache[a] = sf.read(f'limpo/gravacao-{a}.wav')[0]
    return cache[a]
def env(x): return 20*np.log10(np.array([np.sqrt(np.mean(x[i:i+FR]**2)) for i in range(0, len(x)-FR, FR)]) + 1e-9)
rel = {}
for bid, r in sorted(al.items()):
    if r.get('faltando'): continue
    x = aud(r['arquivo']); E = env(x)
    vizinhos = [o for k, o in al.items() if k != bid and not o.get('faltando') and o['arquivo'] == r['arquivo']]
    lim0 = max([o['fim'] for o in vizinhos if o['fim'] <= r['ini']] + [0]) + 0.05
    lim1 = min([o['ini'] for o in vizinhos if o['ini'] >= r['fim']] + [len(x)/SR]) - 0.05
    fala = np.percentile(E[int(r['ini']*100):int(r['fim']*100)], 75); th = fala - 28
    a = max(lim0, r['ini'] - 0.35); i = int(a*100)
    while i < int((r['ini'] + 0.15)*100) and E[i] < th: i += 1
    ini = max(lim0, i/100 - 0.07)
    b = min(lim1, r['fim'] + 0.5); j = int(b*100)
    while j > int((r['fim'] - 0.1)*100) and E[j] < th: j -= 1
    fim = min(lim1, j/100 + 0.14)
    # pausas internas: limite por bloco
    cap = 0.42 if bid in ('01', '02') else (0.75 if '[PAUSA]' in open('bruto/roteiro-narracao-ep01-v3.md').read().split(f'**{bid}**')[1].split('\n\n')[0] else 0.6)
    pal = json.load(open(f'trans/gravacao-{r["arquivo"]}.medium.json'))[r['w0']:r['w1']+1]
    cortes = []
    for p, q in zip(pal, pal[1:]):
        g = q[0] - p[1]
        if g > cap + 0.05:
            # tira o miolo do silêncio, deixando `cap`, procurando o ponto mais quieto
            m0 = p[1] + cap/2; m1 = q[0] - cap/2
            cortes.append((m0, m1))
    pedaços = []; t = ini
    for m0, m1 in cortes:
        pedaços.append((t, m0)); t = m1
    pedaços.append((t, fim))
    xf = int(0.02*SR); y = None
    for s0, s1 in pedaços:
        seg = x[int(s0*SR):int(s1*SR)].copy()
        if y is None: y = seg
        else:
            rmp = np.linspace(1, 0, xf); y = np.concatenate([y[:-xf], y[-xf:]*rmp + seg[:xf]*(1-rmp), seg[xf:]])
    fi, fo = int(0.01*SR), int(0.04*SR)
    y[:fi] *= np.linspace(0, 1, fi); y[-fo:] *= np.linspace(1, 0, fo)
    sf.write(f'{OUT}/b{bid}.wav', y.astype(np.float32), SR)
    rel[bid] = {'arquivo': f'gravacao-{r["arquivo"]}', 'ini': round(ini, 2), 'fim': round(fim, 2), 'dur_bruta': round(fim-ini, 2),
                'dur_final': round(len(y)/SR, 2), 'pausas_apertadas': len(cortes), 'tirado_s': round(sum(m1-m0 for m0, m1 in cortes), 2)}
json.dump(rel, open('cortes_blocos.json', 'w'), ensure_ascii=False, indent=1)
tot = sum(v['dur_final'] for v in rel.values()); tb = sum(v['dur_bruta'] for v in rel.values())
print(len(rel), 'blocos', f'bruto {tb:.1f} s -> final {tot:.1f} s (tirado {tb-tot:.1f} s de pausas)')
for k in ['01', '02', '04', '12']: print(k, rel[k])
