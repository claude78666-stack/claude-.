#!/usr/bin/env python3
"""Explainer v2: the more engaging cut -> sifa_eday_explainer_v2_1080p.mp4

Run: WAV2LIP=/path/to/Wav2Lip python3 render_v2.py [section_id ...]
Builds on render_longform.py (same script, narration and gameplay cuts) and changes the presentation:
  - cold open: fast gameplay montage, slam-in title and Sifa's hook line, before the talking intro
  - Sifa is cut out of her room (sifa_cutout.png, no wallpaper) and sits over the gameplay bottom left,
    waist-up, lip-synced, with a faint soft shadow, like a streamer
  - every section opens with a slanted chapter wipe; a chapter tag and progress bar stay on screen
  - facts pop in as badges with a punch-in zoom on the gameplay and a pop sound
  - word-by-word yellow captions follow her voice, pauses included
  - subscribe reminders that get "clicked"
"""
import difflib
import json
import math
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import render_longform as v1
import sifa_gestures
import sifa_motion

HERE, BUILD, ROOT = v1.HERE, v1.BUILD / "v2", v1.INTRO_DIR
BUILD.mkdir(parents=True, exist_ok=True)
W, H, FPS, LEAD, TAIL = v1.W, v1.H, v1.FPS, v1.LEAD, v1.TAIL
PURPLE, CYAN, RED, YELLOW = (170, 80, 255), (40, 220, 255), (230, 40, 40), (255, 214, 0)
OUT = HERE / "sifa_eday_explainer_v2_1080p.mp4"
MASTER = BUILD / "sifa_eday_explainer_v2_master.mp4"   # full quality, not in git
CUT_H = 470                     # cut-out Sifa height on screen
CUT_SRC = HERE / "sifa_cutout.png"
SUBSCRIBE_IN = {"05_movement", "12b_tips"}
font = v1.font
F_CAP, F_BADGE, F_TAG = font("Black", 62), font("Black", 40), font("Black", 30)
F_BIG, F_SMALL = font("Black", 130), font("Black", 54)


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def ease_back(x):
    x = min(max(x, 0.0), 1.0)
    return 1 + 2.7 * (x - 1) ** 3 + 1.7 * (x - 1) ** 2


# ---------------------------------------------------------------- Sifa cut-out
def clean_matte(a):
    """Keep only Sifa (largest blob: no specks or chair bits), tighten the hair fringe a little, and fade her
    out over the bottom so there's no hard crop line across her arms."""
    from scipy import ndimage
    m = np.asarray(a).astype(float) / 255
    lab, n = ndimage.label(m > 0.35)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(m), lab, range(1, n + 1))
        keep = ndimage.binary_dilation(lab == 1 + int(np.argmax(sizes)), iterations=3)
        m = m * keep
    m = ndimage.grey_erosion(m, size=(3, 3))
    m = ndimage.gaussian_filter(m, 1.2)
    h = m.shape[0]
    fade = np.clip((h - 1 - np.arange(h)) / 120.0, 0, 1) ** 1.5
    m = m * fade[:, None]
    return Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), "L")


def cutout_assets():
    """RGB still for Wav2Lip, the alpha mask, and the glow/shadow layer (all static: only her mouth moves)."""
    rgba = Image.open(CUT_SRC).convert("RGBA")
    rgb, alpha = BUILD / "cut_rgb.png", BUILD / "cut_alpha.png"
    bg = Image.new("RGB", rgba.size, (20, 16, 30))
    bg.paste(rgba, mask=rgba.split()[3])
    Image.open(ROOT / "ai" / "shot1_last_1080.png").convert("RGB").crop((680, 150, 1380, 790)).save(rgb)
    a = clean_matte(rgba.split()[3])
    a.save(alpha)
    layer = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    shadow = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    # no coloured glow, just a faint soft shadow so she sits on the footage naturally
    shadow.putalpha(a.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.35)))
    layer.alpha_composite(shadow, (10, 6))
    layer.save(BUILD / "cut_glow.png")
    return rgb, alpha


def lipsync(sid, voice, face_src):
    moving = Path(face_src).suffix == ".mp4"
    kind = "gest_" if Path(face_src).name.startswith("track_") else "live_" if moving else ""
    out = BUILD / f"face_{kind}{sid}.mp4"
    if not out.exists():
        run([sys.executable, "inference.py", "--checkpoint_path", "checkpoints/wav2lip_gan.pth",
             "--face", str(face_src), "--audio", str(voice), "--outfile", str(out),
             # Wav2Lip parses --static with type=bool, so any value (even "False") means static: only pass it for stills
             *([] if moving else ["--static", "True"]), "--fps", str(FPS), "--pads", "0", "15", "0", "0"],
            cwd=v1.WAV2LIP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


# ---------------------------------------------------------------- captions
def speech_segments(path, gap=0.22):
    with wave.open(str(path)) as w:
        sr = w.getframerate()
        x = np.abs(np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(float))
    win = sr // 50
    env = np.convolve(x, np.ones(win) / win, "same") > 450
    segs, start, quiet = [], None, 0
    for i in range(0, len(env), win):
        if env[i]:
            if start is None:
                start = i
            quiet = 0
        elif start is not None:
            quiet += win
            if quiet > gap * sr:
                segs.append((start / sr, (i - quiet) / sr))
                start, quiet = None, 0
    if start is not None:
        segs.append((start / sr, len(env) / sr))
    return segs


def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen " \
       "seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def spoken(tok):
    """Whisper writes numbers as digits ("9", ".5", "90", "%", "80s", "360"); the script spells them out."""
    t = tok.lower().rstrip(",.!?;:")
    if t == ".5":
        return ["and", "a", "half"]
    t = t.lstrip(".")
    if t == "%":
        return ["percent"]
    plural = t.endswith("s") and t[:-1].isdigit()
    t = t.rstrip("s") if plural else t
    if not t.isdigit():
        return [tok]
    n, out = int(t), []
    if n >= 1000:                          # years: "2026" is said "twenty twenty-six"
        return spoken(str(n // 100)) + spoken(f"{n % 100}{'s' if plural else ''}")
    if n >= 100:
        out, n = [ONES[n // 100]], n % 100   # "360" is said "three sixty"
    if n >= 20:
        out += [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])
    elif n or not out:
        out.append(ONES[n])
    if plural:
        out[-1] = out[-1][:-1] + "ies" if out[-1].endswith("y") else out[-1] + "s"
    return out


def whisper_words(voice):
    """Word timestamps of what she actually says (faster-whisper, local, cached next to the build)."""
    cache = BUILD / f"align_{Path(voice).stem}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    from faster_whisper import WhisperModel
    audio = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(voice), "-ac", "1", "-ar", "16000",
                                          "-f", "s16le", "-"], capture_output=True, check=True).stdout, "<i2")
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(audio.astype(np.float32) / 32768, word_timestamps=True)
    words = [(w.word.strip(), w.start, w.end) for seg in segs for w in seg.words]
    cache.write_text(json.dumps(words))
    return words


def word_times(text, voice, offset):
    """Script words timed by forced alignment to the transcript; words whisper heard differently
    (numbers, names) are spread between their aligned neighbours."""
    words = text.split()
    heard = []
    for w, a, b in whisper_words(voice):
        parts = spoken(w)
        step = (b - a) / len(parts)
        heard += [(p, a + step * k, a + step * (k + 1)) for k, p in enumerate(parts)]
    sm = difflib.SequenceMatcher(None, [_norm(w) for w in words], [_norm(h[0]) for h in heard], autojunk=False)
    t = [None] * len(words)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            t[a + k] = (heard[b + k][1], heard[b + k][2])
    if not any(t):
        return word_times_even(text, voice, offset)
    end = heard[-1][2]
    i = 0
    while i < len(words):
        if t[i] is None:
            j = i
            while j < len(words) and t[j] is None:
                j += 1
            a = t[i - 1][1] if i else 0.0
            b = t[j][0] if j < len(words) else end
            step = (b - a) / (j - i)
            for k in range(i, j):
                t[k] = (a + step * (k - i), a + step * (k - i + 1))
            i = j
        i += 1
    return [(w, offset + a, offset + b) for w, (a, b) in zip(words, t)]


def word_times_even(text, voice, offset):
    """Fallback: spread the words over the spoken time only (pauses skipped), weighted by word length."""
    segs = speech_segments(voice)
    total = sum(b - a for a, b in segs)
    words = text.split()
    weights = np.array([len(w) + 1.5 for w in words])
    cum = np.concatenate([[0], np.cumsum(weights)]) / weights.sum() * total

    def to_time(s):
        for a, b in segs:
            if s <= b - a:
                return a + s
            s -= b - a
        return segs[-1][1]
    return [(w, offset + to_time(cum[i]), offset + to_time(cum[i + 1])) for i, w in enumerate(words)]


def pages(words, n=4):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == n or w[0][-1] in ".,:!?;":
            out.append(cur)
            cur = []
    return out + ([cur] if cur else [])


def draw_caption(d, t, cap_pages, cx=1180, y=965):
    for page in cap_pages:
        if page[0][1] <= t < page[-1][2] + 0.12:
            texts = [w[0].upper() for w in page]
            widths = [d.textlength(x + " ", font=F_CAP) for x in texts]
            x = cx - sum(widths) / 2
            for (word, a, b), txt, wd in zip(page, texts, widths):
                col = YELLOW if a <= t < b else (255, 255, 255)
                d.text((x, y), txt, font=F_CAP, fill=(*col, 255), stroke_width=7, stroke_fill=(0, 0, 0, 255), anchor="ls")
                x += wd
            return


# ---------------------------------------------------------------- per-section motion graphics
def section_gfx(num, section, total, fact_times, cap_pages):
    out = BUILD / f"gfx_{section['id']}"
    out.mkdir(exist_ok=True)
    n = int(round(total * FPS))
    if len(list(out.glob("*.png"))) == n:
        return out
    heading = section["heading"].upper()
    sub_at = total * 0.6 if section["id"] in SUBSCRIBE_IN else None
    for i in range(n):
        t = i / FPS
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # slanted panel wipe with the chapter title
        if t < 1.45:
            if t < 0.35:
                off = -W - 500 + (W + 500) * ease_back(t / 0.35)
            elif t < 0.95:
                off = 0
            else:
                off = (W + 600) * ((t - 0.95) / 0.5) ** 2
            for k, col in enumerate((PURPLE, RED)):
                x0 = off - k * 60
                d.polygon([(x0 - 300, 0), (x0 + W + 300, 0), (x0 + W, H), (x0 - 600, H)], fill=(*col, 255))
            if 0.3 < t < 1.0:
                d.text((W // 2 + off, H // 2 - 100), f"{num:02d}", font=F_SMALL, fill=(*YELLOW, 255), anchor="mm")
                d.text((W // 2 + off, H // 2 + 10), heading, font=F_BIG, fill=(255, 255, 255, 255), anchor="mm",
                       stroke_width=6, stroke_fill=(0, 0, 0, 255))
        if t >= 1.2:
            # chapter tag + progress bar
            tw = d.textlength(f"{num:02d}  {heading}", font=F_TAG) + 50
            d.rounded_rectangle([50, 36, 50 + tw, 90], 12, fill=(8, 6, 18, 205))
            d.text((75, 63), f"{num:02d}  {heading}", font=F_TAG, fill=(255, 255, 255, 255), anchor="lm")
            d.rectangle([0, 0, int(W * t / total), 7], fill=(*YELLOW, 255))
            # name tag above Sifa
            d.rounded_rectangle([150, H - CUT_H - 6, 345, H - CUT_H + 36], 10, fill=(8, 6, 18, 215))
            d.ellipse([166, H - CUT_H + 8, 180, H - CUT_H + 22], fill=(255, 60, 60, 255))
            d.text((192, H - CUT_H + 15), "SIFA  LIVE", font=F_TAG, fill=(255, 255, 255, 255), anchor="lm")
        # fact badge: pops in, holds until the next fact
        for k, t0 in enumerate(fact_times):
            t1 = min(fact_times[k + 1] if k + 1 < len(fact_times) else total, t0 + 6.0, total - 0.3)
            if t0 <= t < t1:
                s = ease_back((t - t0) / 0.3) * (1 if t < t1 - 0.25 else max(0.0, (t1 - t) / 0.25))
                text = section["cards"][k].upper()
                bw = int(d.textlength(text, font=F_BADGE) + 70)
                badge = Image.new("RGBA", (bw + 14, 98), (0, 0, 0, 0))
                bd = ImageDraw.Draw(badge)
                bd.rounded_rectangle([0, 0, bw, 90], 22, fill=(*(CYAN if k % 2 else YELLOW), 245))
                bd.text((bw // 2, 46), text, font=F_BADGE, fill=(8, 8, 16, 255), anchor="mm")
                if s > 0.05:
                    badge = badge.resize((max(1, int(badge.width * s)), max(1, int(badge.height * s))))
                    img.alpha_composite(badge, (60, 118))
        # subscribe reminder, gets "clicked"
        if sub_at and sub_at <= t < sub_at + 3.0:
            k = ease_back((t - sub_at) / 0.35)
            clicked = t >= sub_at + 1.2
            x = int(W + 20 - 470 * k)
            d.rounded_rectangle([x, 270, x + 420, 350], 40, fill=((90, 90, 100, 245) if clicked else (*RED, 255)))
            d.text((x + 210, 310), "SUBSCRIBED" if clicked else "SUBSCRIBE", font=F_BADGE,
                   fill=(255, 255, 255, 255), anchor="mm")
            if sub_at + 0.7 <= t < sub_at + 1.7:
                ck = min(1, (t - sub_at - 0.7) / 0.5)
                px, py = int(x + 330 + 160 * (1 - ck)), int(330 + 120 * (1 - ck))
                d.polygon([(px, py), (px, py + 44), (px + 12, py + 33), (px + 22, py + 52), (px + 30, py + 48),
                           (px + 20, py + 30), (px + 36, py + 30)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        draw_caption(d, t, cap_pages)
        img.save(out / f"{i:05d}.png", compress_level=1)
    return out


# ---------------------------------------------------------------- sound effects
def sfx():
    sr = 48000
    rng = np.random.default_rng(4)

    def save(name, sig):
        with wave.open(str(BUILD / name), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes((sig / np.abs(sig).max() * 0.7 * 32767).astype("<i2").tobytes())
    t = np.arange(int(0.7 * sr)) / sr
    save("whoosh.wav", np.convolve(rng.standard_normal(len(t)), np.ones(10) / 10, "same") * np.sin(np.pi * t / 0.7) ** 2)
    t = np.arange(int(0.18 * sr)) / sr
    save("pop.wav", np.sin(2 * np.pi * (500 + 900 * np.exp(-t * 30)) * t) * np.exp(-t * 28))
    t = np.arange(int(0.08 * sr)) / sr
    save("click.wav", rng.standard_normal(len(t)) * np.exp(-t * 90))


# ---------------------------------------------------------------- one section
def card_times(section, timed, dur):
    """Each badge pops in when its keyword is spoken (aligned word times), in order, at least 1.2 s apart."""
    norm = [_norm(w) for w, _, _ in timed]
    times, last, pos = [], LEAD, 0
    for i, card in enumerate(section["cards"]):
        keys = [_norm(w) for w in card.split() if len(_norm(w)) > 3]
        hit = next((k for k in range(pos, len(norm)) for key in keys if norm[k].startswith(key)), None)
        if hit is None:
            t = LEAD + 0.5 + (i + 0.5) * (dur - 1.5) / len(section["cards"])
        else:
            t, pos = timed[hit][1], hit + 1
        t = min(max(t, last + 1.2), LEAD + dur - 0.5)
        times.append(round(t, 2))
        last = t
    return times


def render_section(num, section, face_src, alpha_png):
    sid = section["id"]
    out = BUILD / f"section_{sid}.mp4"
    if out.exists():
        return out
    voice = v1.BUILD / f"vo_{sid}.wav"
    if not voice.exists():
        run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "voice" / f"{sid}.wav"), "-af", f"atempo={v1.TEMPO}", str(voice)])
    dur = v1.wav_seconds(voice)
    total = LEAD + dur + TAIL
    timed = word_times(section["text"], voice, LEAD)
    facts = card_times(section, timed, dur)
    caps = pages(timed)
    gfx = section_gfx(num, section, total, facts, caps)
    gesture = None
    if Path(face_src) == sifa_motion.LOOP:   # hand gestures from the Flow clips, at the times gestures.json plans
        track, gesture = sifa_gestures.face_track(sid, dur, LEAD)
        face_src = track or face_src
    face = lipsync(sid, voice, face_src)
    live = face.name.startswith(("face_live_", "face_gest_"))
    if live:   # moving Sifa: a matte for every frame, cut from the lip-synced video itself
        alpha_png = sifa_motion.mask_video(face, BUILD / f"mask_{'gest_' if gesture else ''}{sid}.mkv", clean_matte,
                                             Image.open(alpha_png), gesture)

    punch = "+".join(f"0.06*exp(-pow(on/{FPS}-{t0 + 0.05:.2f},2)/0.03)" for t0 in facts) or "0"
    cw = int(700 * CUT_H / 640)
    fx, fy = 10, H - CUT_H
    graph = ";".join([
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
        f"zoompan=z='1+{punch}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS},format=yuva420p[bg]",
        f"[1:v]fps={FPS},tpad=start_duration={LEAD}:start_mode=clone:stop_mode=clone:stop_duration={TAIL + 1},"
        f"scale={cw}:{CUT_H}:flags=lanczos,unsharp=5:5:0.7:5:5:0,format=rgba[f]",
        *([f"[2:v]fps={FPS},tpad=start_duration={LEAD}:start_mode=clone:stop_mode=clone:stop_duration={TAIL + 1},"
           f"scale={cw}:{CUT_H}:flags=lanczos,format=gray,split[m][ms]",
           # faint soft shadow that follows her
           f"[ms]gblur=sigma=14,lut=y=val*0.35[msa]",
           f"color=black:s={cw}x{CUT_H}:r={FPS},format=gray[blk]",
           "[blk][msa]alphamerge,format=rgba[gl]"] if live else
          [f"[2:v]scale={cw}:{CUT_H}:flags=lanczos,format=gray[m]",
           f"[3:v]scale={cw}:{CUT_H},format=rgba[gl]"]),
        "[f][m]alphamerge[fa]",
        # the still gets a gentle drift so it never looks frozen; the live one (head and face already move)
        # also breathes: chest and shoulders rise a little every ~4.5 s, with a slow sway, feet of the frame fixed
        *([f"[fa]scale=w={cw}:h='{CUT_H}*(1+0.009*sin(2*PI*t/4.5))':eval=frame[fb]",
           f"[gl]scale=w={cw}:h='{CUT_H}*(1+0.009*sin(2*PI*t/4.5))':eval=frame[gb]",
           f"[bg][gb]overlay=x='{fx + 10}+3*sin(t*0.45)':y='H-h+6':shortest=0[s1]",
           f"[s1][fb]overlay=x='{fx}+3*sin(t*0.45)':y='H-h':shortest=0[s2]"] if live else
          [f"[bg][gl]overlay=x='{fx}+4*sin(t*0.9)':y='{fy}+3*sin(t*0.6)':shortest=0[s1]",
           f"[s1][fa]overlay=x='{fx}+4*sin(t*0.9)':y='{fy}+3*sin(t*0.6)':shortest=0[s2]"]),
        f"[s2][4:v]overlay=0:0:format=auto,fade=t=in:st=0:d=0.2,fade=t=out:st={total - 0.2}:d=0.2,format=yuv420p[v]",
    ])
    ms = lambda s: int(s * 1000)
    sfx_in, mix = [], [f"[5:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms(LEAD)}|{ms(LEAD)},apad[vox]"]
    sfx_in += ["-i", str(BUILD / "whoosh.wav")]
    mix.append("[6:a]volume=0.5,aformat=channel_layouts=stereo,apad[w]")
    labels = ["[vox]", "[w]"]
    for k, t0 in enumerate(facts):
        sfx_in += ["-i", str(BUILD / "pop.wav")]
        mix.append(f"[{7 + k}:a]volume=0.35,aformat=channel_layouts=stereo,adelay={ms(t0)}|{ms(t0)},apad[p{k}]")
        labels.append(f"[p{k}]")
    # voice + whoosh + pops can sum past full scale; limit here so nothing is clipped into the PCM
    mix.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,atrim=0:{total},"
               "alimiter=limit=0.7:level=0:attack=2:release=60[a]")
    run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", str(HERE / "gameplay" / f"{sid}.mp4"),
         "-i", str(face), *([] if live else ["-loop", "1"]), "-i", str(alpha_png),
         "-loop", "1", "-i", str(BUILD / "cut_glow.png"),
         "-framerate", str(FPS), "-i", str(gfx / "%05d.png"), "-i", str(voice), *sfx_in,
         "-filter_complex", graph + ";" + ";".join(mix), "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "pcm_s16le", str(out)])
    print("section", sid, f"{total:.1f}s", flush=True)
    return out


# ---------------------------------------------------------------- cold open
def cold_open():
    out = BUILD / "cold_open.mp4"
    if out.exists():
        return out
    hook = ROOT / "previz" / "voice" / "hook.wav"
    shots = [("gameplay_demo", 84, 2.0), ("gameplay_reveal_trailer", 72, 1.9), ("multiplayer_trailer", 36, 1.9),
             ("gameplay_demo", 180, 2.0), ("gameplay_demo", 300, 2.0)]
    length = sum(s[2] for s in shots)
    parts = []
    for k, (src, start, dur) in enumerate(shots):
        p = BUILD / f"co{k}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", str(HERE / "official_video" / f"{src}.mp4"),
             "-vf", f"scale={W}:{H},fps={FPS},zoompan=z='1+0.0025*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS},format=yuv420p",
             "-an", "-c:v", "libx264", "-crf", "17", str(p)])
        parts.append(p)
    (BUILD / "co.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(BUILD / "co.txt"), "-c", "copy", str(BUILD / "co.mp4")])
    caps = pages(word_times("Gears of War: E-Day is finally here, and it might be the best Gears in fifteen years. "
                            "Here's everything you need to know before you buy.", hook, 0.3))
    gdir = BUILD / "gfx_cold"
    gdir.mkdir(exist_ok=True)
    for i in range(int(length * FPS)):
        t = i / FPS
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        if 0.9 <= t < length - 0.3:
            k = ease_back((t - 0.9) / 0.3)
            layer = Image.new("RGBA", (1800, 330), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            ld.text((900, 120), "GEARS OF WAR: E-DAY", font=font("Black", 150), fill=(255, 255, 255, 255), anchor="mm",
                    stroke_width=6, stroke_fill=(0, 0, 0, 255))
            sub = "EVERYTHING YOU NEED TO KNOW"
            half = ld.textlength(sub, font=F_SMALL) / 2 + 30
            ld.rectangle([900 - half, 215, 900 + half, 290], fill=(*RED, 255))
            ld.text((900, 252), sub, font=F_SMALL, fill=(255, 255, 255, 255), anchor="mm")
            s = 1.06 - 0.06 * k
            layer = layer.resize((int(1800 * s), int(330 * s)))
            img.alpha_composite(layer, (int(W / 2 - layer.width / 2), int(420 - layer.height / 2)))
        d.text((W - 70, H - 36), "Footage: Xbox / The Coalition", anchor="rm", font=font("Medium", 20),
               fill=(255, 255, 255, 160))
        draw_caption(d, t, caps, cx=W // 2, y=930)
        img.save(gdir / f"{i:05d}.png", compress_level=1)
    cuts = np.cumsum([s[2] for s in shots])[:-1]
    ins = ["-i", str(BUILD / "co.mp4"), "-framerate", str(FPS), "-i", str(gdir / "%05d.png"), "-i", str(hook)]
    mix = ["[2:a]aresample=48000,aformat=channel_layouts=stereo,adelay=300|300,apad[h]"]
    labels = ["[h]"]
    for k, c in enumerate(cuts):
        ins += ["-i", str(BUILD / "whoosh.wav")]
        ms = int((c - 0.3) * 1000)
        mix.append(f"[{3 + k}:a]volume=0.45,aformat=channel_layouts=stereo,adelay={ms}|{ms},apad[w{k}]")
        labels.append(f"[w{k}]")
    mix.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,atrim=0:{length},"
               "alimiter=limit=0.7:level=0:attack=2:release=60[a]")
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex",
         "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v];" + ";".join(mix),
         "-map", "[v]", "-map", "[a]", "-t", str(length), "-c:v", "libx264", "-crf", "17", "-c:a", "pcm_s16le", str(out)])
    return out


def main():
    wanted = set(sys.argv[1:])
    sfx()
    face_src, alpha_png = cutout_assets()
    if sifa_motion.LOOP.exists():
        face_src = sifa_motion.LOOP
    parts = []
    for num, s in enumerate(v1.SECTIONS, 1):
        if wanted and s["id"] not in wanted:
            continue
        parts.append(render_section(num, s, face_src, alpha_png))
    if wanted:
        return
    intro = ROOT / "sifa_intro_talking_1080p.mp4"
    parts = [v1.normalise(cold_open(), BUILD / "p_cold.mp4"), v1.normalise(intro, BUILD / "p_intro.mp4"), *parts,
             v1.normalise(v1.BUILD / "endcard.mp4", BUILD / "p_end.mp4"), v1.normalise(ROOT / "sifa_si_outro.mp4", BUILD / "p_outro.mp4")]
    (BUILD / "parts.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(BUILD / "parts.txt"), "-c", "copy",
         str(BUILD / "joined.mov")])
    dur = lambda p: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                          str(p)], capture_output=True, text=True).stdout)
    total, head = dur(BUILD / "joined.mov"), dur(BUILD / "p_cold.mp4") + dur(BUILD / "p_intro.mp4")
    music = BUILD / "bed.wav"
    run([sys.executable, str(HERE / "make_bed.py"), str(music), f"{total - head:.2f}"])
    ms = int(head * 1000)
    chain = (f"[0:a]asplit=2[mix][key];[1:a]volume=0.3,adelay={ms}|{ms},apad[mus];"
             "[mus][key]sidechaincompress=threshold=0.025:ratio=10:attack=15:release=400[duck];"
             "[mix][duck]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,alimiter=limit=0.75:level=0:attack=2:release=60[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(BUILD / "joined.mov"), "-i", str(music), "-filter_complex", chain,
         "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", str(MASTER)])
    # the copy kept in git has to stay under GitHub's 100 MB file limit
    run(["ffmpeg", "-v", "error", "-y", "-i", str(MASTER), "-c:v", "libx264", "-b:v", "1250k", "-preset", "slow",
         "-maxrate", "1500k", "-bufsize", "3000k", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-c:a", "aac", "-b:a", "128k", str(OUT)])
    print("wrote", OUT, f"{total / 60:.1f} min")


if __name__ == "__main__":
    main()
