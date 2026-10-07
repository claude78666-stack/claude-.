"""Add the three-quarter view, aligned to the front view (centroid and floor)."""
import json
from PIL import Image
import numpy as np
K = 1100 / 1406.0
front = Image.open('../video/public/axolotlion/stand-cut.png').convert('RGBA'); fa = np.array(front)[..., 3] > 128
cF = np.where(fa)[1].mean() * K
v = Image.open('rigwork/v34-cut.png').convert('RGBA'); va = np.array(v)[..., 3] > 128
cV = np.where(va)[1].mean() * K
w, h = round(v.width * K), round(v.height * K)
v.resize((w, h), Image.LANCZOS).save('assets/v34.webp', 'WEBP', quality=90, method=6)
m = json.load(open('assets/stand_rig.json'))
m['v34'] = {'x': round(cF - cV), 'y': round(m['h'] - h), 'w': w, 'h': h}; m['cx'] = round(cF)
json.dump(m, open('assets/stand_rig.json', 'w')); print(m['v34'], m['cx'], m['w'], m['h'])
