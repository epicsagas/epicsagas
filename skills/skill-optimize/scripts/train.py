#!/usr/bin/env python3
"""Minimal SkillOpt training wrapper using pip-installed skillopt.

Usage
-----
    python scripts/train.py --config configs/{env_name}/default.yaml
    python scripts/train.py --config configs/default.yaml --cfg-options train.num_epochs=2

Uses ReflACTTrainer from the installed skillopt package.
Built-in environment adapters are registered automatically.
"""

from __future__ import annotations

import argparse
import datetime
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
    return p.parse_args()


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

    adapter = get_adapter(flat)
    trainer = ReflACTTrainer(flat, adapter)
    summary = trainer.train()

    print(f"\n  Output saved to: {flat['out_root']}")
    if summary.get("test_hard") is not None:
        print(f"  Final test: {summary['test_hard']:.4f}")


if __name__ == "__main__":
    main()
