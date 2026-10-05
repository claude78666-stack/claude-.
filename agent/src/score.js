// Turns findings into a score, a verdict and a short report in Detective Sniffles' voice.
export const DISCLAIMER = 'Opinion based on public data. Can be wrong or out of date. Not financial advice.';

export function scoreFindings(findings) {
  return Math.min(100, findings.reduce((a, x) => a + x.severity, 0) * 10);
}

/** `limited` is true when on-chain checks could not run, so a clean result means less. */
export function verdictFor(score, { limited = false } = {}) {
  if (score > 40) return 'STINKS TO HIGH HEAVEN';
  if (score > 10) return 'SNIFFY';
  return limited ? 'NOTHING OBVIOUS (LIMITED CHECK)' : 'SMELLS CLEAN (SO FAR)';
}

const QUIPS = {
  no_liquidity: 'I sniffed everywhere for the pool. Even under the couch.',
  thin_liquidity: 'A puddle wearing a crown.',
  one_sided_flow: 'That smells like a robot with a keyboard.',
  very_new: 'Still has that new-puppy smell. Also that new-scam smell.',
  volume_churn: 'Hamster-wheel energy.',
  no_socials: 'A coin with no website is a dog with no bark.',
  copycats: 'Copycat trail. I follow it to a dead end.',
  crashed: 'I smell smoke. The fire already happened.',
  mint_authority: 'The printer is still plugged in.',
  freeze_authority: 'Someone is holding the freeze button.',
  top_holder: 'One big paw on the supply.',
  top10: 'A few paws hold most of the bone.',
  creator_holding: 'The launcher is still sitting on a big bag.',
};

export function buildSummary({ symbol, verdict, score, findings, skipped }) {
  const lines = [`Case file: $${symbol}. Verdict: ${verdict}. Stink meter: ${score}/100.`];
  const sorted = [...findings].sort((a, b) => b.severity - a.severity);
  if (!sorted.length) lines.push('My nose found no red flags in the data I could reach.');
  for (const x of sorted) lines.push(`- ${x.title}. ${x.detail}${QUIPS[x.id] ? ` ${QUIPS[x.id]}` : ''}`);
  if (skipped.length) lines.push(`Could not check: ${skipped.map((s) => s.id).join(', ')}.`);
  lines.push(DISCLAIMER);
  return lines.join('\n');
}
