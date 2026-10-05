// Live smoke test: runs the agent against real, currently trading tokens and prints one line each.
// Usage: node scripts/smoke.js [mint ...]
import { checkToken } from '../src/agent.js';
import { fetchJson } from '../src/http.js';

let mints = process.argv.slice(2);
if (!mints.length) {
  // Pick a few currently active pump.fun coins plus a well-known one.
  const live = await fetchJson('https://frontend-api-v3.pump.fun/coins?offset=0&limit=3&sort=market_cap&order=DESC&includeNsfw=false');
  mints = [...live.slice(0, 3).map((c) => c.mint), '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump'];
}
for (const m of mints) {
  const t0 = Date.now();
  try {
    const r = await checkToken(m);
    const skipped = r.coverage.skipped.map((s) => s.id).join(',') || 'none';
    console.log(`$${(r.token.symbol || '?').padEnd(10)} ${r.verdict.padEnd(34)} score=${String(r.score).padStart(3)} flags=${r.findings.length} skipped=[${skipped}] ${Date.now() - t0}ms`);
  } catch (e) {
    console.log(`${m.slice(0, 8)}… FAILED: ${e.message}`);
  }
}
