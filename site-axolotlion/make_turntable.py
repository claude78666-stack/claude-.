"""Build a full 360-degree turntable (72 frames) by flow-morphing between the photographed angles:
front (0), three-quarter (45), rear three-quarter (135), and their mirrors for the other side."""
import json, pathlib, sys
import numpy as np, cv2
from PIL import Image

CW, CH = 1400, 764            # working canvas
K = 1100 / 1406.0
OUT = pathlib.Path('turntable'); OUT.mkdir(exist_ok=True)

def place(path, scale, cx_target=CW // 2):
    im = Image.open(path).convert('RGBA')
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    a = np.array(im)[..., 3] > 128
    cx = np.where(a)[1].mean()
    canvas = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    canvas.alpha_composite(im, (round(cx_target - cx), CH - im.height))
    return np.array(canvas)

front = place('../video/public/axolotlion/stand-cut.png', K)
v34 = place('rigwork/v34-cut.png', K * 976 / 982)
v135 = place('rigwork/v135-cut.png', K * 976 / 1040)
mir = lambda a: a[:, ::-1].copy()
GRAY = np.array([120, 130, 140], np.float32)
def over_gray(rgba):
    a = rgba[..., 3:4].astype(np.float32) / 255
    return (rgba[..., :3].astype(np.float32) * a + GRAY * (1 - a)).astype(np.uint8)
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
dis.setFinestScale(1)
def flow(a, b):
    ga = cv2.cvtColor(over_gray(a), cv2.COLOR_RGB2GRAY); gb = cv2.cvtColor(over_gray(b), cv2.COLOR_RGB2GRAY)
    return dis.calc(ga, gb, None)           # for each pixel of a, where it is in b
yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
def warp(img, fl, t):
    # sample img at (x + t*fl)
    mx = xx + t * fl[..., 0]; my = yy + t * fl[..., 1]
    return cv2.remap(img.astype(np.float32), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
def premul(rgba):
    f = rgba.astype(np.float32); f[..., :3] *= f[..., 3:4] / 255; return f
def unpremul(f):
    a = np.clip(f[..., 3:4], 1e-3, 255); rgb = f[..., :3] / (a / 255); return np.dstack([np.clip(rgb, 0, 255), np.clip(f[..., 3], 0, 255)]).astype(np.uint8)
def morph(a, b, fab, fba, t):
    A, B = premul(a), premul(b)
    # I_t(x) = (1-t) A(x + t*F_BA(x)) + t B(x + (1-t)*F_AB(x))
    return unpremul((1 - t) * warp(A, fba, t) + t * warp(B, fab, 1 - t))

def back_warp(r135m, u, k1=0.6, k2=0.16, body=330.0):
    """Turn the (mirrored) rear three-quarter photo toward a straight-back view. u in [0,1]: 0 = unchanged, 1 = seen end-on.
    The mane stays round and slides to the centre line; the body and tail are squeezed toward it; at u=1 the result is symmetric."""
    al = r135m[..., 3] > 128
    ys, xs = np.where(al); top, bot = ys.min(), ys.max()
    xm = xs[ys < top + (bot - top) * 0.14].mean()                 # mane centre
    kk1, kk2 = 1 - (1 - k1) * u, 1 - (1 - k2) * u
    def g_inv(xo):
        d = np.abs(xo); sgn = np.sign(xo)
        src = np.where(d < body * kk1, d / kk1, body + (d - body * kk1) / kk2)
        return sgn * src
    H = r135m.shape[0]
    t = np.clip((np.arange(H) - (top + (bot - top) * 0.30)) / ((bot - top) * 0.28), 0, 1); t = t * t * (3 - 2 * t)
    src_f = premul(r135m); out = np.zeros_like(src_f); X = np.arange(CW, dtype=np.float32)
    for y in range(H):
        sx = (1 - t[y]) * X + t[y] * (xm + g_inv(X - xm))
        out[y] = cv2.remap(src_f[y:y + 1], sx[None, :].astype(np.float32), np.zeros((1, CW), np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)[0]
    out = np.roll(out, round(u * (CW / 2 - xm)), axis=1)             # slide the mane onto the centre line
    w = 0.0
    out = (1 - w) * out + w * out[:, ::-1]
    return unpremul(out)

def back_view(r135m): return back_warp(r135m, 1.0)

F180 = back_view(mir(v135))
KEYS = [(0, front), (45, v34), (135, mir(v135))]
R135 = mir(v135)

STEP = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
frames = {}
for (a0, A), (a1, B) in zip(KEYS[:-1], KEYS[1:]):
    fab, fba = flow(A, B), flow(B, A)
    ang = a0
    while ang < a1 - 1e-6:
        t = (ang - a0) / (a1 - a0)
        frames[round(ang, 3)] = A if t == 0 else morph(A, B, fab, fba, t)
        ang += STEP
    print('segment', a0, '->', a1, 'done')
frames[135.0] = R135
ang = 135.0 + STEP
while ang < 180 - 1e-6:
    frames[round(ang, 3)] = back_warp(R135, (ang - 135) / 45.0); ang += STEP
frames[180.0] = F180
full = dict(frames)
for ang, fr in list(frames.items()):
    if 0 < ang < 180: full[round(360 - ang, 3)] = fr[:, ::-1].copy()      # the other half is an exact mirror, so the loop is seamless
frames = {a: full[a] for a in sorted(full)}
meta = {'step': STEP, 'count': len(frames), 'w': CW, 'h': CH}
for ang, fr in frames.items():
    Image.fromarray(fr).save(OUT / f'f{int(round(ang / STEP)):03d}.png')
json.dump(meta, open(OUT / 'meta.json', 'w')); print(meta)
