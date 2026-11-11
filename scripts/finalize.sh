#!/bin/sh
# Junta vídeo (Remotion) + mix e exporta H.264/AAC ~12 Mbps
set -e
ffmpeg -v error -y -i "$1" -i build/mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 12M -maxrate 14M -bufsize 24M -pix_fmt yuv420p -profile:v high -r 30 -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$2"
