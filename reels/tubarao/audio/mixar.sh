#!/usr/bin/env bash
# Mixa narração (Google TTS) + trilha (com ducking sob a voz) + efeitos, normaliza a -14 LUFS (padrão Instagram)
# e junta com o vídeo. Uso: bash audio/mixar.sh   (rode depois de npm run render)
set -euo pipefail
cd "$(dirname "$0")/.."
python3 audio/montar_narracao.py
python3 audio/trilha.py out/trilha.wav
python3 audio/sfx.py out/sfx.wav
ffmpeg -v error -y -i out/narracao.wav -i out/trilha.wav -i out/sfx.wav -filter_complex "\
[0]asplit=2[voz][sc];\
[1]volume=0.5[mus];\
[mus][sc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=400:makeup=1[musd];\
[2]volume=0.55[fx];\
[voz][musd][fx]amix=inputs=3:normalize=0,alimiter=limit=0.9:level=disabled,\
loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]" -map "[a]" -c:a pcm_s16le out/mix_final.wav
# vídeo mudo (H.264 High, yuv420p, faststart)
if [ out/render_raw.mp4 -nt out/reel_tubarao_sem_audio.mp4 ] 2>/dev/null || [ ! -f out/reel_tubarao_sem_audio.mp4 ]; then
  ffmpeg -v error -y -i out/render_raw.mp4 -vf "scale=in_range=full:out_range=tv,format=yuv420p" \
    -c:v libx264 -profile:v high -preset slow -crf 17 -r 30 -movflags +faststart -an out/reel_tubarao_sem_audio.mp4
fi
ffmpeg -v error -y -i out/reel_tubarao_sem_audio.mp4 -i out/mix_final.wav -c:v copy -c:a aac -b:a 256k \
  -shortest -movflags +faststart out/reel_tubarao_narrado.mp4
echo "ok out/reel_tubarao_narrado.mp4"
