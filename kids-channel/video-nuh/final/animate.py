"""Animates the still scene images into the final video frames.

Each clip in clips.json names an image, a time span, a camera move and effects.
Frames are piped straight into ffmpeg; narration, captions and ambience are
mixed in by mix.py afterwards.

Prophet Nuh is drawn here as a faceless glow of white light (never generated
by the image model), so he can never be given a face.
"""
import json, math, os, subprocess, sys
import cv2
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 24
FADE = 0.6
clips = json.load(open(os.path.join(D, "clips.json")))
rng = np.random.default_rng(3)


def ease(t):
    return t * t * (3 - 2 * t)


def load(name):
    img = cv2.imread(os.path.join(D, "images", f"{name}.png"), cv2.IMREAD_COLOR)
    big = cv2.resize(img, (int(W * 1.25), int(H * 1.25)), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(big, (0, 0), 2.0)
    return cv2.addWeighted(big, 1.35, blur, -0.35, 0).astype(np.float32) / 255.0


def camera(img, t, cam):
    """cam: [zoom0, zoom1, x0, y0, x1, y1] with x/y as -1..1 pan within the margin."""
    z0, z1, x0, y0, x1, y1 = cam
    e = ease(t)
    z = z0 + (z1 - z0) * e
    cx, cy = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
    ih, iw = img.shape[:2]
    cw, ch = W / z, H / z                       # crop size in source pixels (z>=1 means zoomed in)
    cw, ch = cw * iw / (W * 1.25), ch * ih / (H * 1.25)
    cw, ch = min(cw, iw), min(ch, ih)
    mx, my = (iw - cw) / 2, (ih - ch) / 2
    left = mx + cx * mx
    top = my + cy * my
    M = np.float32([[W / cw, 0, -left * W / cw], [0, H / ch, -top * H / ch]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def nuh_glow(frame, t_abs, x, y, s):
    """Soft faceless pillar of white light at (x, y) in 0..1 screen units, height s."""
    px, py, hh = x * W, y * H, s * H
    pulse = 1 + 0.08 * math.sin(t_abs * 2.2)
    dx, dy = (XX - px) / (hh * 0.14), (YY - py) / (hh * 0.5)
    core = np.exp(-(dx ** 2 + np.abs(dy) ** 3) * 2.0) * 1.4 * pulse     # tall soft pillar, no features
    halo = np.exp(-((XX - px) ** 2 + ((YY - py) * 0.7) ** 2) / (2 * (hh * 0.45) ** 2)) * 0.4 * pulse
    ang = np.arctan2(YY - py, XX - px)
    rays = (0.5 + 0.5 * np.cos(ang * 10 + t_abs * 0.4)) ** 10 * np.exp(-np.hypot(XX - px, YY - py) / (hh * 0.6)) * 0.07
    g = np.clip(core + halo + rays, 0, None)[..., None]
    tint = np.array([0.92, 0.98, 1.0], np.float32)   # BGR: warm white
    return frame + g * tint


class Rain:
    def __init__(self, n=900):
        self.x = rng.uniform(0, W, n); self.y = rng.uniform(0, H, n)
        self.v = rng.uniform(45, 75, n); self.l = rng.uniform(18, 40, n)

    def draw(self, frame, amount):
        layer = np.zeros((H, W), np.float32)
        k = int(len(self.x) * amount)
        for i in range(k):
            x, y, l = int(self.x[i]), int(self.y[i]), self.l[i]
            cv2.line(layer, (x, y), (int(x - l * 0.15), int(y - l)), 0.55, 1, cv2.LINE_AA)
        self.y = (self.y + self.v) % (H + 60); self.x = (self.x - self.v * 0.15) % W
        layer = cv2.GaussianBlur(layer, (0, 0), 0.7)
        return frame * (1 - 0.18 * amount) + layer[..., None] * 0.9


def mist(frame, t_abs, amount):
    n = 0.5 + 0.5 * np.sin(XX / 260 + t_abs * 0.15) * np.sin(YY / 190 - t_abs * 0.1)
    n = n * np.clip((YY / H - 0.35) * 1.8, 0, 1)
    return frame * (1 - 0.25 * amount * n[..., None]) + 0.85 * 0.25 * amount * n[..., None]


def shimmer(frame, t_abs, top):
    """Gentle water ripple below the horizon line `top` (0..1)."""
    y0 = int(top * H)
    sub = frame[y0:]
    yy = YY[y0:]
    dx = (np.sin(yy / 9 + t_abs * 3) * 2.2 * ((yy - y0) / (H - y0) + 0.2)).astype(np.float32)
    mx = (XX[y0:] + dx).astype(np.float32)
    frame[y0:] = cv2.remap(sub, mx, yy - y0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return frame


def daynight(frame, t_abs, period):
    k = 0.5 + 0.5 * math.cos(2 * math.pi * t_abs / period)
    night = frame * np.array([0.55, 0.32, 0.25], np.float32)
    return frame * (1 - k) + night * k


VIGNETTE = (1 - 0.35 * (((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2) ** 1.2)[..., None]


def render():
    total = clips[-1]["end"]
    n = round(total * FPS)
    out = os.path.join(D, "video_silent.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
                          stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    cache, rain = {}, Rain()
    flashes = []
    for i in range(n):
        ta = i / FPS
        layers = []
        for c in clips:
            if c["start"] - FADE / 2 <= ta < c["end"] + FADE / 2:
                a = 1.0
                if ta < c["start"] + FADE / 2 and c is not clips[0]:
                    a = (ta - (c["start"] - FADE / 2)) / FADE
                if ta > c["end"] - FADE / 2 and c is not clips[-1]:
                    a = min(a, (c["end"] + FADE / 2 - ta) / FADE)
                layers.append((c, max(0, min(1, a))))
        frame = np.zeros((H, W, 3), np.float32)
        for c, a in layers:
            if c["image"] not in cache:
                cache = {k: v for k, v in cache.items() if any(k == x["image"] for x in clips if x["end"] > ta - 2)}
                cache[c["image"]] = load(c["image"])
            t = (ta - c["start"]) / (c["end"] - c["start"])
            f = camera(cache[c["image"]], min(max(t, 0), 1), c.get("cam", [1.0, 1.08, 0, 0, 0, 0]))
            fx = c.get("fx", {})
            if "shimmer" in fx: f = shimmer(f, ta, fx["shimmer"])
            if "daynight" in fx: f = daynight(f, ta - c["start"], fx["daynight"])
            if "mist" in fx: f = mist(f, ta, fx["mist"])
            if "glow" in fx:
                g = fx["glow"]                      # [x, y, size] or [x0, y0, size, x1, y1]
                gx0, gy0, gs = g[:3]
                gx1, gy1 = g[3:5] if len(g) == 5 else (gx0, gy0)
                e = ease(min(max(t, 0), 1))
                f = nuh_glow(f, ta, gx0 + (gx1 - gx0) * e, gy0 + (gy1 - gy0) * e, gs)
            if "rain" in fx: f = rain.draw(f, fx["rain"])
            if "lightning" in fx:
                ph = (ta * 0.37 + c["start"]) % fx["lightning"]
                if ph < 0.12 or 0.25 < ph < 0.32:
                    f = f * 1.9 + 0.12
                    flashes.append(round(ta, 2))
            if "fade_in" in fx and t < fx["fade_in"]:
                f = f * (t / fx["fade_in"])
            frame += f * a
        frame = frame * VIGNETTE
        frame += rng.normal(0, 0.012, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1).astype(np.float32)
        ff.stdin.write((np.clip(frame, 0, 1) * 255).astype(np.uint8).tobytes())
        if i % 240 == 0:
            print(f"frame {i}/{n}", flush=True)
    ff.stdin.close(); ff.wait()
    json.dump(sorted(set(round(x, 1) for x in flashes)), open(os.path.join(D, "flashes.json"), "w"))
    print("wrote", out)


def stills(times):
    """Quick preview: write single frames at the given seconds (no video)."""
    for ta in times:
        c = next(x for x in clips if x["start"] <= ta < x["end"])
        img = load(c["image"])
        t = (ta - c["start"]) / (c["end"] - c["start"])
        f = camera(img, t, c.get("cam", [1.0, 1.08, 0, 0, 0, 0]))
        fx = c.get("fx", {})
        if "shimmer" in fx: f = shimmer(f, ta, fx["shimmer"])
        if "daynight" in fx: f = daynight(f, ta - c["start"], fx["daynight"])
        if "mist" in fx: f = mist(f, ta, fx["mist"])
        if "glow" in fx:
            g = fx["glow"]
            gx1, gy1 = g[3:5] if len(g) == 5 else g[:2]
            e = ease(t)
            f = nuh_glow(f, ta, g[0] + (gx1 - g[0]) * e, g[1] + (gy1 - g[1]) * e, g[2])
        if "rain" in fx: f = Rain().draw(f, fx["rain"])
        cv2.imwrite(os.path.join(D, f"still_{ta:06.1f}.png"), (np.clip(f * VIGNETTE, 0, 1) * 255).astype(np.uint8))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        stills([float(x) for x in sys.argv[1:]])
    else:
        render()
