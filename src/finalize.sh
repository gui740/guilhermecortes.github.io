#!/bin/bash
# Junta vídeo (Remotion) + mix de áudio, adiciona granulado de luma e codifica H.264 ~12Mbps + AAC.
# uso: src/finalize.sh in_video.mp4 in_audio.wav out.mp4
set -e
ffmpeg -y -v error -i "$1" -i "$2" -filter_complex "[0:v]noise=c0s=13:c0f=t+u,format=yuv420p[v];[1:a]apad[a]" -map "[v]" -map "[a]" \
  -c:v libx264 -profile:v high -preset slow -b:v 12M -maxrate 14M -bufsize 24M -r 30 -movflags +faststart \
  -c:a aac -b:a 192k -ar 48000 -t "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1")" "$3"
ffprobe -v error -show_entries format=duration,bit_rate -show_entries stream=codec_name,width,height,r_frame_rate -of compact "$3"
