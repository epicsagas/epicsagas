# Rust — Porting Notes

## As source (porting OUT of Rust)

- **Ownership is load-bearing.** A `Box<T>` (unique owner), `Rc<T>`/`Arc<T>`
  (shared, single-/multi-threaded), `&T`/`&mut T` (borrow), `Cow<T>` (clone-on-
  write), `Weak<T>` (non-owning) each encode a distinct ownership story. A
  target with GC collapses most of these into "a reference" — that is usually
  fine, but **record the intended lifetime**: a `Weak<T>` becomes a weak ref,
  an `Arc` cycle that relied on `Weak` to break leaks must be re-checked under GC.
- **`Result`/`Option` are values, not exceptions.** When porting to an
  exception language, do not blanket-`unwrap()` into throws — a `?` that
  propagated is a normal control-flow return, distinguishable from a panic.
  Panics (`unwrap`, `expect`, `panic!`) are *not* for normal error handling in
  idiomatic Rust; map them to the target's abort/assert, not its exception type.
- **`unsafe` blocks carry invariants.** Every `unsafe` in Rust exists because
  of a stated precondition. Port the *precondition* (often a comment or an
  inherent safety argument), not just the raw pointer op. If the target is
  memory-safe by default, the `unsafe` may vanish — but only if the invariant
  is genuinely upheld by the safe target construct.
- **No default async runtime.** `async fn` returns a `Future` that does nothing
  unless polled by a runtime (`tokio`/`async-std`/`smol`). Porting Rust async
  to Go/Node/Python maps to goroutines/Promises/asyncio — but Rust futures are
  **lazy** (created ≠ started) and **cancel-safe-by-convention**; most targets'
  async is eager. Capture the laziness if the source depends on it.
- **Traits are nominal, not structural.** `impl Trait for Type` is explicit. A
  target with structural typing (Go interfaces, TS) can satisfy implicitly —
  fine going out, but going *in* you lose the "must declare impl" check.

## As target (porting INTO Rust)

- **Borrow checker is the #1 porting cost.** Overlapping `&mut` aliases that S
  freely used (two mutable references into the same structure, self-referential
  state) will not compile. Reshape per the SKILL "borrow rule": copy the scalar
  out, drop the borrow, re-borrow. Do **not** reach for raw pointers to silence
  it — `unsafe` should mirror S's actual `unsafe`, not borrowck frustration.
- **Decide `String`/`&str`/`&[u8]` from ownership.** `&str` borrows, `String`
  owns and grows, `&[u8]`/`Vec<u8>` for bytes. If S treated paths/source/HTTP as
  bytes (WTF-8, invalid UTF-8), keep `&[u8]` — `String` inserts validation that
  S never did (correctness bug + perf tax).
- **Error type discipline.** Phase A: one `Result<T, Error>`. Phase B: narrow to
  a `thiserror` enum per call graph. Never `anyhow::Error` in `#[repr(C)]` or
  `Copy` payloads. Errors carry no payload in most sources → keep Rust errors
  payload-light (`Copy` newtype where the source snapshots error tags).
- **`Drop` replaces `defer`/`deinit`.** S's `defer x.close()` / `deinit()` →
  `impl Drop`. Do not expose `pub fn deinit` — that's un-idiomatic. For early
  release (sockets, fds), take ownership: `fn close(self)`.
- **Closures/iterators are zero-cost** — port S's loops/collects to iterators
  freely. `?` propagates `Result` through `collect()`; use it.
- **`#[derive]` over hand-written impls** for `PartialEq`/`Eq`/`Hash`/`Clone`/
  `Debug`/`Default` unless field order or skip logic differs.

## Idiom map (key traps)

| Source pattern | Rust | Trap |
|---|---|---|
| nullable ref / `null` | `Option<T>` | Don't conflate "absent" with "error" — use `Result` for failure |
| checked exception | `Result<T, E>` + `?` | E must be sized; don't use `Box<dyn Error>` everywhere |
| `defer close()` | `impl Drop` | Drop runs once, in reverse field order — matches `defer` |
| shared mutable global | `static`/`lazy_static`/`once_cell` | `static mut` is unsafe; use interior mutability (`Mutex`, `Atomic*`) |
| self-referential struct | `&'a self` field won't work | Use indices/handles into a slab, or `ouroboros`/`rental` — rare and slow |
| async callback | `async fn` + `Future`, or channels | Eager-target habits (fire-and-forget) need explicit `tokio::spawn` |
| tagged union / `enum` w/ data | `enum` with variants | Rust enums are already tagged unions — flatten, don't wrap in `Option<Enum>` |
| integer narrowing `as` | `T::try_from(x)?` | `as` silently truncates; checked cast panics in debug — match S |
| `void*` / `Object` | `Box<dyn Trait>` or generic `<T>` | Avoid `Any` unless S truly erased the type |
