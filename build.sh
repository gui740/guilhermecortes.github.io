#!/usr/bin/env bash
# Reconstrói out/reel.mp4 do zero. Requisitos: python3 (rembg, edge-tts, opencv, scipy, pillow), node + playwright, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/recortes.py          # fotos recortadas dos slides  -> assets/recortes/
python3 scripts/texturas.py          # papel, pontinhos, retícula   -> reel/tex/
python3 scripts/tts.py build/tts     # narração frase a frase (edge-tts pt-BR)
python3 scripts/narracao.py          # corta silêncios, -16 LUFS, timestamps -> reel/timeline.js
node scripts/render.js check 0       # exporta lista de efeitos sonoros -> build/info.json
python3 scripts/audio.py             # efeitos + mixagem -> build/audio.wav
node scripts/render.js all           # quadros 1080x1920 @30fps -> build/frames/
mkdir -p out
ffmpeg -y -v error -framerate 30 -i build/frames/f%05d.jpg -i build/audio.wav \
  -c:v libx264 -preset slow -crf 21 -maxrate 9M -bufsize 18M -pix_fmt yuv420p -profile:v high -r 30 \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest out/reel.mp4
python3 scripts/conferir.py
