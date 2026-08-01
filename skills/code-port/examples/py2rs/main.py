import sys


def count_words(text):
    counts = {}
    for word in text.split():
        w = word.lower().strip(",.;:!?")
        if not w:
            continue
        counts[w] = counts.get(w, 0) + 1
    return counts


def top_n(counts, n):
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return items[:n]


def main():
    if len(sys.argv) < 2:
        print("usage: wc <file> [n]", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    counts = count_words(text)
    for word, c in top_n(counts, n):
        print(f"{c:6} {word}")


if __name__ == "__main__":
    main()
