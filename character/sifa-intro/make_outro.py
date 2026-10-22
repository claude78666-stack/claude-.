#!/usr/bin/env python3
"""Animated "SIFA SI" sign-off that ends every Sifa video -> sifa_si_outro.mp4

Run: python3 make_outro.py [out.mp4]
5 s, 1080p24: a neon "SIFA" flickers on, "SI" slides in beside it in cyan, a short tagline fades up,
then everything fades to black. Comes with a low synth swell so it can be cut straight onto any video.
"""
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "sifa_si_outro.mp4"
TMP = HERE / "build" / "outro"
TMP.mkdir(parents=True, exist_ok=True)
W, H, FPS, DUR = 1920, 1080, 24, 5.0
FONT = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
PURPLE, CYAN = (190, 90, 255), (40, 220, 255)
big, si, tag = (ImageFont.truetype(FONT.format(w), s) for w, s in (("Black", 260), ("Black", 150), ("SemiBold", 44)))


def neon(text, fnt, color, alpha):
    layer = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(layer)
    d.text((0, 0), text, font=fnt, fill=(*color, int(255 * alpha)))
    glow = layer.filter(ImageFilter.GaussianBlur(22))
    core = Image.new("RGBA", (W, H))
    ImageDraw.Draw(core).text((0, 0), text, font=fnt, fill=(255, 255, 255, int(235 * alpha)))
    return glow, layer, core


probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
w_sifa, w_si = probe.textlength("SIFA", font=big), probe.textlength("SI", font=si)
gap = 50
x0 = (W - (w_sifa + gap + w_si)) / 2
for f in range(int(DUR * FPS)):
    t = f / FPS
    img = Image.new("RGBA", (W, H), (5, 4, 14, 255))
    # neon flicker-on for SIFA over the first 0.8 s
    flick = 1.0 if t > 0.8 else (0.0 if t < 0.15 else (1.0 if math.sin(t * 90) > -0.2 else 0.25) * min(1, t / 0.6))
    si_in = min(1, max(0, (t - 0.9) / 0.35))
    tag_in = min(1, max(0, (t - 1.6) / 0.5))
    fade = min(1, max(0, (DUR - t) / 0.7))
    for text, fnt, color, a, x, y in (("SIFA", big, PURPLE, flick, x0, 300),
                                      ("SI", si, CYAN, si_in, x0 + w_sifa + gap + (1 - si_in) * 120, 390)):
        if a <= 0:
            continue
        glow, layer, core = neon(text, fnt, color, a * fade)
        for lyr in (glow, glow, layer):
            img.alpha_composite(lyr, (int(x), int(y)))
        img.alpha_composite(core.filter(ImageFilter.GaussianBlur(1)), (int(x), int(y)))
    if tag_in > 0:
        d = ImageDraw.Draw(img)
        d.text((W // 2, 700), "THE FIRST SI AGENT", font=tag, fill=(220, 220, 240, int(255 * tag_in * fade)), anchor="mm")
        d.rectangle([W // 2 - 80, 742, W // 2 + 80, 748], fill=(*PURPLE, int(255 * tag_in * fade)))
    img.convert("RGB").save(TMP / f"{f:04d}.png")

# low swell under the logo
SR = 48000
ts = np.arange(int(DUR * SR)) / SR
env = np.minimum(1, ts / 0.8) * np.clip((DUR - ts) / 1.5, 0, 1)
tone = sum(np.sin(2 * np.pi * f * ts) * g for f, g in ((110, 0.5), (164.8, 0.3), (220, 0.25), (329.6, 0.12)))
hit = np.sin(2 * np.pi * (50 + 80 * np.exp(-(ts - 0.15).clip(0) * 9)) * ts) * np.exp(-(ts - 0.15).clip(0) * 4) * (ts > 0.15)
audio = 0.35 * tone * env + 0.5 * hit
audio = (audio / np.abs(audio).max() * 0.8 * 32767).astype("<i2")
with wave.open(str(TMP / "swell.wav"), "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(audio.tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(TMP / "%04d.png"),
                "-i", str(TMP / "swell.wav"), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", str(OUT)], check=True)
print("wrote", OUT)
