# Go — Porting Notes

## As source (porting OUT of Go)

- **Errors are values, no exceptions.** `if err != nil { return err }` is the
  whole model. Porting to an exception language: these are **normal returns**,
  map to the exception type only if the target has no error-value idiom — and
  preserve which errors are sentinel-vs-wrapped (`fmt.Errorf("%w", err)`).
- **`nil` is typed and pervasive.** A typed nil pointer is not the same as an
  interface nil — `var p *T = nil; var i any = p; i == nil` is **false** (Go's
  classic footgun). When porting out, do not collapse "nil interface" and "nil
  concrete pointer" into one null; in targets with `Option` they are different.
- **Goroutines are cheap, scheduled cooperatively at function-call boundaries
  (preemptive since 1.14 at async-signal points), with **no guaranteed
  scheduling**.** Channels synchronize; `select` multiplexes. Porting to OS
  threads is expensive and wrong (1:1); porting to Rust async needs a runtime;
  porting to Node/Python asyncio needs care — goroutines are M:N, not single-
  threaded like asyncio.
- **Interfaces are structural and implicit.** `type Reader interface { Read() }`
  is satisfied by *any* type with that method, no declaration. Porting to a
  nominal-trait target (Rust, Java) requires writing `impl Trait for Type` for
  every satisfying type; porting to TS is 1:1.
- **Slices are fat pointers (ptr+len+cap) over a backing array;** assigning a
  slice aliases the array. `append` may or may not copy. Porting to a target
  with value-semantic arrays (Rust `Vec`) changes aliasing — capture intent.
- **Maps are reference types, unordered, not concurrency-safe.** Iteration order
  is randomized. Porting to Rust `HashMap` (owned) or Java `HashMap` changes
  aliasing and ordering semantics.

## As target (porting INTO Go)

- **No exceptions.** S exceptions → `error` return values + `if err != nil`.
  Panics exist but are for *truly unrecoverable* bugs; do not port normal error
  paths to `panic`/`recover`. Checked exceptions with payloads → a typed `error`
  (struct implementing `Error() string`), often with `errors.Is`/`errors.As`.
- **No generics-free generics tricks.** Generics exist (1.18+) but are
  constrained. S's higher-kinded / variadic generics / compile-time metaprogramming
  have no direct equivalent — use codegen or `any` + type switch + `// TODO(port)`.
- **No method/operator overloading, no default args.** Port overloaded
  constructors to `NewX`, `NewXWithOptions` variants. Port operator overloading
  to named methods.
- **Nil interface trap when returning errors:** declare error return as the
  concrete error type or pre-wrap; returning a nil concrete pointer in an
  `error` interface yields a non-nil error. Test `err != nil` at the boundary.
- **Closures capture by reference** (loop variable capture was a pre-1.22 bug;
  1.22+ fixes per-loop semantics — confirm the Go version). Goroutine-per-loop
  needs the value copied if targeting <1.22.
- **`defer` runs at function end, LIFO**, and its args are evaluated at `defer`
  time. Map S's RAII/try-finally to `defer`; note `defer` is function-scoped,
  not block-scoped like Rust `Drop`.
- **Concurrency:** `sync.Mutex`/`RWMutex`, `sync.WaitGroup`, channels. Map S's
  condition variables to channels where idiomatic; `context.Context` threads
  cancellation — S code with cancellation tokens maps to `ctx` propagation.

## Idiom map (key traps)

| Source pattern | Go | Trap |
|---|---|---|
| exceptions | `error` return + `if err != nil` | Don't use `panic`; preserve error chain with `%w` |
| generics w/ constraints | `[T any]` / `[T Ordered]` | No higher-kinded; codegen for HKT |
| operator overloading | named method (`Add`) | No `+` overload |
| RAII/try-with-resources | `defer x.Close()` | Function-scoped, not block; args evaluated now |
| `Option<T>` | `*T` (nil) or `(T, bool)` | Nil-pointer deref panics; no compile-time null check |
| enums | `type Color int` + `const (...) iota` | Not type-safe by default; use `stringer` + careful |
| async/await tasks | goroutine + channel | Goroutines are not 1:1 threads, not single-threaded |
| set | `map[T]struct{}` | No built-in set |
| inheritance | embedding (composition) | No true inheritance; promote fields via embed |
