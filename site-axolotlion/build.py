"""Inline every asset as a data URI so the site is one portable HTML file.
python3 build.py              -> index.html
python3 build.py --artifact P -> fragment for claude.ai artifacts at path P"""
import base64, json, pathlib, re, sys
A = pathlib.Path('assets')
mime = {'.webp': 'image/webp', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.png': 'image/png'}
assets = {}
for p in sorted(A.iterdir()):
    if p.suffix in mime and p.stem not in ('v34', 'v135'):
        key = {'solana.svg': 'solana', 'pumpfun.webp': 'pumpfun', 'bg.jpg': 'bg', 'stand.webp': 'stand', 'face.webp': 'face'}.get(p.name, p.stem)
        assets[key] = f'data:{mime[p.suffix]};base64,' + base64.b64encode(p.read_bytes()).decode()
rig = json.load(open(A / 'rig.json'))
srig = json.load(open(A / 'stand_rig.json'))
t = open('index.template.html').read()
t = t.replace('/*ASSETS*/{}', json.dumps(assets)).replace('/*RIG*/{}', json.dumps(rig)).replace('/*SRIG*/{}', json.dumps(srig))
if len(sys.argv) > 2 and sys.argv[1] == '--artifact':
    t = t.replace('<title>Axolotlion</title>', '<title>Axolotlion World</title>')
    head = re.search(r'<head>(.*?)</head>', t, re.S).group(1)
    body = re.search(r'<body>(.*?)</body>', t, re.S).group(1)
    title = re.search(r'<title>.*?</title>', head).group(0)
    fonts = ''.join(re.findall(r'<link[^>]*>', head))
    css = re.search(r'<style>.*?</style>', head, re.S).group(0)
    t = title + fonts + css + body
    pathlib.Path(sys.argv[2]).write_text(t)
else:
    pathlib.Path('index.html').write_text(t)
print('built', len(t) // 1024, 'KB')
