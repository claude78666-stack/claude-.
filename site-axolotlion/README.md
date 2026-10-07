# Axolotlion website

One self-contained page (`index.html`, about 550 KB). Open it in a browser or upload it to any static host (Vercel, Netlify, GitHub Pages, Cloudflare Pages).

- Tap the character: he jumps and toots (sounds are synthesised in the browser, no audio files). Hold to build up a bigger one.
- Running section: four legs and a tail animate with CSS.
- Meme maker: caption, download as PNG.
- Fill in `CONFIG` at the top of the script in `index.template.html` (contract address, pump.fun, DexScreener, X, Telegram), then run `python3 build.py`. Empty values stay hidden.

Rebuild: `python3 prep_assets.py` (only if art changed) then `python3 build.py`.
