import test from 'node:test';
import assert from 'node:assert/strict';
import { checkToken, InputError } from '../src/agent.js';
import { scoreFindings, verdictFor, buildSummary } from '../src/score.js';

const MINT = 'SH6SfUf5pPbdq9h7RjnsoGjNvP3onox7P5tKJGEpump';
const NOW = Date.parse('2026-10-05T12:00:00Z');

const pair = (over = {}) => ({
  dexId: 'pumpswap', pairAddress: 'POOL', url: 'https://dexscreener.com/solana/pool',
  baseToken: { address: MINT, name: 'Test Coin', symbol: 'TEST' },
  marketCap: 1_000_000, liquidity: { usd: 400_000 }, volume: { h24: 50_000 },
  txns: { h24: { buys: 100, sells: 90 } }, priceChange: { h1: 1, h24: 2 },
  pairCreatedAt: NOW - 100 * 3.6e6, info: { websites: [{ url: 'https://x.test' }] }, ...over,
});

const goodSources = (over = {}) => ({
  pairs: async () => [pair()],
  copycats: async () => [],
  mintInfo: async () => ({ program: 'spl-token', decimals: 6, supply: 1000, mintAuthority: null, freezeAuthority: null, extensions: [] }),
  holders: async () => [{ tokenAccount: 't', owner: 'POOL', amount: 300 }, { tokenAccount: 't2', owner: 'W', amount: 20 }],
  creator: async () => 'CREATOR',
  ...over,
});

test('rejects invalid addresses', async () => {
  await assert.rejects(() => checkToken('hello', { sources: goodSources(), now: NOW }), InputError);
  await assert.rejects(() => checkToken(undefined, { sources: goodSources(), now: NOW }), InputError);
});

test('clean token with full coverage', async () => {
  const r = await checkToken(MINT, { sources: goodSources(), now: NOW });
  assert.equal(r.verdict, 'LOW RISK (SO FAR)');
  assert.equal(r.score, 0);
  assert.deepEqual(r.coverage.skipped, []);
  assert.equal(r.token.symbol, 'TEST');
  assert.equal(r.creator, 'CREATOR');
  assert.ok(r.holders && r.holders.top1Pct > 0);
  assert.match(r.summary, /No red flags/);
});

test('risky token is flagged and scored', async () => {
  const sources = goodSources({
    pairs: async () => [pair({ liquidity: { usd: 3_000 }, txns: { h24: { buys: 900, sells: 5 } }, info: {} })],
    mintInfo: async () => ({ program: 'spl-token', decimals: 6, supply: 1000, mintAuthority: 'Mint1111aaaa', freezeAuthority: null, extensions: [] }),
  });
  const r = await checkToken(MINT, { sources, now: NOW });
  assert.equal(r.verdict, 'HIGH RISK');
  assert.ok(r.score > 40);
  const ids = r.findings.map((x) => x.id);
  for (const id of ['thin_liquidity', 'one_sided_flow', 'no_socials', 'mint_authority']) assert.ok(ids.includes(id), id);
});

test('holder lookup failing is reported, not fatal, and lowers confidence', async () => {
  const sources = goodSources({ holders: async () => { throw new Error('Indexed requests require a personal token'); } });
  const r = await checkToken(MINT, { sources, now: NOW });
  assert.equal(r.verdict, 'LOW RISK (LIMITED CHECK)');
  assert.deepEqual(r.coverage.skipped.map((s) => s.id), ['holders']);
  assert.match(r.summary, /Could not check: holders/);
});

test('no trading pair: on-chain checks still run', async () => {
  const r = await checkToken(MINT, { sources: goodSources({ pairs: async () => [] }), now: NOW });
  assert.equal(r.market, null);
  assert.ok(r.coverage.skipped.some((s) => s.id === 'market'));
  assert.notEqual(r.verdict, 'NOT FOUND');
});

test('nothing reachable at all gives NOT FOUND', async () => {
  const boom = async () => { throw new Error('down'); };
  const r = await checkToken(MINT, { sources: goodSources({ pairs: async () => [], mintInfo: boom }), now: NOW });
  assert.equal(r.verdict, 'NOT FOUND');
});

test('market source down is reported', async () => {
  const r = await checkToken(MINT, { sources: goodSources({ pairs: async () => { throw new Error('dex down'); } }), now: NOW });
  assert.ok(r.coverage.skipped.some((s) => s.id === 'market' && /dex down/.test(s.reason)));
});

test('score is capped and verdict tiers', () => {
  assert.equal(scoreFindings([{ severity: 3 }, { severity: 3 }, { severity: 3 }, { severity: 3 }]), 100);
  assert.equal(scoreFindings([]), 0);
  assert.equal(verdictFor(0), 'LOW RISK (SO FAR)');
  assert.equal(verdictFor(10), 'LOW RISK (SO FAR)');
  assert.equal(verdictFor(20), 'ELEVATED RISK');
  assert.equal(verdictFor(50), 'HIGH RISK');
  assert.equal(verdictFor(0, { limited: true }), 'LOW RISK (LIMITED CHECK)');
});

test('summary lists findings worst-first and ends with the disclaimer', () => {
  const s = buildSummary({ symbol: 'X', verdict: 'ELEVATED RISK', score: 20, skipped: [], findings: [{ id: 'no_socials', severity: 1, title: 'No socials', detail: 'none.' }, { id: 'mint_authority', severity: 3, title: 'Mint open', detail: 'open.' }] });
  assert.ok(s.indexOf('Mint open') < s.indexOf('No socials'));
  assert.match(s, /Not financial advice\.$/);
});
