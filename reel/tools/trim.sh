#!/bin/bash
# trim leading/trailing silence, convert to 48k mono wav
mkdir -p assets/vo/trim
for f in assets/vo/raw/*.mp3; do b=$(basename $f .mp3)
ffmpeg -v error -y -i $f -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse" -ar 48000 -ac 1 assets/vo/trim/$b.wav; done
