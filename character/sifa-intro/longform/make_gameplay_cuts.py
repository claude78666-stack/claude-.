#!/usr/bin/env python3
"""Cuts Xbox's official E-Day trailers into per-section gameplay backdrops -> gameplay/<id>.mp4

Run: python3 make_gameplay_cuts.py [section_id ...]
Downloads the official trailers from the game's Steam store page into official_video/ (not committed),
then follows cuts.json: for each section it cuts the listed trailer moments in order, matched to what
Sifa is explaining, until the section's narration is covered (looping the list if needed). Adds a dark
fade on the left for the headings and a "Footage: Xbox / The Coalition" credit. render_longform.py uses
gameplay/<id>.mp4 as the section background; drop in your own recorded gameplay of the same name instead.
Microsoft's Game Content Usage Rules allow using its game footage in videos like this.
"""
import json
import re
import subprocess
import sys
import urllib.request
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SRC, OUT, TMP = HERE / "official_video", HERE / "gameplay", HERE / "build" / "cuts"
for d in (SRC, OUT, TMP):
    d.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 24
LEAD, TAIL, TEMPO = 1.3, 0.9, 0.94  # keep in step with render_longform.py
STEAM_APP = 3010850
plan = json.load(open(HERE / "cuts.json"))


def run(cmd):
    subprocess.run(cmd, check=True)


def fetch_trailers():
    want = set(plan["sources"].values())
    if all((SRC / f"{n}.mp4").exists() for n in want):
        return
    url = f"https://store.steampowered.com/api/appdetails?appids={STEAM_APP}&cc=us&l=en"
    movies = json.load(urllib.request.urlopen(url, timeout=60))[str(STEAM_APP)]["data"]["movies"]
    for m in movies:
        name = re.sub(r"[^a-z0-9]+", "_", m["name"].lower()).strip("_")
        if name in want and not (SRC / f"{name}.mp4").exists():
            run(["ffmpeg", "-v", "error", "-y", "-i", m["hls_h264"], "-map", "0:v:0", "-c", "copy",
                 str(SRC / f"{name}.mp4")])  # master playlist: first video stream is 1080p


def overlay_png():
    path = TMP / "overlay.png"
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x in range(0, 1300, 4):
        d.rectangle([x, 0, x + 3, H], fill=(4, 3, 12, int(170 * (1 - x / 1300) ** 1.4)))
    d.text((W - 70, H - 36), "Footage: Xbox / The Coalition", anchor="rm",
           font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 20), fill=(255, 255, 255, 160))
    img.save(path)
    return path


def seconds(sid):
    with wave.open(str(HERE / "voice" / f"{sid}.wav")) as w:
        return LEAD + w.getnframes() / w.getframerate() / TEMPO + TAIL


def build(sid, shots, total, overlay):
    parts, t, i = [], 0.0, 0
    while t < total - 0.05:
        src, start, length = shots[i % len(shots)]
        length = min(length, total - t)
        part = TMP / f"{sid}_{len(parts):02d}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", f"{length:.3f}",
             "-i", str(SRC / f"{plan['sources'][src]}.mp4"), "-an",
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,format=yuv420p",
             "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", str(part)])
        parts.append(part)
        t += length
        i += 1
    (TMP / f"{sid}.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(TMP / f"{sid}.txt"),
         "-loop", "1", "-i", str(overlay), "-filter_complex", "[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]",
         "-map", "[v]", "-t", f"{total:.3f}", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
         str(OUT / f"{sid}.mp4")])
    print(sid, f"{total:.1f}s", len(parts), "shots", flush=True)


fetch_trailers()
overlay = overlay_png()
wanted = set(sys.argv[1:])
for sid, shots in plan["sections"].items():
    if not wanted or sid in wanted:
        build(sid, shots, seconds(sid), overlay)
