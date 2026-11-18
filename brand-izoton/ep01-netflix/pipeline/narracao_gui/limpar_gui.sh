#!/bin/bash
# uso: limpar_gui.sh entrada saida  (voz do Guilherme: limpeza + tratamento + -16 LUFS por arquivo)
D=$(dirname "$0")/narr_gui
CADEIA="highpass=f=80:poles=2,afftdn=nr=18:nf=-46:tn=1,equalizer=f=140:t=q:w=0.9:g=1,equalizer=f=350:t=q:w=1.2:g=-1.5,equalizer=f=4200:t=q:w=1.1:g=2,deesser=i=0.45:m=0.5:f=0.5:s=o,acompressor=threshold=-21dB:ratio=2.5:attack=10:release=180:knee=4:makeup=1.5,agate=threshold=0.018:range=0.2:ratio=2:attack=4:release=180:knee=3"
ffmpeg -y -v error -i "$1" -i $D/sala_pequena.wav -filter_complex "[0:a]aformat=sample_rates=48000:channel_layouts=mono,$CADEIA,asplit=2[seco][env];[env][1:a]afir=dry=0:wet=1[mol];[seco][mol]amix=inputs=2:weights=1 0.11:normalize=0,alimiter=limit=0.89:attack=5:release=60:level=disabled" -ar 48000 -ac 1 "$2.tmp.wav"
J=$(ffmpeg -nostats -i "$2.tmp.wav" -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(-16-float(d['input_i']))")
ffmpeg -y -v error -i "$2.tmp.wav" -af "volume=${g}dB,alimiter=limit=0.89:level=disabled" -c:a pcm_s24le "$2" && rm "$2.tmp.wav"
