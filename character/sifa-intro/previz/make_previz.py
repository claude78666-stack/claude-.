#!/usr/bin/env python3
"""Cuts the 45 s preview of the new Sifa video format -> sifa_format_preview.mp4

Run: python3 make_previz.py   (after rendering build/wide and build/face with previz_sifa.py)
  1. cold open: fast gameplay montage, slam-in title, Sifa's hook line
  2. Sifa in her room (Blender stand-in): wave, yes-pump on "first S-I agent", hand gestures,
     chair swivel to the monitor and a push into the screen
  3. gameplay full screen with her facecam bottom left, word-by-word captions, a feature badge
  4. SIFA SI sign-off
Word-by-word yellow captions run throughout, like the reference short.
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT, LONG = HERE.parent, HERE.parent / "longform"
B = HERE / "build"
GFX = B / "gfx"
GFX.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 24
FONT = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
PURPLE, CYAN, RED, YELLOW = (170, 80, 255), (40, 220, 255), (230, 40, 40), (255, 214, 0)
OV = {k: LONG / "official_video" / f"{v}.mp4" for k, v in
      (("GD", "gameplay_demo"), ("GR", "gameplay_reveal_trailer"), ("MP", "multiplayer_trailer"), ("LT", "launch_trailer"))}

A_LEN, B_LEN, C_LEN = 9.8, 13.0, 16.0
D_LEN = 5.0
A0, B0, C0, D0 = 0.0, A_LEN, A_LEN + B_LEN, A_LEN + B_LEN + C_LEN
TOTAL = D0 + D_LEN
VOICE_IN_B, LOOK_IN_B = 1.4, 8.6  # voice.wav and "let's take a look" inside the room shot
MONTAGE = [("GD", 84, 2.0), ("GR", 72, 1.9), ("MP", 36, 1.9), ("GD", 180, 2.0), ("GD", 300, 2.0)]


def run(cmd):
    subprocess.run(cmd, check=True)


def wav_len(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def speech_span(p):
    with wave.open(str(p)) as w:
        x = np.abs(np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(int))
        sr = w.getframerate()
    loud = np.where(x > 800)[0]
    return loud[0] / sr, loud[-1] / sr


def word_times(text, t0, t1):
    """Spread words over the spoken span by length (good enough for a preview)."""
    words = text.split()
    weights = np.array([len(w) + 2 for w in words], float)
    edges = t0 + (t1 - t0) * np.concatenate([[0], np.cumsum(weights) / weights.sum()])
    return list(zip(words, edges[:-1], edges[1:]))


# ---------------------------------------------------------------- caption timeline
hook_text = ("Gears of War: E-Day is finally here, and it might be the best Gears in fifteen years. "
             "Here's everything you need to know before you buy.")
intro_text = "Hi, I'm Sifa, the first S-I agent. Today, we're jumping into Gears of War: E-Day, the brand new prequel"
look_text = "Okay, let's take a look at the gameplay."
move_text = ("Now the part that surprised me most: movement. It still has that heavy roadie run into cover feeling, "
             "but the whole system was rebuilt. For the first time you can properly jump across gaps")
hs, he = speech_span(HERE / "voice" / "hook.wav")
ls, le = speech_span(HERE / "voice" / "look.wav")
ms, me = speech_span(LONG / "build" / "vo_05_movement.wav")
move_cut = 15.4  # seconds of the movement narration used
words = (word_times(hook_text, A0 + 0.3 + hs, A0 + 0.3 + he)
         + word_times(intro_text, B0 + VOICE_IN_B, B0 + VOICE_IN_B + 7.6)
         + word_times(look_text, B0 + LOOK_IN_B + ls, B0 + LOOK_IN_B + le)
         + [w for w in word_times(move_text, C0 + ms, C0 + ms + (me - ms) * 0.6) if w[1] < C0 + move_cut])


def caption_pages(ws, n=4):
    pages, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) == n or w[0][-1] in ".,:!?":
            pages.append(cur)
            cur = []
    return pages + ([cur] if cur else [])


PAGES = caption_pages(words)
cap_font = ImageFont.truetype(FONT.format("Black"), 64)


def draw_caption(d, t):
    for page in PAGES:
        if page[0][1] <= t < page[-1][2] + 0.15:
            cx = 1150 if C0 <= t < D0 else W // 2  # stay clear of the facecam in the gameplay part
            texts = [w[0].upper() for w in page]
            widths = [d.textlength(x + " ", font=cap_font) for x in texts]
            x = cx - sum(widths) / 2
            for (word, a, b), txt, wd in zip(page, texts, widths):
                active = a <= t < b
                col = YELLOW if active else (255, 255, 255)
                d.text((x, 930), txt, font=cap_font, fill=(*col, 255), stroke_width=7, stroke_fill=(0, 0, 0, 255),
                       anchor="ls")
                x += wd
            return


def ease_back(x):  # overshoot "pop"
    x = min(max(x, 0), 1)
    c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


title_big, title_small = ImageFont.truetype(FONT.format("Black"), 150), ImageFont.truetype(FONT.format("Black"), 54)
badge_font = ImageFont.truetype(FONT.format("Black"), 40)
lt_big, lt_small = ImageFont.truetype(FONT.format("Black"), 56), ImageFont.truetype(FONT.format("SemiBold"), 28)
chap_font = ImageFont.truetype(FONT.format("Black"), 30)


def frame(i):
    t = i / FPS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if A0 + 0.9 <= t < A0 + A_LEN - 0.3:  # cold-open title slams in, then sits top-left
        k = ease_back((t - 0.9) / 0.3)
        layer = Image.new("RGBA", (1800, 330), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text((900, 120), "GEARS OF WAR: E-DAY", font=title_big, fill=(255, 255, 255, 255), anchor="mm",
                stroke_width=6, stroke_fill=(0, 0, 0, 255))
        sub = "EVERYTHING YOU NEED TO KNOW"
        half = ld.textlength(sub, font=title_small) / 2 + 30
        ld.rectangle([900 - half, 215, 900 + half, 290], fill=(*RED, 255))
        ld.text((900, 252), sub, font=title_small, fill=(255, 255, 255, 255), anchor="mm")
        s = 1.6 - 0.6 * k
        layer = layer.resize((int(1800 * s), int(330 * s)))
        img.alpha_composite(layer, (int(W / 2 - layer.width / 2), int(420 - layer.height / 2)))
    if B0 + 3.4 <= t < B0 + 7.2:  # lower third
        k = ease_back((t - B0 - 3.4) / 0.35)
        x = int(-700 + 770 * k)
        d.rounded_rectangle([x, 740, x + 600, 870], 14, fill=(8, 6, 18, 215))
        d.rectangle([x, 740, x + 10, 870], fill=(*PURPLE, 255))
        d.text((x + 34, 795), "SIFA", font=lt_big, fill=(255, 255, 255, 255), anchor="ls")
        d.text((x + 34, 840), "THE FIRST SI AGENT", font=lt_small, fill=(*CYAN, 255), anchor="lm")
    if C0 <= t < D0:  # chapter tag, progress bar and the feature badge in the gameplay part
        d.rounded_rectangle([60, 40, 520, 96], 12, fill=(8, 6, 18, 200))
        d.text((84, 68), "06  ALL-NEW MOVEMENT", font=chap_font, fill=(255, 255, 255, 255), anchor="lm")
        d.rectangle([0, 0, int(W * (t - C0) / C_LEN), 8], fill=(*YELLOW, 255))
        if C0 + 6.0 <= t < C0 + 12.5:
            k = ease_back((t - C0 - 6.0) / 0.35)
            badge = Image.new("RGBA", (980, 120), (0, 0, 0, 0))
            bd = ImageDraw.Draw(badge)
            bd.rounded_rectangle([0, 0, 979, 119], 26, fill=(*CYAN, 240))
            bd.text((490, 60), "NEW:  JUMP  •  SLIDE  •  CLIMB  •  CRAWL", font=badge_font, fill=(5, 5, 15, 255), anchor="mm")
            s = max(0.05, k)
            badge = badge.resize((int(980 * s), int(120 * s)))
            img.alpha_composite(badge, (int(1150 - badge.width / 2), int(230 - badge.height / 2)))
    draw_caption(d, t)
    return img


def render_gfx():
    for i in range(int(TOTAL * FPS)):
        p = GFX / f"{i:05d}.png"
        if not p.exists():
            frame(i).save(p)


def base_video():
    vf = f"scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1,format=yuv420p"
    parts = []
    for n, (src, start, length) in enumerate(MONTAGE):  # punch-in on every montage cut
        p = B / f"a{n}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(length), "-i", str(OV[src]),
             "-vf", f"{vf},zoompan=z='1+0.0025*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS}",
             "-an", "-c:v", "libx264", "-crf", "17", str(p)])
        parts.append(p)
    # Sifa's room; the last 0.7 s pushes into the monitor
    n_b = int(B_LEN * FPS)
    push0 = n_b - 17
    p = B / "b.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS // 2), "-pattern_type", "glob", "-i", str(B / "wide" / "wide_*.png"),
         "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos,zoompan=z='if(gte(on,{push0}),1+(on-{push0})*0.16,1)':"
                f"x='if(gte(on,{push0}),1420-iw/zoom/2,iw/2-iw/zoom/2)':y='if(gte(on,{push0}),430-ih/zoom/2,ih/2-ih/zoom/2)'"
                f":d=1:s={W}x{H}:fps={FPS},format=yuv420p", "-frames:v", str(n_b), "-c:v", "libx264", "-crf", "17", str(p)])
    parts.append(p)
    # gameplay with the facecam bottom left
    fa = LONG / "build"
    p = B / "c.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-ss", "84", "-t", str(C_LEN), "-i", str(OV["GD"]),
         "-stream_loop", "-1", "-framerate", str(FPS // 2), "-pattern_type", "glob", "-i", str(B / "face" / "face_*.png"),
         "-loop", "1", "-i", str(fa / "face_mask.png"), "-loop", "1", "-i", str(fa / "face_frame.png"),
         "-loop", "1", "-i", str(fa / "face_tag.png"),
         "-filter_complex", f"[0:v]{vf}[g];[1:v]fps={FPS},scale=360:360,format=rgba[fc];[2:v]format=gray[m];[fc][m]alphamerge[f];"
                            f"[g][f]overlay=60:{H - 430}:shortest=1[s1];[s1][3:v]overlay=48:{H - 442}[s2];"
                            f"[s2][4:v]overlay=76:{H - 494},format=yuv420p[v]",
         "-map", "[v]", "-t", str(C_LEN), "-an", "-c:v", "libx264", "-crf", "17", str(p)])
    parts.append(p)
    p = B / "d.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "sifa_si_outro.mp4"), "-vf", vf, "-an", "-t", str(D_LEN),
         "-c:v", "libx264", "-crf", "17", str(p)])
    parts.append(p)
    (B / "parts.txt").write_text("".join(f"file '{x}'\n" for x in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(B / "parts.txt"), "-c", "copy",
         str(B / "base.mp4")])


def whoosh(path, dur=0.6):
    sr = 48000
    t = np.arange(int(dur * sr)) / sr
    n = np.random.default_rng(1).standard_normal(len(t))
    env = np.sin(np.pi * t / dur) ** 2
    sig = np.convolve(n, np.ones(8) / 8, "same") * env * 0.5
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((sig / np.abs(sig).max() * 0.6 * 32767).astype("<i2").tobytes())


def audio_and_final():
    whoosh(B / "whoosh.wav")
    cut_times = [A0 + sum(m[2] for m in MONTAGE[:k]) for k in range(1, len(MONTAGE))] + [B0, C0 - 0.6, D0]
    inputs = ["-i", str(B / "base.mp4"), "-framerate", str(FPS), "-i", str(B / "gfx" / "%05d.png"),
              "-i", str(HERE / "voice" / "hook.wav"), "-i", str(ROOT / "voice.wav"), "-i", str(HERE / "voice" / "look.wav"),
              "-i", str(LONG / "build" / "vo_05_movement.wav"), "-i", str(LONG / "build" / "music_bed.wav"),
              "-ss", "84", "-t", str(C_LEN), "-i", str(OV["GD"]), "-i", str(ROOT / "sifa_si_outro.mp4"),
              "-i", str(B / "whoosh.wav")]
    ms_ = lambda s: int(s * 1000)
    a = [
        f"[2:a]adelay={ms_(A0 + 0.3)}|{ms_(A0 + 0.3)}[hook]",
        f"[3:a]atrim=0:7.6,afade=t=out:st=7.2:d=0.4,adelay={ms_(B0 + VOICE_IN_B)}|{ms_(B0 + VOICE_IN_B)}[intro]",
        f"[4:a]adelay={ms_(B0 + LOOK_IN_B)}|{ms_(B0 + LOOK_IN_B)}[look]",
        f"[5:a]atrim=0:{C_LEN - 0.2},afade=t=out:st={C_LEN - 0.9}:d=0.7,adelay={ms_(C0)}|{ms_(C0)}[move]",
        "[hook][intro][look][move]amix=inputs=4:normalize=0,aresample=48000,aformat=channel_layouts=stereo,"
        f"apad,atrim=0:{TOTAL},asplit=2[vox][key]",
        f"[6:a]atrim=0:{D0},volume=0.5,afade=t=out:st={D0 - 1}:d=1,aformat=channel_layouts=stereo[mus]",
        f"[7:a]volume=0.55,adelay={ms_(C0)}|{ms_(C0)},aformat=channel_layouts=stereo[game]",
        f"[8:a]adelay={ms_(D0)}|{ms_(D0)},aformat=channel_layouts=stereo[out]",
        "[mus][game]amix=inputs=2:normalize=0[bed]",
        "[bed][key]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=400[duck]",
    ]
    for k, ct in enumerate(cut_times):
        a.append(f"[9:a]adelay={ms_(max(0, ct - 0.25))}|{ms_(max(0, ct - 0.25))},volume=0.6[w{k}]")
    a.append("[duck][vox][out]" + "".join(f"[w{k}]" for k in range(len(cut_times)))
             + f"amix=inputs={3 + len(cut_times)}:normalize=0,atrim=0:{TOTAL},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    v = f"[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join([v] + a), "-map", "[v]", "-map", "[a]",
         "-t", str(TOTAL), "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(HERE / "sifa_format_preview.mp4")])
    print("wrote", HERE / "sifa_format_preview.mp4", f"{TOTAL:.1f}s")


render_gfx()
base_video()
audio_and_final()
