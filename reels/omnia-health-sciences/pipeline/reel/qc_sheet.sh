#!/bin/bash
# contact sheet of a video: one frame every 0.5s, 8 columns
V=$1; OUT=${2:-sheet.jpg}
ffmpeg -y -loglevel error -i "$V" -vf "fps=2,scale=270:-1,tile=8x7:padding=4:color=0x222222" -frames:v 1 "$OUT"
echo "$OUT"
