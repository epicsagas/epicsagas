#!/usr/bin/env python3
"""Generate data splits for SkillOpt training.

Usage:
    cd /Volumes/T5/projects/SkillOpt
    source .venv/bin/activate
    python scripts/build_{env_name}_split.py

Override via env vars:
    SPLIT_DIR, VAULT_ROOT, RATIO, SEED
"""
import json
import os
import random
from collections import defaultdict

SPLIT_DIR = os.environ.get("SPLIT_DIR", "")
RATIO = tuple(int(x) for x in os.environ.get("RATIO", "6:2:2").split(":"))
SEED = int(os.environ.get("SEED", "42"))


def collect_tasks() -> list[dict]:
    """Override this per environment. Collect raw task instances."""
    raise NotImplementedError("Implement collect_tasks() for your environment")


def build_items(raw_tasks: list[dict]) -> list[dict]:
    """Convert raw tasks into SkillOpt items.

    Required fields per item:
        id, question, answers, task_type
    Optional:
        kind (for stratified split), context, file, severity, detail
    """
    raise NotImplementedError("Implement build_items() for your environment")


def stratified_split(items: list[dict], ratio: tuple, seed: int):
    by_kind = defaultdict(list)
    for item in items:
        by_kind[item.get("kind", "default")].append(item)

    rng = random.Random(seed)
    train, val, test = [], [], []
    for kind_items in by_kind.values():
        rng.shuffle(kind_items)
        n = len(kind_items)
        t = round(n * ratio[0] / sum(ratio))
        v = round(n * ratio[1] / sum(ratio))
        train.extend(kind_items[:t])
        val.extend(kind_items[t:t + v])
        test.extend(kind_items[t + v:])
    return train, val, test


def main():
    assert SPLIT_DIR, "Set SPLIT_DIR env var or override in subclass"
    raw = collect_tasks()
    items = build_items(raw)
    train, val, test = stratified_split(items, RATIO, SEED)
    print(f"Total: {len(items)} → train={len(train)} val={len(val)} test={len(test)}")

    for name, split in [("train", train), ("val", val), ("test", test)]:
        path = os.path.join(SPLIT_DIR, name)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "items.json"), "w", encoding="utf-8") as f:
            json.dump(split, f, ensure_ascii=False, indent=2)

    manifest = {
        "total": len(items),
        "ratio": f"{RATIO[0]}:{RATIO[1]}:{RATIO[2]}",
        "seed": SEED,
        "counts": {"train": len(train), "val": len(val), "test": len(test)},
    }
    with open(os.path.join(SPLIT_DIR, "split_manifest.json"), "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
