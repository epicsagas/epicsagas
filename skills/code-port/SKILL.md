---
name: code-port
description: "Faithfully ports one source file in one language to a target language — a draft in Phase A (logic-correct, need not compile) then compile-by-module in Phase B. Preserves structure (names, field order, control flow), infers ownership/error/concurrency mappings instead of guessing, and marks every uncertain spot. Language-agnostic methodology with per-language pitfall references. Triggers on: 'port X to Rust/Go/TS/...', 'translate this file to <lang>', 'rewrite <lang> code in <lang>', 'migrate to <lang>', 포팅, 변환, 이식."
---

# Code Port — Cross-Language File Translation

You are translating **one source file** from language **S** to language **T**.
Read this whole document before writing any code.

Phase A produces a **draft** file next to the source that captures the logic
faithfully — it does **not** need to compile. Phase B makes it compile
module-by-module. The two-phase split exists because faithful translation and
compilation pull in opposite directions: optimize Phase A for a reviewer who
diffs source ↔ draft side-by-side, and Phase B for the compiler.

## When to use

- "Port `foo.<ext>` to Rust/Go/TypeScript/Python/…"
- "Rewrite this <S> module in <T>"
- "Migrate this file to <T>"
- Any 1:1 file translation across languages where **structure and behavior
  must be preserved** (not a greenfield rewrite, not an architectural redesign).

If the request is "redesign / refactor / improve this" — that is **not** a
port. Use a refactor skill instead. A port changes the language, not the design.

## The two-phase model

| Phase | Goal | Compiles? | Optimized for |
|-------|------|-----------|---------------|
| **A — Draft** | Faithful logic + idiom in T | No | The diff reader (`.src` ↔ `.t`) |
| **B — Compile** | Type-checks, links, tests pass | Yes | The compiler + tests |

Never do both at once. A draft that fights the borrow checker / type system
while you are still translating logic produces both a wrong port *and* a slow
one. Get the logic down, mark uncertainty, then make it compile.

## Ground rules

1. **Write the target file next to the source, same basename** — unless T's
   module conventions demand otherwise (e.g. one-file modules, `index.<ext>`,
   `mod.rs`). If the source basename equals its immediate parent dir, name the
   target by that dir's module file. Match T's project layout, do not invent one.

2. **Match the source's structure.** Same function/method names converted to
   T's casing convention (see §Naming). Same field order. Same control flow.
   Same parameter order. Phase B reviewers diff side-by-side; surprise
   reordering slows them down.

3. **Do not invent external dependencies.** Map a third-party library used in S
   to its established T equivalent **only** if you are confident it exists and
   matches. Otherwise write `// TODO(port): T equivalent of <S lib>` and a
   faithful stub. Flagging beats a wrong guess that compiles.

4. **Preserve the safety level.** If S was performing a checked operation, T
   must too. If S used an unchecked/unsafe primitive, T may use the equivalent
   and **must annotate it** (`unsafe`/`// SAFETY:` in Rust, `@Suppress` /
   `// @ts-expect-error` with reason in TS, `# type: ignore` in Python, etc.).
   Never silently turn a checked op into an unchecked one or vice versa.

5. **No speculative abstraction.** If S has one implementation, T has one
   implementation — do not introduce an interface/trait/protocol "for
   flexibility". Match the source's abstraction level.

6. **Mark, don't guess.** Leave `// TODO(port): <reason>` for anything you
   cannot translate confidently. Leave `// PERF(port): <S idiom> — revisit in
   Phase B` wherever S used a perf-specific idiom and the draft uses the plain
   idiomatic T form. Leave `// PORT NOTE: <why>` wherever you deliberately
   reshaped control flow to satisfy T's constraints (lifetimes, ownership,
   definite assignment, etc.) so the diff reader is not confused.

## Translation methodology

Work top-down. Read the whole source file once, classify every construct on
the axes below, then write the draft in one pass.

### Ownership & memory

Decide each field/buffer's ownership from **how S treats it**, not from its
declaration syntax:

- If S frees it (`free`, `delete`, `drop`, `defer release`) → **owned** in T
  (`Box`/`Vec`/owned handle, or manual free if T is manual).
- If S holds it for the call only and the caller keeps it alive → **borrowed**
  (reference/pointer/`&`, with the right lifetime/annotation).
- If S only ever assigns literals / it's immortal → **static/shared constant**.
- If S uses a region/arena/pool that is bulk-freed → keep that model in T if T
  supports it (bump arena, arena allocator); otherwise owned + `// PERF(port)`.

**Prerequisite:** if T's default allocator differs from S's and the code is
allocator-sensitive (custom allocators, placement, alignment assumptions),
note it. Phase A can assume the global allocator; Phase B verifies.

### Error model

Map S's error model to T's *closest structural* equivalent, preserving whether
the error carries a payload, whether it is checked at compile time, and whether
control flow unwinds:

| S model | T mapping decision |
|---|---|
| Exceptions (unchecked, unwinding) | T exceptions if T has them; else `Result`/`Either`/error value + propagate |
| Checked exceptions / typed error sets | `Result<T, E>` with a typed `E`, or T's checked-error equivalent |
| Error return codes / sentinel values | Same sentinel, or upgrade to `Result`/`Option` if T idiomatic — but keep behavior identical |
| `null` as "absence or failure" | `Option`/nullable — keep the failure-vs-absence distinction S made |
| Union error + payload (`try`/`catch` with typed union) | `Result` or tagged union |

**In Phase A, use one broad error type** (T's general error) and leave
`// TODO(port): narrow error set` for Phase B. Do not invent a precise enum you
cannot verify against all call sites.

### Null & optionality

Map `null`/`nil`/`None`/`undefined` deliberately. S often uses a single null
value for three different things — *absence*, *not-yet-initialized*, and
*failure*. In T these may need three representations (`Option<T>`,
MaybeUninit<T>/late-init, Result<T,E>). Read the call sites to tell them apart;
do not blanket-convert to one nullable.

### Concurrency & async

Map the *model*, not the syntax. This is the highest-bug-rate axis:

- S async/await → T async/await only if T's runtime is compatible. If S owns
  its event loop / uses raw syscalls / uses callbacks, and T's `async` implies
  a specific runtime, **do not** reach for `async`. Use callbacks + state
  machines, matching S. Leave `// TODO(port): async runtime` if unsure.
- S threads → T threads, preserving the synchronization primitives (mutex,
  condvar, channels) with T's equivalents. Note lock granularity.
- S actors/goroutines → map to T's closest construct; goroutine ↔ task/actor
  is not free — capture scheduling assumptions.
- S lock-free atomics → T atomics with the **same memory ordering**. If S
  relied on relaxed/acquire/release semantics, T must match exactly.

### Generics & metaprogramming

- S compile-time generics → T generics with trait/typeclass/bound/constraint.
- S compile-time *value* params (`const`, `comptime`, template non-type) → T's
  const generics / constexpr / `const` where supported; otherwise a runtime
  param + `// PERF(port): was compile-time`.
- S reflection / runtime type introspection with **no T equivalent** → do not
  fake it. Either a T idiom (derive macro, codegen, trait with default method)
  or `// TODO(port): reflection`. See §Paradigm axes.
- S macros/token-pasting/type-list iteration → T macros (procedural macro,
  `macro_rules!`, TS template-literal types, Python decorators) — only when
  there is genuine no-shared-trait metaprogramming.

### Idiom mapping

For each S idiom, ask: *what is the closest T idiom with the same behavior and
roughly the same cost?* Apply the **defer/cleanup rule** and **borrow rule**
below — they generalize across most languages:

- **Cleanup / `defer` / RAII:** if S uses `defer x.release()` / finally /
  destructor, map to T's scope-exit mechanism (RAII `Drop`, `using`/`IDisposable`,
  `try`-with-resources, `defer`-like, `contextlib`). Do not hand-roll a cleanup
  flag unless T lacks the mechanism. Where S has out-of-order cleanup (cleanup
  order ≠ declaration order) and it matters, keep explicit and `// PORT NOTE`.
- **Borrow / aliasing constraints:** when matching S flow yields overlapping
  mutable aliases that T forbids (Rust borrow checker, single-ownership rule,
  Swift exclusivity), capture the needed scalar (length, index, copy) into a
  local, drop the borrow, then continue. **Do not** punch through to raw
  pointers / `unsafe` / `@unchecked` just to silence the checker — that hides
  the aliasing the checker was warning about. Leave `// PORT NOTE: reshaped for
  aliasing`.
- **Numeric casts:** S narrowing cast that can overflow → T's *checked* cast
  (panic/Result on overflow), not a silent wrap, unless S itself wrapped
  (`as`/truncating). Match wrap-vs-check semantics exactly. Reserve silent
  truncation for where S explicitly truncated.

## Naming conversion

Convert identifiers to T's casing convention, collapsing acronyms consistently.
Common rules (apply T's, consistently):

- `camelCase`/`PascalCase` → `snake_case` when T is snake: `toAPI`→`to_api`,
  `isCSS`→`is_css`, `toUTF8`→`to_utf8`. Rule of thumb: a run of ≥2 uppercase
  letters collapses to one lowercase segment.
- Preserve names that are domain terms / API surface / FFI symbols verbatim
  (do not rename a C symbol the linker must find).
- T may have a linter/formatter that *enforces* casing — let it, do not
  pre-argue with it.

## FFI & platform conditionals

- `extern` / `@export` / native declarations → T's FFI (`extern "C"`, `DllImport`,
  `cgo`, `ctypes`/`cffi`, FFI namespace). Group externs; do not scatter.
- Platform conditionals (`#ifdef`, `if isWindows`, `cfg`) → T's equivalent
  (`#[cfg(...)]`, build tags, `#if DEBUG`, `process.platform`). Beware:
  value-level `if (cond)` in T may keep **both** branches type-checked, unlike
  S's compile-time conditional that removes the dead branch. Use T's
  compile-time form when the disabled branch references platform-only items.

## Don't translate

- Import/include boilerplate at the bottom → T's imports at the top. Do not 1:1
  the import block.
- Pure alias re-exports → collapse to a direct use.
- Generated files (`*_generated.*`, large tables) → write a 3-line stub:
  `// GENERATED: re-run <generator> with <T> output`.
- Test blocks → T's test module (`#[cfg(test)]`, `func TestX(t *testing.T)`,
  `describe`/`it`, `def test_`). Preserve test names.
- Build configuration / project files → out of scope for a single-file port;
  flag for Phase B.

## Paradigm axes → load the right reference

Before translating, classify S and T on these axes. Where they differ sharply,
load the matching per-language note from `references/` for the specific traps:

| Axis | Diverges hardest between |
|------|--------------------------|
| **Memory** — manual / GC / ownership+borrow / RC | C/C++ ↔ Rust ↔ Go/Java/Python |
| **Error** — exceptions / typed values / codes | Python/Java ↔ Rust/Go/Haskell |
| **Null** — nullable refs / Option / nil-everything | Java/C# ↔ Rust/Kotlin/Swift ↔ Go |
| **Concurrency** — OS threads / async-await / green threads / actors | Go ↔ Rust ↔ Node/Python ↔ Erlang |
| **Typing** — nominal / structural / dynamic / gradual | Java/Rust ↔ TS/Go(structural iface) ↔ Python/Ruby |
| **Metaprogramming** — templates / macros / reflection / decorators | C++/Zig ↔ Rust ↔ Java ↔ Python |

Reference files (load the one for **each** of S and T):

- [`references/rust.md`](references/rust.md) — ownership, lifetimes, `Result`/`Option`, traits, `unsafe`, async
- [`references/go.md`](references/go.md) — goroutines, interfaces, error-as-value, channels, nil
- [`references/c-cpp.md`](references/c-cpp.md) — manual memory, UB, templates/macros, pointers
- [`references/python.md`](references/python.md) — dynamic typing, GIL, dunder, iterators, decorators
- [`references/typescript.md`](references/typescript.md) — structural types, unions, narrowing, async
- [`references/jvm.md`](references/jvm.md) — checked exceptions, nullables, streams (Java + Kotlin)
- [`references/csharp.md`](references/csharp.md) — nullable refs, `IDisposable`, LINQ, async/await
- [`references/zig.md`](references/zig.md) — `comptime`, explicit allocators, tagged unions, error sets

If neither S nor T is listed, the methodology above still applies — fall back
to the axis table and your knowledge of both languages, and add a per-language
note if the port repeats.

## Output format

End the target file with a trailer comment (comment syntax of T):

```
PORT STATUS
  source:     <path> (<NNN> lines)
  confidence: high | medium | low
  todos:      N
  notes:      <one line: anything Phase B needs to know>
```

Confidence levels:

- **low** — logic is probably wrong; re-read the source in Phase B.
- **medium** — types/imports/wiring need fixing but the logic is right.
- **high** — should compile with only mechanical import fixes.

Count `TODO(port)` markers for `todos`. The trailer is the Phase B entry point.

## Phase B (compile) — once Phase A is done

1. Wire the module into T's build (manifest/package/import).
2. Resolve imports and the external-dependency `TODO(port)`s.
3. Make it type-check, fixing only what the compiler demands — do not refactor.
4. For each `PERF(port)`, decide (with a benchmark) whether to restore the S idiom.
5. Add/restore tests mirroring the source's tests.
6. Re-read any `low` confidence file against the source before declaring done.
