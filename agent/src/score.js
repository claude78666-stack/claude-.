// Turns findings into a score, a verdict and a short report .
export const DISCLAIMER = 'Opinion based on public data. Can be wrong or out of date. Not financial advice.';

export function scoreFindings(findings) {
  return Math.min(100, findings.reduce((a, x) => a + x.severity, 0) * 10);
}

/** `limited` is true when on-chain checks could not run, so a clean result means less. */
export function verdictFor(score, { limited = false } = {}) {
  if (score > 40) return 'HIGH RISK';
  if (score > 10) return 'ELEVATED RISK';
  return limited ? 'LOW RISK (LIMITED CHECK)' : 'LOW RISK (SO FAR)';
}

export function buildSummary({ symbol, verdict, score, findings, skipped }) {
  const lines = [`Case file: $${symbol}. Verdict: ${verdict}. Risk score: ${score}/100.`];
  const sorted = [...findings].sort((a, b) => b.severity - a.severity);
  if (!sorted.length) lines.push('No red flags found in the data reached.');
  for (const x of sorted) lines.push(`- ${x.title}. ${x.detail}`);
  if (skipped.length) lines.push(`Could not check: ${skipped.map((s) => s.id).join(', ')}.`);
  lines.push(score > 40 ? 'Hold your nose.' : score > 10 ? 'Something smells off.' : 'Nose approves, cautiously.');
  lines.push(DISCLAIMER);
  return lines.join('\n');
}
