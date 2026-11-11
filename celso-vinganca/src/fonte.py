"""Fonte bitmap 5x7 feita à mão (maiúsculas, minúsculas, acentos PT-BR, ♥).

Cada glifo tem 2 linhas de acento acima, 7 linhas principais e 2 de descendente.
Renderiza para arrays RGBA numpy (sem anti-aliasing).
"""
import numpy as np

ACC_ROWS, MAIN_ROWS, DESC_ROWS = 2, 7, 2
GLYPH_H = ACC_ROWS + MAIN_ROWS + DESC_ROWS  # 11

_U = {
    'A': ".###. #...# #...# ##### #...# #...# #...#",
    'B': "####. #...# #...# ####. #...# #...# ####.",
    'C': ".###. #...# #.... #.... #.... #...# .###.",
    'D': "####. #...# #...# #...# #...# #...# ####.",
    'E': "##### #.... #.... ####. #.... #.... #####",
    'F': "##### #.... #.... ####. #.... #.... #....",
    'G': ".###. #...# #.... #.### #...# #...# .####",
    'H': "#...# #...# #...# ##### #...# #...# #...#",
    'I': "### .#. .#. .#. .#. .#. ###",
    'J': "..### ...#. ...#. ...#. ...#. #..#. .##..",
    'K': "#...# #..#. #.#.. ##... #.#.. #..#. #...#",
    'L': "#.... #.... #.... #.... #.... #.... #####",
    'M': "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    'N': "#...# ##..# #.#.# #.#.# #..## #...# #...#",
    'O': ".###. #...# #...# #...# #...# #...# .###.",
    'P': "####. #...# #...# ####. #.... #.... #....",
    'Q': ".###. #...# #...# #...# #.#.# #..#. .##.#",
    'R': "####. #...# #...# ####. #.#.. #..#. #...#",
    'S': ".#### #.... #.... .###. ....# ....# ####.",
    'T': "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..",
    'U': "#...# #...# #...# #...# #...# #...# .###.",
    'V': "#...# #...# #...# #...# #...# .#.#. ..#..",
    'W': "#...# #...# #...# #.#.# #.#.# #.#.# .#.#.",
    'X': "#...# #...# .#.#. ..#.. .#.#. #...# #...#",
    'Y': "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..",
    'Z': "##### ....# ...#. ..#.. .#... #.... #####",
    '0': ".###. #...# #..## #.#.# ##..# #...# .###.",
    '1': "..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.",
    '2': ".###. #...# ....# ...#. ..#.. .#... #####",
    '3': "####. ....# ....# .###. ....# ....# ####.",
    '4': "...#. ..##. .#.#. #..#. ##### ...#. ...#.",
    '5': "##### #.... ####. ....# ....# #...# .###.",
    '6': ".###. #.... #.... ####. #...# #...# .###.",
    '7': "##### ....# ...#. ..#.. .#... .#... .#...",
    '8': ".###. #...# #...# .###. #...# #...# .###.",
    '9': ".###. #...# #...# .#### ....# ....# .###.",
    '!': "# # # # # . #",
    '?': ".###. #...# ....# ...#. ..#.. ..... ..#..",
    '.': ". . . . . # #",
    ':': ". # # . # # .",
    '-': "... ... ... ### ... ... ...",
    '–': "..... ..... ..... ##### ..... ..... .....",
    '/': "....# ....# ...#. ..#.. .#... #.... #....",
    '(': "..# .#. #.. #.. #.. .#. ..#",
    ')': "#.. .#. ..# ..# ..# .#. #..",
    '%': "##..# ##..# ...#. ..#.. .#... #..## #..##",
    '@': ".###. #...# #.### #.#.# #.### #.... .####",
    "'": "# # . . . . .",
    '"': "#.# #.# ... ... ... ... ...",
    '…': "..... ..... ..... ..... ..... ..... #.#.#",
    '+': "..... ..#.. ..#.. ##### ..#.. ..#.. .....",
    '=': "..... ..... ##### ..... ##### ..... .....",
    '>': "#... .#.. ..#. ...# ..#. .#.. #...",
    '<': "...# ..#. .#.. #... .#.. ..#. ...#",
    '♥': ".##.##. ####### ####### .#####. ..###.. ...#... .......",
    '©': ".###. #...# #.#.# #.#.# #.#.# #...# .###.",
    '_': "..... ..... ..... ..... ..... ..... #####",
}
# minúsculas: 7 linhas principais (+ 2 de descendente opcionais após '|')
_L = {
    'a': "..... ..... .###. ....# .#### #...# .####",
    'b': "#.... #.... ####. #...# #...# #...# ####.",
    'c': "..... ..... .###. #.... #.... #...# .###.",
    'd': "....# ....# .#### #...# #...# #...# .####",
    'e': "..... ..... .###. #...# ##### #.... .###.",
    'f': "..##. .#..# .#... ###.. .#... .#... .#...",
    'g': "..... ..... .#### #...# #...# #...# .####|....# .###.",
    'h': "#.... #.... #.##. ##..# #...# #...# #...#",
    'i': ".#. ... ##. .#. .#. .#. ###",
    'j': "...# .... ..## ...# ...# ...# ...#|#..# .##.",
    'k': "#... #... #..# #.#. ##.. #.#. #..#",
    'l': "##. .#. .#. .#. .#. .#. ###",
    'm': "..... ..... ##.#. #.#.# #.#.# #.#.# #.#.#",
    'n': "..... ..... #.##. ##..# #...# #...# #...#",
    'o': "..... ..... .###. #...# #...# #...# .###.",
    'p': "..... ..... ####. #...# #...# #...# ####.|#.... #....",
    'q': "..... ..... .#### #...# #...# #...# .####|....# ....#",
    'r': "..... ..... #.##. ##..# #.... #.... #....",
    's': "..... ..... .#### #.... .###. ....# ####.",
    't': ".#... .#... ###.. .#... .#... .#..# ..##.",
    'u': "..... ..... #...# #...# #...# #..## .##.#",
    'v': "..... ..... #...# #...# #...# .#.#. ..#..",
    'w': "..... ..... #...# #...# #.#.# #.#.# .#.#.",
    'x': "..... ..... #...# .#.#. ..#.. .#.#. #...#",
    'y': "..... ..... #...# #...# #...# #...# .####|....# .###.",
    'z': "..... ..... ##### ...#. ..#.. .#... #####",
    'ı': "... ... ##. .#. .#. .#. ###",
    ',': ". . . . . # #|# .",
    ';': ". # # . # # #|# .",
}
_ACC = {
    'acute': ["..#", ".#."],
    'grave': ["#..", ".#."],
    'circ': [".#.", "#.#"],
    'tilde': [".#.#", "#.#."],
}
_COMPOSE = {
    'Á': ('A', 'acute'), 'À': ('A', 'grave'), 'Â': ('A', 'circ'), 'Ã': ('A', 'tilde'),
    'É': ('E', 'acute'), 'Ê': ('E', 'circ'), 'Í': ('I', 'acute'), 'Ó': ('O', 'acute'),
    'Ô': ('O', 'circ'), 'Õ': ('O', 'tilde'), 'Ú': ('U', 'acute'),
    'á': ('a', 'acute'), 'à': ('a', 'grave'), 'â': ('a', 'circ'), 'ã': ('a', 'tilde'),
    'é': ('e', 'acute'), 'ê': ('e', 'circ'), 'í': ('ı', 'acute'), 'ó': ('o', 'acute'),
    'ô': ('o', 'circ'), 'õ': ('o', 'tilde'), 'ú': ('u', 'acute'),
}


def _parse(spec):
    main, _, desc = spec.partition('|')
    rows = main.split()
    drows = desc.split() if desc else []
    w = max(len(r) for r in rows + drows)
    g = np.zeros((GLYPH_H, w), bool)
    for i, r in enumerate(rows):
        for j, ch in enumerate(r):
            g[ACC_ROWS + i, j] = ch == '#'
    for i, r in enumerate(drows):
        for j, ch in enumerate(r):
            g[ACC_ROWS + MAIN_ROWS + i, j] = ch == '#'
    return g


GLYPHS = {}
for k, v in {**_U, **_L}.items():
    GLYPHS[k] = _parse(v)
GLYPHS[' '] = np.zeros((GLYPH_H, 3), bool)


def _compose(base, acc, upper):
    g = GLYPHS[base].copy()
    a = _ACC[acc]
    aw = len(a[0])
    x0 = max(0, (g.shape[1] - aw + 1) // 2)
    if x0 + aw > g.shape[1]:
        g = np.pad(g, ((0, 0), (0, x0 + aw - g.shape[1])))
    y0 = 0 if upper else ACC_ROWS  # minúsculas: acento nas 2 primeiras linhas da área principal
    for i, r in enumerate(a):
        for j, ch in enumerate(r):
            if ch == '#':
                g[y0 + i, x0 + j] = True
    return g


for ch, (b, a) in _COMPOSE.items():
    GLYPHS[ch] = _compose(b, a, ch.isupper())
# Ç / ç com cedilha
for ch, b in (('Ç', 'C'), ('ç', 'c')):
    g = GLYPHS[b].copy()
    g[ACC_ROWS + MAIN_ROWS, 2] = True
    g[ACC_ROWS + MAIN_ROWS + 1, 1:3] = True
    GLYPHS[ch] = g


def glyph(ch):
    if ch in GLYPHS:
        return GLYPHS[ch]
    if ch.upper() in GLYPHS:
        return GLYPHS[ch.upper()]
    return GLYPHS['?']


def text_width(text, spacing=1):
    if not text:
        return 0
    return sum(glyph(c).shape[1] for c in text) + spacing * (len(text) - 1)


def text_mask(text, spacing=1):
    w = max(1, text_width(text, spacing))
    m = np.zeros((GLYPH_H, w), bool)
    x = 0
    for c in text:
        g = glyph(c)
        m[:, x:x + g.shape[1]] |= g
        x += g.shape[1] + spacing
    return m


def wrap(text, max_px, spacing=1):
    out = []
    for para in text.split('\n'):
        words, line = para.split(' '), ''
        for w in words:
            t = (line + ' ' + w) if line else w
            if text_width(t, spacing) <= max_px or not line:
                line = t
            else:
                out.append(line)
                line = w
        out.append(line)
    return out


def _dilate(m, r=1):
    """Dilatação quadrada (contorno) sem scipy."""
    h, w = m.shape
    p = np.pad(m, r)
    out = np.zeros_like(m)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= p[r + dy:r + dy + h, r + dx:r + dx + w]
    return out


def render(text, color=(255, 255, 255), scale=1, outline=None, outline_px=1,
           shadow=None, spacing=1):
    """Retorna RGBA uint8. outline/shadow em pixels da fonte (antes do scale)."""
    m = text_mask(text, spacing)
    pad = outline_px + (1 if shadow else 0)
    m = np.pad(m, pad)
    h, w = m.shape
    img = np.zeros((h, w, 4), np.uint8)
    if shadow is not None:
        sm = np.zeros_like(m)
        sm[1:, 1:] = m[:-1, :-1]
        sm = _dilate(sm, outline_px) if outline is not None else sm
        img[sm] = (*shadow, 255)
    if outline is not None:
        om = _dilate(m, outline_px)
        img[om] = (*outline, 255)
    img[m] = (*color, 255)
    if scale != 1:
        img = img.repeat(scale, 0).repeat(scale, 1)
    return img


def render_lines(lines, color=(255, 255, 255), scale=1, outline=None, outline_px=1,
                 line_gap=2, align='center', shadow=None):
    imgs = [render(l, color, 1, outline, outline_px, shadow) for l in lines]
    w = max(i.shape[1] for i in imgs)
    lh = GLYPH_H + line_gap
    h = lh * (len(imgs) - 1) + imgs[0].shape[0]
    out = np.zeros((h, w, 4), np.uint8)
    for k, im in enumerate(imgs):
        x = (w - im.shape[1]) // 2 if align == 'center' else 0
        y = k * lh
        a = im[..., 3:] > 0
        reg = out[y:y + im.shape[0], x:x + im.shape[1]]
        np.copyto(reg, im, where=a)
    if scale != 1:
        out = out.repeat(scale, 0).repeat(scale, 1)
    return out
