# SI coin-check agent (Detective Sniffles)

A read-only checker for Solana tokens. Give it a token address, get back a risk score, a verdict and a list of findings. It never holds keys, never signs anything and never trades. Zero dependencies, Node 20+.

Verdicts: `SMELLS CLEAN (SO FAR)` · `SNIFFY` · `STINKS TO HIGH HEAVEN` · `NOTHING OBVIOUS (LIMITED CHECK)` (clean, but on-chain checks could not run) · `NOT FOUND`.

## Run it

```bash
cd agent
npm test                                   # 24 tests, no network needed
node src/cli.js <token-address>            # readable report
node src/cli.js <token-address> --json     # full structured report
npm run serve                              # HTTP API on :8787
npm run smoke                              # live run against a few real coins
```

## What it checks

| Group | Check | Source |
|---|---|---|
| Market | Pool cash vs market cap, one-sided buys/sells, brand-new coin, volume far above pool size, no website/socials, copycat tickers (last 72h), crashed, absurd price moves | DexScreener |
| On-chain | Mint authority still active, freeze authority present, risky Token-2022 extensions (permanent delegate, transfer hook, transfer fee, non-transferable, pausable) | Solana RPC |
| Holders | Biggest real holder, top-10 concentration (liquidity pools set aside), creator still holding a large share | Solana RPC (needs a personal key) |

Each finding has a severity (1 note, 2 warning, 3 serious). Score = sum of severities x 10, capped at 100. Over 40 is "stinks", over 10 is "sniffy".

## HTTP API

```
GET /health                      -> { "ok": true }
GET /check?mint=<address>        -> report (JSON)
```
Errors: `400` bad address, `429` rate limit (20/min per IP), `502` data sources down. Results are cached for 60 seconds. Report fields: `verdict`, `score`, `findings[]`, `market`, `onchain`, `holders`, `creator`, `coverage` (`ran` and `skipped` with reasons), `summary` (plain text), `disclaimer`.

## Settings (environment variables)

| Name | Default | Purpose |
|---|---|---|
| `SOLANA_RPC_URL` | public Solana RPC | **Set this to a personal RPC URL (for example a free Helius or QuickNode key) to turn on the holder checks.** The free public endpoints refuse that lookup (HTTP 429/403), so without a key the report says `holders` was skipped and uses the "limited check" verdict. |
| `PORT` | 8787 | HTTP port |
| `ALLOW_ORIGIN` | `*` | CORS origin allowed to call the API (set to your site's address when hosted) |

The RPC URL contains a secret. Keep it in the host's environment settings, never in the repo or the website.

## Honest limits

- Holder and creator checks are covered by unit tests but have **not** been run against a live RPC here (no key was available). Test with your own key before relying on them.
- It only sees coins that already have a trading pair. Coins launched minutes ago may show `NOT FOUND`.
- Creator detection is best effort and skipped for very busy tokens. It does not yet look at the creator's other launches.
- A clean result is not a safety guarantee. It reads public numbers and can be wrong or out of date. Not financial advice.

## Hosting it and connecting the website

1. **Host the agent** on any small Node host. On Render (works from a phone): New, Web Service, pick this repo and the branch, set **Root Directory** to `agent`, Build Command empty, **Start Command** `npm start`. Add the environment variables below. Railway, Fly or a $5 VPS work the same way.
2. **Set the environment variables:**
   - `ALLOW_ORIGIN` = the address your website is hosted at (for example `https://yoursite.example.com`). Use `*` only while testing.
   - `SOLANA_RPC_URL` = your personal RPC URL (optional, turns on the holder checks). Keep it in the host's settings, never in the repo.
3. **Check it is up:** open `https://your-agent-address/health`. It should say `{"ok":true}`.
4. **Connect the website** by rebuilding it with the agent's address, then upload the new `site/index.html` to wherever the site is hosted:

```bash
python3 site/build.py --agent-url=https://your-agent-address
```

With that address set, the Coin Sniffer sends each address to the agent and shows the full report (market numbers, mint and freeze authority, holder concentration). If the agent is down or unreachable, the page says so and falls back to the quick market-only check. Without the setting the site behaves as before.

The private preview page on claude.ai cannot call outside servers, so the connection only works on a normally hosted copy of the site.
