# FITA 13: O ARSENAL

Vídeo analog horror vertical (1080x1920, 30 fps, ~85 s): imagem, ícones, efeitos VHS e áudio gerados por código, com narração do Zé Canhãozinho e fotos reais do Arsenal (licenças livres).

```
python render.py --preview   # 1 PNG por cena em saida/preview/
python render.py             # vídeo completo em saida/fita13_arsenal.mp4
```

Requisitos: Python 3.10+, numpy, Pillow, ffmpeg no PATH e, para a narração, `pip install piper-tts`.
Na primeira execução a voz pt-BR do Piper (`pt_BR-faber-medium`, ~60 MB) é baixada para `assets/vozes/`.
Sem Piper/sem internet, o vídeo sai com "blips" de voz no lugar da narração.

- `config.py` — tempos, textos, `HANDLE` do canal (troque ou deixe `""`), seed 1987.
- `eventos.py` — lista de falhas (estática, tracking, drop-outs, glitches) compartilhada entre vídeo e áudio (salva em `saida/eventos.json`).
- `cenas/` — uma função por bloco: `cena(t, frame_idx) -> PIL.Image 360x640`.
- `narracao.py` — roteiro falado e voz de mascote (Piper + reamostragem; o tom sobe a cada regra). Velocidade em `VELOCIDADE`.
- `fx_vhs.py` — pipeline VHS; `icones.py` — ícones pixel-art 16x16; `audio.py` — síntese de áudio.
- `assets/fonts/*.ttf` — opcional, fonte estilo VCR OSD (senão usa DejaVu Sans Mono Bold).
- `assets/fotos/` — `fachada.jpg` e `varanda.jpg` são fotos reais do Wikimedia Commons (créditos em `assets/fotos/CREDITOS.txt` e no cartão final). Dá para trocar por fotos próprias, e também adicionar `patio.jpg` e `porao.jpg`.

Obra de ficção. Fatos históricos reais; eventos sobrenaturais inventados. Sem relação com o Sesc.
