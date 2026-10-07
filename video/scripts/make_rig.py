"""Split public/axolotlion/run-a-cut.png into a base body plus tail and four two-segment legs, so the runner can swing real legs."""
import json, pathlib
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np

SRC = pathlib.Path('public/axolotlion/run-a-cut.png')
OUT = pathlib.Path('public/axolotlion/rig'); OUT.mkdir(exist_ok=True)
im = Image.open(SRC).convert('RGBA'); W, H = im.size
alpha = im.split()[3]

def poly_mask(pts, grow=10, blur=3):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    if grow: m = m.filter(ImageFilter.MaxFilter(grow * 2 + 1))
    return m.filter(ImageFilter.GaussianBlur(blur)) if blur else m

def below(y):  # mask of everything with row >= y
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rectangle([0, y, W, H], fill=255); return m

# name: polygon, hip pivot, knee pivot, y where the leg leaves the torso
LEGS = {
 'hindA': dict(poly=[(660,545),(780,545),(795,600),(770,670),(745,740),(715,805),(640,810),(598,795),(590,730),(615,660),(640,600)], hip=(720,575), knee=(680,700), cut=590),
 'hindB': dict(poly=[(830,540),(1000,540),(1005,600),(960,660),(905,705),(865,745),(845,795),(790,812),(745,805),(735,775),(755,730),(790,690),(805,640),(815,590)], hip=(930,585), knee=(850,725), cut=600),
 'foreC': dict(poly=[(1250,560),(1400,560),(1405,620),(1385,690),(1345,745),(1300,765),(1255,745),(1245,690),(1230,640),(1240,590)], hip=(1330,580), knee=(1305,690), cut=600),
 'foreD': dict(poly=[(1440,560),(1560,570),(1650,640),(1730,720),(1785,775),(1775,805),(1720,805),(1660,775),(1590,720),(1520,670),(1460,650),(1430,610)], hip=(1480,615), knee=(1620,700), cut=635),
}
# tail: everything left of x=600 (soft edge), pivot where it joins the body
TAIL_X, TAIL_PIVOT = 600, (650, 470)

# belly line b(x): lowest opaque row per column with the legs masked out, interpolated across the leg gaps
legs_union = Image.new('L', (W, H), 0)
for L in LEGS.values():
    legs_union = ImageChops.lighter(legs_union, poly_mask(L['poly'], grow=16, blur=0))
body_only = np.array(ImageChops.multiply(alpha, Image.eval(legs_union, lambda v: 255 - v))) > 40
cols = np.arange(W); belly = np.full(W, np.nan)
for x in cols:
    ys = np.where(body_only[:, x])[0]
    if len(ys) and x > 560: belly[x] = ys.max()
ok = ~np.isnan(belly)
belly = np.interp(cols, cols[ok], belly[ok]) if ok.any() else np.full(W, 600.)
belly = np.convolve(np.pad(belly, 20, mode='edge'), np.ones(41) / 41, mode='valid')
BELLY = belly
belly_mask = Image.fromarray(np.where(np.arange(H)[:, None] > BELLY[None, :] + 34, 255, 0).astype('uint8'))
meta = {'w': W, 'h': H, 'legs': {}, 'tail': {}}
remove = Image.new('L', (W, H), 0)

def save_layer(name, mask):
    layer = im.copy(); layer.putalpha(ImageChops.multiply(alpha, mask))
    bb = layer.getbbox()
    layer.crop(bb).save(OUT / f'{name}.png')
    return {'x': bb[0], 'y': bb[1], 'w': bb[2] - bb[0], 'h': bb[3] - bb[1]}

def with_top_extension(pts):
    top = [x for x, y in pts if y <= 600]
    x0, x1 = min(top) + 10, max(top) - 10
    m = poly_mask(pts)
    ext = Image.new('L', (W, H), 0); ImageDraw.Draw(ext).rectangle([x0, 470, x1, 600], fill=255)
    return ImageChops.lighter(m, ext.filter(ImageFilter.GaussianBlur(3)))
ramp_v = Image.fromarray((np.tile(np.clip((np.arange(H) - 480) / 90.0, 0, 1)[:, None], (1, W)) * 255).astype('uint8'))

for name, L in LEGS.items():
    full = ImageChops.multiply(with_top_extension(L['poly']), ramp_v)
    kx, ky = L['knee']
    upper = ImageChops.multiply(full, Image.new('L', (W, H), 255).point(lambda v: v))
    up_mask = ImageChops.multiply(full, Image.eval(below(ky - 14), lambda v: 255 - v))   # above knee (+ overlap)
    up_mask = ImageChops.multiply(full, Image.eval(below(ky + 14), lambda v: 255 - v))
    lo_mask = ImageChops.multiply(full, below(ky - 14))
    meta['legs'][name] = {'hip': L['hip'], 'knee': L['knee'], 'upper': save_layer(name + '_up', up_mask), 'lower': save_layer(name + '_lo', lo_mask)}
    remove = ImageChops.lighter(remove, ImageChops.multiply(poly_mask(L['poly'], grow=26, blur=0), belly_mask))

ramp = np.clip((TAIL_X + 60 - np.arange(W)) / 100.0, 0, 1)  # 1 left of x=560, 0 right of x=660
tail_soft = Image.fromarray((np.tile(ramp, (H, 1)) * 255).astype('uint8'))
meta['tail'] = {'pivot': TAIL_PIVOT, **save_layer('tail', tail_soft)}
remove = ImageChops.lighter(remove, tail_soft)

base = im.copy(); base.putalpha(ImageChops.multiply(alpha, Image.eval(remove, lambda v: 255 - v)))
base.save(OUT / 'base.png')
json.dump(meta, open(OUT / 'rig.json', 'w'), indent=1)
print('ok', {k: v['upper'] for k, v in meta['legs'].items()})

# typed copy of the rig for Remotion
ts = 'export const RIG = ' + json.dumps(meta) + ' as const;\n'
pathlib.Path('src/axolotlion/rig.ts').write_text(ts)
