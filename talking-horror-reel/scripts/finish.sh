#!/bin/bash
# Finalização: motion blur leve só nos deslocamentos rápidos + áudio + H.264 ~12 Mbps / AAC.
# uso: scripts/finish.sh <video_sem_audio.mp4> <audio.wav> <saida.mp4> [faixas de blur "between(t,a,b)+..."]
set -e
IN="$1"; AUD="$2"; OUT="$3"
BLUR="${4:-between(t,0,1.3)+between(t,4.05,5.5)+between(t,24.25,25.6)+between(t,31.6,32.9)+between(t,35.9,37)}"
# o último frame funde no primeiro (0,2 s) para o loop fechar sem salto
ffmpeg -y -v error -i "$IN" -frames:v 1 /tmp/_f0.png
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN"); ST=$(python3 -c "print($DUR-0.2)")
ffmpeg -y -v error -i "$IN" -i "$AUD" -loop 1 -framerate 30 -t "$DUR" -i /tmp/_f0.png -filter_complex \
 "[0:v]split[a][b];[b]tmix=frames=3:weights='1 2 1'[m];[a][m]overlay=enable='$BLUR':shortest=1[x];[2:v]format=yuva420p,fade=t=in:st=$ST:d=0.2:alpha=1[f];[x][f]overlay=shortest=1,format=yuv420p[v]" \
 -map "[v]" -map 1:a -c:v libx264 -preset slow -b:v 12M -maxrate 14M -bufsize 24M -profile:v high -pix_fmt yuv420p -r 30 \
 -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest "$OUT"
ffprobe -v error -show_entries format=duration,bit_rate:stream=codec_name,width,height,r_frame_rate -of default=nw=1 "$OUT"
