#!/usr/bin/env bash
# Vídeo completo: narração (Gemini) -> tempos/legendas -> trilha -> render com áudio
#   GEMINI_KEY_FILE=arquivo_da_chave ./make.sh
set -euo pipefail
cd "$(dirname "$0")"
[ -f out/narr/words.json ] || python3 tts_gemini.py out/narr Puck
python3 tempos.py
python3 audio.py
node render.js --workers 4 --out chapado_expectativa_de_vida.mp4
