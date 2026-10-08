# Axolotlion website

One self-contained page (`index.html`, about 550 KB). Open it in a browser or upload it to any static host (Vercel, Netlify, GitHub Pages, Cloudflare Pages).

- Tap the character: he jumps and toots (sounds are synthesised in the browser, no audio files). Hold to build up a bigger one.
- Running section: four legs and a tail animate with CSS.
- Meme maker: caption, download as PNG.
- Fill in `CONFIG` at the top of the script in `index.template.html` (contract address, pump.fun, DexScreener, X, Telegram), then run `python3 build.py`. Empty values stay hidden.

Rebuild: `python3 prep_assets.py` (only if art changed) then `python3 build.py`.

## Turn him around, and he looks at you
- Drag sideways to spin him a full 360 degrees, as many turns as you like. `make_turntable.py` builds 72 frames (every 5 degrees) by optical-flow morphing between the real views (front, three-quarter, rear three-quarter) and mirroring them for the other side; the page crossfades neighbouring frames on a canvas. When he faces you, the live rig (moving head, tail, blinking) takes over. A tap or hold still makes him toot.
- His head turns in 3D toward your cursor or finger. When nobody is touching the screen he looks around on his own.
- "Spin him" sweeps him through all the angles.
- The straight-back stretch (about 150-210 degrees) is synthesised from the rear three-quarter photo (`back_warp`), not a real photo. To improve it, generate a true rear view, add it as a keyframe in `make_turntable.py`, and re-run `python3 make_turntable.py 5` then convert `turntable/*.png` to `assets/tt_NNN.webp` (1000px wide).

## Showroom stand
The hero is a display case with spotlight beams (no platform or floor reflection). Drag and release to flick him; he keeps turning with momentum. If nobody touches the page for about 6 seconds he starts a slow endless turn like a car on a showroom turntable, and stops the moment you touch him. The Spin button does one smooth full turn.
Art is stored at 1100 px wide (`make_stand_rig.py`, `make_v34.py`, `prep_assets.py`) so it stays sharp on high-density screens.
