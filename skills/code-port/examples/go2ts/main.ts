// Port of main.go (concurrent URL fetcher) — Go -> TypeScript.
// Phase A draft, verified to type-check in Phase B (tsc --strict).
//
// Axis classification (S=Go, T=TypeScript):
//   Typing:      nominal interface -> structural interface (1:1 in TS).
//   Error:       (string, error) value-tuples -> throw + try/catch. fetchAll
//                still aggregates into Result.Err (value), preserving behavior;
//                only the *transport* (Fetch return) moved from value to throw.
//   Concurrency: goroutines + WaitGroup writing results[idx] -> Promise.all
//                (eager, single-threaded event loop). Concurrency preserved,
//                not parallelism (Node is single-threaded; Go was M:N). Flagged.
//   Cleanup:     `defer resp.Body.Close()` -> fetch drains the body automatically
//                (no manual close needed in the web fetch API).
//   Bytes:       Go len(string)=bytes; TS .length=UTF-16 units -> TODO(port).

interface Fetcher {
  fetch(url: string): Promise<string>;
}

class HttpFetcher implements Fetcher {
  async fetch(url: string): Promise<string> {
    // PORT NOTE: Go http.Get + io.ReadAll + defer Close; web fetch drains itself.
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}`);
    }
    return await resp.text();
  }
}

interface Result {
  url: string;
  body: string;
  err: Error | null;
}

async function fetchAll(f: Fetcher, urls: string[]): Promise<Result[]> {
  const results: Result[] = new Array<Result>(urls.length);
  // PORT NOTE: Go spawns a goroutine per url writing results[idx] under a
  // WaitGroup; here Promise.all awaits all in flight. Field order preserved.
  await Promise.all(
    urls.map(async (url, idx) => {
      try {
        const body = await f.fetch(url);
        results[idx] = { url, body, err: null };
      } catch (e) {
        results[idx] = {
          url,
          body: "",
          err: e instanceof Error ? e : new Error(String(e)),
        };
      }
    }),
  );
  return results;
}

async function main(): Promise<void> {
  const urls = ["https://example.com", "https://example.org"];
  const res = await fetchAll(new HttpFetcher(), urls);
  for (const r of res) {
    if (r.err) {
      console.log(`${r.url}: error: ${r.err.message}`);
      continue;
    }
    // TODO(port): Go len(string) counts bytes; TS .length counts UTF-16 code units.
    console.log(`${r.url}: ${r.body.length} chars`);
  }
}

main();

// ──────────────────────────────────────────────────────────────────────────
// PORT STATUS
//   source:     main.go (55 lines)
//   confidence: high
//   todos:      1 (byte-vs-char length on r.body)
//   notes:      error model mapped value->throw at the Fetch boundary, kept as
//               value (Result.err) at the aggregation boundary, matching Go.
//               Concurrency preserved; parallelism not (single-threaded runtime).
// ──────────────────────────────────────────────────────────────────────────
