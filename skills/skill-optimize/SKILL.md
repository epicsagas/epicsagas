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

Copy `configs/default.yaml` → `TARGET_DIR/.skillopt/configs/default.yaml`, fill env-specific fields.

Set `skill_init` to the original SKILL.md path directly — **never copy the skill document**:
```yaml
env:
  skill_init: "TARGET_DIR/SKILL.md"
```

### Step 5: Run training

**Recommended: probe mode** — runs 1 lightweight epoch first, exits early if skill is already optimal:
```bash
python scripts/train.py --config TARGET_DIR/.skillopt/configs/default.yaml --probe
```

Full training (all epochs unconditionally):
```bash
python scripts/train.py --config TARGET_DIR/.skillopt/configs/default.yaml
```

Training loop: Rollout → Reflect → Aggregate → Select (gate) → Update (bounded edit)

Output: `TARGET_DIR/.skillopt/outputs/{env_name}_{model}_{timestamp}/best_skill.md`

### Step 6: Evaluate and apply

Compare baseline vs optimized accuracy. If positive delta → apply `best_skill.md` to skill path.

## Token Cost Control

SkillOpt edits skill documents in text space — the trained artifact is a compact `best_skill.md` (~300-2000 tokens) with **zero inference-time cost at deployment**. But training itself calls LLM APIs for rollouts and optimizer analysis.

### Cost Formula

```
total_calls ≈ epochs × steps × (batch / minibatch)   # reflect + aggregate
            + epochs × steps × batch                   # rollout + gate (target model)
            + epochs × use_slow_update × samples × 2   # slow update re-rollout
            + epochs × use_meta_skill                   # meta skill optimizer
```

### 10 Built-in Token-Saving Mechanisms

| # | Mechanism | How it saves | Config |
|---|-----------|-------------|--------|
| 1 | **Minibatching** | N trajectories share 1 optimizer call instead of N | `minibatch_size: 4` |
| 2 | **Selection cache** | Same skill hash → skip gate re-evaluation | automatic |
| 3 | **Checkpoint resume** | Interrupted runs never repeat completed work | automatic |
| 4 | **Skip on no patches** | 0 patches → skip aggregate+select+update+gate | automatic |
| 5 | **`failure_only`** | Skip success analysis → ~50% fewer reflect calls | `failure_only: true` |
| 6 | **Trajectory truncation** | Caps prompt tokens: 12K chars reflect, 3K slow_update | automatic |
| 7 | **Edit budget + cosine decay** | Bounds edits/step, decays over training | `learning_rate: 4`, `lr_scheduler: cosine` |
| 8 | **Step buffer** | Remembers rejected edits → avoids repeat proposals | automatic |
| 9 | **Model separation** | Cheap optimizer model for reflect/aggregate, powerful model only for rollout | `optimizer` vs `target` |
| 10 | **Gate = early stopping** | Rejects worse candidates immediately | `use_gate: true` |

### Default Config (token-efficient)

```yaml
# Already set in configs/default.yaml:
failure_only: true          # skip success patches → ~50% fewer reflect calls
use_slow_update: false      # disable expensive epoch-boundary re-rollout (20×2 calls)
use_meta_skill: false       # skip meta-skill overhead (+1 optimizer call/epoch)
```

### Probe Mode (`--probe`)

Two-pass training that auto-detects whether full training is worthwhile:

1. **Pass 1 (probe)**: 1 epoch, no slow_update, no meta_skill → ~15-20% of full-run tokens
2. **If 0 patches** → exit immediately (skill already optimal, ~80-85% token savings)
3. **If patches found** → resume with remaining epochs, re-enable slow_update/meta_skill

### Optimizer/Target Model Separation

Biggest cost lever: use a cheaper model for all optimizer calls (reflect, aggregate, ranking, slow_update) while keeping a powerful model only for rollouts.

```yaml
model:
  optimizer: claude-haiku-4-5    # cheap model for analysis
  target: claude-sonnet-4-6      # powerful model for execution
```

Since ~60-70% of calls are optimizer calls, this can reduce cost by 50-70%.

### Quick Cost Comparison

| Scenario | Target calls | Optimizer calls | Total |
|----------|-------------|-----------------|-------|
| Probe (1 epoch, defaults) | ~40 | ~8 | ~48 |
| Full (4 epochs, no slow/meta) | ~160 | ~32 | ~192 |
| Full (4 epochs, slow+meta on) | ~280 | ~36 | ~316 |
| Full + cheap optimizer | ~160 | ~32 (cheap) | ~192 mixed |

## SkillOpt Architecture Reference

- **Text-space optimization**: edits natural-language skill documents, not weights
- **Validation gate**: rejects revisions that score worse than current best
- **Bounded edit budget**: `learning_rate` controls max edits per step
- **Resume-aware**: `runtime_state.json` allows interrupted runs to continue
- **Backend**: `claude_chat` uses claude CLI subprocess (no API key needed)

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|--------|----------|-----------|
| "My skill is already good enough" | Have you measured it? | Run baseline evaluation first. |
| "I can just manually improve it" | Manual edits are untested guesses. | Let the data drive improvements. |
| "Training takes too long" | 4 epochs × ~4 steps is ~30-60 min. | Start training, do something else. |
| "It might make it worse" | Validation gate prevents regression. | The gate is the safety net. |
| "It uses too many tokens" | Probe mode exits early if skill is optimal. | Use `--probe` first. |

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
- Use `--probe` first to check if optimization is needed
- Consider cheap optimizer model for reflect/aggregate

### Do Not
- Skip the validation gate
- Hardcode API keys in config files
- Apply optimized skill without reviewing changes
- Delete training output directory (contains audit trail)
- Enable slow_update/meta_skill for short runs (≤2 epochs)
