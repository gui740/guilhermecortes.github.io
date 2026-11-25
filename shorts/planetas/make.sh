#!/usr/bin/env bash
# Gera o Short completo: narração -> áudio -> vídeo -> mux final
set -euo pipefail
cd "$(dirname "$0")"
NARR=${NARR:-out/narr}
if [ ! -f "$NARR/n00.mp3" ] && [ ! -f "$NARR/n00.wav" ]; then python3 tts_provisorio.py "$NARR"; fi
python3 audio.py "$NARR"
[ -f out/video_mudo.mp4 ] || python3 render.py video
ffmpeg -v error -y -i out/video_mudo.mp4 -i out/audio.wav \
  -c:v libx264 -preset slow -crf 17 -profile:v high -pix_fmt yuv420p -r 30 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=7" -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart -shortest out/tamanho_real_dos_planetas.mp4
echo "pronto: out/tamanho_real_dos_planetas.mp4"
