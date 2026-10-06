#!/bin/bash
# Usage: render_all.sh <out_name> [workers]
set -e
cd "$(dirname "$0")"
PY=../venv/bin/python
OUT=${1:-omnia_reel}
NW=${2:-4}
N=$($PY -c "import timeline as TL; print(int(round(TL.DURATION*TL.FPS)))")
echo "frames: $N workers: $NW"
mkdir -p chunks; rm -f chunks/*.mp4
pids=()
for i in $(seq 0 $((NW-1))); do
  f0=$(( i * N / NW )); f1=$(( (i+1) * N / NW ))
  OMP_NUM_THREADS=1 nice -n 5 $PY comp.py render $f0 $f1 chunks/c$i.mp4 > chunks/c$i.log 2>&1 &
  pids+=($!)
done
fail=0; for p in "${pids[@]}"; do wait $p || fail=1; done
if [ $fail -ne 0 ]; then echo "RENDER FAILED"; tail -5 chunks/*.log; exit 1; fi
(cd chunks && ls c*.mp4 | sort -V | sed "s/^/file '/; s/$/'/" > list.txt)
ffmpeg -y -loglevel error -f concat -safe 0 -i chunks/list.txt -c copy ${OUT}_video.mp4
$PY mix.py ${OUT}_audio.wav
$PY mix.py ${OUT}_audio_novo.wav --novo
for v in "" "_novo"; do
  ffmpeg -y -loglevel error -i ${OUT}_video.mp4 -i ${OUT}_audio${v}.wav -map 0:v -map 1:a \
    -c:v libx264 -preset slow -crf 16 -maxrate 25M -bufsize 50M -profile:v high -level 4.2 -pix_fmt yuv420p \
    -color_primaries bt709 -color_trc bt709 -colorspace bt709 -r 30 \
    -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest ${OUT}${v}.mp4
done
ffprobe -v error -show_entries format=duration,size,bit_rate -of default=nw=1 ${OUT}.mp4
echo "RENDER OK"
