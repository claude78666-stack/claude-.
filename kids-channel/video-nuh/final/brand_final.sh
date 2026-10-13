#!/bin/sh
# Prepends the Toon Noon intro and adds the logo watermark (top-left) to the story.
set -e
cd "$(dirname "$0")"
B=../brand
# Watermark hidden during the big end logo (from 276.5 s of the story).
ffmpeg -y -i nuh_and_the_ark.mp4 -i $B/intro.mp4 -i $B/watermark.png -filter_complex "\
[2:v]scale=128:128,format=rgba,colorchannelmixer=aa=0.85[wm];\
[0:v][wm]overlay=36:30:enable='lt(t,276.5)'[story];\
[1:v][story]xfade=transition=fade:duration=0.6:offset=5.4,format=yuv420p[v];\
[1:a][0:a]acrossfade=d=0.6[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -b:v 6M -maxrate 8M -bufsize 12M -c:a aac -b:a 192k \
  toon_noon_nuh_and_the_ark_1080p.mp4
ffmpeg -y -i toon_noon_nuh_and_the_ark_1080p.mp4 -vf scale=1280:720:flags=lanczos -c:v libx264 -preset slow \
  -b:v 2300k -maxrate 3M -bufsize 5M -c:a aac -b:a 128k toon_noon_nuh_and_the_ark_720p.mp4
