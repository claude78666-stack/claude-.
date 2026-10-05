import test from 'node:test';
import assert from 'node:assert/strict';
import { marketChecks, onchainChecks, analyzeHolders, holderChecks, countCopycats, bestPair, marketSnapshot } from '../src/checks.js';

const base = { marketCap: 1_000_000, liquidityUsd: 500_000, volume24h: 100_000, buys24h: 100, sells24h: 90, priceChange1h: 0, priceChange24h: 5, ageHours: 100, hasSocials: true };
const ids = (arr) => arr.map((x) => `${x.id}:${x.severity}`);

test('healthy token has no market findings', () => {
  assert.deepEqual(marketChecks(base, 'OK'), []);
});

test('thin liquidity scales with severity', () => {
  assert.deepEqual(ids(marketChecks({ ...base, liquidityUsd: 5_000 }, 'X')), ['thin_liquidity:3']);
  assert.deepEqual(ids(marketChecks({ ...base, liquidityUsd: 20_000 }, 'X')), ['thin_liquidity:2']);
  assert.deepEqual(ids(marketChecks({ ...base, liquidityUsd: 50_000 }, 'X')), ['thin_liquidity:1']);
});

test('no liquidity is serious', () => {
  assert.deepEqual(ids(marketChecks({ ...base, liquidityUsd: 0 }, 'X')), ['no_liquidity:3']);
});

test('one-sided flow: zero sells, heavy skew, mild skew, and too few trades', () => {
  assert.deepEqual(ids(marketChecks({ ...base, buys24h: 500, sells24h: 0 }, 'X')), ['one_sided_flow:3']);
  assert.deepEqual(ids(marketChecks({ ...base, buys24h: 1600, sells24h: 100 }, 'X')), ['one_sided_flow:2']);
  assert.deepEqual(ids(marketChecks({ ...base, buys24h: 700, sells24h: 100 }, 'X')), ['one_sided_flow:1']);
  assert.deepEqual(marketChecks({ ...base, buys24h: 100, sells24h: 0 }, 'X').filter((x) => x.id === 'one_sided_flow'), []);
});

test('age, socials, crash and wild moves', () => {
  assert.deepEqual(ids(marketChecks({ ...base, ageHours: 0.5 }, 'X')), ['very_new:2']);
  assert.deepEqual(ids(marketChecks({ ...base, ageHours: 3 }, 'X')), ['very_new:1']);
  assert.deepEqual(ids(marketChecks({ ...base, hasSocials: false }, 'X')), ['no_socials:1']);
  assert.deepEqual(ids(marketChecks({ ...base, priceChange24h: -90 }, 'X')), ['crashed:2']);
  assert.deepEqual(ids(marketChecks({ ...base, priceChange24h: 500000 }, 'X')), ['wild_move:1']);
});

test('copycat counting uses unique mints, same ticker, recent only', () => {
  const now = Date.now();
  const mk = (addr, sym, ageH, chain = 'solana') => ({ chainId: chain, baseToken: { symbol: sym, address: addr }, pairCreatedAt: now - ageH * 3.6e6 });
  const pairs = [mk('a', 'DOTF', 1), mk('a', 'DOTF', 1), mk('b', 'dotf', 5), mk('c', 'DOTF', 80), mk('d', 'DOTF', 2, 'base'), mk('e', 'OTHER', 1)];
  assert.equal(countCopycats(pairs, 'DOTF', now), 2);
  assert.deepEqual(ids(marketChecks(base, 'DOTF', 3)), ['copycats:2']);
  assert.deepEqual(ids(marketChecks(base, 'DOTF', 6)), ['copycats:3']);
  assert.deepEqual(marketChecks(base, 'DOTF', 2), []);
});

test('bestPair picks the deepest pool; snapshot handles missing pair', () => {
  assert.equal(bestPair([{ liquidity: { usd: 1 }, id: 'a' }, { liquidity: { usd: 9 }, id: 'b' }]).id, 'b');
  assert.equal(bestPair([]), null);
  assert.equal(marketSnapshot(null), null);
});

test('on-chain authority and extension findings', () => {
  assert.deepEqual(onchainChecks({ mintAuthority: null, freezeAuthority: null, extensions: [] }), []);
  assert.deepEqual(ids(onchainChecks({ mintAuthority: 'Aaaa1111bbbb', freezeAuthority: null, extensions: [] })), ['mint_authority:3']);
  assert.deepEqual(ids(onchainChecks({ mintAuthority: null, freezeAuthority: 'Cccc2222dddd', extensions: [] })), ['freeze_authority:2']);
  assert.deepEqual(ids(onchainChecks({ extensions: [{ name: 'permanentDelegate' }, { name: 'metadataPointer' }] })), ['ext_permanentDelegate:3']);
  const fee = onchainChecks({ extensions: [{ name: 'transferFeeConfig', state: { newerTransferFee: { transferFeeBasisPoints: 1000 } } }] });
  assert.deepEqual(ids(fee), ['ext_transferFee:3']);
  assert.deepEqual(onchainChecks({ extensions: [{ name: 'transferFeeConfig', state: { newerTransferFee: { transferFeeBasisPoints: 0 } } }] }), []);
});

test('holder analysis sets the pool aside and finds the creator', () => {
  const holders = [
    { tokenAccount: 't0', owner: 'POOL', amount: 400 },
    { tokenAccount: 't1', owner: 'CREATOR', amount: 120 },
    { tokenAccount: 't2', owner: 'W2', amount: 50 },
    { tokenAccount: 't3', owner: 'W3', amount: 30 },
  ];
  const h = analyzeHolders({ holders, supply: 1000, pairAddress: 'POOL', dexId: 'pumpswap', creator: 'CREATOR' });
  assert.equal(Math.round(h.poolPct), 40);
  assert.equal(Math.round(h.top1Pct), 12);
  assert.equal(Math.round(h.creatorPct), 12);
  assert.equal(h.top[0].label, 'liquidity pool');
  assert.deepEqual(ids(holderChecks(h)), ['top_holder:1', 'creator_holding:3']);
});

test('on pump.fun bonding curve the biggest account is treated as the curve', () => {
  const h = analyzeHolders({ holders: [{ owner: 'CURVE', amount: 800 }, { owner: 'A', amount: 100 }], supply: 1000, pairAddress: 'P', dexId: 'pumpfun', creator: null });
  assert.equal(Math.round(h.poolPct), 80);
  assert.equal(Math.round(h.top1Pct), 10);
});

test('concentration thresholds', () => {
  const mk = (top1, top10) => ({ top1Pct: top1, top10Pct: top10, creatorPct: 0 });
  assert.deepEqual(ids(holderChecks(mk(35, 80))), ['top_holder:3', 'top10:3']);
  assert.deepEqual(ids(holderChecks(mk(20, 55))), ['top_holder:2', 'top10:2']);
  assert.deepEqual(ids(holderChecks(mk(9, 40))), ['top_holder:1', 'top10:1']);
  assert.deepEqual(holderChecks(mk(5, 20)), []);
  assert.deepEqual(holderChecks(null), []);
});
