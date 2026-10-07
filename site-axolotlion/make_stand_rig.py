"""Split the standing Axolotlion into moving parts: base, face, two gill clusters, two tail segments."""
import json, pathlib
import numpy as np, cv2
from PIL import Image

SRC = pathlib.Path('../video/public/axolotlion/stand-cut.png')
OUT = pathlib.Path('assets'); OUT.mkdir(exist_ok=True)
K = 900 / 1406.0            # page art is 900px wide
im = Image.open(SRC).convert('RGBA'); A = np.array(im); H, W = A.shape[:2]
alpha = A[..., 3].astype(np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W]

def ellipse(cx, cy, rx, ry, feather, ang=0.0):
    c, s = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    dx, dy = xx - cx, yy - cy
    u, v = (dx * c + dy * s) / rx, (-dx * s + dy * c) / ry
    r = np.sqrt(u * u + v * v)
    return np.clip((1 - r) * (min(rx, ry) / feather), 0, 1).astype(np.float32)

def ramp_x(x_full, x_zero):   # 1 for x < x_full, falls to 0 at x_zero
    return np.clip((x_zero - xx) / float(x_zero - x_full), 0, 1).astype(np.float32)

FACE = ellipse(1040, 352, 170, 160, 26)
GILL_L = ellipse(850, 285, 120, 215, 38, ang=-6)
GILL_R = ellipse(1250, 265, 130, 225, 38, ang=8)
TAIL_B = ramp_x(330, 420)
TAIL_A = ramp_x(560, 660) * (1 - TAIL_B)
TAIL_ALL = ramp_x(560, 660)

# base: fill under the face so nothing shows when the head turns; remove the tail (it moves on its own)
rgb = A[..., :3].copy()
fill = (ellipse(1040, 352, 200, 190, 6) > 0).astype(np.uint8) * 255
inp = cv2.inpaint(rgb, fill, 18, cv2.INPAINT_TELEA)
mix = fill[..., None] > 0
rgb = np.where(mix, inp, rgb)
base_alpha = alpha * (1 - TAIL_ALL)
base_alpha = np.maximum(base_alpha, (fill > 0) * alpha.max() * 0 + (fill > 0) * 1.0 * 0)  # keep original silhouette
base = np.dstack([rgb, (base_alpha * 255).astype(np.uint8)])
fill_alpha = (ellipse(1040, 352, 200, 190, 6) > 0)
base[..., 3] = np.where(fill_alpha, np.maximum(base[..., 3], 255), base[..., 3])  # face hole is inside the body, keep opaque

meta = {'w': 900, 'h': round(H * K)}
def save(name, mask, src_rgb=None):
    rgb_ = A[..., :3] if src_rgb is None else src_rgb
    layer = np.dstack([rgb_, (alpha * mask * 255).astype(np.uint8)])
    ys, xs = np.where(layer[..., 3] > 3)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    crop = Image.fromarray(layer[y0:y1, x0:x1]).resize((max(1, round((x1 - x0) * K)), max(1, round((y1 - y0) * K))), Image.LANCZOS)
    crop.save(OUT / f'st_{name}.webp', 'WEBP', quality=88, method=6)
    return {'x': round(x0 * K), 'y': round(y0 * K), 'w': crop.width, 'h': crop.height}

Image.fromarray(base).resize((meta['w'], meta['h']), Image.LANCZOS).save(OUT / 'st_base.webp', 'WEBP', quality=88, method=6)
p = lambda x, y: [round(x * K), round(y * K)]
meta['face'] = {**save('face', FACE), 'pivot': p(1040, 500)}
meta['gillL'] = {**save('gillL', GILL_L), 'pivot': p(935, 355)}
meta['gillR'] = {**save('gillR', GILL_R), 'pivot': p(1160, 355)}
meta['tailA'] = {**save('tailA', TAIL_A), 'pivot': p(610, 600)}
meta['tailB'] = {**save('tailB', TAIL_B), 'pivot': p(340, 735)}
meta['eyes'] = [p(958, 334), p(1112, 334)]
meta['neck'] = p(1040, 500)
json.dump(meta, open(OUT / 'stand_rig.json', 'w'))
print({k: v for k, v in meta.items() if k not in ('eyes',)})
