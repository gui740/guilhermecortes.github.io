# PANTADEX — Fauna do Pantanal Mato-Grossense

Vídeo vertical (1080x1920, 30 fps, H.264 + AAC, ~71 s): `pantadex.mp4`.
Quadros de prévia em `previews/`.

Tudo é gerado por código, sem assets de terceiros além das fontes:

- **Arte**: pixel art desenhada em Python/Pillow (`pdx/`). A tela do jogo é renderizada em 240x160 e ampliada 4x com nearest-neighbor; o corpo do aparelho é desenhado em grade 540x960 e ampliado 2x.
- **Trilha e efeitos**: chiptune original sintetizado em numpy (`pdx/audio.py`).
- **Narração**: pt-BR, gerada offline com Kokoro TTS (voz `pf_dora`), clipes em `assets/narration/`.
- **Fontes**: Press Start 2P e Tiny5 (Google Fonts, licença SIL OFL 1.1).

## Reproduzir

    pip install pillow numpy scipy soundfile
    python render.py                # gera out/pantadex.mp4 (requer ffmpeg)
    python render.py shots 8.5 24   # só quadros de prévia

Para regenerar a narração: `pip install kokoro-onnx` e `python tts.py <pasta com kokoro-v1.0.onnx e voices-v1.0.bin>`.
O roteiro e os dados das fichas ficam em `pdx/script.py`.
