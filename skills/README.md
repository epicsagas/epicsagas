# epicsagas/skills

Personal agent skill collection — problem discovery, cognitive self-analysis, corrective routines, and OSS distribution readiness.

## Skills

### Core

| Skill | Description | Triggers |
|-------|-------------|----------|
| **discover** | Problem discovery for individuals, teams, and startups. Reframes vague ideas into structured problem definitions (5 Whys, JTBD, Fishbone, Socratic, etc.) | Vague requests, solution-first thinking, "what should we build" |
| **introspect** | Evidence-based analysis of thinking patterns from conversation history — cognitive biases, decision-making style, actionable routines | "cognitive audit", "analyze my thinking", "my biases" |
| **oss-dist** | OSS project release readiness across the full lifecycle — community standards, README, launch strategy, distribution pipeline, i18n, security | "is this ready to open-source", "how do I distribute", "write a README" |

### Corrective Routines

Born from `introspect` analysis — individual skills targeting specific cognitive biases and decision-making blind spots.

| Skill | Routine | Corrects | Triggers |
|-------|---------|----------|----------|
| **five-whys** | 5-level root-cause drill on technical decisions | Surface-level justification, self-referential reasoning | "why", "root cause", "justify this" |
| **biz-risk** | Business impact quantification before coding | Building without business case, technical-first thinking | "biz risk", "business value", "is this worth it" |
| **devils-advocate** | 3-angle adversarial counter-argument generation | Overconfidence, unchallenged convictions | "devil's advocate", "challenge my thinking", "counter-argument" |
| **mvp-force** | 3-day MVP scope enforcement | Over-engineering, scope creep, perfectionism | "MVP", "scope check", "3-day rule" |
| **system-diet** | Forced 20% tool/plugin removal quarterly | Tool hoarding, complexity stagnation | "system diet", "declutter", "tool audit" |
| **ship-over-perfect** | Monthly mandatory external release | Perfectionism, "not ready yet" syndrome | "ship it", "not ready yet", "release" |
| **non-tech-feedback** | Non-technical audience comprehension test | Self-referential complexity, user-blind design | "explain simply", "for non-tech", "mom test" |
| **asymmetric-learning** | Weekly cross-domain book learning | Domain myopia, innovation plateau | "learn something new", "outside my field" |
| **tech-debt-scan** | Codebase debt inventory with risk scoring | Hidden debt compounding, "fix it later" pattern | "tech debt", "TODO scan", "debt audit" |
| **env-test** | Cross-environment compatibility validation | "Works on my machine" syndrome | "env test", "compatibility", "works elsewhere" |

### Tooling

| Skill | Description | Triggers |
|-------|-------------|----------|
| **git-workspace** | Git workspace manager — sync repos, bump versions, project health dashboard. Works in submodule monorepos, flat multi-repo, and single projects. | "sync repos", "pull all", "bump version", "git tags", "overview", "dashboard", "project status" |

### Experimental

| Skill | Description | Triggers |
|-------|-------------|----------|
| **skill-optimize** | SkillOpt pipeline — optimizes skill documents through trajectory-driven edits, validation-gated updates | "optimize skill", "SkillOpt", "skill training", "improve this skill" |

## Install

```bash
# Claude Code
claude plugin marketplace add epicsagas/plugins
claude plugin enable epicsagas

# Codex CLI
codex plugin marketplace add epicsagas/plugins
# In Codex TUI
/plugins install epicsagas

# Antigravity
agy plugin install https://github.com/epicsagas/epicsagas
```

## License

Apache-2.0
