# Axolotlion website

One self-contained page (`index.html`, about 550 KB). Open it in a browser or upload it to any static host (Vercel, Netlify, GitHub Pages, Cloudflare Pages).

- Tap the character: he jumps and toots (sounds are synthesised in the browser, no audio files). Hold to build up a bigger one.
- Running section: four legs and a tail animate with CSS.
- Meme maker: caption, download as PNG.
- Fill in `CONFIG` at the top of the script in `index.template.html` (contract address, pump.fun, DexScreener, X, Telegram), then run `python3 build.py`. Empty values stay hidden.

Rebuild: `python3 prep_assets.py` (only if art changed) then `python3 build.py`.

## Turn him around, and he looks at you
- Drag the character sideways to turn him. Three real views (front, three-quarter, side) blend, and mirrored copies cover the other side. A tap or hold still makes him toot.
- His head turns in 3D toward your cursor or finger. When nobody is touching the screen he looks around on his own.
- "Spin him" sweeps him through all the angles.
- He now turns +/- 135 degrees (270 degrees in total): front, three-quarter, side and rear three-quarter views, mirrored for the other side. The only missing slice is the straight-back view at 180 degrees. To finish the 360, generate a view from directly behind, add it like `v135` (see `make_v34.py` for the alignment recipe), and extend `render()` and the +/-135 clamps in the turntable block of `index.template.html`.

## Showroom stand
The hero is a display case with spotlight beams (no platform or floor reflection). Drag and release to flick him; he keeps turning with momentum. If nobody touches the page for about 7 seconds he sweeps slowly left and right like a car on a display plinth, and stops the moment you move.
Art is stored at 1100 px wide (`make_stand_rig.py`, `make_v34.py`, `prep_assets.py`) so it stays sharp on high-density screens.
