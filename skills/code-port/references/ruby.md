# Ruby — Porting Notes

## As source (porting OUT of Ruby)

- **Dynamic typing, everything is an object (incl. integers), no primitives.**
  `5.times { ... }` — methods on `Integer`. Porting to a static target (Rust/
  Go/Java/TS) means inferring types from usage; `5.times` becomes a range/loop.
  Duck typing is the norm — port to trait/interface/typeclass bounds, not to
  "has a method named X" reflection (unless genuinely needed).
- **Blocks, `Proc`, `lambda`.** A block (`{ }` / `do...end`) is the idiomatic
  closure passed to methods; `yield` invokes it. `Proc.new`/`lambda` are
  first-class callable objects; `lambda` enforces arity, `Proc` doesn't. Porting
  to closures (JS/TS, Python, Kotlin, Swift) is close; to Rust, closures capture
  by ref/move explicitly — capture mode matters.
- **Modules as mixins (multiple inheritance via `include`/`prepend`/`extend`).**
  No classes-only single inheritance; modules supply shared behavior to many
  classes. Porting to a single-inheritance target (Java/Python-CSS): compose via
  interfaces/traits/mixins. To Rust — traits with default methods.
- **Open classes / monkey-patching.** `class String; def foo; ...; end; end`
  reopens and adds a method at runtime. Porting to a target that forbids this
  (Rust, Go, Java) requires refactoring to extension methods / wrapper types /
  newtypes — *do not fake runtime mutation*. Flag `// TODO(port): monkey-patch`.
- **`nil` is the null**, unchecked, `NoMethodError` on `nil.foo`. The "null
  object" pattern (`&.` safe-nav) is common. Porting to `Option`/nullable —
  decide which nils are "absent" vs "failure".
- **Exceptions are control flow** — `begin/rescue/ensure/retry`, widely used
  (`rescue` for normal paths in some idioms). Port intent, not the mechanism.
- **MRI GIL** — CRuby threads don't run bytecode in parallel; concurrency via
  Ractor (3.0+, true parallel with restrictions), Fibers, or processes. Porting
  to a free-threaded target (Go/Rust/Java) — locks unnecessary under GIL become
  necessary. JRuby/TruffleRuby have no GIL (real threads) — capture which Ruby.
- **Symbols (`:foo`) vs strings.** Symbols are interned, immutable, identity-
  based; strings are mutable (until frozen), value-based. Porting: symbols →
  enum/atoms/`&'static str`; frozen strings → immutable string types.
- **Metaprogramming** — `method_missing`, `define_method`, `eval`, reflection.
  Heavy in Rails. Porting to a static target: codegen / macro / trait-with-
  default-method, or `// TODO(port): metaprogramming`. Rarely 1:1.

## As target (porting INTO Ruby)

- **Dynamic and flexible — embrace it, but add discipline.** Sorbet/RBS type
  sigs (`# typed: strict`) for static checking; port S's static types to sigs
  (they document, and Sorbet enforces). S's `Option`/`Result` → `nil`-return +
  exceptions, or the `dry-monads` `Result` if you want value-errors.
- **Blocks/yield over explicit closures** where idiomatic. S lambdas/closures →
  blocks at call sites, `Proc`/`lambda` when stored.
- **Modules for mixins**, `prepend` for override-injection. S interfaces/traits →
  modules with default method implementations.
- **GC + GIL (MRI).** S RAII/`Drop` → `ensure` blocks / finalizer (non-
  deterministic; don't rely on prompt teardown). For real parallelism use Ractor
  (message-passing, isolated) or JRuby threads — MRI threads are GIL-bound.
- **Symbols for identifiers**, frozen-string-literal magic comment for
  immutability. Avoid monkey-patching core classes in new code (fragile).
- **`case`/`when` with `===`** for type/regex/range matching — flexible but
  `===` semantics surprise (it's not `==`). Pattern matching (`in`/`case-in`,
  3.0+) for destructuring, closer to S's match.
- **Numeric tower:** `Integer` (bignum, no overflow), `Float` (f64), `Rational`.
  S fixed-width ints → Ruby `Integer` loses overflow; mask explicitly if needed.

## For static-language readers: Phase A/B here

Ruby is interpreted, dynamically typed. **There is no compile step.** Redefine:
- **Phase A** = logic-faithful draft that *runs* (Ruby executes as written).
- **Phase B** = `sorbet`/`steep` type-checker passes (if using RBS/Sorbet) +
  test suite (RSpec/Minitest) passes + Rubocop lint clean.

## Idiom map (key traps)

| Source pattern | Ruby | Trap |
|---|---|---|
| `Option<T>` | `nil` return / `dry-monads` | `nil` unchecked; `NoMethodError` |
| `Result<T,E>` | exception, or `dry-monads` | Exceptions are idiomatic |
| checked exception | `raise`/`rescue` | No checked distinction |
| RAII `Drop` | `ensure` / finalizer | Non-deterministic; no RAII |
| generics | duck typing / generics (2.7+) | Rarely declared; duck typing norm |
| value type / struct | immutable class / `Struct` | `Struct` is value-ish but reference-y |
| mixin / trait | module `include`/`prepend` | Multiple mixins; MRO matters |
| operator overload | supported (method defs) | `+` is just `def +` |
| tagged union | no native | `dry-types` / pattern match on Hash |
