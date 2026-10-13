"""Animated Toon Noon intro (1920x1080, 24 fps, ~6 s) with pop/whoosh sound effects.

The letters reuse the logo geometry from kids-channel/logo-v2/gen.py: rounded
navy T/N strokes and four coloured O rings, the last O a sun disc with a heart.
Writes intro.mp4 next to this file. No music, only sound effects.
"""
import math, os, subprocess, wave
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1920, 1080, 24, 6.0
SS = 2                                         # supersampling for smooth edges
BG = (236, 248, 255)                           # cream, BGR
INK = (68, 42, 31)
CORAL, SUN, TEAL = (91, 107, 255), (60, 194, 255), (168, 181, 31)
FONT = os.path.join(D, "..", "previz", "fonts", "Fredoka-SemiBold.ttf")

S, GAP = 52, 26                                # stroke, gap in logo units (letter height 200)
WID = {"T": 150, "N": 160, "O": 200}
WORD = "TOON NOON"


def layout():
    xs, x = [], 0
    for i, ch in enumerate(WORD):
        if ch == " ":
            x += 90 - GAP
            continue
        xs.append((ch, x, i))
        x += WID[ch] + GAP
    return xs, x - GAP


LETTERS, TOTAL_W = layout()
K = 0.86                                       # logo units -> pixels
OX, OY = (W - TOTAL_W * K) / 2, H * 0.40 - 100 * K


def ease_out_back(t, s=2.2):
    t = min(max(t, 0), 1) - 1
    return 1 + (s + 1) * t ** 3 + s * t ** 2


def ease(t):
    t = min(max(t, 0), 1)
    return t * t * (3 - 2 * t)


def heart_pts(cx, cy, s):
    pts = []
    for a in np.linspace(0, 2 * math.pi, 80):
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * s, cy + y * s))
    return np.int32(pts)


def draw_frame(t):
    img = np.full((H * SS, W * SS, 3), BG, np.uint8)
    o_idx = 0
    for ch, lx, i in LETTERS:
        x0 = (OX + lx * K) * SS
        y0 = OY * SS
        k = K * SS
        if ch == "O":
            start = 0.35 + 0.2 * o_idx
            sc = ease_out_back((t - start) / 0.45)
            col = [CORAL, SUN, TEAL, SUN][o_idx]
            cx, cy = int(x0 + 100 * k), int(y0 + 100 * k)
            if sc > 0.01:
                if o_idx == 3:
                    cv2.circle(img, (cx, cy), int(100 * k * sc), col, -1, cv2.LINE_AA)
                    hs = ease_out_back((t - 2.0) / 0.4)
                    if hs > 0.01:
                        cv2.fillPoly(img, [heart_pts(cx, cy + 4 * k, 2.9 * k * hs)], BG, cv2.LINE_AA)
                else:
                    cv2.circle(img, (cx, cy), int(74 * k * sc), col, int(S * k * sc), cv2.LINE_AA)
            o_idx += 1
        else:
            start = 1.2 + 0.1 * i
            p = ease((t - start) / 0.35)
            if p <= 0:
                continue
            dy = (1 - p) * -120 * SS
            th = int(S * k)
            if ch == "T":
                segs = [((26, 26), (124, 26)), ((75, 26), (75, 174))]
            else:
                segs = [((26, 174), (26, 26)), ((26, 26), (134, 174)), ((134, 174), (134, 26))]
            layer = img.copy()
            for (ax, ay), (bx, by) in segs:
                cv2.line(layer, (int(x0 + ax * k), int(y0 + ay * k + dy)), (int(x0 + bx * k), int(y0 + by * k + dy)),
                         INK, th, cv2.LINE_AA)
            img = cv2.addWeighted(layer, p, img, 1 - p, 0)
    img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
    # tagline
    tp = ease((t - 2.6) / 0.6)
    if tp > 0:
        pil = Image.fromarray(img[..., ::-1])
        dr = ImageDraw.Draw(pil, "RGBA")
        f = ImageFont.truetype(FONT, 76)
        txt = "Little stories, big hearts"
        tw = dr.textlength(txt, font=f)
        dr.text(((W - tw) / 2, H * 0.66 + (1 - tp) * 30), txt, font=f, fill=(31, 42, 68, int(255 * tp)))
        img = np.array(pil)[..., ::-1].copy()
    # gentle zoom and fade-out to white-cream at the end
    z = 1 + 0.03 * ease(t / DUR)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
    img = cv2.warpAffine(img, M, (W, H), borderValue=BG)
    return img


def sfx():
    sr = 44100
    out = np.zeros(int(sr * DUR), np.float32)

    def add(at, sig):
        i = int(at * sr)
        out[i:i + len(sig)] += sig[: len(out) - i]

    for j in range(4):                         # soft pops for the four O's
        n = int(0.16 * sr)
        tt = np.arange(n) / sr
        f = 520 + 90 * j
        add(0.38 + 0.2 * j, 0.35 * np.sin(2 * math.pi * f * tt * (1 - 1.8 * tt)) * np.exp(-tt * 28))
    rng = np.random.default_rng(1)
    n = int(0.6 * sr)                          # whoosh for the letters
    wn = rng.normal(0, 1, n).astype(np.float32)
    wn = np.convolve(wn, np.ones(40) / 40, "same")
    env = np.sin(np.linspace(0, math.pi, n)) ** 2
    add(1.15, 0.5 * wn * env)
    n = int(0.25 * sr)                         # little sparkle for the heart
    tt = np.arange(n) / sr
    add(2.02, 0.22 * (np.sin(2 * math.pi * 1320 * tt) + 0.5 * np.sin(2 * math.pi * 1980 * tt)) * np.exp(-tt * 14))
    out = np.clip(out, -1, 1)
    path = os.path.join(D, "intro_sfx.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())
    return path


def main():
    wav = sfx()
    ff = subprocess.Popen(["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", "-shortest",
                           os.path.join(D, "intro.mp4")], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for i in range(int(DUR * FPS)):
        ff.stdin.write(draw_frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    print("wrote intro.mp4")


if __name__ == "__main__":
    main()
