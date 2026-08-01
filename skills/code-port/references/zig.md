# Zig — Porting Notes

## As source (porting OUT of Zig)

Zig is a manual-memory, no-hidden-control-flow systems language. Its distinctive
features all need deliberate handling on the way out.

- **Explicit allocators everywhere.** `std.mem.Allocator` is a *parameter*
  passed to every allocating function/struct. `allocator.create(T)`,
  `allocator.alloc(T,n)`, `allocator.dupe(u8,s)`, `allocator.free(...)`. This is
  Zig's core idea. Porting out:
  - GC'd target (Go/Java/Python/JS): **delete the allocator param entirely** —
    the GC owns it. Delete every `free`. Leave `// PERF(port): was explicit alloc`
    only where Zig arena-bulk-freed in a hot loop.
  - Ownership target (Rust): retype fields to own their storage (`Box`/`Vec`) so
    `Drop` frees them; delete `free`. `allocator.create(T)`→`Box::new`;
    `allocator.dupe(u8,s)`→`Box::<[u8]>::from(s)`.
  - Manual target (C/C++): keep the allocator, match malloc/free pairs.
- **`defer` / `errdefer`** run at scope exit (defer always, errdefer only on the
  error path). `errdefer` often rolls back side effects (a counter, a registry
  entry, a remote handle). Port `defer x.deinit()` → target RAII/`using`/`Drop`
  (delete the line). Port `errdefer`-with-side-effects → target's scope guard
  (`scopeguard`, `try`/`finally` with a flag) — *don't* hand-roll a Drop struct.
- **`comptime`** = compile-time evaluation/type params. `comptime T: type` →
  generic `<T>`. `comptime flag: bool` → const generic `<const FLAG: bool>` or a
  runtime arg (note perf). `comptime` on expressions → `const`/`constexpr`.
  Reflection (`@typeInfo`, `@field`, `@hasDecl`) has **no direct equivalent** in
  most targets — port to derive macros / codegen / traits-with-default-methods,
  or flag `// TODO(port): reflection`.
- **Tagged unions (`union(enum)`)** — Zig's sum type. Port directly to the
  target's enum-with-payload (Rust enum, TS discriminated union, Kotlin sealed).
  Untagged `union` (rare, `extern union`) is C-style reinterpret — `unsafe`.
- **Error sets / `anyerror` / `!T`.** Zig errors are zero-payload tags, `Copy`,
  no allocation, `try`/`catch` to propagate/handle. `anyerror!T` is "any error."
  Port to the target's error model — but preserve *payload-free* and *Copy*:
  Rust `Result<T, E>` with a `Copy`/`NonZero`-newtype `E` (not `Box<dyn Error>`).
  `@errorName` → a static name (don't use `Display` — that's the message, not
  the tag; snapshot tests / `error.code` depend on the exact string).
- **`@`-builtins map to target ops, not always 1:1:**
  - `@intCast` → **checked** cast (`T::try_from`), not silent truncation.
  - `@truncate` → silent wrap (`x as u8`).
  - `@intFromBool(b)` / `@intFromEnum(e)` / `@intFromPtr(p)` → `b as u8` / `e as uN` / `p as usize`.
  - `@bitCast` → `transmute`/`from_bits`.
  - `+%`/`-%`/`*%` (wrapping) → `wrapping_add` etc; `+%` is NOT plain `+` (debug
    panics in Rust). `+|`/`-|` (saturating) → `saturating_add`.
  - `@min`/`@max` → `a.min(b)`/`a.max(b)` (method form).
- **`*T`/`[*]T`/`[]T`/`[:0]T`** — many pointer/slice kinds. `*T` single pointer,
  `[*]T` many-item pointer (no len), `[]T` slice (ptr+len), `[:0]T` sentinel-
  terminated. Port `[]T` (param/return) → `&[T]`; `[]T` (owned field, freed in
  deinit) → owned `Vec`/`Box<[T]>`; `[*:0]const u8` → `*const c_char` at FFI,
  `&CStr` in Rust. Sentinel-terminated slices need the target's NUL-terminated
  type (`CString`, `ZStr`).
- **`packed struct(uN)` / `extern struct`** → `#[repr(C, packed)]` / bitfield
  library; field order is load-bearing. `extern union` → `#[repr(C)] union`
  (Rust `union`, unsafe to read).
- **`opaque {}`** as FFI handle (`*Foo`) → newtype with `PhantomData<(*mut u8,
  PhantomPinned)>` (`!Send + !Sync + !Unpin`); as a type-tag → drop it (Rust
  newtypes are already distinct).

## As target (porting INTO Zig)

- **You regain explicit memory management — use it.** Every allocation takes an
  `std.mem.Allocator`. Choose the allocator per workload: `std.heap.page_allocator`
  (OS pages), `GeneralPurposeAllocator` (debug, leak-detect), `ArenaAllocator`
  (bulk-free a region — great for parsers/compilers), `FixedBufferAllocator`
  (stack/inline). Match S's memory model: GC'd → `GeneralPurposeAllocator` or
  arena; ownership → arena or GPA; manual → mirror S's allocator choice.
- **No hidden allocations, no hidden control flow.** Zig calls what you write.
  Port S's implicit boxing/GC into explicit `allocator` calls. S's exceptions →
  Zig error sets (`error{ Foo, Bar }!T`), payload-free tags, `try`/`catch`.
  No exception objects with payloads — flatten to tags.
- **`comptime` is your generics + metaprogramming.** Port S's generics to
  `comptime T: type`. Port S's constexpr to `comptime`. Port S's reflection to
  `@typeInfo`/`@field` (Zig *has* runtime-less reflection you can use here).
  Port S's derive macros to `comptime` functions generating structs.
- **`defer`/`errdefer`** replace S's RAII/try-finally. `defer` for cleanup,
  `errdefer` for rollback-on-error. Idiomatic and encouraged.
- **Slices over pointers.** Prefer `[]T` (bounds-checked in safe builds) over
  `[*]T` (raw, unchecked). Sentinel-terminated `[:0]T` for C interop.
- **Tagged unions for sum types.** `union(enum) { a: A, b: B }` with `switch`
  — exhaustive, payload-capturing. Port S's enum-with-data here.
- **`@`-builtins for low-level ops** — use `@intCast` (checked), `@truncate`
  (wrap), `@bitCast`, `@memcpy`/`@memset`. No UB without saying so.

## Idiom map (key traps)

| Source pattern (porting OUT of Zig) | Common targets | Trap |
|---|---|---|
| `Allocator` param | GC target: delete; Rust: own via Box/Vec | Don't carry a meaningless allocator param into a GC language |
| `defer`/`errdefer` | RAII / scopeguard / try-finally | errdefer-with-side-effects needs a guard, not just Drop |
| `comptime T` | generic `<T>` | const-value params ≠ generic type params |
| `anyerror!T` | `Result<T, E>`, E payload-free | Don't use `anyhow`/`Box<dyn Error>`; lose Copy + tag-name |
| `union(enum)` | Rust enum / sealed class / disc union | Direct port |
| `@intCast` | checked cast | Not silent `as` |
| `+%/-%/*%` | `wrapping_*` | Plain `+` panics in debug (Rust) |
| `[:0]const u8` | NUL-terminated string type | Len excludes NUL; FFI boundary conversion |
| `*Foo` (FFI opaque) | newtype + PhantomData | `!Send + !Sync + !Unpin` |
| `errdefer { side effects }` | scopeguard / try-finally+flag | Don't hand-roll a Drop struct |
