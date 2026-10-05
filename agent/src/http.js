// Small fetch wrapper: timeout + retry with backoff on rate limits and server errors.
export class HttpError extends Error {
  constructor(status, url, body) {
    super(`HTTP ${status} from ${new URL(url).host}`);
    this.status = status;
    this.body = String(body || '').slice(0, 300);
  }
}

const RETRY_STATUS = new Set([429, 500, 502, 503, 504]);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function fetchJson(url, { method = 'GET', headers = {}, body, timeoutMs = 15000, retries = 2 } = {}) {
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), timeoutMs);
    try {
      const res = await fetch(url, { method, headers: { 'user-agent': 'si-coin-check-agent/0.1', ...headers }, body, signal: ac.signal });
      const text = await res.text();
      if (!res.ok) {
        const err = new HttpError(res.status, url, text);
        if (RETRY_STATUS.has(res.status) && attempt < retries) { lastErr = err; await sleep(500 * 2 ** attempt); continue; }
        throw err;
      }
      try { return JSON.parse(text); } catch { throw new Error(`Bad JSON from ${new URL(url).host}`); }
    } catch (e) {
      if (e instanceof HttpError) throw e;
      lastErr = e.name === 'AbortError' ? new Error(`Timeout after ${timeoutMs}ms from ${new URL(url).host}`) : e;
      if (attempt < retries) { await sleep(500 * 2 ** attempt); continue; }
      throw lastErr;
    } finally {
      clearTimeout(timer);
    }
  }
  throw lastErr;
}
