# JVM (Java / Kotlin) — Porting Notes

## As source (porting OUT of Java/Kotlin)

- **GC + references, no value semantics for objects.** Assignment aliases;
  `==` is reference identity (Java), `.equals()` is value. Kotlin `data class`
  gives value `equals`. Porting to a value-semantic target (Rust move, C++ copy
  ctor) flips aliasing — capture whether S relied on shared mutation.
- **Checked exceptions (Java).** `throws FooException` is part of the signature
  and enforced. Porting to Rust/Go: these become `Result`/`error` values (no
  forced declaration). Porting to Kotlin: Kotlin does *not* enforce checked
  exceptions — they're just documented. Preserve which are checked vs unchecked
  (RuntimeException) as intent.
- **`null` is pervasive and unchecked (Java).** `String x` may be null; NPE at
  runtime. Kotlin has nullable types (`String?`) enforced at compile time. When
  porting Java out, treat every reference type as potentially-null and decide
  `Option`/nullable per call site — don't blanket-convert. Kotlin source already
  carries nullability; port 1:1.
- **Inheritance is nominal and single (class) + multiple (interface, default
  methods).** Porting to a target without class inheritance (Rust, Go): model
  via composition + trait/interface. Default methods (Java 8) → trait default
  methods. `super` calls and the inheritance hierarchy don't port cleanly.
- **Generics are erased.** `List<String>` is `List` at runtime; you can't
  `new T()` or get the type arg at runtime without a `Class<T>` token. Porting
  to reified-generics targets (C#) is freer; to monomorphizing targets (Rust,
  C++) each instantiation is real code.
- **JVM concurrency:** threads, `synchronized`, `volatile` (memory barrier),
  `java.util.concurrent` (`Lock`, `Atomic*`, `ExecutorService`, `CompletableFuture`).
  `volatile` here *is* a real memory barrier (unlike C). Map to target atomics
  with matching ordering; `synchronized` → mutex.

## As target (porting INTO Java)

- **No operator overloading** (except `String +`). Port overloaded operators to
  named methods. No top-level functions — everything is a method on a class.
- **No value types for objects (pre-Valhalla);** primitives (`int`/`double`) are
  value, boxed (`Integer`/`Double`) are references with autoboxing (cache traps
  for small values). S value types become immutable classes; watch autoboxing
  allocation in hot loops.
- **Checked exceptions must be declared or caught.** S `Result<T,E>` → either a
  checked exception (declared) or an unchecked `RuntimeException`. Pick a
  codebase convention; don't mix.
- **Null unchecked** — use `Optional<T>` for return types, but don't store it in
  fields (anti-pattern). `@Nullable` annotations for documentation.
- **`try-with-resources`** for RAII (`AutoCloseable`). Maps S's `Drop`/`using`/
  `defer` cleanly. `finally` for the rest.
- **Records (Java 16+)** for value-like data classes — `record Point(int x, int y)`.
  Immutable, value `equals`/`hashCode`. Port S's struct/POD here.
- **Pattern matching / sealed interfaces (17+)** for sum types — sealed interface
  + records + `switch` pattern matching. Port S's enum-with-data here (before 17,
  enum-with-field + visitor/switch-on-ordinal).

## As target (porting INTO Kotlin)

- **Nullability in the type system** — port nullable refs to `T?`, non-null to
  `T`. S's `Option<T>` → `T?` (idiomatic) or keep a `Result`/sealed type. The
  compiler enforces — so get the nullability right, it's load-bearing.
- **`data class`** for value types (auto `equals`/`hashCode`/`copy`). **Sealed
  classes/interfaces** for sum types (exhaustive `when`). **`object`** for
  singletons (thread-safe lazy). **`companion object`** for static-like members.
- **Coroutines** (`suspend fun`, `Dispatchers`) — structured concurrency,
  cancellable. Maps S's async/await closely; not OS threads. `runBlocking` to
  bridge to blocking code.
- **Extension functions** let you add methods to existing types — port S's
  utility/helper functions as extensions. Top-level functions allowed.
- **Operator overloading is supported** (`operator fun plus`). Port S's operators.
- **Smart casts** after `is`/`null` checks — no manual cast. `when` is exhaustive
  on sealed types.

## Idiom map (key traps)

| Source pattern | Java | Kotlin | Trap |
|---|---|---|---|
| `Option<T>` | `Optional<T>` (return only) | `T?` | Don't store `Optional` in fields |
| enum-with-data | enum + field, or sealed+record | sealed class | Pre-16 Java: enum + visitor |
| `Result<T,E>` | checked/unchecked exception | `Result` lib or exception | Checked must be declared (Java) |
| RAII `Drop` | `try-with-resources` | `use {}` / `Closeable` | Resource must be `AutoCloseable` |
| generics | erased | erased (reified w/ `inline`) | No `new T()` without token |
| value type / struct | immutable class / record | `data class` | Objects are heap/reference |
| operator overload | not supported | `operator fun` | Java: named methods |
| `Option::map` | `Optional.map` | `?.let {}` / `?.` | `Optional` chains differ from null-chains |
