#!/usr/bin/env bash
# Folha de contato: 1 frame a cada 0,5s, com as margens de segurança desenhadas (topo 250, base 420, direita 140).
# uso: scripts/contact_sheet.sh <video> <prefixo_saida>
set -e
IN="$1"; OUT="$2"
ffmpeg -v error -y -i "$IN" -vf "select='not(mod(n\,15))',setpts=N/2/TB,drawbox=x=0:y=250:w=940:h=1250:color=cyan@0.9:t=4,scale=270:480,drawtext=text='%{eif\:n/2\:d}.%{eif\:mod(n\,2)*5\:d}s':x=6:y=6:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.7,tile=7x4" -q:v 3 -fps_mode passthrough "${OUT}_%d.jpg"
