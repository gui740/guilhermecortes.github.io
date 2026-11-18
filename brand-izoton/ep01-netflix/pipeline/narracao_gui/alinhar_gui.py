import json, re, unicodedata, difflib
rot = open('bruto/roteiro-narracao-ep01-v3.md').read()
blocos = {}
for m in re.finditer(r'^\*\*(S?\d\d)\*\*(.*?)\n(?=\n|>|##|\*\*S?\d\d\*\*|---)', rot, re.S | re.M):
    bid, corpo = m.group(1), m.group(2)
    corpo = re.sub(r'^\s*\*\([^)]*\)\*', '', corpo.strip())
    linhas = [l for l in corpo.split('\n') if l.strip() and not l.startswith('>')]
    t = ' '.join(linhas)
    t = t.replace('[PAUSA]', ' ').replace('**', '')
    blocos[bid] = re.sub(r'\s+', ' ', t).strip()
json.dump(blocos, open('blocos_roteiro.json', 'w'), ensure_ascii=False, indent=1)
NUM = set('zero um uma dois duas tres quatro cinco seis sete oito nove dez onze doze treze quatorze catorze quinze dezesseis dezessete dezoito dezenove vinte trinta quarenta cinquenta sessenta setenta oitenta noventa cem cento duzentos duzentas trezentos quatrocentos quinhentos mil e virgula'.split())
def norm(w):
    w = unicodedata.normalize('NFKD', w.lower()); w = ''.join(c for c in w if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', w)
def toks(texto): return [t for t in (norm(w) for w in texto.split()) if t and not t.isdigit() and t not in NUM]
arquivos = {'05': ['01','02','03','04','05'], '06': ['06','07','08','09','10','11'], '07': [f'{i}' for i in range(11,20)], '08': ['20','21','22','23'],
            '09': [f'{i}' for i in range(24,29)], '10': [f'{i}' for i in range(29,34)], '11': [f'{i}' for i in range(34,38)], '12': [f'{i}' for i in range(38,44)],
            '13': [f'{i}' for i in range(44,50)], '14': [f'{i}' for i in range(50,56)]}
res = {}
for arq, ids in arquivos.items():
    pal = json.load(open(f'trans/gravacao-{arq}.medium.json'))
    # tokens do transcrito, com índice da palavra de origem
    tt = [(norm(w), i) for i, (a, b, w) in enumerate(pal)]
    tt = [(t, i) for t, i in tt if t and not t.isdigit() and t not in NUM]
    seq = [t for t, _ in tt]
    limite = len(seq)
    for bid in reversed(ids):
        bt = toks(blocos[bid]); L = len(bt)
        melhor = None
        for i in range(limite - 1, -1, -1):
            if i + 2 > limite: continue
            janela = seq[i:min(limite, i + L)]
            r = difflib.SequenceMatcher(None, bt, janela, autojunk=False).ratio()
            if r > 0.72 and (melhor is None or r > melhor[1] + 0.05):
                melhor = (i, r)
                if r > 0.9: break
            if melhor and i < melhor[0] - L: break
        if not melhor:
            res[bid] = {'arquivo': arq, 'faltando': True}; continue
        i, r = melhor
        sm = difflib.SequenceMatcher(None, bt, seq[i:min(limite, i + int(L * 1.3) + 2)], autojunk=False)
        blocosm = [b for b in sm.get_matching_blocks() if b.size]
        j0 = i + blocosm[0].b; j1 = i + blocosm[-1].b + blocosm[-1].size - 1
        w0, w1 = tt[j0][1], tt[j1][1]
        # estende o fim para números/palavras finais filtradas (ex.: "2017.")
        while w1 + 1 < len(pal) and pal[w1 + 1][0] - pal[w1][1] < 0.35 and (norm(pal[w1 + 1][2]).isdigit() or norm(pal[w1+1][2]) in NUM) and (j1 + 1 >= len(tt) or tt[j1+1][1] > w1 + 1):
            w1 += 1
        # estende o início para trás por números (ex.: "Em 2017") — palavras antes do 1º token casado e coladas
        cob = sum(b.size for b in blocosm) / L
        res[bid] = {'arquivo': arq, 'w0': w0, 'w1': w1, 'ini': pal[w0][0], 'fim': pal[w1][1], 'ratio': round(r, 2), 'cobertura': round(cob, 2),
                    'lido': ' '.join(p[2] for p in pal[w0:w1 + 1])}
        limite = j0
json.dump(res, open('alinhamento.json', 'w'), ensure_ascii=False, indent=1)
for bid in sorted(res, key=lambda k: (k.startswith('S'), k)):
    r = res[bid]
    print(bid, r['arquivo'], 'FALTA' if r.get('faltando') else f"{r['ini']:.2f}-{r['fim']:.2f} r={r['ratio']} cob={r['cobertura']} | {r['lido'][:90]}")
print(len(blocos), 'blocos no roteiro')
