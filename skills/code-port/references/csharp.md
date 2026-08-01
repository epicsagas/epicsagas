# C# — Porting Notes

## As source (porting OUT of C#)

- **Nullable reference types (8.0+) are *annotations*, not enforcement** without
  `?`-aware flow analysis on. `string` vs `string?` is documentation + compiler
  warnings, not runtime guarantees. Treat every reference as potentially null at
  a trust boundary; `!` (null-forgiving) is an unchecked assertion. Porting out,
  capture the `?` annotations as real nullability.
- **`IDisposable` + `using` / `Dispose()`** is deterministic cleanup (RAII-ish).
  `using var x = ...;` disposes at scope end; `using (...) {}` is a block.
  Finalizers (`~T()`) are separate and non-deterministic (GC). Port the `using`
  pattern to the target's RAII; do not confuse finalizer with deterministic
  dispose.
- **`async`/`await` returns `Task`/`Task<T>`/`ValueTask`**, eager-starting on a
  thread pool / sync context. `ValueTask` avoids allocation for sync-completed
  paths. Porting to Rust needs lazy futures + runtime; to Python asyncio
  (closest); to Go goroutines (different model).
- **LINQ** is lazy sequence operators (`Where`, `Select`, `SelectMany`) over
  `IEnumerable<T>` — deferred execution. Porting to Rust iterators / Kotlin
  sequences / Python generators is close, but LINQ-to-objects vs LINQ-to-SQL
  differ; capture which. `.ToList()` materializes.
- **Generics are reified** (unlike JVM) — you can `typeof(T)`, `new T()` (with
  `new()` constraint), runtime type checks. Porting to erased targets (JVM,
  Python) loses runtime type info; to monomorphizing targets (Rust/C++) it's
  codegen.
- **`struct` (value type) vs `class` (reference type).** `struct` copies on
  assignment, stack-allocated (usually), no inheritance (only interfaces).
  Mutable structs are a famous footgun. Port value semantics (struct) to
  target's value type; reference (class) to heap/owned.
- **Delegates/events, `ref`/`out` params, `params`, extension methods,
  pattern matching, records (9.0+).** Records are value-equality reference types
  (or `record struct`). `out`/`ref` params have no direct equivalent in many
  targets — port to tuples/`Result`/returned struct.

## As target (porting INTO C#)

- **Enable nullable reference types** (`<Nullable>enable</Nullable>`). Port S's
  `Option<T>` → `T?` (nullable ref) for absence; S's checked errors → exceptions
  (C# has no checked exceptions) or a `Result<T,E>`/`OneOf` library for
  value-errors.
- **`IDisposable` for deterministic cleanup.** Port S's RAII/`Drop`/`defer` to
  `using`/`IDisposable`. Implement `Dispose()` (and `Dispose(bool)` pattern for
  finalizer+managed). `IAsyncDisposable` + `await using` for async cleanup.
- **`record` for value-equality data** (S's struct/dataclass/POD). `record`
  (reference, value-equality) or `record struct` (value type, value-equality).
  Plain `struct` for stack value types; `class` for reference/heaped.
- **`async`/`await`** — port S's async here naturally, but watch sync context
  (`ConfigureAwait(false)` in libs). Prefer `Task`/`ValueTask`. Cancellation
  via `CancellationToken` (S's cancellation token / Go `ctx` → `CancellationToken`).
- **No checked exceptions** — declare intent via XML docs / analyzer; catch
  broad `Exception` is common but discouraged. S `Result<T,E>` → either
  exception or `OneOf<T,E>`/`Result`-style library.
- **Generics with constraints** (`where T : new(), IComparable<T>`). Port S's
  trait bounds to `where` constraints; reified, so `typeof(T)`/`new T()` work.
- **LINQ over `IEnumerable`** for S's map/filter/flatMap chains. Avoid eager
  `.ToList()` unless S materialized.
- **No standalone functions pre-9.0;** local functions / static methods on a
  class. Top-level statements (9.0+) for `Main`. Match the target's style.

## Idiom map (key traps)

| Source pattern | C# | Trap |
|---|---|---|
| `Option<T>` | `T?` (nullable ref) | Enable NRTs; `T?` on value types needs `Nullable<T>` |
| enum-with-data | no direct type | OneOf library / record + factory / nested types |
| `Result<T,E>` | exception or `Result`/`OneOf` lib | No checked exceptions |
| RAII `Drop` | `IDisposable` + `using` | Finalizer ≠ Dispose; don't conflate |
| generics w/ bounds | `<T> where T : ...` | Reified; `new T()` works with constraint |
| value type / struct | `struct` / `record struct` | Mutable struct is a footgun; prefer immutable |
| async runtime | `async`/`await` + `Task` | Eager; cancellation via `CancellationToken` |
| operator overload | supported (`operator +`) | Idiomatic for math/value types |
| tagged union | no native | `OneOf<...>` / sealed hierarchy + pattern matching |
