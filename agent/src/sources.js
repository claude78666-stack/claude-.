// Data sources. Everything here is read-only. Each method can be replaced in tests.
import { fetchJson } from './http.js';

const DEFAULT_RPC = 'https://api.mainnet-beta.solana.com';

export function makeRpc(url = process.env.SOLANA_RPC_URL || DEFAULT_RPC) {
  let id = 0;
  const call = async (method, params) => {
    const res = await fetchJson(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: ++id, method, params }),
      retries: 3,
    });
    if (res.error) throw Object.assign(new Error(res.error.message || 'RPC error'), { code: res.error.code });
    return res.result;
  };
  call.isPublicDefault = url === DEFAULT_RPC;
  return call;
}

export function makeSources({ rpc = makeRpc() } = {}) {
  return {
    /** All DEX pairs for a token mint (DexScreener). */
    async pairs(mint) {
      const arr = await fetchJson(`https://api.dexscreener.com/tokens/v1/solana/${mint}`);
      return Array.isArray(arr) ? arr : [];
    },

    /** Pairs found when searching a ticker, used to spot copycat launches. */
    async copycats(symbol) {
      const d = await fetchJson(`https://api.dexscreener.com/latest/dex/search?q=${encodeURIComponent(symbol)}`);
      return d.pairs || [];
    },

    /** Mint account: authorities, supply, Token-2022 extensions. */
    async mintInfo(mint) {
      const r = await rpc('getAccountInfo', [mint, { encoding: 'jsonParsed' }]);
      const parsed = r?.value?.data?.parsed;
      if (!parsed || parsed.type !== 'mint') throw new Error('Address is not a token mint');
      const i = parsed.info;
      return {
        program: r.value.data.program,
        decimals: i.decimals,
        supply: Number(BigInt(i.supply)) / 10 ** i.decimals,
        mintAuthority: i.mintAuthority || null,
        freezeAuthority: i.freezeAuthority || null,
        extensions: (i.extensions || []).map((e) => ({ name: e.extension, state: e.state || null })),
      };
    },

    /** Top 20 token accounts with the wallet that owns each. Needs an RPC that allows indexed calls. */
    async holders(mint) {
      const largest = await rpc('getTokenLargestAccounts', [mint]);
      const accounts = largest?.value || [];
      if (!accounts.length) return [];
      const info = await rpc('getMultipleAccounts', [accounts.map((a) => a.address), { encoding: 'jsonParsed' }]);
      return accounts.map((a, idx) => ({
        tokenAccount: a.address,
        owner: info?.value?.[idx]?.data?.parsed?.info?.owner || null,
        amount: a.uiAmount ?? Number(a.amount) / 10 ** a.decimals,
      }));
    },

    /** Best-effort creator lookup: fee payer of the oldest transaction. Skipped for busy tokens. */
    async creator(mint) {
      const sigs = await rpc('getSignaturesForAddress', [mint, { limit: 1000 }]);
      if (!sigs.length || sigs.length >= 1000) return null;
      const oldest = sigs[sigs.length - 1].signature;
      const tx = await rpc('getTransaction', [oldest, { encoding: 'jsonParsed', maxSupportedTransactionVersion: 0 }]);
      const key = tx?.transaction?.message?.accountKeys?.[0];
      return (typeof key === 'string' ? key : key?.pubkey) || null;
    },
  };
}
