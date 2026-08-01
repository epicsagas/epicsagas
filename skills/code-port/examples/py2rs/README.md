# Example: Python → Rust (word counter)

A worked end-to-end port following `code-port`. `main.py` → `main.rs`, both
runnable. Use this as a reference for what Phase A/B look like in practice.

## Source

A small CLI word-frequency counter: reads a file, lowercases + strips
punctuation, counts, prints top-N. Exercises GC→ownership, exceptions→`Result`,
dict→map, and arg-parsing error paths.

## Axis classification (load `references/python.md` + `references/rust.md`)

| Axis | Python (S) | Rust (T) | Decision |
|------|-----------|----------|----------|
| Memory | GC | ownership + borrow | `text` owned in `main`, borrowed as `&str` into `count_words`; `counts` owned `HashMap` |
| Error | exceptions (`OSError`) | `Result` / early exit | file open → `fs::read_to_string` + `match`; `sys.exit(1)` → `process::exit(1)` |
| Null | `counts.get(w, 0)` (absent default) | `Option` / entry API | `.entry(w).or_insert(0)` — the "0 default" is explicit, no nullable |
| Casts | `int(argv[2])` (raises `ValueError`) | checked parse | `args[2].parse::<usize>()` with `Err` → exit |

Names preserved (both already `snake_case`). Control flow, parameter order,
and output format are 1:1.

## Phase A → Phase B

- **Phase A** — wrote `main.rs` with the mapping above; `// PORT NOTE` flags the
  `.split()`↔`split_whitespace()` equivalence and the sort-key translation.
- **Phase B** — `rustc -O main.rs -o wc` → **exit 0**.

## Equivalence check

Sample input run through both:

```
     5 dog
     5 the
     3 quick
     2 fox
     1 brown
```

`diff` of Python-vs-Rust output → **empty (byte-identical)**. The port preserves
behavior, not just shape.

## Notes

- Text kept as UTF-8 `String` because `main.py` opens with `encoding="utf-8"`.
  A byte-path port (arbitrary bytes, invalid UTF-8) would use `fs::read()` →
  `Vec<u8>` + `bstr` — that decision comes from §Ownership in the skill.
- No `unsafe`, no `TODO(port)` left — confidence `high`.
