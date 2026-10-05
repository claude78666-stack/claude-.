// Orchestrates the checks for one token and returns a structured report.
import { BASE58, bestPair, marketSnapshot, countCopycats, marketChecks, onchainChecks, analyzeHolders, holderChecks } from './checks.js';
import { scoreFindings, verdictFor, buildSummary, DISCLAIMER } from './score.js';
import { makeSources } from './sources.js';

export class InputError extends Error {}

const attempt = async (id, fn, skipped) => {
  try { return await fn(); } catch (e) { skipped.push({ id, reason: e.message || String(e) }); return undefined; }
};

export async function checkToken(mint, { sources = makeSources(), now = Date.now() } = {}) {
  if (typeof mint !== 'string' || !BASE58.test(mint)) throw new InputError('That does not look like a Solana token address.');

  const skipped = [];
  const pairs = (await attempt('market', () => sources.pairs(mint), skipped)) || [];
  const pair = bestPair(pairs);
  const market = marketSnapshot(pair, now);
  const symbol = pair?.baseToken?.symbol || '?';
  const name = pair?.baseToken?.name || null;

  const [copySearch, mintInfo] = await Promise.all([
    pair ? attempt('copycats', () => sources.copycats(symbol), skipped) : undefined,
    attempt('mint_authorities', () => sources.mintInfo(mint), skipped),
  ]);
  // RPC calls run one after another to stay inside public rate limits.
  const rawHolders = mintInfo ? await attempt('holders', () => sources.holders(mint), skipped) : undefined;
  const creator = mintInfo ? await attempt('creator', () => sources.creator(mint), skipped) : undefined;

  const findings = [];
  if (market) findings.push(...marketChecks(market, symbol, copySearch ? countCopycats(copySearch, symbol, now) : 0));
  if (mintInfo) findings.push(...onchainChecks(mintInfo));
  const holders = mintInfo && rawHolders?.length
    ? analyzeHolders({ holders: rawHolders, supply: mintInfo.supply, pairAddress: market?.pairAddress, dexId: market?.dex, creator })
    : null;
  findings.push(...holderChecks(holders));

  const ran = ['market', 'copycats', 'mint_authorities', 'holders', 'creator'].filter((id) => !skipped.some((s) => s.id === id) && (id !== 'market' || pair) && (id !== 'copycats' || pair));
  if (!pair && !skipped.some((s) => s.id === 'market')) skipped.push({ id: 'market', reason: 'No trading pair found on DexScreener (too new, wrong address, or not on Solana).' });

  const score = scoreFindings(findings);
  const limited = !mintInfo || !holders;
  const verdict = !pair && !mintInfo ? 'NOT FOUND' : verdictFor(score, { limited });

  return {
    mint,
    token: { name, symbol: pair ? symbol : null },
    checkedAt: new Date(now).toISOString(),
    verdict,
    score,
    findings,
    market,
    onchain: mintInfo ? { program: mintInfo.program, decimals: mintInfo.decimals, supply: mintInfo.supply, mintAuthority: mintInfo.mintAuthority, freezeAuthority: mintInfo.freezeAuthority, extensions: mintInfo.extensions.map((e) => e.name) } : null,
    holders,
    creator: creator || null,
    coverage: { ran, skipped },
    summary: buildSummary({ symbol, verdict, score, findings, skipped }),
    disclaimer: DISCLAIMER,
  };
}
