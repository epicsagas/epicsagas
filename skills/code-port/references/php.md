# PHP — Porting Notes

## As source (porting OUT of PHP)

- **Gradual typing: type declarations exist but optional, not fully enforced
  without strict mode.** `declare(strict_types=1);` at file top makes param/
  return types checked at *that file's* calls (per-file contract!). Without it,
  weak-mode coerces (`"5"` → `int 5`). Porting out, capture *whether the source
  file was strict* — it changes type semantics. Weak-mode coercion is a real
  behavior to preserve or a bug to fix; decide per case.
- **`null` is unchecked; `?T` marks nullable (7.1+).** `TypeError` on wrong type
  in strict mode. Porting to `Option`/nullable — `?T` is the nullable signal.
- **Arrays are ordered maps (hash tables) — dual-purpose as list AND dict.**
  `[1,2,3]` (list) and `['a'=>1]` (map) are the same type (`array`). Numeric vs
  string keys; insertion order preserved; auto-increment numeric keys. Porting
  to a list/map-distinct target (Rust `Vec` vs `HashMap`, Go slice vs map): **you
  must split** — read usage to tell list-array from assoc-map. Don't map every
  `array` to one type.
- **Pass by value by default, but objects (and arrays? no — arrays are value).**
  Confusing: objects pass by handle (reference-like), arrays/scalars by value
  (copy-on-write). Porting to a reference-target, capture object-handle vs
  array-copy semantics.
- **Exceptions (`throw`/`try`/`catch`/`finally`) are control flow;** many legacy
  paths use return-`false`-on-failure instead. Mixed in the wild. Read call sites.
- **References (`&`)** — explicit pass-by-reference. `$a =& $b` aliasing. Porting
  to Rust/Go — `&` maps to references/pointers but aliasing semantics differ.
- **No true generics** (until recently limited; traditionally erased/absent). S
  uses `array<int>` doc-comments (PHPDoc), not enforced. Porting to real generics
  is freer.
- **Properties/magic methods** (`__get`, `__set`, `__call`, `__toString`) +
  metaprogramming. Traits for mixin. Porting to a static target: trait/default-
  method, or `// TODO(port): magic method`.
- **PHP-FPM / request-lifecycle model** — globals reset per request (shared-
  nothing). Long-lived state needs external store (Redis/DB). Porting to a
  server-runtime target (Go/Node/Rust server) — "global state resets per request"
  is *not* true anymore; capture stateful assumptions.
- **`declare(strict_types=1)` is per-file** — one of PHP's sharpest footguns.
  A library file strict + caller weak = caller coerces, callee sees coerced.

## As target (porting INTO PHP)

- **Enable `declare(strict_types=1);`** at every file top. Port S's static types
  to PHP type declarations (param/return/property). Use PHPStan/Psalm for static
  analysis — they catch far more than the runtime.
- **Split arrays into lists vs maps deliberately.** `list<T>` (`@return list<T>`)
  vs `array<K,V>`. PHP arrays conflate them; PHPStan/psalm types disambiguate.
- **`?T` for nullables**, non-`?` for required (enforced in strict mode). S's
  `Option<T>`/`Result` → `?T` + exceptions, or a `Result`-style value object.
- **Objects by handle, arrays by value.** `clone` for deep copy of objects.
  Match S's value-vs-reference intent — port value types to readonly classes
  (8.2+ `readonly`) or arrays.
- **Match expression (8.0+)** for sum-type dispatch — `match($x) { 1 => ..., }`,
  exhaustive over conditions, returns value. Port S's `match`/`switch` here.
  Enums (8.1+) are real backed enums (incl. `enum X: int`).
- **Constructor property promotion (8.0+)** + readonly (8.2) + `readonly class`
  for value objects. Port S's record/struct here.
- **`finally` / RAII**: PHP has no RAII; use `try/finally` or `__destruct` (runs
  at GC, not deterministic). For resources (file/socket), explicit `close()`.
- **Fibers (8.1+) / async** — Revolt/ReactPHP/Amp for async I/O. S async → Amp/
  Revolt; no built-in `async`/`await` syntax (use promise/fiber APIs). S threads
  → processes or async runtimes (shared-nothing heritage).
- **Composer for deps; PSR standards** for interop. S's package manager → Composer.

## For static-language readers: Phase A/B here

PHP is interpreted, gradually typed. **No compile step** (opcache pre-compiles,
but not a type-check). Redefine:
- **Phase A** = logic-faithful draft that *runs* + has `declare(strict_types=1)`.
- **Phase B** = PHPStan/Psalm level-max passes + PHPUnit/Pest tests pass +
  PHP-CS-Fixer/PHPCS lint clean.

## Idiom map (key traps)

| Source pattern | PHP | Trap |
|---|---|---|
| `Option<T>` | `?T` (strict mode) | Enforced only in strict mode |
| `Result<T,E>` | exception / value object | Mixed return-false-in-legacy |
| list vs map | same `array` type | Split deliberately; PHPStan `list<T>` vs `array<K,V>` |
| RAII `Drop` | `try/finally` / `__destruct` | Non-deterministic; explicit `close()` |
| generics | PHPDoc `array<T>` / @template | Not runtime-enforced (until recently) |
| value type | readonly class (8.2) / array | Objects by handle; arrays by value |
| enum (nominal) | `enum` (8.1, backed) | Real enums; no data variants (use match+class) |
| operator overload | not supported | Use named methods |
| tagged union | no native | match + classes / PHPStan `T\|U` |
