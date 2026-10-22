#!/usr/bin/env python3
"""Cuts the full Sifa intro: Veo shot 1 (walk and sit) + shots 2-4 (she talks to camera) -> sifa_intro_full_1080p.mp4

Run: python3 build_full_intro.py [out.mp4]
Needs ai/shot1_walk_sit_veo.mp4 and ai/shot{2..4}_*_veo.mp4 (from ai/gen_veo.py), voice.wav, music.wav
(make_music.py) and ffmpeg. Her voice is always voice.wav, so it stays the same in every video; the Veo
clips' own audio is dropped except shot 1's room tone. Ducks the music under the voice and adds the lower thirds.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "sifa_intro_full_1080p.mp4"
TMP = HERE / "build"
TMP.mkdir(exist_ok=True)
W, H, FPS = 1920, 1080, 24
FONT = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
PURPLE, CYAN = (170, 80, 255), (40, 220, 255)

SHOTS = [  # (file, seconds to keep)
    ("ai/shot1_walk_sit_veo.mp4", 4.0),
    ("ai/shot2_hello_veo.mp4", 8.0),
    ("ai/shot3_prequel_veo.mp4", 8.0),
    ("ai/shot4_lets_go_veo.mp4", 8.0),
]
VOICE_AT = 4.3  # voice.wav starts just after she sits; "Let's get started!" lands at 4.3 + 18.2 = 22.5 s
TOTAL = sum(d for _, d in SHOTS)
# lower thirds: (kicker, title, accent, start, end)
LOWER_THIRDS = [
    ("", "SIFA", PURPLE, 4.5, 7.4, "The First SI Agent"),
    ("TODAY", "GEARS OF WAR: E-DAY  -  Honest Walkthrough", CYAN, 7.6, 15.0, ""),
]


def lower_third(path, kicker, title, accent, sub):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    big, small = ImageFont.truetype(FONT.format("Bold"), 46), ImageFont.truetype(FONT.format("SemiBold"), 24)
    x, y = 72, 880
    width = max(d.textlength(title, font=big), d.textlength(sub or kicker, font=small)) + 64
    d.rectangle([x, y, x + width, y + 118], fill=(8, 6, 18, 170))
    d.rectangle([x, y, x + 8, y + 118], fill=(*accent, 255))
    if kicker:
        d.text((x + 32, y + 14), kicker, font=small, fill=(*accent, 255))
        d.text((x + 32, y + 46), title, font=big, fill=(255, 255, 255, 255))
    else:
        d.text((x + 32, y + 12), title, font=big, fill=(255, 255, 255, 255))
        d.text((x + 32, y + 74), sub, font=small, fill=(220, 220, 235, 255))
    img.save(path)


def run(cmd):
    subprocess.run(cmd, check=True)


# 1. normalise every shot to 1080p24 with stereo 48 kHz audio
parts = []
for i, (src, dur) in enumerate(SHOTS):
    part = TMP / f"part{i}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / src), "-t", str(dur),
         "-vf", f"scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1,format=yuv420p",
         "-af", "aresample=48000,aformat=channel_layouts=stereo,apad", "-t", str(dur),
         "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-c:a", "pcm_s16le", str(part)])
    parts.append(part)
(TMP / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(TMP / "list.txt"),
     "-c", "copy", str(TMP / "joined.mov")])

# 2. lower thirds, music ducked under the dialogue, fade out, loudness to -14 LUFS
inputs = ["-i", str(TMP / "joined.mov"), "-i", str(HERE / "music.wav"), "-i", str(HERE / "voice.wav")]
chain, last = [], "[0:v]"
for n, (kicker, title, accent, t0, t1, sub) in enumerate(LOWER_THIRDS):
    png = TMP / f"lt{n}.png"
    lower_third(png, kicker, title, accent, sub)
    inputs += ["-loop", "1", "-t", str(TOTAL), "-i", str(png)]
    k = n + 3
    chain.append(f"[{k}:v]format=rgba,fade=t=in:st={t0}:d=0.4:alpha=1,fade=t=out:st={t1 - 0.4}:d=0.4:alpha=1[lt{n}]")
    chain.append(f"{last}[lt{n}]overlay=0:0:enable='between(t,{t0},{t1})'[v{n}]")
    last = f"[v{n}]"
chain.append(f"{last}fade=t=in:st=0:d=0.5,fade=t=out:st={TOTAL - 0.8}:d=0.8[vout]")
ms = int(VOICE_AT * 1000)
chain.append(f"[0:a]atrim=0:{SHOTS[0][1]},afade=t=out:st={SHOTS[0][1] - 0.5}:d=0.5,volume=0.6,apad[room]")
chain.append(f"[2:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms},apad,asplit=2[vox][key]")
chain.append(f"[room][vox]amix=inputs=2:normalize=0:duration=first,atrim=0:{TOTAL}[dlg]")
chain.append(f"[1:a]atrim=0:{TOTAL},volume=0.55[mus]")
chain.append("[mus][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[ducked]")
chain.append(f"[dlg][ducked]amix=inputs=2:normalize=0,afade=t=out:st={TOTAL - 1.0}:d=1.0,"
             "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain),
     "-map", "[vout]", "-map", "[aout]", "-t", str(TOTAL),
     "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
     "-c:a", "aac", "-b:a", "192k", str(OUT)])
print("wrote", OUT, f"{TOTAL:.1f}s")
