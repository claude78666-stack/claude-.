import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from '../src/server.js';
import { InputError } from '../src/agent.js';

const start = async (opts) => {
  const server = createServer(opts);
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}`;
  return { base, close: () => new Promise((r) => server.close(r)) };
};

test('health, 404, bad method and CORS preflight', async () => {
  const s = await start({ check: async () => ({}) });
  try {
    assert.deepEqual(await (await fetch(`${s.base}/health`)).json(), { ok: true });
    assert.equal((await fetch(`${s.base}/nope`)).status, 404);
    assert.equal((await fetch(`${s.base}/check`, { method: 'POST' })).status, 405);
    const pre = await fetch(`${s.base}/check`, { method: 'OPTIONS' });
    assert.equal(pre.status, 204);
    assert.equal(pre.headers.get('access-control-allow-origin'), '*');
  } finally { await s.close(); }
});

test('input errors give 400, other errors give 502 without leaking details', async () => {
  const s = await start({ check: async (m) => { if (m === 'bad') throw new InputError('bad address'); throw new Error('secret internal detail'); } });
  try {
    const bad = await fetch(`${s.base}/check?mint=bad`);
    assert.equal(bad.status, 400);
    assert.equal((await bad.json()).error, 'bad address');
    const boom = await fetch(`${s.base}/check?mint=other`);
    assert.equal(boom.status, 502);
    assert.ok(!JSON.stringify(await boom.json()).includes('secret'));
  } finally { await s.close(); }
});

test('results are cached for repeat requests', async () => {
  let calls = 0;
  const s = await start({ check: async (m) => { calls++; return { mint: m, verdict: 'OK' }; } });
  try {
    const a = await (await fetch(`${s.base}/check?mint=abc`)).json();
    const b = await (await fetch(`${s.base}/check?mint=abc`)).json();
    assert.equal(a.cached, undefined);
    assert.equal(b.cached, true);
    assert.equal(calls, 1);
  } finally { await s.close(); }
});

test('rate limit returns 429 after the cap', async () => {
  const s = await start({ check: async () => ({ ok: 1 }), rateLimit: { max: 2, windowMs: 60_000 } });
  try {
    assert.equal((await fetch(`${s.base}/check?mint=a`)).status, 200);
    assert.equal((await fetch(`${s.base}/check?mint=b`)).status, 200);
    assert.equal((await fetch(`${s.base}/check?mint=c`)).status, 429);
  } finally { await s.close(); }
});
