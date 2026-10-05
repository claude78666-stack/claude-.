# SI Agents site

Single-file demo site with all 10 characters. Everything runs in the browser; nothing is sent anywhere
except the Coin Sniffer's public DexScreener lookups. **Test mode: no coin, wallet or payments.**

- `index.template.html` — the page (edit this one)
- `build.py` — inlines the character SVGs and the site name into `index.html`
- Rename the whole site: `python3 site/build.py "New Name"`
- Characters: `../character/` (Judge SI) and `../character/cast/` (the other nine; regenerate with `node character/gen-cast.cjs`)
