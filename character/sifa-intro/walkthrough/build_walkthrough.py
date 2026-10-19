#!/usr/bin/env python3
"""Edits a Gears of War: E-Day walkthrough episode from your own gameplay -> sifa_walkthrough_<n>.mp4

Run: python3 build_walkthrough.py [episode_number]
Put your recorded gameplay in clips/ (Xbox capture, Game Bar or OBS; any resolution or frame rate). They
play in filename order, so name them like "01 Prologue - Kalona Falls.mp4"; the part after the number
becomes the chapter title card. Optional: trims.json {"<file name>": [start_s, end_s]} keeps only that
part of a clip.
The episode opens with ../sifa_intro_full_1080p.mp4 (or ../sifa_intro_ai_1080p.mp4), keeps the game audio,
puts the SIFA SI watermark top left and a chapter title over the start of each clip, and ends with the
"SIFA SI" sign-off (../sifa_si_outro.mp4).
Only use footage you recorded yourself or have permission to use.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
INTRO_DIR = HERE.parent
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)
EP = int(sys.argv[1]) if len(sys.argv) > 1 else 1
OUT = HERE / f"sifa_walkthrough_{EP:02d}.mp4"
W, H, FPS = 1920, 1080, 60
FONT = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
PURPLE, CYAN = (170, 80, 255), (40, 220, 255)
trims = json.load(open(HERE / "trims.json")) if (HERE / "trims.json").exists() else {}


def run(cmd):
    subprocess.run(cmd, check=True)


def chapter_png(path, kicker, title):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    big, small = ImageFont.truetype(FONT.format("Black"), 64), ImageFont.truetype(FONT.format("Bold"), 28)
    width = max(d.textlength(title.upper(), font=big), d.textlength(kicker, font=small)) + 80
    d.rounded_rectangle([70, 820, 70 + width, 990], 16, fill=(8, 6, 18, 190))
    d.rectangle([70, 820, 80, 990], fill=(*PURPLE, 255))
    d.text((110, 842), kicker, font=small, fill=(*CYAN, 255))
    d.text((110, 884), title.upper(), font=big, fill=(255, 255, 255, 255))
    img.save(path)


def watermark_png(path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((60, 40), "SIFA", font=ImageFont.truetype(FONT.format("Black"), 44), fill=(*PURPLE, 200))
    d.text((186, 54), "SI", font=ImageFont.truetype(FONT.format("Bold"), 26), fill=(*CYAN, 200))
    img.save(path)


def normalise(src, out, start=None, end=None, overlay=None):
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if start is not None:
        cmd += ["-ss", str(start)]
    if end is not None:
        cmd += ["-to", str(end)]
    cmd += ["-i", str(src)]
    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1"
    if overlay:
        cmd += ["-loop", "1", "-i", str(BUILD / "watermark.png"), "-loop", "1", "-i", str(overlay)]
        graph = (f"[0:v]{vf}[g];[g][1:v]overlay=0:0:shortest=1[w];"
                 "[2:v]format=rgba,fade=t=in:st=0.5:d=0.4:alpha=1,fade=t=out:st=5:d=0.5:alpha=1[c];"
                 "[w][c]overlay=0:0:shortest=1:enable='lt(t,5.6)',format=yuv420p[v]")
        cmd += ["-filter_complex", graph, "-map", "[v]", "-map", "0:a?"]
    else:
        cmd += ["-vf", vf + ",format=yuv420p"]
    cmd += ["-af", "aresample=48000,aformat=channel_layouts=stereo", "-c:v", "libx264", "-crf", "17",
            "-preset", "medium", "-c:a", "aac", "-b:a", "192k", str(out)]
    run(cmd)
    return out


clips = sorted(p for p in (HERE / "clips").glob("*") if p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm"))
if not clips:
    sys.exit("No gameplay in clips/ yet. Record your own E-Day gameplay and drop the files there.")
watermark_png(BUILD / "watermark.png")
intro = INTRO_DIR / "sifa_intro_full_1080p.mp4"
intro = intro if intro.exists() else INTRO_DIR / "sifa_intro_ai_1080p.mp4"
parts = [normalise(intro, BUILD / "intro.mp4")]
for i, clip in enumerate(clips, 1):
    title = re.sub(r"^\d+[\s._-]*", "", clip.stem) or f"Part {i}"
    card = BUILD / f"chapter_{i:02d}.png"
    chapter_png(card, f"EPISODE {EP}  |  CHAPTER {i}", title)
    start, end = trims.get(clip.name, (None, None))
    parts.append(normalise(clip, BUILD / f"clip_{i:02d}.mp4", start, end, overlay=card))
    print("clip", clip.name, flush=True)
parts.append(normalise(INTRO_DIR / "sifa_si_outro.mp4", BUILD / "outro.mp4"))
(BUILD / "parts.txt").write_text("".join(f"file '{p}'\n" for p in parts))
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(BUILD / "parts.txt"),
     "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", str(OUT)])
print("wrote", OUT)
