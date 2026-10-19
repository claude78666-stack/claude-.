#!/usr/bin/env python3
"""Builds the 8-9 minute Gears of War: E-Day explainer -> sifa_eday_explainer_1080p.mp4

Run: python3 render_longform.py [section_id ...]   (no ids = every section, then the full cut)
Needs, per section in script.json: voice/<id>.wav (make_voice.py). Optional: gameplay/<id>.mp4 is used as
the scene background instead of the drawn skyline, so real gameplay can be dropped in later.
Sifa's facecam is lip-synced to the narration with Wav2Lip (WAV2LIP env var = path to a Wav2Lip checkout
with checkpoints/wav2lip_gan.pth). The intro is ../sifa_intro_full_1080p.mp4 if it exists, else
../sifa_intro_ai_1080p.mp4.
"""
import json
import math
import os
import random
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
INTRO_DIR = HERE.parent
BUILD = HERE / "build"
OUT = HERE / "sifa_eday_explainer_1080p.mp4"
W, H, FPS = 1920, 1080, 24
FONT = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
PURPLE, CYAN, EMBER = (170, 80, 255), (40, 220, 255), (255, 120, 40)
STING, LEAD, TAIL = 1.4, 1.3, 0.9  # title sting length, narration start, hold after narration
FACE = 520                          # facecam size
WAV2LIP = Path(os.environ.get("WAV2LIP", "/tmp/Wav2Lip"))

script = json.load(open(HERE / "script.json"))
SECTIONS = script["sections"]
BUILD.mkdir(exist_ok=True)


def font(weight, size):
    return ImageFont.truetype(FONT.format(weight), size)


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def wav_seconds(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


# ---------- shared assets ----------
def skyline(path, tint, seed):
    """Dark war-torn industrial skyline with a burning horizon, slightly larger than the frame for drift."""
    rnd = random.Random(seed)
    bw, bh = W + 120, H + 68
    y = np.linspace(0, 1, bh)[:, None, None]
    sky = np.zeros((bh, bw, 3))
    top, mid = np.array((8, 6, 20)), np.array(tint) * 0.35
    glow = np.array(EMBER) * 0.6
    sky += top * (1 - y) + mid * y
    sky += glow * 1.3 * np.exp(-((y - 0.5) / 0.16) ** 2)
    img = Image.fromarray(np.clip(sky, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(img)
    for layer, (base, shade) in enumerate(((0.62, 34), (0.70, 20), (0.78, 9))):
        x = -40
        while x < bw:
            w = rnd.randint(40, 160)
            h = rnd.randint(60, 380) * (1.2 - layer * 0.25)
            top_y = bh * base - h
            d.rectangle([x, top_y, x + w, bh], fill=(shade, shade - 2 if shade > 2 else 0, shade + 6))
            if rnd.random() < 0.25:  # chimney / crane
                d.rectangle([x + w // 3, top_y - rnd.randint(40, 160), x + w // 3 + 10, top_y], fill=(shade,) * 3)
            if layer == 0:
                for _ in range(rnd.randint(0, 6)):  # lit windows
                    wx, wy = x + rnd.randint(6, max(7, w - 10)), top_y + rnd.randint(10, int(h))
                    d.rectangle([wx, wy, wx + 4, wy + 6], fill=(255, 170, 80))
            x += w + rnd.randint(-10, 20)
    smoke = Image.new("L", (bw, bh), 0)
    sd = ImageDraw.Draw(smoke)
    for _ in range(18):
        cx, cy, r = rnd.randint(0, bw), rnd.randint(int(bh * 0.2), int(bh * 0.6)), rnd.randint(120, 380)
        sd.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], fill=rnd.randint(30, 70))
    smoke = smoke.filter(ImageFilter.GaussianBlur(60))
    img = Image.composite(Image.new("RGB", (bw, bh), (40, 34, 48)), img, smoke)
    vignette = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(vignette).ellipse([-bw * 0.2, -bh * 0.3, bw * 1.2, bh * 1.3], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(img, Image.new("RGB", (bw, bh), (0, 0, 0)), vignette)
    # darken the left side so the cards read well
    shade = Image.linear_gradient("L").rotate(90).resize((bw, bh))
    img = Image.composite(img, Image.new("RGB", (bw, bh), (4, 3, 10)), shade.point(lambda v: 140 + v * 115 // 255))
    img.save(path)


def embers(path, seconds=8):
    """Looping drifting embers on black, blended over every scene with 'screen'."""
    if path.exists():
        return
    rng = np.random.default_rng(3)
    n = 140
    x, y = rng.uniform(0, W, n), rng.uniform(0, H, n)
    vx, vy = rng.uniform(-12, 18, n), rng.uniform(-60, -20, n)
    size, phase = rng.uniform(1.5, 4.5, n), rng.uniform(0, 2 * math.pi, n)
    frames = BUILD / "embers"
    frames.mkdir(exist_ok=True)
    total = seconds * FPS
    for f in range(total):
        t = f / FPS
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        px = (x + vx * t + 20 * np.sin(t + phase)) % W
        py = (y + vy * t) % H
        for i in range(n):
            a = 0.5 + 0.5 * math.sin(2 * math.pi * f / total * 2 + phase[i])  # loops cleanly
            c = tuple(int(v * a) for v in EMBER)
            r = size[i]
            d.ellipse([px[i] - r, py[i] - r, px[i] + r, py[i] + r], fill=c)
        img.filter(ImageFilter.GaussianBlur(1.2)).save(frames / f"{f:04d}.png")
    run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(frames / "%04d.png"),
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", str(path)])


def face_assets():
    """Rounded mask and neon frame for the facecam."""
    mask = Image.new("L", (FACE, FACE), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, FACE - 1, FACE - 1], 36, fill=255)
    mask.save(BUILD / "face_mask.png")
    frame = Image.new("RGBA", (FACE + 24, FACE + 24), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    for i, a in enumerate((40, 80, 255)):
        fd.rounded_rectangle([8 - i * 3 + 6, 8 - i * 3 + 6, FACE + 16 + i * 3 - 6, FACE + 16 + i * 3 - 6],
                             42, outline=(*PURPLE, a), width=3)
    frame = frame.filter(ImageFilter.GaussianBlur(1))
    ImageDraw.Draw(frame).rounded_rectangle([10, 10, FACE + 13, FACE + 13], 38, outline=(*CYAN, 255), width=3)
    frame.save(BUILD / "face_frame.png")
    tag = Image.new("RGBA", (220, 48), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rounded_rectangle([0, 0, 219, 47], 12, fill=(8, 6, 18, 210))
    td.ellipse([16, 17, 30, 31], fill=(255, 60, 60, 255))
    td.text((42, 9), "SIFA  LIVE", font=font("Bold", 24), fill=(255, 255, 255, 255))
    tag.save(BUILD / "face_tag.png")
    mark = Image.new("RGBA", (300, 70), (0, 0, 0, 0))
    md = ImageDraw.Draw(mark)
    md.text((0, 4), "SIFA", font=font("Black", 44), fill=(*PURPLE, 235))
    md.text((126, 18), "SI", font=font("Bold", 26), fill=(*CYAN, 235))
    mark.save(BUILD / "watermark.png")


# ---------- per-section layers ----------
def card_png(path, text, n):
    img = Image.new("RGBA", (980, 92), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 979, 91], 14, fill=(10, 8, 24, 200))
    d.rounded_rectangle([0, 0, 9, 91], 4, fill=(*(CYAN if n % 2 else PURPLE), 255))
    f = font("SemiBold", 38)
    while d.textlength(text, font=f) > 920 and f.size > 24:
        f = font("SemiBold", f.size - 2)
    d.text((36, 46), text, font=f, fill=(255, 255, 255, 255), anchor="lm")
    img.save(path)


def heading_png(path, num, text):
    img = Image.new("RGBA", (1100, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((0, 0), f"{num:02d}", font=font("Black", 40), fill=(*CYAN, 255))
    d.text((0, 46), text.upper(), font=font("Black", 76), fill=(255, 255, 255, 255))
    d.rectangle([0, 140, 120, 146], fill=(*PURPLE, 255))
    img.save(path)


def sting_png(path, num, text):
    img = Image.new("RGBA", (W, H), (4, 3, 12, 235))
    d = ImageDraw.Draw(img)
    d.text((W // 2, H // 2 - 90), f"{num:02d}", font=font("Black", 72), fill=(*CYAN, 255), anchor="mm")
    d.text((W // 2, H // 2 + 10), text.upper(), font=font("Black", 110), fill=(255, 255, 255, 255), anchor="mm")
    d.rectangle([W // 2 - 90, H // 2 + 92, W // 2 + 90, H // 2 + 100], fill=(*PURPLE, 255))
    img.save(path)


def card_times(section, dur):
    """When each card appears: where its first words are spoken, kept in order and at least 1.2 s apart."""
    text = section["text"].lower()
    times, last = [], LEAD
    n = len(section["cards"])
    for i, card in enumerate(section["cards"]):
        words = [w.strip(".,:+|-").lower() for w in card.split() if len(w.strip(".,:+|-")) > 3]
        pos = next((text.find(w) for w in words if text.find(w) >= 0), -1)
        even = LEAD + 0.5 + (i + 0.5) * (dur - 1.5) / n
        t = LEAD + pos / len(text) * dur if pos >= 0 else even
        t = min(max(t, last + 1.2), LEAD + dur - 0.5)
        times.append(round(t, 2))
        last = t
    return times


def lipsync(section, voice):
    out = BUILD / f"face_{section['id']}.mp4"
    if out.exists():
        return out
    run([sys.executable, "inference.py", "--checkpoint_path", "checkpoints/wav2lip_gan.pth",
         "--face", str(HERE / "facecam_src.png"), "--audio", str(voice), "--outfile", str(out),
         "--static", "True", "--fps", str(FPS), "--pads", "0", "15", "0", "0"],
        cwd=WAV2LIP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


def render_section(num, section):
    sid = section["id"]
    voice = HERE / "voice" / f"{sid}.wav"
    dur = wav_seconds(voice)
    total = LEAD + dur + TAIL
    face = lipsync(section, voice)
    bg = BUILD / f"bg_{sid}.png"
    skyline(bg, PURPLE if num % 2 else CYAN, num)
    heading_png(BUILD / f"head_{sid}.png", num, section["heading"])
    sting_png(BUILD / f"sting_{sid}.png", num, section["heading"])
    times = card_times(section, dur)
    for i, c in enumerate(section["cards"]):
        card_png(BUILD / f"card_{sid}_{i}.png", c, i)

    gameplay = HERE / "gameplay" / f"{sid}.mp4"
    if gameplay.exists():
        inputs = ["-stream_loop", "-1", "-i", str(gameplay)]
        chain = [f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
                 "eq=brightness=-0.12:saturation=0.9,format=gbrp[bg]"]
    else:
        inputs = ["-loop", "1", "-i", str(bg)]
        chain = [f"[0:v]fps={FPS},crop={W}:{H}:x='60+55*sin(t/11)':y='34+30*cos(t/13)',format=gbrp[bg]"]
    inputs += ["-stream_loop", "-1", "-i", str(BUILD / "embers.mp4"),
               "-i", str(face), "-loop", "1", "-i", str(BUILD / "face_mask.png"),
               "-loop", "1", "-i", str(BUILD / "face_frame.png"), "-loop", "1", "-i", str(BUILD / "face_tag.png"),
               "-loop", "1", "-i", str(BUILD / "watermark.png"),
               "-loop", "1", "-i", str(BUILD / f"head_{sid}.png"), "-loop", "1", "-i", str(BUILD / f"sting_{sid}.png")]
    first_card = 9
    for i in range(len(section["cards"])):
        inputs += ["-loop", "1", "-i", str(BUILD / f"card_{sid}_{i}.png")]
    voice_in = first_card + len(section["cards"])
    inputs += ["-i", str(voice)]

    fx, fy = W - FACE - 90, H - FACE - 110
    chain += [
        "[1:v]format=gbrp[emb]",
        "[bg][emb]blend=all_mode=screen,format=yuva420p[s0]",
        # facecam: lip-synced still, gently breathing, starts with the narration
        f"[2:v]scale={FACE + 16}:{FACE + 16},crop={FACE}:{FACE}:x='8+6*sin(t*0.9)':y='8+5*sin(t*0.6)',"
        f"tpad=start_duration={LEAD}:start_mode=clone:stop_mode=clone:stop_duration={TAIL + 1},format=rgba[fc]",
        "[3:v]format=gray[fm]",
        "[fc][fm]alphamerge,fade=t=in:st=0.9:d=0.4:alpha=1[fcm]",
        f"[s0][fcm]overlay={fx}:{fy}:shortest=0[s1]",
        f"[4:v]format=rgba,fade=t=in:st=0.9:d=0.4:alpha=1[ff]",
        f"[s1][ff]overlay={fx - 12}:{fy - 12}[s2]",
        f"[5:v]format=rgba,fade=t=in:st=1.0:d=0.4:alpha=1[ft]",
        f"[s2][ft]overlay={fx + 16}:{fy - 64}[s3]",
        f"[s3][6:v]overlay=60:40[s4]",
        f"[7:v]format=rgba,fade=t=in:st={STING - 0.2}:d=0.4:alpha=1[hd]",
        f"[s4][hd]overlay=x='if(lt(t,{STING - 0.2}),-1200,min(110,110-600*({STING + 0.15}-t)))':y=150[s5]",
    ]
    last = "[s5]"
    for i, t0 in enumerate(times):
        k = first_card + i
        chain.append(f"[{k}:v]format=rgba,fade=t=in:st={t0}:d=0.35:alpha=1[c{i}]")
        chain.append(f"{last}[c{i}]overlay=x='if(lt(t,{t0}),-1100,min(110,110-1800*({t0 + 0.35}-t)))':"
                     f"y={340 + i * 118}[v{i}]")
        last = f"[v{i}]"
    chain += [
        f"[8:v]format=rgba,fade=t=out:st={STING - 0.35}:d=0.35:alpha=1[st]",
        f"{last}[st]overlay=0:0:enable='lt(t,{STING})',fade=t=in:st=0:d=0.25,"
        f"fade=t=out:st={total - 0.25}:d=0.25,format=yuv420p[vout]",
        f"[{voice_in}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},"
        f"apad,atrim=0:{total}[aout]",
    ]
    out = BUILD / f"section_{sid}.mp4"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain),
         "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}", "-r", str(FPS),
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "pcm_s16le", str(out)])
    print("section", sid, f"{total:.1f}s", flush=True)
    return out


def end_card():
    out = BUILD / "endcard.mp4"
    img = Image.open(BUILD / f"bg_{SECTIONS[-1]['id']}.png").crop((60, 34, 60 + W, 34 + H)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.text((W // 2, 380), "THANKS FOR WATCHING", font=font("Black", 96), fill=(255, 255, 255, 255), anchor="mm")
    d.text((W // 2, 480), "Next: the full Gears of War: E-Day campaign with Sifa", font=font("SemiBold", 40),
           fill=(*CYAN, 255), anchor="mm")
    d.rounded_rectangle([W // 2 - 220, 590, W // 2 + 220, 690], 22, fill=(230, 30, 50, 255))
    d.text((W // 2, 640), "SUBSCRIBE", font=font("Black", 54), fill=(255, 255, 255, 255), anchor="mm")
    img.convert("RGB").save(BUILD / "endcard.png")
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(BUILD / "endcard.png"),
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "6",
         "-vf", f"fps={FPS},fade=t=in:st=0:d=0.4,fade=t=out:st=5.2:d=0.8,format=yuv420p",
         "-c:v", "libx264", "-crf", "18", "-c:a", "pcm_s16le", str(out)])
    return out


def normalise(src, out):
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src),
         "-vf", f"scale={W}:{H},fps={FPS},setsar=1,format=yuv420p",
         "-af", "aresample=48000,aformat=channel_layouts=stereo",
         "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "pcm_s16le", str(out)])
    return out


def main():
    wanted = set(sys.argv[1:])
    embers(BUILD / "embers.mp4")
    face_assets()
    parts = []
    for num, s in enumerate(SECTIONS, 1):
        if wanted and s["id"] not in wanted:
            continue
        parts.append(render_section(num, s))
    if wanted:
        return
    intro = INTRO_DIR / "sifa_intro_full_1080p.mp4"
    intro = intro if intro.exists() else INTRO_DIR / "sifa_intro_ai_1080p.mp4"
    parts = [normalise(intro, BUILD / "intro.mp4"), *parts, end_card()]
    (BUILD / "parts.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(BUILD / "parts.txt"),
         "-c", "copy", str(BUILD / "joined.mov")])
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                  str(BUILD / "joined.mov")], capture_output=True, text=True).stdout)
    intro_len = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                      "csv=p=0", str(BUILD / "intro.mp4")], capture_output=True, text=True).stdout)
    music = BUILD / "music_bed.wav"
    run([sys.executable, str(HERE / "make_bed.py"), str(music), f"{total - intro_len:.2f}"])
    # music bed starts after the intro (which has its own music) and ducks under Sifa's voice
    ms = int(intro_len * 1000)
    chain = (f"[0:a]asplit=2[mix][key];[1:a]volume=0.32,adelay={ms}|{ms},apad[mus];"
             "[mus][key]sidechaincompress=threshold=0.025:ratio=10:attack=15:release=400[duck];"
             f"[mix][duck]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,"
             "aresample=48000[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(BUILD / "joined.mov"), "-i", str(music),
         "-filter_complex", chain, "-map", "0:v", "-map", "[a]",
         "-c:v", "libx264", "-crf", "19", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-c:a", "aac", "-b:a", "192k", str(OUT)])
    print("wrote", OUT, f"{total / 60:.1f} min")


if __name__ == "__main__":
    main()
