#!/usr/bin/env bash
# Pipeline completo: narração -> timeline -> áudio -> Remotion -> ffmpeg (H.264 ~12 Mbps + AAC)
set -e
cd "$(dirname "$0")/.."
BROWSER=${BROWSER_EXECUTABLE:-/opt/pw-browsers/chromium}
# --tts: gera de novo a voz (precisa de GEMINI_API_KEY no ambiente), confere e alinha as palavras
if [ "$1" = "--tts" ]; then python3 scripts/gemini_tts.py; python3 scripts/check_vo.py; python3 scripts/align_words.py; fi
python3 scripts/assemble_vo.py
python3 scripts/make_events.py
python3 scripts/make_audio.py
mkdir -p out build
render() { # comp, mix, saída   (AUDIO_ONLY=1 reaproveita o vídeo já renderizado e só troca o áudio)
  [ -n "$AUDIO_ONLY" ] && [ -f "build/$1.mp4" ] || npx remotion render src/index.ts "$1" "build/$1.mp4" --browser-executable="$BROWSER" --codec=h264 --crf=8 --concurrency=4 --muted --log=error
  ffmpeg -v error -y -i "build/$1.mp4" -i "build/mix_$2.wav" -map 0:v -map 1:a \
    -c:v libx264 -preset slow -profile:v high -pix_fmt yuv420p -b:v 12M -maxrate 14M -bufsize 24M -r 30 \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
    -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart "out/$3"
}
render Reel main reel.mp4
render GanchoA gA gancho_A.mp4
render GanchoB gB gancho_B.mp4
render GanchoC gC gancho_C.mp4
[ -n "$AUDIO_ONLY" ] || npx remotion still src/index.ts Capa out/capa.png --browser-executable="$BROWSER" --log=error
