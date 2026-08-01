// Port of main.py (word counter) — Python -> Rust.
// Phase A draft, verified to compile in Phase B.
//
// Axis classification (S=Python, T=Rust):
//   Memory: GC -> ownership+borrow. `text` owned in main, borrowed as &str in
//     count_words. `counts` owned HashMap.
//   Error: exceptions -> Result/early exit. OSError -> io::Error; arg parse
//     and missing-arg paths exit(1) (Python sys.exit(1) behavior preserved).
//   Null:  `counts.get(w,0)` -> entry API (no null; the "0 default" is or_insert).
//   Casts: `int(argv[2])` -> str::parse::<usize>() (checked).
//
// Names preserved (both snake_case). Field order / control flow 1:1.

use std::collections::HashMap;
use std::env;
use std::fs;
use std::process;

fn count_words(text: &str) -> HashMap<String, u32> {
    let mut counts: HashMap<String, u32> = HashMap::new();
    for word in text.split_whitespace() {
        // PORT NOTE: Python .split() collapses runs; Rust split_whitespace does too.
        let w = word
            .trim_matches(|c| matches!(c, ',' | '.' | ';' | ':' | '!' | '?'))
            .to_ascii_lowercase();
        if w.is_empty() {
            continue;
        }
        *counts.entry(w).or_insert(0) += 1;
    }
    counts
}

fn top_n(counts: &HashMap<String, u32>, n: usize) -> Vec<(String, u32)> {
    let mut items: Vec<(String, u32)> =
        counts.iter().map(|(k, &v)| (k.clone(), v)).collect();
    // Python key=lambda kv: (-kv[1], kv[0]) => count desc, word asc.
    items.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));
    items.truncate(n);
    items
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("usage: wc <file> [n]");
        process::exit(1);
    }
    let path = &args[1];
    let n: usize = if args.len() > 2 {
        match args[2].parse() {
            Ok(v) => v,
            Err(_) => {
                eprintln!("error: invalid integer");
                process::exit(1);
            }
        }
    } else {
        10
    };
    let text = match fs::read_to_string(path) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("error: {e}");
            process::exit(1);
        }
    };
    let counts = count_words(&text);
    for (word, c) in top_n(&counts, n) {
        println!("{c:6} {word}");
    }
}

// ──────────────────────────────────────────────────────────────────────────
// PORT STATUS
//   source:     main.py (35 lines)
//   confidence: high
//   todos:      0
//   notes:      text kept as UTF-8 String (Python opened with encoding=utf-8);
//               byte-path port would use read() -> Vec<u8> + bstr. Verified compiles.
// ──────────────────────────────────────────────────────────────────────────
