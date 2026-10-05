// Pure check functions: data in, findings out. No network. Severity: 1 = note, 2 = warning, 3 = serious.
export const BASE58 = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;

// Wallets that hold pool liquidity and should not count as "whales".
const KNOWN_POOL_OWNERS = new Set([
  '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', // Raydium AMM authority
  'GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL', // Raydium CPMM authority
]);

const f = (id, severity, title, detail, data) => ({ id, severity, title, detail, ...(data ? { data } : {}) });
const n0 = (x) => Math.round(x).toLocaleString('en-US');
const pct = (x) => `${x.toFixed(1)}%`;

/** Pick the pair with the deepest liquidity. */
export function bestPair(pairs) {
  return [...pairs].sort((a, b) => (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0))[0] || null;
}

export function marketSnapshot(pair, now = Date.now()) {
  if (!pair) return null;
  return {
    dex: pair.dexId,
    pairAddress: pair.pairAddress,
    url: pair.url,
    marketCap: pair.marketCap || pair.fdv || 0,
    liquidityUsd: pair.liquidity?.usd || 0,
    volume24h: pair.volume?.h24 || 0,
    buys24h: pair.txns?.h24?.buys || 0,
    sells24h: pair.txns?.h24?.sells || 0,
    priceChange1h: pair.priceChange?.h1 ?? null,
    priceChange24h: pair.priceChange?.h24 ?? null,
    ageHours: pair.pairCreatedAt ? (now - pair.pairCreatedAt) / 3.6e6 : null,
    hasSocials: (pair.info?.websites?.length || 0) + (pair.info?.socials?.length || 0) > 0,
  };
}

/** Count other recent launches that reuse the ticker (includes this token itself). */
export function countCopycats(searchPairs, symbol, now = Date.now()) {
  const seen = new Set();
  for (const p of searchPairs) {
    if (p.chainId === 'solana' && p.baseToken?.symbol?.toLowerCase() === symbol.toLowerCase() && p.pairCreatedAt > now - 72 * 3.6e6) {
      seen.add(p.baseToken.address);
    }
  }
  return seen.size;
}

export function marketChecks(m, symbol, copycats = 0) {
  const out = [];
  if (!m.liquidityUsd) {
    out.push(f('no_liquidity', 3, 'No liquidity found', 'There is no pool cash on record, so there may be nothing to sell into.'));
  } else if (m.marketCap) {
    const ratio = m.marketCap / m.liquidityUsd;
    const x = Math.round(ratio);
    if (m.liquidityUsd / m.marketCap < 0.01) out.push(f('thin_liquidity', 3, 'Pool is tiny next to the market cap', `Market cap is ${n0(x)}x the cash in the pool. A small sale would move the price a lot.`, { ratio }));
    else if (m.liquidityUsd / m.marketCap < 0.03) out.push(f('thin_liquidity', 2, 'Thin pool', `Market cap is ${n0(x)}x the pool cash.`, { ratio }));
    else if (m.liquidityUsd / m.marketCap < 0.08) out.push(f('thin_liquidity', 1, 'Somewhat thin pool', `Market cap is ${n0(x)}x the pool cash.`, { ratio }));
  }
  const { buys24h: b, sells24h: s } = m;
  if (b + s > 200) {
    const r = s ? b / s : Infinity;
    if (s === 0 && b >= 100) out.push(f('one_sided_flow', 3, 'Nobody is selling', `${n0(b)} buys and zero sells in 24h. Real markets have sellers.`));
    else if (r > 15) out.push(f('one_sided_flow', 2, 'Buys outnumber sells heavily', `${n0(b)} buys vs ${n0(s)} sells in 24h. That pattern often means automated buying.`));
    else if (r > 6) out.push(f('one_sided_flow', 1, 'Buying is lopsided', `${n0(b)} buys vs ${n0(s)} sells in 24h.`));
  }
  if (m.ageHours !== null) {
    if (m.ageHours < 1) out.push(f('very_new', 2, 'Brand new', `Trading started ${Math.round(m.ageHours * 60)} minutes ago. There is no history to judge.`));
    else if (m.ageHours < 6) out.push(f('very_new', 1, 'Very new', `Trading started ${m.ageHours.toFixed(1)} hours ago.`));
  }
  if (m.liquidityUsd && m.volume24h / m.liquidityUsd > 20) {
    const x = Math.round(m.volume24h / m.liquidityUsd);
    out.push(f('volume_churn', x > 60 ? 2 : 1, 'Volume far above pool size', `24h volume is ${n0(x)}x the pool. That can be wash trading or a very hot coin.`));
  }
  if (!m.hasSocials) out.push(f('no_socials', 1, 'No website or socials listed', 'DexScreener has no links for this token.'));
  if (copycats >= 6) out.push(f('copycats', 3, 'Many copies of this ticker', `${copycats} different coins used $${symbol} in the last 3 days. Only one can be the original.`, { copycats }));
  else if (copycats >= 3) out.push(f('copycats', 2, 'Copycat tickers', `${copycats} different coins used $${symbol} in the last 3 days.`, { copycats }));
  if (m.priceChange24h !== null) {
    if (m.priceChange24h <= -80) out.push(f('crashed', 2, 'Already crashed', `Price is down ${Math.abs(Math.round(m.priceChange24h))}% in 24h.`));
    if (Math.abs(m.priceChange24h) > 100000) out.push(f('wild_move', 1, 'Absurd price move', `A 24h move of ${n0(m.priceChange24h)}% is either a data glitch or a one-off pump.`));
  }
  if (m.priceChange1h !== null && m.priceChange1h <= -50) out.push(f('dumping', 1, 'Falling fast', `Price is down ${Math.abs(Math.round(m.priceChange1h))}% in the last hour.`));
  return out;
}

const RISKY_EXTENSIONS = {
  permanentDelegate: [3, 'Permanent delegate', 'Someone can move or burn tokens out of any holder wallet.'],
  transferHook: [3, 'Transfer hook', 'Custom code runs on every transfer and could block selling.'],
  nonTransferable: [3, 'Non-transferable', 'Tokens cannot be moved or sold.'],
  pausableConfig: [2, 'Pausable', 'The token can be paused by its authority.'],
};

export function onchainChecks(mi) {
  const out = [];
  if (mi.mintAuthority) out.push(f('mint_authority', 3, 'More tokens can be created', `The mint authority (${short(mi.mintAuthority)}) can print new supply and dilute holders.`));
  if (mi.freezeAuthority) out.push(f('freeze_authority', 2, 'Tokens can be frozen', `A freeze authority (${short(mi.freezeAuthority)}) can freeze holder accounts.`));
  for (const e of mi.extensions || []) {
    const r = RISKY_EXTENSIONS[e.name];
    if (r) out.push(f(`ext_${e.name}`, r[0], r[1], r[2]));
    if (e.name === 'transferFeeConfig') {
      const bps = Math.max(e.state?.newerTransferFee?.transferFeeBasisPoints || 0, e.state?.olderTransferFee?.transferFeeBasisPoints || 0);
      if (bps > 0) out.push(f('ext_transferFee', bps >= 500 ? 3 : 2, 'Transfer fee', `Every transfer pays a ${(bps / 100).toFixed(2)}% fee.`));
    }
  }
  return out;
}

const short = (a) => (a ? `${a.slice(0, 4)}…${a.slice(-4)}` : 'unknown');

/** Concentration among real holders, with pool/curve accounts set aside. */
export function analyzeHolders({ holders, supply, pairAddress, dexId, creator }) {
  if (!holders?.length || !supply) return null;
  const rows = holders.map((h, i) => {
    const isPool = h.owner === pairAddress || KNOWN_POOL_OWNERS.has(h.owner) || (dexId === 'pumpfun' && i === 0);
    return { owner: h.owner, tokenAccount: h.tokenAccount, pct: (h.amount / supply) * 100, isPool, isCreator: !!creator && h.owner === creator };
  });
  const real = rows.filter((r) => !r.isPool);
  const sum = (arr) => arr.reduce((a, r) => a + r.pct, 0);
  return {
    poolPct: sum(rows.filter((r) => r.isPool)),
    top1Pct: real[0]?.pct ?? 0,
    top5Pct: sum(real.slice(0, 5)),
    top10Pct: sum(real.slice(0, 10)),
    creatorPct: sum(rows.filter((r) => r.isCreator)),
    top: rows.slice(0, 10).map((r) => ({ owner: r.owner ? short(r.owner) : 'unknown', pct: Number(r.pct.toFixed(2)), label: r.isPool ? 'liquidity pool' : r.isCreator ? 'creator' : 'wallet' })),
  };
}

export function holderChecks(h) {
  const out = [];
  if (!h) return out;
  if (h.top1Pct > 30) out.push(f('top_holder', 3, 'One wallet holds a huge share', `The largest real holder owns ${pct(h.top1Pct)} of the supply.`, { pct: h.top1Pct }));
  else if (h.top1Pct > 15) out.push(f('top_holder', 2, 'Large single holder', `The largest real holder owns ${pct(h.top1Pct)} of the supply.`, { pct: h.top1Pct }));
  else if (h.top1Pct > 8) out.push(f('top_holder', 1, 'Notable single holder', `The largest real holder owns ${pct(h.top1Pct)} of the supply.`, { pct: h.top1Pct }));
  if (h.top10Pct > 70) out.push(f('top10', 3, 'Supply is concentrated', `The top 10 real wallets own ${pct(h.top10Pct)} of the supply.`, { pct: h.top10Pct }));
  else if (h.top10Pct > 50) out.push(f('top10', 2, 'Fairly concentrated supply', `The top 10 real wallets own ${pct(h.top10Pct)}.`, { pct: h.top10Pct }));
  else if (h.top10Pct > 35) out.push(f('top10', 1, 'Moderately concentrated supply', `The top 10 real wallets own ${pct(h.top10Pct)}.`, { pct: h.top10Pct }));
  if (h.creatorPct > 10) out.push(f('creator_holding', 3, 'Creator holds a big bag', `The wallet that launched this coin still holds ${pct(h.creatorPct)}.`, { pct: h.creatorPct }));
  else if (h.creatorPct > 5) out.push(f('creator_holding', 2, 'Creator holds a notable share', `The wallet that launched this coin still holds ${pct(h.creatorPct)}.`, { pct: h.creatorPct }));
  return out;
}
