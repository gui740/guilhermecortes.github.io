"""Narration lines, scene layout and timing (shared by video and audio)."""
import json, os, wave, contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO = os.path.join(ROOT, "vo")
BUILD = os.path.join(ROOT, "build")
FPS = 30
GAPK = 0.6

# id, text spoken (TTS, with tags), caption text, style hint
LINES = [
    ("L00", "Se ouvir esse assobio no mato... <whisper> não responde.", "Se ouvir esse assobio no mato... não responde.", "whisper"),
    ("L01", "Meu avô era poaieiro, lá pras bandas de Cáceres.", "Meu avô era poaieiro, lá pras bandas de Cáceres.", "tell"),
    ("L02", "Ele contava que tem um bicho nessa mata... de uma perna só.", "Ele contava que tem um bicho nessa mata... de uma perna só.", "tell"),
    ("L03", "Peludo. Alto que nem pé de piúva. Um olho só, no meio da testa.", "Peludo. Alto que nem pé de piúva. Um olho só, no meio da testa.", "tell"),
    ("L04", "E o pé... é redondo. Que nem fundo de garrafa.", "E o pé... é redondo. Que nem fundo de garrafa.", "tense"),
    ("L05", "A pegada não tem ponta, nem calcanhar. Ninguém sabe pra que lado ele foi.", "A pegada não tem ponta, nem calcanhar.", "tense"),
    ("L06", "Uma noite, o compadre Bento foi atrás de uma anta... e não voltou.", "Uma noite, o compadre Bento foi atrás de uma anta... e não voltou.", "tense"),
    ("L07", "Lá pela meia-noite, veio o grito.", "Lá pela meia-noite, veio o grito.", "tense"),
    ("L07B", "Ô, compadreeeee!", "Ô, COMPADREEE!", "shout"),
    ("L08", "Era a voz do Bento. Tchá por Deus... igualzinha.", "Era a voz do Bento. Tchá por Deus... igualzinha.", "whisper"),
    ("L10", "Quanto mais andava, mais o grito mudava de lado. Na frente. Atrás. Em cima.", "Quanto mais andava, mais o grito mudava de lado. Na frente. Atrás. Em cima.", "fast"),
    ("L11", "E as pegadas redondas... davam volta nele.", "E as pegadas redondas... davam volta nele.", "whisper"),
    ("L12", "O bicho só tem um ponto fraco. O umbigo. Branco, no meio daquele pelo todo.", "O bicho só tem um ponto fraco. O umbigo.", "whisper"),
    ("L13", "Ele levantou a lamparina...", "Ele levantou a lamparina...", "whisper"),
    ("L14", "O Bento apareceu três dias depois. Andando em círculo. Assobiando.", "O Bento apareceu três dias depois. Andando em círculo. Assobiando.", "tell"),
    ("L15", "Meu avô nunca contou como saiu de lá. Só dizia uma coisa...", "Meu avô nunca contou como saiu de lá. Só dizia uma coisa...", "whisper"),
]
LINE = {l[0]: l for l in LINES}

# scene: (name, [(line_id, gap_before)], pre, post, fixed_duration)
SCENES = [
    ("hook",      [("L00", 0.55)], 0.0, 0.25, None),
    ("title",     [], 0, 0, 1.05),
    ("forest",    [("L01", 0.15), ("L02", 0.3)], 0, 0.15, None),
    ("silhouette",[("L03", 0.1)], 0, 0.2, None),
    ("footclose", [("L04", 0.1)], 0, 0.25, None),
    ("circle",    [("L05", 0.1)], 0, 0.3, None),
    ("camp",      [("L06", 0.25)], 0, 0.35, None),
    ("scream",    [("L07", 0.1), ("L07B", 0.25), ("L08", 0.35)], 0, 0.25, None),
    ("lantern",   [("L10", 0.15)], 0, 0.15, None),
    ("circletop", [("L11", 0.1)], 0, 0.45, None),
    ("boss",      [("L12", 0.15)], 0, 0.3, None),
    ("raise",     [("L13", 0.1)], 0, 0.85, None),
    ("jumpscare", [], 0, 0, 1.7),
    ("morning",   [("L14", 0.5)], 0, 0.4, None),
    ("gameover",  [("L15", 0.5)], 0, 0.35, None),
    ("continue",  [], 0, 0, 2.3),
]


def estimate(text):
    import re
    t = re.sub(r"<[^>]+>", "", text)
    words = t.split()
    d = sum(0.12 + 0.058 * len(w) for w in words)
    d += 0.25 * t.count(",") + 0.4 * t.count(".") + 0.5 * t.count("...")
    return d


def wav_duration(p):
    with contextlib.closing(wave.open(p)) as w:
        return w.getnframes() / w.getframerate()


def line_audio(lid):
    p = os.path.join(VO, "lines", lid + ".wav")
    return p if os.path.exists(p) else None


def build():
    words_path = os.path.join(VO, "lines", "words.json")
    words = json.load(open(words_path)) if os.path.exists(words_path) else {}
    t = 0.0
    scenes, lines = [], []
    for name, ls, pre, post, fixed in SCENES:
        start = t
        t += pre
        for lid, gap in ls:
            t += gap * GAPK
            p = line_audio(lid)
            dur = wav_duration(p) if p else estimate(LINE[lid][1])
            lw = words.get(lid)
            if not lw:  # proportional estimate
                cap = LINE[lid][2].split()
                tot = sum(len(w) + 2 for w in cap)
                acc = 0.0
                lw = []
                for w in cap:
                    s = acc / tot * dur
                    acc += len(w) + 2
                    lw.append({"w": w, "s": s, "e": acc / tot * dur})
            lines.append({"id": lid, "start": t, "dur": dur, "caption": LINE[lid][2],
                          "words": [{"w": w["w"], "s": t + w["s"], "e": t + w["e"]} for w in lw]})
            t += dur
        t += post * GAPK
        if fixed:
            t = start + fixed
        scenes.append({"name": name, "start": start, "end": t})
    tl = {"scenes": scenes, "lines": lines, "total": t}
    os.makedirs(BUILD, exist_ok=True)
    json.dump(tl, open(os.path.join(BUILD, "timing.json"), "w"), indent=1, ensure_ascii=False)
    return tl


if __name__ == "__main__":
    tl = build()
    for s in tl["scenes"]:
        print("%-11s %6.2f %6.2f" % (s["name"], s["start"], s["end"]))
    print("total", round(tl["total"], 2))
