# Example: Go → TypeScript (concurrent fetcher)

A worked end-to-end port following `code-port`. `main.go` → `main.ts`, both
type-check. Use this as a reference for how the concurrency/error/interface axes
translate.

## Source

A concurrent URL fetcher: a `Fetcher` interface, an `httpFetcher` impl, a
`fetchAll` that fans out goroutines under a `WaitGroup` writing into a
pre-sized `results` slice, then prints body lengths or errors. Exercises
goroutines→async, error-values→throw, nominal→structural interfaces, and
`defer` cleanup.

## Axis classification (load `references/go.md` + `references/typescript.md`)

| Axis | Go (S) | TypeScript (T) | Decision |
|------|--------|----------------|----------|
| Typing | nominal interface | structural interface | **1:1** — both structural-ish; the `Fetcher` interface ports verbatim |
| Error | `(string, error)` value-tuple | throw + `try/catch` | dual mapping: `Fetch` boundary → `throw`; `fetchAll` aggregation still collects `Result.err` (value), preserving Go's behavior |
| Concurrency | goroutines + `WaitGroup` writing `results[idx]` | `Promise.all` (eager, single-threaded) | concurrency preserved, **parallelism not** (Node is single-threaded; Go was M:N) — flagged `// PORT NOTE` |
| Cleanup | `defer resp.Body.Close()` | fetch drains body automatically | no manual close needed in the web `fetch` API |
| Bytes | `len(string)` = bytes | `.length` = UTF-16 code units | flagged `// TODO(port)` — real divergence, needs `TextEncoder` for byte count |

## Phase A → Phase B

- **Phase A** — wrote `main.ts`; `// PORT NOTE` marks the goroutine→Promise and
  defer→fetch-drain decisions; `// TODO(port)` records the byte-vs-char length.
- **Phase B** — `tsc --noEmit --strict --target es2022 --lib es2022,dom main.ts`
  → **exit 0**. `go vet ./...` on the source → **exit 0**.

## Notes

- The error-model decision is the interesting one: Go returns errors as values,
  so `Fetch` returning `(string, error)` and `fetchAll` collecting `Result.Err`
  are the *same* mechanism. In TS the idiomatic form is `throw`, so `Fetch`
  throws — but `fetchAll` deliberately `try/catch`es back into `Result.err` to
  keep the aggregation behavior (caller sees per-URL success/failure, not one
  throw aborting the batch). This is §Error model "preserve the failure-vs-
  success aggregation the source made."
- `todos: 1` in the trailer — the byte/char length, honestly counted.
- Confidence `high` on structure; the single `TODO` is a real semantic gap, not
  uncertainty about the port.
