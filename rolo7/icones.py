"""Ícones pixel-art 16x16 ('.' vazio, '#' principal, 'o' secundária, 'x' contorno)."""
from PIL import Image

MAPAS = {
    "microfone": """
....xxxxxxxx....
...x########x...
..x#o#o#o#o##x..
..x##o#o#o#o#x..
..x#o#o#o#o##x..
..x##o#o#o#o#x..
..x#o#o#o#o##x..
...x########x...
....xxxxxxxx....
.......xx.......
.......oo.......
.......oo.......
.......oo.......
.....xxxxxx.....
....xoooooox....
....xxxxxxxx....
""",
    "rolo": """
.....xxxxxx.....
...xx######xx...
..x####oo####x..
.x##oo####oo##x.
.x##oo####oo##x.
x######xx######x
x#####xoox#####x
x###oo#xx#oo###x
x###oo####oo###x
x#####xoox#####x
x######xx######x
.x##oo####oo##x.
.x##oo####oo##x.
..x####oo####x..
...xx######xx...
.....xxxxxx.....
""",
    "lampada": """
......xxxx......
....xx####xx....
...x###oo###x...
..x###o##o###x..
..x##o####o##x..
..x##o####o##x..
..x###o##o###x..
...x###oo###x...
....x######x....
.....x####x.....
.....xooooxx....
.....x####x.....
.....xooooxx....
.....x####x.....
......xxxx......
.......xx.......
""",
    "casa": """
.......xx.......
......x##x..xx..
.....x####x.xx..
....x######xxx..
...x########xx..
..x##########x..
.x############x.
xxxxxxxxxxxxxxxx
.x############x.
.x#oo##xxx#oo#x.
.x#oo##xox#oo#x.
.x#####xox####x.
.x#####xox####x.
.x#####xox####x.
.xxxxxxxxxxxxxx.
................
""",
    "taca": """
..xxxxxxxxxxxx..
..x##########x..
..xoooooooooox..
..xoooooooooox..
...xoooooooox...
...xoooooooox...
....xoooooox....
.....xxooxx.....
.......xx.......
.......##.......
.......##.......
.......##.......
.......##.......
.....x####x.....
...xx######xx...
...xxxxxxxxxx...
""",
    "olho": """
................
................
.....xxxxxx.....
...xx######xx...
..x###xxxx###x..
.x###xooo#x###x.
x###xooxxo#x###x
x###xoxxxx#x###x
x###xoxxxx#x###x
x###xooxxo#x###x
.x###xoooox###x.
..x###xxxx###x..
...xx######xx...
.....xxxxxx.....
................
................
""",
    "gota": """
.......xx.......
.......xx.......
......x##x......
......x##x......
.....x####x.....
.....x####x.....
....x######x....
...x########x...
...x#o######x...
..x#o########x..
..x#o########x..
..x##o#######x..
..x###o######x..
...x########x...
....xx####xx....
......xxxx......
""",
    "tv": """
...x.......x....
....x.....x.....
.....x...x......
......x.x.......
xxxxxxxxxxxxxxxx
x##############x
x#xxxxxxxxxx###x
x#xoooooooox#o#x
x#xooo#ooo#x###x
x#xoooo#oooxo#ox
x#xo#oooo#ox###x
x#xoooooooox#o#x
x#xxxxxxxxxx###x
x##############x
xxxxxxxxxxxxxxxx
.xx..........xx.
""",
    "porta": """
..xxxxxxxxxxxx..
..x##########x..
..x#xxxxxxxx#x..
..x#xoooooox#x..
..x#xoooooox#x..
..x#xoooooox#x..
..x#xxxxxxxx#x..
..x##########x..
..x#######oo#x..
..x#######oo#x..
..x#xxxxxxxx#x..
..x#xoooooox#x..
..x#xoooooox#x..
..x#xxxxxxxx#x..
..x##########x..
.xxxxxxxxxxxxxx.
""",
    "aviso": """
.......xx.......
......x##x......
......x##x......
.....x####x.....
.....x#xx#x.....
....x##xx##x....
....x##xx##x....
...x###xx###x...
...x###xx###x...
..x####xx####x..
..x##########x..
.x#####xx#####x.
.x#####xx#####x.
x##############x
xxxxxxxxxxxxxxxx
................
""",
}

PALETAS = {
    "microfone": {"#": (190, 190, 200), "o": (90, 90, 100), "x": (20, 20, 24)},
    "rolo": {"#": (150, 95, 55), "o": (60, 35, 20), "x": (25, 15, 10)},
    "rolo_vermelho": {"#": (200, 30, 30), "o": (90, 0, 0), "x": (30, 0, 0)},
    "lampada": {"#": (225, 225, 210), "o": (150, 150, 140), "x": (30, 30, 30)},
    "lampada_amarela": {"#": (255, 215, 60), "o": (200, 130, 20), "x": (40, 25, 0)},
    "lampada_vermelha": {"#": (240, 40, 30), "o": (140, 10, 10), "x": (40, 0, 0)},
    "casa": {"#": (200, 185, 150), "o": (255, 210, 70), "x": (30, 25, 20)},
    "taca": {"#": (210, 230, 240), "o": (150, 20, 40), "x": (30, 30, 40)},
    "olho": {"#": (235, 235, 225), "o": (160, 30, 30), "x": (15, 10, 10)},
    "gota": {"#": (90, 160, 230), "o": (210, 235, 255), "x": (10, 30, 60)},
    "tv": {"#": (140, 100, 60), "o": (170, 200, 190), "x": (20, 15, 10)},
    "porta": {"#": (120, 75, 40), "o": (70, 40, 20), "x": (20, 10, 5)},
    "aviso": {"#": (255, 200, 0), "o": (0, 0, 0), "x": (20, 15, 0)},
}
# ícones que reaproveitam o desenho de outro
FORMA = {"rolo_vermelho": "rolo", "lampada_amarela": "lampada",
         "lampada_vermelha": "lampada"}

_cache = {}


def _matriz(nome):
    linhas = [l for l in MAPAS[FORMA.get(nome, nome)].strip("\n").split("\n")]
    assert len(linhas) == 16 and all(len(l) == 16 for l in linhas), nome
    return linhas


def icone(nome, escala=3, corrompido=False, invertido=False):
    """Retorna Image RGBA (16*escala)."""
    chave = (nome, escala, corrompido, invertido)
    if chave in _cache:
        return _cache[chave]
    pal = dict(PALETAS[nome])
    if corrompido:  # paleta trocada
        pal = {"#": pal["o"], "o": pal["x"], "x": pal["#"]}
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for y, linha in enumerate(_matriz(nome)):
        for x, c in enumerate(linha):
            if c in pal:
                r, g, b = pal[c]
                if invertido:
                    r, g, b = 255 - r, 255 - g, 255 - b
                px[x, y] = (r, g, b, 255)
    img = img.resize((16 * escala, 16 * escala), Image.NEAREST)
    _cache[chave] = img
    return img


def colar_animado(base, nome, cx, cy, t_local, fps=30, escala=3, corrompido=False, rng=None):
    """Entrada: escala 0 -> 1.2 -> 1.0 em 6 frames, pisca 2x e fica.

    t_local = segundos desde o pop. Retorna True se desenhou.
    """
    if t_local < 0:
        return False
    f = int(t_local * fps)
    # piscadas: frames 8-9 e 12-13 apagados
    if f in (8, 9, 12, 13):
        return False
    if f < 6:
        s = [0.15, 0.55, 1.0, 1.2, 1.1, 1.0][f]
    else:
        s = 1.0
    invert = corrompido and f in (1, 2, 10)
    img = icone(nome, escala, corrompido=corrompido, invertido=invert)
    if s != 1.0:
        n = max(2, int(img.width * s))
        img = img.resize((n, n), Image.NEAREST)
    dx = dy = 0
    if corrompido and rng is not None:
        dx, dy = int(rng.integers(-2, 3)), int(rng.integers(-2, 3))
    base.paste(img, (int(cx - img.width / 2 + dx), int(cy - img.height / 2 + dy)), img)
    return True
