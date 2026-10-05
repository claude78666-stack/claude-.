#!/usr/bin/env node
// Usage: node src/cli.js <token-address> [--json]
import { checkToken, InputError } from './agent.js';

const args = process.argv.slice(2);
const json = args.includes('--json');
const mint = args.find((a) => !a.startsWith('--'));

if (!mint) {
  console.error('Usage: node src/cli.js <solana-token-address> [--json]');
  process.exit(2);
}
try {
  const report = await checkToken(mint);
  console.log(json ? JSON.stringify(report, null, 2) : report.summary);
} catch (e) {
  console.error(e instanceof InputError ? e.message : `Check failed: ${e.message}`);
  process.exit(1);
}
