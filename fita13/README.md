# FITA 13: O ARSENAL

Vídeo analog horror vertical (1080x1920, 30 fps, ~75 s) 100% procedural — imagem, ícones, efeitos VHS e áudio gerados por código.

```
python render.py --preview   # 1 PNG por cena em saida/preview/
python render.py             # vídeo completo em saida/fita13_arsenal.mp4
```

Requisitos: Python 3.10+, numpy, Pillow, ffmpeg no PATH.

- `config.py` — tempos, textos, `HANDLE` do canal (troque ou deixe `""`), seed 1987.
- `eventos.py` — lista de falhas (estática, tracking, drop-outs, glitches) compartilhada entre vídeo e áudio (salva em `saida/eventos.json`).
- `cenas/` — uma função por bloco: `cena(t, frame_idx) -> PIL.Image 360x640`.
- `fx_vhs.py` — pipeline VHS; `icones.py` — ícones pixel-art 16x16; `audio.py` — síntese de áudio.
- `assets/fonts/*.ttf` — opcional, fonte estilo VCR OSD (senão usa DejaVu Sans Mono Bold).
- `assets/fotos/` — opcional: `fachada.jpg`, `patio.jpg`, `varanda.jpg`, `porao.jpg` (fotos próprias) substituem os desenhos.

Obra de ficção. Fatos históricos reais; eventos sobrenaturais inventados. Sem relação com o Sesc.
