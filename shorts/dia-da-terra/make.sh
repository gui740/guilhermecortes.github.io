#!/usr/bin/env bash
# PERA, OI? — Se a história da Terra fosse um dia de 24 horas
#   GEMINI_KEY_FILE=arquivo_da_chave ./make.sh
set -euo pipefail
cd "$(dirname "$0")"
export NARR=${NARR:-out/narr}
[ -f "$NARR/words.json" ] || python3 tts_gemini.py "$NARR" Puck
python3 audio.py
[ -f out/video_mudo.mp4 ] || python3 render.py video
ffmpeg -v error -y -i out/video_mudo.mp4 -i out/audio.wav \
  -c:v libx264 -preset slow -crf 17 -profile:v high -pix_fmt yuv420p -r 30 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=7" -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart -shortest out/pera_oi_dia_da_terra.mp4
echo "pronto: out/pera_oi_dia_da_terra.mp4"
