// Tiny HTTP API:  GET /check?mint=<address>   GET /health
// Env: PORT (default 8787), ALLOW_ORIGIN (default *), SOLANA_RPC_URL (optional, enables holder checks).
import http from 'node:http';
import { checkToken, InputError } from './agent.js';

export function createServer({ check = checkToken, rateLimit = { max: 20, windowMs: 60_000 }, cacheMs = 60_000, allowOrigin = process.env.ALLOW_ORIGIN || '*' } = {}) {
  const hits = new Map();   // ip -> [timestamps]
  const cache = new Map();  // mint -> { at, body }

  const limited = (ip, now) => {
    const recent = (hits.get(ip) || []).filter((t) => now - t < rateLimit.windowMs);
    recent.push(now);
    hits.set(ip, recent);
    return recent.length > rateLimit.max;
  };

  return http.createServer(async (req, res) => {
    const send = (status, obj) => {
      res.writeHead(status, { 'content-type': 'application/json', 'access-control-allow-origin': allowOrigin, 'cache-control': 'no-store' });
      res.end(JSON.stringify(obj));
    };
    if (req.method === 'OPTIONS') { res.writeHead(204, { 'access-control-allow-origin': allowOrigin, 'access-control-allow-methods': 'GET', 'access-control-allow-headers': 'content-type' }); return res.end(); }
    if (req.method !== 'GET') return send(405, { error: 'Use GET.' });

    const url = new URL(req.url, 'http://x');
    if (url.pathname === '/health') return send(200, { ok: true });
    if (url.pathname !== '/check') return send(404, { error: 'Not found. Try /check?mint=<address>' });

    const now = Date.now();
    const ip = (req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').toString().split(',')[0].trim();
    if (limited(ip, now)) return send(429, { error: 'Too many requests. Try again in a minute.' });

    const mint = url.searchParams.get('mint') || '';
    const hit = cache.get(mint);
    if (hit && now - hit.at < cacheMs) return send(200, { ...hit.body, cached: true });
    try {
      const body = await check(mint);
      cache.set(mint, { at: now, body });
      send(200, body);
    } catch (e) {
      if (e instanceof InputError) return send(400, { error: e.message });
      send(502, { error: 'The check could not be completed. Try again shortly.' });
    }
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const port = Number(process.env.PORT) || 8787;
  createServer().listen(port, () => console.log(`SI coin-check agent listening on :${port}`));
}
