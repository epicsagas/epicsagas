# Swift — Porting Notes

## As source (porting OUT of Swift)

- **ARC (Automatic Reference Counting), deterministic.** `strong` (default,
  owns), `weak` (zeroing, non-owning), `unowned` (non-zeroing, crashes if
  dead). Reference cycles leak under ARC — Swift relies on `weak`/`unowned` to
  break them. Porting to a tracing-GC target (Go/Java/Python): cycles collect
  automatically — `weak`/`unowned` become ordinary references, but *re-check
  every cycle* that Swift broke with `weak`, since GC behavior differs. Porting
  to Rust: ARC↔`Arc`, `weak`↔`Weak`, but Swift value types (`struct`/`enum`)
  are *not* reference-counted — they're stack/copied — map to Rust owned values.
- **Value types (`struct`/`enum`) vs reference types (`class`).** `struct`
  copies on assignment (value semantics), `class` is reference. Mutation of a
  `struct` via `mutating` requires exclusive access. Porting to a reference-only
  target (Java): structs become immutable classes; to Go, structs map naturally
  (Go structs are value types too); to Rust, `struct`↔`struct`, `class`↔`Box`.
- **Optionals are enforced (`Optional<T>` = `T?`).** Non-optional `T` cannot be
  nil — compile-time guarantee via flow analysis. `!` (force-unwrap) crashes on
  nil. Porting to Kotlin (`T?`/`T`), Rust (`Option<T>`), C# (NRTs) is close. To
  Java/Python/JS (unchecked nulls) the safety is lost — capture which were
  non-optional (can't be null) vs optional.
- **Protocols are nominal (declared conformance) with default methods** + protocol
  extensions (retroactive conformance via extension). Like Rust traits. Porting
  to Go (structural interfaces) loses declared-conformance check; to Java
  interfaces (default methods since 8) is close.
- **`async`/`await` + structured concurrency** (`async let`, `TaskGroup`,
  `Actor`). Actors serialize access; `Sendable` marks thread-safe types
  (enforced). Cancellation is cooperative. Porting to Rust async (lazy futures,
  needs runtime), Kotlin coroutines (closest), Go goroutines (no actor
  isolation), Python asyncio (single-threaded).
- **Generics with associated types & constraints (`where T: Protocol`).**
  Reified (unlike JVM). Porting to Rust traits/associated types is close; to
  JVM (erased) loses runtime type info.
- **Error handling: `throws`/`try`/`catch`** — checked-style (propagation
  explicit), no checked-exception-declaration like Java but `throws` annotates.
  Porting to Rust `Result`, Go error-values, Python exceptions.

## As target (porting INTO Swift)

- **`struct` vs `class` is the first decision.** Default to `struct` (value
  type) for data; `class` only when you need identity/inheritance/shared
  mutation. Porting from a reference-only language, most data → `struct`.
- **`Optional<T>` enforced.** Port nullable refs to `T?`, non-null to `T`. S
  `Option<T>`/`Result` → `T?` / `throws`. Force-unwrap (`!`) only with proof.
- **`let` (immutable) vs `var` (mutable)** — default to `let`. `mutating` methods
  on structs; `inout` params.
- **ARC, manage cycles.** Use `weak`/`unowned` for back-references in parent↔child.
  Prefer value types to avoid cycles entirely. No `deinit`-as-cleanup reliance
  for prompt teardown (ARC frees when refcount hits 0, but cycles leak).
- **`Codable`** for serialization (S's serde/JSON libs → `Codable` + `JSONDecoder`).
- **`Sendable` + actors for concurrency.** S threads/locks → `actor` isolation or
  `DispatchQueue`; mark cross-thread types `Sendable`. `async`/`await` is the
  modern path; GCD (`DispatchQueue`) is legacy.
- **No exceptions; `throws`.** S exceptions → `throws` funcs, `try`/`catch`. Define
  `enum Error: Error` conformances.
- **Objective-C interop** — `@objc`/`dynamic` for runtime/dispatch; bridge via
  `NSString`/`NSArray` at FFI. C interop via module imports.

## For dynamic-language readers: Phase A/B here

Swift is a compiled, statically-typed language. **Phase A** = logic-correct
draft (may not compile); **Phase B** = `swiftc`/`swift build` type-checks +
tests pass. Same as Rust/Go model — unlike Python/TS, there is a real compiler.

## Idiom map (key traps)

| Source pattern | Swift | Trap |
|---|---|---|
| `Option<T>` | `T?` (Optional) | Enforced; `!` crashes |
| checked exception | `throws` + `try/catch` | Propagation explicit |
| RAII `Drop` / `deinit` | `deinit` (classes) | Only reference types; cycles leak under ARC |
| value type / struct | `struct` | Copies on assignment; `mutating` to change |
| generics w/ bounds | `<T: Protocol>` | Reified; associated types |
| async runtime | `async`/`await` + `actor`/`Task` | Cooperative cancellation; `Sendable` enforced |
| operator overload | supported (static funcs) | Idiomatic for math/value types |
| tagged union | `enum` with associated values | Swift enums are sum types; exhaustive `switch` |
