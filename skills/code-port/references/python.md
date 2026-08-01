# Python — Porting Notes

## As source (porting OUT of Python)

- **Dynamic typing — types are runtime, on the value not the variable.** A name
  can be rebound to any type. Porting to a static target means *inferring* types
  from usage: read every call site. Where a name holds multiple types, that is a
  real union (`Result`/`enum`/sum type) or a code smell — capture it explicitly.
  `mypy`/`py.typed` stubs are hints, not guarantees.
- **`None` is the universal null** but Python also distinguishes "absent key"
  (`KeyError`) from "value is None". `dict.get(k)` returns `None` for absent —
  ambiguous. Porting to a target with `Option`, split absent-vs-None explicitly.
- **Exceptions are control flow** — widely used for normal paths
  (`StopIteration`, `FileNotFoundError`, `KeyError`). These are not bugs. Port
  the *intent*: `StopIteration` → iterator exhaustion (`None`/`Option` in static
  target), `KeyError` → `Option`/error-value, not necessarily to the target's
  exception type.
- **Duck typing / `__dunder__` protocols.** `len(x)` calls `x.__len__`,
  `for x in y` calls `y.__iter__`. Porting to a static target: the protocol
  becomes a trait/interface (`Sized`, `Iterable`); ad-hoc duck typing needs a
  trait bound or an explicit interface, not "it has a `.foo` method" reflection.
- **Iterators/generators are lazy** and `yield` makes a state machine. `yield`
  in a static target → the target's generator/iterator (`impl Iterator`, JS
  generator). Coroutines (`async def`) are separate — they return a coroutine
  object needing an event loop (`asyncio`).
- **GIL** — CPython threads can't run Python bytecode in parallel; concurrency
  is via `multiprocessing`, async, or C extensions releasing the GIL. Porting to
  a free-threaded target (Go, Rust, Java) changes the concurrency model — locks
  that were unnecessary under the GIL become necessary.
- **Mutable default arguments** (`def f(x=[])`) are a famous trap — the default
  is shared across calls. Port the *fixed* version (`x=None` then `x = []`),
  not the bug.
- **Reference semantics for mutable objects;** assignment aliases. Immutable
  types (tuple, str, int, frozenset) are value-like. Porting to Rust, capture
  shared-vs-unique for mutables.

## As target (porting INTO Python)

- **You lose static guarantees, you gain flexibility — be disciplined.** Add
  `typing` annotations (`list[int]`, `X | None`, `TypedDict`) even if S was
  static; they document intent and let `mypy`/`pyright` help. Port S's generics
  to `TypeVar`/`Generic`; S's `Result`/`Option` → `T | None` + exceptions, or
  `result` library if you want value-errors.
- **Don't port GC'd manual memory mgmt to `__del__`/`del`.** Rely on refcounting
  + GC; use `with` (context manager) for deterministic cleanup of resources
  (files, locks, sockets) — `__enter__`/`__exit__`, mirroring RAII/`using`.
- **`async`/`await` needs `asyncio`.** S's async runtime → `asyncio` (or
  `trio`/`anyio`). Goroutines/threads → `asyncio` tasks are single-threaded;
  for true parallelism use `concurrent.futures`/`multiprocessing`.
- **Properties, not fields with logic.** S getters/setters → `@property`/
  `@x.setter`. Keep it; don't expose raw fields if S had encapsulation.
- **`dataclasses` / `attrs`** for S's plain-data structs (record/struct/POD) —
  auto `__init__`/`__eq__`/`__repr__`. Match S's value-vs-reference semantics.
- **Metaprogramming is easy and dangerous** — decorators, metaclasses,
  `__init_subclass__`, descriptors. Port S's macros/codegen to a decorator when
  it fits; avoid metaclass proliferation unless S genuinely used it.
- **Numeric towers** — `int` is arbitrary precision, `float` is f64, no overflow
  on `int`. S's fixed-width ints (`u32`, `int32`) → Python `int` loses overflow
  semantics; if S relied on wraparound, mask with `& 0xFFFFFFFF` explicitly.

## Idiom map (key traps)

| Source pattern | Python | Trap |
|---|---|---|
| `Option<T>` | `T \| None` | `None` vs absent still ambiguous; mypy: `Optional[T]` |
| `Result<T,E>` | exception, or `T \| E` union | Exceptions are idiomatic for errors |
| enums (typed) | `enum.Enum` | Subclass-based; value identity |
| RAII `Drop` | context manager (`with`) | Only for scoped resources |
| generics w/ bounds | `TypeVar(bound=...)`, `Generic[T]` | Runtime, not enforced without mypy |
| fixed-width int | `int` (bignum) | No overflow; mask explicitly if wrap needed |
| switch/match | `match` (3.10+) or `if/elif` | Structural matching in 3.10+ |
| struct/record | `@dataclass` | Mutable by default; `frozen=True` for value type |
| async runtime | `asyncio` | Single-threaded; GIL still blocks CPU parallelism |

## Phase A/B redefinition (Python is interpreted)

There is no compile step. **Phase A** = logic-faithful draft that *runs* under
CPython. **Phase B** = `mypy`/`pyright` passes (type-check) **and** the test
suite (pytest/unittest) passes **and** `ruff`/flake8 lint is clean. "Compiles?"
becomes "type-checks + tests pass".
