#!/usr/bin/env python3
"""Minimal SkillOpt training wrapper using pip-installed skillopt.

Usage
-----
    python scripts/train.py --config configs/{env_name}/default.yaml
    python scripts/train.py --config configs/default.yaml --cfg-options train.num_epochs=2
    python scripts/train.py --config configs/default.yaml --probe   # 1-epoch probe then decide

Uses ReflACTTrainer from the installed skillopt package.
Built-in environment adapters are registered automatically.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os

from skillopt.config import (
    load_config as _load,
    flatten_config,
    is_structured,
)
from skillopt.engine.trainer import ReflACTTrainer

# ── Environment registry ────────────────────────────────────────────────────

_ENV_REGISTRY: dict[str, type] = {}

_BUILTIN_ENVS = [
    ("alfworld", "skillopt.envs.alfworld.adapter", "ALFWorldAdapter"),
    ("searchqa", "skillopt.envs.searchqa.adapter", "SearchQAAdapter"),
    (
        "livemathematicianbench",
        "skillopt.envs.livemathematicianbench.adapter",
        "LiveMathematicianBenchAdapter",
    ),
    (
        "spreadsheetbench",
        "skillopt.envs.spreadsheetbench.adapter",
        "SpreadsheetBenchAdapter",
    ),
    ("docvqa", "skillopt.envs.docvqa.adapter", "DocVQAAdapter"),
    ("officeqa", "skillopt.envs.officeqa.adapter", "OfficeQAAdapter"),
    # vaultdoctor, alcove_skill — not in pip package; add locally if needed
]

# Local adapters: (name, file_path, class_name)
_CUSTOM_ENVS: list[tuple[str, str, str]] = []


def register_custom_env(name: str, adapter_path: str, class_name: str) -> None:
    """Register a local adapter file for an environment."""
    _CUSTOM_ENVS.append((name, adapter_path, class_name))


def _register_builtins() -> None:
    for name, module_path, cls_name in _BUILTIN_ENVS:
        if name in _ENV_REGISTRY:
            continue
        try:
            import importlib

            mod = importlib.import_module(module_path)
            _ENV_REGISTRY[name] = getattr(mod, cls_name)
        except (ImportError, AttributeError):
            pass

    # Load local adapters from file paths
    for name, adapter_path, cls_name in _CUSTOM_ENVS:
        if name in _ENV_REGISTRY:
            continue
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                f"skillopt_custom_{name}", adapter_path
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                _ENV_REGISTRY[name] = getattr(mod, cls_name)
        except Exception as exc:
            print(
                f"  Warning: failed to load custom env '{name}' from {adapter_path}: {exc}"
            )


def get_adapter(cfg: dict):
    _register_builtins()
    env_name = cfg.get("env") or cfg.get("env_name", "")
    if not env_name:
        raise ValueError("env.name not set in config")
    if env_name not in _ENV_REGISTRY:
        raise ValueError(
            f"Unknown environment '{env_name}'. Available: {list(_ENV_REGISTRY.keys())}"
        )
    adapter_cls = _ENV_REGISTRY[env_name]
    import inspect

    sig = inspect.signature(adapter_cls.__init__)
    accepted = set(sig.parameters.keys()) - {"self"}
    adapter_kwargs = {k: cfg[k] for k in accepted if k in cfg}
    return adapter_cls(**adapter_kwargs)


# ── CLI ──────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="SkillOpt training wrapper")
    p.add_argument("--config", type=str, required=True, help="Path to YAML config file")
    p.add_argument(
        "--cfg-options",
        nargs="+",
        default=[],
        help="Override config: section.key=value",
    )
    p.add_argument(
        "--probe",
        action="store_true",
        help="Run 1-epoch probe with slow_update/meta_skill disabled. "
        "If no patches generated, exit early. Otherwise resume full training.",
    )
    return p.parse_args()


# ── Helpers ──────────────────────────────────────────────────────────────────


def _load_history(out_root: str) -> list[dict]:
    path = os.path.join(out_root, "history.json")
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        return json.load(f)


def _count_patches(history: list[dict]) -> int:
    return sum(h.get("n_patches", 0) for h in history)


def _count_skips(history: list[dict]) -> int:
    return sum(1 for h in history if h.get("action") == "skip_no_patches")


def _print_header(flat: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"  SkillOpt — Text-Space Skill Document Optimizer")
    print(f"{'=' * 60}")
    print(f"  env:             {flat.get('env') or flat.get('env_name')}")
    print(f"  optimizer_model: {flat.get('optimizer_model')}")
    print(f"  target_model:    {flat.get('target_model')}")
    print(f"  epochs:          {flat.get('num_epochs')}")
    print(f"  batch_size:      {flat.get('batch_size')}")
    print(f"  edit_budget:     {flat.get('edit_budget')}")
    print(f"  out_root:        {flat['out_root']}")
    print(f"{'=' * 60}\n")


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    args = parse_args()

    cfg = _load(args.config, overrides=args.cfg_options)
    structured = is_structured(cfg)
    flat = flatten_config(cfg) if structured else cfg

    # Expand ~ in path fields
    for key in ("skill_init", "out_root", "split_dir", "adapter_path", "data_path"):
        if flat.get(key):
            flat[key] = os.path.expanduser(flat[key])

    # Register custom adapter if specified in config
    adapter_path = flat.get("adapter_path", "")
    env_name = flat.get("env") or flat.get("env_name", "")
    if adapter_path and env_name:
        adapter_cls_name = flat.get("adapter_class", "Adapter")
        register_custom_env(env_name, adapter_path, adapter_cls_name)

    # Auto-generate output root
    if not flat.get("out_root"):
        env = flat.get("env") or flat.get("env_name", "unknown")
        model = (flat.get("optimizer_model") or "unknown").replace("/", "-")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        flat["out_root"] = os.path.abspath(
            os.path.join("outputs", f"skillopt_{env}_{model}_{ts}")
        )

    if args.probe:
        _run_probe(flat)
    else:
        _run_full(flat)


def _run_full(flat: dict) -> None:
    """Run full training with all config options."""
    _print_header(flat)

    adapter = get_adapter(flat)
    trainer = ReflACTTrainer(flat, adapter)
    summary = trainer.train()

    _print_summary(flat, summary)


def _run_probe(flat: dict) -> None:
    """Two-pass training: lightweight probe then conditional full run.

    Pass 1 (probe): 1 epoch, slow_update=false, meta_skill=false.
    If 0 patches → skill already optimal, exit.
    If patches → resume with remaining epochs + full features.
    """
    total_epochs = flat.get("num_epochs", 4)
    original_slow = flat.get("use_slow_update", True)
    original_meta = flat.get("use_meta_skill", True)

    # ── Pass 1: probe ───────────────────────────────────────────────────
    flat["num_epochs"] = 1
    flat["use_slow_update"] = False
    flat["use_meta_skill"] = False

    print(f"\n{'=' * 60}")
    print(f"  SkillOpt — PROBE (1 epoch, no slow_update/meta_skill)")
    print(f"{'=' * 60}")
    print(f"  env:             {flat.get('env') or flat.get('env_name')}")
    print(f"  epochs:          1/{total_epochs} (probe)")
    print(f"  slow_update:     OFF")
    print(f"  meta_skill:      OFF")
    print(f"  out_root:        {flat['out_root']}")
    print(f"{'=' * 60}\n")

    adapter = get_adapter(flat)
    trainer = ReflACTTrainer(flat, adapter)
    trainer.train()

    history = _load_history(flat["out_root"])
    n_patches = _count_patches(history)
    n_skips = _count_skips(history)

    print(f"\n  [probe] patches={n_patches} skips={n_skips}")

    if n_patches == 0:
        print(f"\n  ⚠ No patches generated in probe epoch.")
        print(f"  Skill appears already optimal or analyst cannot improve it.")
        print(f"  Skipping remaining {total_epochs - 1} epochs.\n")
        return

    # ── Pass 2: full training with resume ───────────────────────────────
    flat["num_epochs"] = total_epochs
    flat["use_slow_update"] = original_slow
    flat["use_meta_skill"] = original_meta

    print(f"\n{'=' * 60}")
    print(f"  SkillOpt — FULL TRAINING (resume from probe)")
    print(f"{'=' * 60}")
    print(f"  epochs:          {total_epochs} (resume from epoch 2)")
    print(f"  slow_update:     {'ON' if original_slow else 'OFF'}")
    print(f"  meta_skill:      {'ON' if original_meta else 'OFF'}")
    print(f"{'=' * 60}\n")

    adapter = get_adapter(flat)
    trainer = ReflACTTrainer(flat, adapter)
    summary = trainer.train()

    _print_summary(flat, summary)


def _print_summary(flat: dict, summary: dict) -> None:
    print(f"\n  Output saved to: {flat['out_root']}")
    if summary.get("test_hard") is not None:
        print(f"  Final test: {summary['test_hard']:.4f}")


if __name__ == "__main__":
    main()
