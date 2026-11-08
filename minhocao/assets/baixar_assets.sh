#!/usr/bin/env bash
# Baixa a voz Piper pt_BR (não versionada por ser grande, ~63 MB).
set -e
cd "$(dirname "$0")/voz"
B=https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium
curl -fL -o pt_BR-faber-medium.onnx "$B/pt_BR-faber-medium.onnx"
curl -fL -o pt_BR-faber-medium.onnx.json "$B/pt_BR-faber-medium.onnx.json"
curl -fL -o MODEL_CARD_faber "$B/MODEL_CARD"
