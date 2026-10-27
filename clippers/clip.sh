#!/usr/bin/env bash
# Cut a vertical 9:16 clip from a video URL or file.
# Usage: ./clip.sh <url-or-file> <start HH:MM:SS> <end HH:MM:SS> [output.mp4]
# Needs: ffmpeg, and yt-dlp for URLs.
set -euo pipefail

src="$1"; start="$2"; end="$3"; out="${4:-clip.mp4}"

if [[ "$src" =~ ^https?:// ]]; then
  tmp="$(mktemp -d)"
  yt-dlp -f "bv*[height<=1080]+ba/b" --merge-output-format mp4 \
    --download-sections "*${start}-${end}" -o "$tmp/src.mp4" "$src"
  input="$tmp/src.mp4"; seek=()
else
  input="$src"; seek=(-ss "$start" -to "$end")
fi

# Center-crop to 9:16 and scale to 1080x1920.
ffmpeg -y "${seek[@]}" -i "$input" \
  -vf "crop=ih*9/16:ih,scale=1080:1920" \
  -c:v libx264 -preset fast -crf 20 -c:a aac -b:a 160k "$out"

echo "Saved $out — add captions in CapCut (Text > Auto captions)."
