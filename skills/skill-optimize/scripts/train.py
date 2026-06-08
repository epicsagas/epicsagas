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
import math
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


def _estimate_calls(flat: dict) -> dict:
    """Estimate total API calls for current config.

    Returns breakdown of optimizer vs target calls.
    """
    epochs = flat.get("num_epochs", 4)
    batch = flat.get("batch_size", 8)
    mini = flat.get("minibatch_size", 4)
    accumulation = flat.get("accumulation", 1)
    use_slow = flat.get("use_slow_update", False)
    slow_samples = flat.get("slow_update_samples", 20)
    use_meta = flat.get("use_meta_skill", False)

    train_size = flat.get("train_size", 0)
    if train_size > 0:
        steps_per_epoch = max(1, math.ceil(train_size / (batch * accumulation)))
    else:
        # Default: ~4 steps when train_size=0 (auto-detected by trainer)
        steps_per_epoch = 4

    # Rollout: batch_size target calls per step × accumulation
    rollout_target = steps_per_epoch * batch * accumulation * epochs
    # Baseline + test evaluations
    baseline_target = batch  # baseline on selection split
    test_target = batch  # final test

    # Reflect: (batch / minibatch_size) optimizer calls per step
    reflect_opt = steps_per_epoch * math.ceil(batch / mini) * epochs
    # Aggregate: ~ceil(reflect_batches / merge_batch_size) per step
    merge_batch = flat.get("merge_batch_size", 4)
    aggregate_opt = steps_per_epoch * math.ceil(
        math.ceil(batch / mini) / merge_batch
    ) * epochs
    # Select (ranking): 1 per step, only when patches > learning_rate
    select_opt = steps_per_epoch * epochs
    # Gate: selection split evaluation per step → target calls
    gate_target = steps_per_epoch * batch * epochs

    # Slow update: N × 2 target rollouts + 1 optimizer call per epoch (from epoch 2)
    slow_target = (epochs - 1) * slow_samples * 2 if use_slow else 0
    slow_opt = (epochs - 1) if use_slow else 0

    # Meta skill: 1 optimizer call per epoch (from epoch 2)
    meta_opt = (epochs - 1) if use_meta else 0

    total_target = rollout_target + baseline_target + test_target + gate_target + slow_target
    total_opt = reflect_opt + aggregate_opt + select_opt + slow_opt + meta_opt

    return {
        "epochs": epochs,
        "steps_per_epoch": steps_per_epoch,
        "target_calls": total_target,
        "optimizer_calls": total_opt,
        "total_calls": total_target + total_opt,
        "breakdown": {
            "rollout_target": rollout_target,
            "gate_target": gate_target,
            "slow_update_target": slow_target,
            "reflect_opt": reflect_opt,
            "aggregate_opt": aggregate_opt,
            "select_opt": select_opt,
            "slow_update_opt": slow_opt,
            "meta_skill_opt": meta_opt,
        },
    }


def _print_header(flat: dict, mode: str = "FULL") -> None:
    cost = _estimate_calls(flat)
    env = flat.get("env") or flat.get("env_name", "")

    print(f"\n{'=' * 60}")
    print(f"  SkillOpt — Text-Space Skill Document Optimizer [{mode}]")
    print(f"{'=' * 60}")
    print(f"  env:             {env}")
    print(f"  optimizer_model: {flat.get('optimizer_model')}")
    print(f"  target_model:    {flat.get('target_model')}")
    print(f"  epochs:          {flat.get('num_epochs')}")
    print(f"  batch_size:      {flat.get('batch_size')}")
    print(f"  failure_only:    {flat.get('failure_only', False)}")
    print(f"  slow_update:     {flat.get('use_slow_update', False)}")
    print(f"  meta_skill:      {flat.get('use_meta_skill', False)}")
    print(f"  edit_budget:     {flat.get('edit_budget')}")
    print(f"  out_root:        {flat['out_root']}")
    print(f"{'─' * 60}")
    print(f"  Cost estimate:")
    print(f"    target calls:    ~{cost['target_calls']}")
    print(f"    optimizer calls: ~{cost['optimizer_calls']}")
    print(f"    total calls:     ~{cost['total_calls']}")
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
    _print_header(flat, mode="FULL")

    adapter = get_adapter(flat)
    trainer = ReflACTTrainer(flat, adapter)
    summary = trainer.train()

    _print_summary(flat, summary)


def _run_probe(flat: dict) -> None:
    """Two-pass training: lightweight probe then conditional full run.

    Pass 1 (probe): 1 epoch, slow_update=false, meta_skill=false.
    If 0 patches → skill already optimal, exit.
    If patches → resume with remaining epochs + re-enable slow/meta from epoch 2.

    Token savings when skill is already optimal: ~80-85%.
    Token savings when patches found: ~15-20% (probe is lightweight).
    """
    total_epochs = flat.get("num_epochs", 4)
    original_slow = flat.get("use_slow_update", False)
    original_meta = flat.get("use_meta_skill", False)

    # ── Pass 1: probe ───────────────────────────────────────────────────
    flat["num_epochs"] = 1
    flat["use_slow_update"] = False
    flat["use_meta_skill"] = False

    _print_header(flat, mode="PROBE 1/1")

    adapter = get_adapter(flat)
    trainer = ReflACTTrainer(flat, adapter)
    trainer.train()

    history = _load_history(flat["out_root"])
    n_patches = _count_patches(history)
    n_skips = _count_skips(history)

    print(f"\n  [probe result] patches={n_patches} skips={n_skips}")

    if n_patches == 0:
        print(f"\n  ⚠ No patches generated in probe epoch.")
        print(f"  Skill appears already optimal or analyst cannot improve it.")
        saved = total_epochs - 1
        print(f"  Early exit: saved ~{saved} epochs of training.")
        print(f"  Tip: try --cfg-options gradient.failure_only=false if you want")
        print(f"       success-pattern analysis, or increase num_epochs.\n")
        return

    # ── Pass 2: full training with resume ───────────────────────────────
    flat["num_epochs"] = total_epochs
    flat["use_slow_update"] = original_slow
    flat["use_meta_skill"] = original_meta

    _print_header(flat, mode=f"FULL (resume 2/{total_epochs})")

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
