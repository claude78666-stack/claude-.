"""Optimise the Axolotlion art into small WebP files and a manifest for the single-file build."""
import json, pathlib, base64, io
from PIL import Image

SRC = pathlib.Path('../video/public/axolotlion')
OUT = pathlib.Path('assets'); OUT.mkdir(exist_ok=True)

def save(img, name, q=90, size=None):
    if size: img = img.resize(size, Image.LANCZOS)
    img.save(OUT / name, 'WEBP', quality=q, method=6)
    return img.size

man = {}
man['stand'] = save(Image.open(SRC / 'stand-cut.png').convert('RGBA'), 'stand.webp', 88, (900, 625))
man['face'] = save(Image.open(SRC / 'face.png').convert('RGBA'), 'face.webp', 88, (520, 520))
bg = Image.open(SRC / 'bg.jpg').convert('RGB'); bg.thumbnail((1700, 956)); bg.save(OUT / 'bg.jpg', quality=82); man['bg'] = bg.size
for f in ['solana.svg']: (OUT / f).write_bytes((SRC / f).read_bytes())
pf = Image.open(SRC / 'pumpfun.png').convert('RGBA'); save(pf, 'pumpfun.webp', 90, (160, 160))

# rig at half resolution
rig = json.load(open(SRC / 'rig/rig.json'))
half = lambda v: round(v * 0.6)
meta = {'w': half(rig['w']), 'h': half(rig['h']), 'legs': {}}
def conv(name, b):
    im = Image.open(SRC / f'rig/{name}.png')
    w, h = max(1, half(im.width)), max(1, half(im.height))
    save(im, f'rig_{name}.webp', 88, (w, h))
    return {'x': half(b['x']), 'y': half(b['y']), 'w': w, 'h': h}
save(Image.open(SRC / 'rig/base.png'), 'rig_base.webp', 88, (meta['w'], meta['h']))
for n, L in rig['legs'].items():
    meta['legs'][n] = {'hip': [half(v) for v in L['hip']], 'knee': [half(v) for v in L['knee']], 'upper': conv(n + '_up', L['upper']), 'lower': conv(n + '_lo', L['lower'])}
meta['tail'] = {'pivot': [half(v) for v in rig['tail']['pivot']], **conv('tail', rig['tail'])}
json.dump(meta, open(OUT / 'rig.json', 'w'))
total = sum(p.stat().st_size for p in OUT.iterdir())
print('assets', len(list(OUT.iterdir())), 'total KB', total // 1024)
