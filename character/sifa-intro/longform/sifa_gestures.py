#!/usr/bin/env python3
"""Hand gestures for the living Sifa facecam, from the Google Flow (Veo 3.1) clips in ai/gestures/.

  python3 sifa_gestures.py            -> prepares every clip found: build/v2/gest_<kind>.mp4 (+ a contact sheet)

Every Flow clip starts and ends on her rest pose (shot1_last_1080.png as start and end frame), but Veo adds a slow
camera move, so each frame is registered back onto the reference photo (SIFT on the room, Sifa masked out), cropped
to the same 700x640 facecam box as cut_rgb.png and colour-matched to it. Only the gesture itself is kept: the span
where her hands move away from rest.

face_track() then builds a section's facecam: the LivePortrait head-motion loop, with a gesture crossfaded in at
every time gestures.json plans for that section, so between gestures she is always the calm, nodding Sifa.
render_v2.py lip-syncs that track and cuts her out (the per-frame matte follows the hands during gestures).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

import sifa_motion

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = HERE / "build" / "v2"
CLIPS = ROOT / "ai" / "gestures"
REF = ROOT / "ai" / "shot1_last_1080.png"
BOX = (680, 150, 1380, 790)     # facecam crop in the 1920x1080 reference (same as cut_rgb.png)
FPS = sifa_motion.FPS
FADE = 6                        # crossfade frames in and out of a gesture
# gesture span (seconds) picked by eye from each clip's contact sheet; clips not listed use _gesture_span()
SPANS = {"flow_yes.mp4": (1.7, 4.4)}
PLAN = json.loads((HERE / "gestures.json").read_text())
# gesture -> Flow clips that can play it (the first one that exists is used, the rest add variety)
KINDS = {
    "yes": ["flow_yes.mp4", "yes.mp4", "yes2.mp4"],
    "palm": ["palm.mp4", "palm2.mp4"],
    "count": ["count.mp4", "count2.mp4"],
    "point": ["point.mp4"],
    "both": ["both.mp4"],
}


def run(cmd):
    subprocess.run(cmd, check=True)


def _register(frames):
    """Similarity transform of every (1280x720 or 1920x1080) frame onto the reference, smoothed over time."""
    import cv2
    ref = cv2.imread(str(REF), cv2.IMREAD_GRAYSCALE)
    mask = np.full(ref.shape, 255, np.uint8)
    mask[200:, 760:1300] = 0                       # Sifa moves; only the room is used to register
    sift = cv2.SIFT_create(4000)
    kr, dr = sift.detectAndCompute(ref, mask)
    bf = cv2.BFMatcher()
    params = []
    for f in frames:
        g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_RGB2GRAY), (1920, 1080), interpolation=cv2.INTER_CUBIC)
        kf, df = sift.detectAndCompute(g, mask)
        good = [a for a, b in bf.knnMatch(df, dr, k=2) if a.distance < 0.75 * b.distance]
        src = np.float32([kf[m.queryIdx].pt for m in good])
        dst = np.float32([kr[m.trainIdx].pt for m in good])
        M, _ = cv2.estimateAffinePartial2D(src, dst, ransacReprojThreshold=4)
        params.append([np.hypot(M[0, 0], M[1, 0]), np.arctan2(M[1, 0], M[0, 0]), M[0, 2], M[1, 2]])
    p = np.array(params)
    k = np.ones(5) / 5                            # Veo's camera move is smooth; this removes match jitter
    p = np.stack([np.convolve(np.pad(c, 2, mode="edge"), k, "valid") for c in p.T], 1)
    return [np.array([[s * np.cos(a), -s * np.sin(a), tx], [s * np.sin(a), s * np.cos(a), ty]]) for s, a, tx, ty in p]


def _colour_match(crops, target, alpha):
    """Match the clip's colours (Lab mean/std over Sifa) to cut_rgb.png so the swap is invisible."""
    import cv2
    m = alpha > 0.5
    to_lab = lambda im: cv2.cvtColor(im, cv2.COLOR_RGB2LAB).astype(np.float32)
    t, s = to_lab(target)[m], to_lab(crops[0])[m]
    gain, off = t.std(0) / (s.std(0) + 1e-6), t.mean(0)
    out = []
    for c in crops:
        lab = (to_lab(c) - s.mean(0)) * gain + off
        out.append(cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB))
    return out


def _gesture_span(crops, alpha):
    """Frames where her arms/hands leave the rest pose: motion below the shoulders vs. the clip's first frame."""
    body = alpha.copy()
    body[:sifa_motion.HEAD_Y] = 0
    from scipy import ndimage
    zone = ndimage.binary_dilation(body > 0.3, iterations=60)   # hands can go outside her rest outline
    zone[:sifa_motion.HEAD_Y - 40] = False
    e = np.array([np.abs(c.astype(float) - crops[0].astype(float)).mean(2)[zone].mean() for c in crops])
    e = np.convolve(e, np.ones(5) / 5, "same")
    hi = e > e.min() + 0.35 * (e.max() - e.min())
    start = int(np.argmax(hi))
    end = start + int(np.argmin(hi[start:])) if not hi[start:].all() else len(e)
    pad = FPS // 5
    return max(0, start - pad), min(len(crops), end + pad)


def prepare(name):
    """ai/gestures/<name> -> build/v2/gest_<stem>.mp4: registered, cropped, colour-matched gesture frames."""
    out = BUILD / f"gest_{Path(name).stem}.mp4"
    if out.exists():
        return out
    import cv2
    from PIL import Image
    frames = list(sifa_motion.frames(sifa_motion.normalise_fps(CLIPS / name, BUILD / f"_src_{Path(name).stem}.mp4")))
    crops = []
    for f, M in zip(frames, _register(frames)):
        big = cv2.resize(f, (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
        reg = cv2.warpAffine(big, M, (1920, 1080), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        crops.append(np.ascontiguousarray(reg[BOX[1]:BOX[3], BOX[0]:BOX[2]]))
    target = np.asarray(Image.open(BUILD / "cut_rgb.png").convert("RGB"))
    alpha = np.asarray(Image.open(BUILD / "cut_alpha.png")).astype(float) / 255
    crops = _colour_match(crops, target, alpha)
    a, b = ([int(round(x * FPS)) for x in SPANS[name]] if name in SPANS else _gesture_span(crops, alpha))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "700x640",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)],
                           stdin=subprocess.PIPE)
    for c in crops[a:b]:
        enc.stdin.write(c.tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"{name}: gesture {a / FPS:.2f}-{b / FPS:.2f}s -> {out.name}", flush=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-vf", "fps=6,scale=233:-1,tile=8x3", "-frames:v", "1",
         str(BUILD / f"gest_{Path(name).stem}_sheet.jpg")])
    return out


def available():
    """gesture kind -> prepared clips, for every kind with at least one Flow clip uploaded."""
    have = {}
    for kind, names in KINDS.items():
        clips = [prepare(n) for n in names if (CLIPS / n).exists()]
        if clips:
            have[kind] = clips
    return have


def face_track(sid, seconds, lead):
    """Facecam for one section: the head-motion loop, with the planned gestures crossfaded in.
    Returns (track.mp4, per-frame gesture weight list) or (None, None) when no gesture clip is available."""
    have = available()
    events = [(t, k) for t, k, _ in PLAN.get(sid, []) if k in have]
    if not events:
        return None, None
    out, wfile = BUILD / f"track_{sid}.mp4", BUILD / f"track_{sid}.json"
    n = int(np.ceil(seconds * FPS)) + FPS
    if out.exists() and wfile.exists():
        return out, json.loads(wfile.read_text())
    loop = list(sifa_motion.frames(sifa_motion.LOOP))
    weight = np.zeros(n)
    inserts = {}
    used = {}
    for t, kind in events:
        clip = have[kind][used.get(kind, 0) % len(have[kind])]   # rotate between takes of the same gesture
        used[kind] = used.get(kind, 0) + 1
        g = list(sifa_motion.frames(clip))
        s0 = max(0, int(round((t - lead) * FPS)))
        ramp = np.minimum(1, np.minimum(np.arange(1, len(g) + 1), np.arange(len(g), 0, -1)) / FADE)
        for j, (fr, w) in enumerate(zip(g, ramp)):
            if s0 + j < n:
                inserts[s0 + j] = fr
                weight[s0 + j] = w
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "700x640",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)],
                           stdin=subprocess.PIPE)
    for i in range(n):
        fr = loop[i % len(loop)]
        if i in inserts:
            fr = (fr * (1 - weight[i]) + inserts[i] * weight[i]).astype(np.uint8)
        enc.stdin.write(np.ascontiguousarray(fr).tobytes())
    enc.stdin.close()
    enc.wait()
    wfile.write_text(json.dumps([round(float(w), 3) for w in weight]))
    print(f"track {sid}: {len(events)} gestures ({', '.join(k for _, k in events)})", flush=True)
    return out, weight.tolist()


if __name__ == "__main__":
    for kind, clips in available().items():
        print(kind, [c.name for c in clips])
