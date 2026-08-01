# C / C++ — Porting Notes

## As source (porting OUT of C/C++)

- **Manual memory management is the whole game.** `malloc`/`free`, `new`/`delete`,
  `new[]`/`delete[]`, placement new, custom allocators, arenas. Map to the
  target's owned type (Rust `Box`/`Vec`, Go slice, smart pointer) — and **delete
  every explicit `free`/`delete`**, letting the target's GC/RAII own it. Track
  *which* allocator a buffer came from (mismatched free = bug in C, often silent
  in the target).
- **Undefined behavior is real and silent.** Signed overflow, use-after-free,
  null deref, data race, out-of-bounds — C/C++ "works" until it doesn't. A
  memory-safe target (Rust, Go, Java) will *catch* some of these at runtime.
  Port the *intent*, and where S relied on UB "working" (signed overflow wrap,
  pointer arithmetic aliasing), port to the target's defined-wrap equivalent
  and `// PORT NOTE`.
- **Pointers do triple duty: array, optional, borrow.** `T*` may be an array
  start, a nullable optional, or a non-owning borrow. Read call sites to split
  into the target's distinct types (slice, `Option`, reference). Do not map
  every `*` to one pointer/reference type.
- **`memcpy`/`memset`/`memmove`** → target's slice ops. Note `memmove` allows
  overlap, `memcpy` does not — the target's `copy_from_slice` is non-overlapping.
- **Templates and macros** are compile-time metaprogramming. Templates
  (parametric) → target generics. C macros (token paste, `#ifdef`) → target
  macros/codegen/const. C++ template metaprogramming (SFINAE, concepts) often
  has no clean equivalent — codegen or `// TODO(port)`.
- **`struct` value semantics, POD layout.** C structs copy by value; C++ classes
  have copy/move ctors. The target's default copy behavior (reference in Go/Java,
  move in Rust) differs — capture intent (deep copy vs shallow vs move).
- **`volatile` ≠ atomic.** `volatile` is for MMIO/compiler barrier, **not**
  thread-safety. Port to the target's atomics with the right memory ordering,
  never to a "volatile-equivalent."

## As target (porting INTO C/C++)

- **You now own memory safety.** Every allocation needs a matching free with the
  *same* allocator. Prefer RAII: C++ `std::unique_ptr`/`std::shared_ptr`,
  `std::vector`, `std::string`, `std::lock_guard`; in C, paired alloc/free via a
  cleanup convention. `defer`-like cleanup (`goto cleanup`, `cleanup_t`).
- **Define UB away or own it.** Signed overflow → use unsigned or `__builtin_*_overflow`.
  Casts → checked helpers. Where S (a safe language) had defined wrap, C++ has UB
  on signed overflow — port to unsigned or saturating intrinsics.
- **No exceptions by default in C; C++ has them but many codebases disable.**
  Decide the error model (`-fno-exceptions` → return codes / `std::expected`;
  exceptions on → `throw`). Match the codebase convention, do not mix.
- **Pointers still alias everything.** `restrict` hints non-aliasing. Be
  conservative; the source's borrow checker (if Rust) gave you aliasing facts
  C/C++ cannot express — add `restrict`/comments where it matters.
- **Header/source split.** Declarations in headers, definitions in `.c`/`.cpp`.
  Port S's single-file module into the split; ODR (one-definition rule) matters.
- **`NULL` vs `nullptr` (C++).** Use `nullptr`. C uses `NULL` (macro).
- **Templates inflate binary size** — each instantiation is code. Port a generic
  that S monomorphized few times; consider runtime polymorphism (`virtual`) if
  S was dynamically dispatched.

## Idiom map (key traps)

| Source pattern | C/C++ | Trap |
|---|---|---|
| `Option<T>` / nullable | raw pointer `T*` (nullable) or `std::optional<T>` | No compile-time null check; deref is UB |
| `Result<T,E>` | return code / `std::expected<T,E>` / exception | Pick one model, stay consistent |
| RAII `Drop` | destructor / `std::lock_guard` / `goto cleanup` | C has no dtor — manual |
| generics | `template<typename T>` | Code bloat; no HKT |
| bounds-checked array | raw `T[]` (no check!) | Add explicit checks or use `std::span`/`std::array` |
| tagged union | `union` + tag (manual) or `std::variant` | C `union` has no tag — UB if misread |
| string (UTF-8 validated) | `char*` / `std::string` (bytes!) | No encoding guarantee; re-add validation |
| async/await | callbacks / `std::coroutine` / threads | No universal runtime |
| `defer` | RAII or `goto cleanup` | Order matters for resources |
