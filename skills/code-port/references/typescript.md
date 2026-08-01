# TypeScript — Porting Notes

## As source (porting OUT of TypeScript)

- **Types are erased at runtime.** TS types exist only at compile time; runtime
  is JS. `interface`/`type`/generics vanish — porting to a runtime-typed target
  (Python) is near 1:1; to a nominal target (Rust/Java) requires turning every
  `interface` into a declared trait/type. `any`/`unknown`/casts (`as`) are
  escape hatches that hide real type uncertainty — capture *why* the cast was
  there, it's often "JSON shape I can't verify."
- **Structural typing.** `type Pt = { x: number }` — any object with an `x`
  matches. Nominal targets (Rust, Java, Swift) need an explicit struct/class;
  duck-typed matches become explicit interfaces. Porting to Go (structural
  interfaces) is closer but Go interfaces are method-sets, not field-shapes.
- **`null` and `undefined` are two different things.** `null` = explicit absence,
  `undefined` = uninitialized/missing. Strict-mode code often collapses to one,
  but the distinction leaks (optional params default to `undefined`, JSON has no
  `undefined`). Porting to `Option`/nullable, decide which maps to None — usually
  both, but flag where S treated them differently.
- **Union types + narrowing** (`x: A | B`, then `if (x.kind === 'a')`). This is
  sum-type ergonomics via control-flow. Port to the target's enum/sum type
  (Rust enum, Kotlin sealed class) — `switch` on a discriminant becomes `match`.
  **Discriminated unions are the portable pattern;** `string`-tagged unions need
  care (the tag must be `const`/literal).
- **`Promise`/`async`/`await`** — single-threaded event loop, microtask queue,
  eager (a `Promise` starts running when created). Porting to Rust needs a
  runtime + lazy futures (different semantics); to Go, goroutines + channels
  (no single-thread guarantee); to Python, asyncio (closest, also eager-ish).
- **Prototypal + class sugar.** ES6 `class` is sugar over prototypes; `this`
  binding is dynamic and a famous trap (detached callbacks). Port `this`-reliant
  code carefully — capture into closures or explicit receiver params.
- **`===` vs `==`.** Porting equality: `===` is strict; targets without type
  coercion (Rust, Go) have one `==`. Do not port `==` coercion bugs.

## As target (porting INTO TypeScript)

- **Nominal → structural:** S's nominal class still works as a `class`, but TS
  structurally matches any compatible shape. To enforce nominal-ness, use a
  branded/opaque type (`type UserId = string & { __brand: 'UserId' }`) where S
  required distinctness.
- **Sum types → discriminated unions.** S enums/Rust variants → `type X =
  { kind: 'a'; ... } | { kind: 'b'; ... }` with a literal `kind`. Add an
  `_tag`/`kind` discriminant — TS narrowing needs it. Exhaustiveness via
  `assertNever(x)`.
- **`null`/`undefined` discipline.** With `strictNullChecks`, model S's `Option`
  as `T | null` (or `T | undefined`); prefer one consistently. S checked
  exceptions → throw (no checked exceptions in TS) or a `Result`-type library
  (`neverthrow`) if you want value-errors.
- **No checked exceptions, no overload resolution by return type.** S method
  overloads → TS function overloads (signatures) but the *implementation* is one
  body — type-narrow inside. Runtime can't distinguish, so guard with `typeof`/
  `Array.isArray`/discriminants.
- **GC + event loop.** RAII/`Drop` → `using` (ES2025 explicit resource mgmt) or
  `try/finally`. Deterministic teardown needs explicit `dispose()`.
- **Generics are reified-erased** but TS can express higher-kinded-ish patterns
  via conditional/mapped types. S's `const` generics / value-level params → TS
  `const` type params (5.0+) or literal types.
- **Beware `.toString()`/coercion** when porting numeric/byte code — TS `number`
  is f64, no `int`/`bigint` by default. S integers >2^53 need `bigint`.

## Idiom map (key traps)

| Source pattern | TypeScript | Trap |
|---|---|---|
| `Option<T>` | `T \| null` (strict) | Pick `null` or `undefined` consistently |
| enum (nominal) | discriminated union or `enum` (string) | Numeric `enum` is quirky; prefer union |
| RAII `Drop` | `using` (ES2025) / `try/finally` | Manual otherwise |
| generics | `<T>` | Reified-erased; `typeof` can't see `T` |
| switch exhaustiveness | `switch` + `assertNever` | No compiler-enforced exhaustiveness otherwise |
| checked exception | throw (unchecked) or `Result` lib | No `throws` in type signature |
| operator overloading | not supported | Use named methods |
| `void*` / any | `unknown` then narrow | Avoid `any`; it opts out of checking |
