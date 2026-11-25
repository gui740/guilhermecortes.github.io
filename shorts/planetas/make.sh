#!/usr/bin/env bash
# Gera o Short completo: narração -> áudio -> vídeo -> mux final
#   GEMINI_KEY_FILE=arquivo_da_chave ./make.sh        (narração Gemini TTS)
#   NARR=out/narr ./make.sh                            (narração provisória Edge TTS)
set -euo pipefail
cd "$(dirname "$0")"
export NARR=${NARR:-out/narr_gemini}
if [ ! -f "$NARR/words.json" ]; then
  if [ "$NARR" = "out/narr" ]; then python3 tts_provisorio.py "$NARR"; else python3 tts_gemini.py "$NARR" Puck; fi
fi
python3 audio.py
[ -f out/video_mudo.mp4 ] || python3 render.py video
ffmpeg -v error -y -i out/video_mudo.mp4 -i out/audio.wav \
  -c:v libx264 -preset slow -crf 17 -profile:v high -pix_fmt yuv420p -r 30 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=7" -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart -shortest out/tamanho_real_dos_planetas_v2.mp4
echo "pronto: out/tamanho_real_dos_planetas_v2.mp4"
