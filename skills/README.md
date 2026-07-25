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

### Writing — Korean (윤문)

A staged Korean prose-polishing suite. `korean-polish` orchestrates the five
specialists top-down (verbosity → translationese → register → norm-lint →
cohesion) under a meaning-preserving contract (math, numbers, citations, and
defined terms are frozen). Grounded in 국립국어원 어문규범, translationese
research, and **real Korean 경제학/CS journal conventions** (the register stage
retargets prose to native academic register — 화자 표지, 분야 주어 강등, field-specific
한자어/외래어); tuned for academic/technical Korean and English→Korean translations.
Shared reference packs live in `korean-polish/references/`.

| Skill | Description | Triggers |
|-------|-------------|----------|
| **korean-polish** | Orchestrator — staged 윤문 pass with term glossary, intensity dial, and a meaning-preserving diff report | "윤문", "한국어 다듬어", "번역투 고쳐", "polish Korean" |
| **korean-translationese** | English→Korean interference: 무생물 주어, we/우리, ~의 그것, 피동·이중피동, have/there-is/사동, 숙어, 하나의, 무정물 ~들 | "번역투", "번역체 고쳐", "직역투", "translationese" |
| **korean-verbosity** | 만연체 splitting, 명사화→동사화, 겹말 removal | "만연체", "문장 분할", "간결하게", "명사화 풀어" |
| **korean-register** | Academic 서술체·시제, 구어체 removal, one-term-per-concept | "학술 문체", "용어 일관성", "구어체 고쳐", "논문체" |
| **korean-norm-lint** | Deterministic 어문규범: 띄어쓰기·조사·문장부호·맞춤법 | "띄어쓰기", "맞춤법", "어문규범", "문장부호" |
| **korean-cohesion** | 주술 호응, 지시어·접속부사 남용, 병렬 | "호응", "지시어 남용", "접속부사", "병렬" |

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
