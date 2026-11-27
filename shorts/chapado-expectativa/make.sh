#!/usr/bin/env bash
# Perguntas que eu me fiz quando tava chapado — expectativa de vida (motion graphics)
#   GEMINI_KEY_FILE=arquivo_da_chave ./make.sh
set -euo pipefail
cd "$(dirname "$0")"
export NARR=${NARR:-out/narr}
[ -f "$NARR/words.json" ] || python3 tts_gemini.py "$NARR" Algenib
python3 audio.py
[ -f out/video_mudo.mp4 ] || python3 render.py video
ffmpeg -v error -y -i out/video_mudo.mp4 -i out/audio.wav -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p \
  -af "loudnorm=I=-14:TP=-1.5:LRA=9" -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest out/chapado_expectativa_de_vida.mp4
echo "pronto: out/chapado_expectativa_de_vida.mp4"
