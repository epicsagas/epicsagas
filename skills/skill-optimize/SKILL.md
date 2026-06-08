---
name: skill-optimize
description: "Uses SkillOpt (text-space optimizer) to train and evolve natural-language skill documents for frozen LLM agents. Generates benchmark data from real tasks, builds environment adapters, runs rollout-reflect-aggregate-update training loops, and produces an optimized skill document. Triggers on: 'optimize skill', 'SkillOpt', 'skill training', 'improve this skill', 'skill experiment'."
---

# Skill Optimize — Text-Space Skill Document Optimizer

Use SkillOpt to automatically improve agent skill documents through trajectory-driven edits and validation-gated updates.

## Path Convention

```
SKILL_DIR  = {this skill-optimize directory}
TARGET_DIR = {target skill directory}    # e.g. ~/.claude/skills/sqlx
WORK_DIR   = TARGET_DIR/.skillopt       # training data persists at target
```

All training outputs live under `TARGET_DIR/.skillopt/` — the target skill's own directory, **not** skill-optimize's directory. Different skills → different data locations.

`.skillopt/` stores training outputs, data splits, and run history. **Never delete `.skillopt/`** — it contains the audit trail and enables resume.

## When to Trigger

**Auto-trigger**: Skill underperforms repeatedly (wrong commands, missed edge cases, inconsistent behavior across similar tasks).

**Explicit** (`/skill-optimize`): User wants to experimentally improve a specific skill document.

## Constraints (NON-NEGOTIABLE)

1. **Real data only** — benchmark splits must come from actual task traces, not synthetic examples
2. **Before/After comparison** — always measure baseline accuracy before training
3. **Validation gate** — never accept a skill revision that scores lower than the previous best
4. **No API key leakage** — use claude CLI auth (already logged in), never hardcode keys
5. **Answer in Korean** unless user writes in English

## Prerequisites

```bash
# Install SkillOpt (pip)
pip install skillopt

# Verify
python -c "import skillopt; print('ok')"
claude auth status 2>/dev/null || echo "Run claude auth login"
```

## Process

### Step 1: Choose target skill

Identify the skill document to optimize:

```
Target: {skill_name}
Path:   {skill_path}/SKILL.md
Goal:   Improve {specific metric or behavior}
```

Validation criteria:
- Skill document exists and is readable
- Skill has measurable success/failure (commands, outputs, structured responses)
- Enough real-world task data exists to form train/val/test splits (≥50 items)

### Step 2: Generate benchmark data

Use `scripts/build_env_split.py` — override `collect_tasks()` and `build_items()` for your environment.

```bash
SPLIT_DIR=TARGET_DIR/.skillopt/envs/{env}/data/split python scripts/build_env_split.py
```

### Step 3: Build environment adapter

Use `templates/adapter.py` — copy to your project, implement `rollout()` and evaluator.

Required adapter structure (all under `TARGET_DIR/.skillopt/`):
```
TARGET_DIR/.skillopt/
├── envs/{env_name}/
│   ├── adapter.py      # from template
│   ├── dataloader.py   # SplitDataLoader subclass
│   ├── rollout.py      # rollout logic (ThreadPoolExecutor)
│   ├── evaluator.py    # response scoring (em, f1)
│   ├── data/
│   │   └── split/      # train.json, val.json, test.json
│   └── prompts/
│       └── rollout_system.md
└── outputs/            # training results
```

Key methods to implement (from `EnvAdapter` ABC):
- `rollout(env_manager, skill_content, out_dir)` — run agent + evaluate
- `reflect(results, skill_content, out_dir)` — generate edit suggestions (default: `run_minibatch_reflect`)
- `get_task_types()` — return list of task type strings

### Step 4: Configure

Copy `configs/default.yaml` → `configs/{env_name}/default.yaml`, fill env-specific fields.

Set `skill_init` to the original SKILL.md path directly — **never copy the skill document**:
```yaml
env:
  skill_init: "TARGET_DIR/SKILL.md"
```

### Step 5: Run training

**Recommended: probe mode** — runs 1 lightweight epoch first, exits early if skill is already optimal:
```bash
python scripts/train.py --config configs/{env_name}/default.yaml --probe
```

Full training (all epochs unconditionally):
```bash
python scripts/train.py --config configs/{env_name}/default.yaml
```

Training loop: Rollout → Reflect → Aggregate → Select (gate) → Update (bounded edit)

Output: `TARGET_DIR/.skillopt/outputs/{env_name}_{model}_{timestamp}/best_skill.md`

### Step 6: Evaluate and apply

Compare baseline vs optimized accuracy. If positive delta → apply `best_skill.md` to skill path.

## Token-Saving Defaults

SkillOpt is text-space (not weight-space), but each epoch calls claude CLI for rollouts and the optimizer API for reflect/merge. Token cost scales with `num_epochs × batch_size × (1 + use_slow_update × 20)`.

Recommended config for token efficiency:
```yaml
num_epochs: 4
failure_only: true          # skip success patches unless needed
use_slow_update: false      # disable expensive epoch-boundary re-rollout (20×2 items)
use_meta_skill: false       # skip meta-skill overhead
```

Use `--probe` to auto-detect whether full training is worthwhile:
- Probe: 1 epoch, no slow_update, no meta_skill → ~15-20% of full-run tokens
- If 0 patches → exit (skill already optimal)
- If patches found → resume with remaining epochs + optional slow_update

## SkillOpt Architecture Reference

- **Text-space optimization**: edits natural-language skill documents, not weights
- **Validation gate**: rejects revisions that score worse than current best
- **Bounded edit budget**: `learning_rate` controls max edits per step
- **Resume-aware**: `results.jsonl` allows interrupted runs to continue
- **Backend**: `claude_chat` uses claude CLI subprocess (no API key needed)

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|--------|----------|-----------|
| "My skill is already good enough" | Have you measured it? | Run baseline evaluation first. |
| "I can just manually improve it" | Manual edits are untested guesses. | Let the data drive improvements. |
| "Training takes too long" | 4 epochs × ~14 steps is ~1-2 hours. | Start training, do something else. |
| "It might make it worse" | Validation gate prevents regression. | The gate is the safety net. |

## Known Working Environments

| Environment | Target Skill | Data Source | Baseline → Optimized |
|-------------|-------------|-------------|---------------------|
| vaultdoctor | vault-doctor | vault-doctor scan --json | 70.6% → 100% (+29.4%p, 1 step) |

## Red Flags

- Baseline accuracy <30% (adapter or evaluator broken)
- No improvement across epochs (data quality issue or skill already optimal)
- Validation gate rejects every update (try different model or increase edit budget)
- All items have same answer (benchmark too easy)

## Agent Instructions

### Do
- Always measure baseline before training
- Use real task data, not synthetic
- Keep the original skill as backup
- Document experiment results (positive or negative)

### Do Not
- Skip the validation gate
- Hardcode API keys in config files
- Apply optimized skill without reviewing changes
- Delete training output directory (contains audit trail)
