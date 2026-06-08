---
name: oss-dist
description: "Audits and guides OSS project release readiness across the full lifecycle: community standards, README quality, launch strategy, distribution pipeline, and governance/security posture. Activates when reviewing, planning, or shipping an open-source project — at any stage from initial setup to public launch."
---

# OSS Distribution & Readiness Skill

## When to Use

- User asks **"is this project ready to open-source / release / launch?"**
- User asks about **what files an OSS project needs** (README, LICENSE, CONTRIBUTING, etc.)
- User asks **how to install or distribute** a tool (language-specific packaging)
- User asks about **GitHub Actions release pipelines** or CI/CD for releases
- User wants **launch strategy** — which channels, timing, Korean ecosystem
- User asks about **security practices** for OSS publishing (SBOM, secret scanning, supply chain)
- User asks about **governance**, maintainer roles, or RFC process
- User wants to know **how to package** for Homebrew, apt, npm, PyPI, etc.
- User asks about **version management tools** (release-please, semantic-release, cargo-dist)
- User asks about **multilingual README** or translation workflow (Crowdin, Weblate, community contributions)
- User asks about **software i18n/l10n** (gettext, Fluent, react-i18next, go-i18n, rust-i18n)
- User asks **how to update / upgrade** a tool (detects brew, cargo, npm, apt, choco, etc.)
- User asks **what update command to put in README**

## Process

### Step 1: Identify the review scope

Ask (or infer from context) what the user needs:

| User intent | Files to load |
|-------------|--------------|
| Full readiness audit | All checklist files |
| "Do I have the right files?" | `checklist/community.md` |
| "Write / improve / polish my README" | `checklist/readme.md` |
| "How do I launch / promote this?" | `checklist/promotion.md` |
| "How do I package / distribute this?" | `checklist/release.md` |
| "How do I update / upgrade this tool?" | `checklist/update.md` |
| "What update command for my README?" | `checklist/update.md` |
| "Is my security / governance solid?" | `checklist/governance.md` |
| "Add translations / multilingual README" | `checklist/i18n.md` |
| "How do I i18n my CLI / library / app?" | `checklist/i18n.md` |
| Language-specific install method | `checklist/release.md` → routing table → `languages/<lang>.md` |
| Platform-specific packaging | `checklist/release.md` → `platforms/<platform>.md` |
| Tool comparison (mise, uv, etc.) | `tools/<tool>.md` |
| **epicsagas project install standard validation** | `install-best-practices.md` |
| "write install section" / "one-line install" / "unify install section" | `install-best-practices.md` + `languages/rust.md` §R.2 |
| "badge style", "배지 스타일", `--badge <preset>` | `checklist/readme.md § Badge Design Style` |
| "update", "upgrade", "self-update", "updating section" | `checklist/update.md` |
| "pre-release", "beta", "alpha", "rc", "nightly", "--pre" | `checklist/prerelease.md` |
| "docker", "container", "ghcr", "image", "multi-arch" | `checklist/docker.md` |
| "CVE", "security advisory", "patch release", "vulnerability response" | `checklist/cve-response.md` |

**Load only what's needed. Do not load all files at once.**

### Step 2: Read the relevant checklist file(s)

Checklist files are under `checklist/`:

| File | Covers |
|------|--------|
| `checklist/community.md` | GitHub community standards, license selection, repo settings |
| `checklist/readme.md` | README generate (no README) or polish (README exists) — hook copy, UX, structure |
| `checklist/promotion.md` | Launch channels, Korean ecosystem, growth milestones |
| `checklist/release.md` | CI/CD pipeline, install methods, language routing table |
| `checklist/update.md` | Update/upgrade commands, package manager detection, self-update |
| `checklist/governance.md` | Security policy, SBOM, secret scanning, governance model |
| `checklist/i18n.md` | README multilingual strategy, software i18n/l10n, translation tooling |
| `checklist/update.md` | Update/upgrade commands per install method, Updating README section template |
| `checklist/prerelease.md` | Beta/alpha/rc/nightly channels, pre-release config, graduation criteria |
| `checklist/docker.md` | Docker image distribution, GHCR, multi-arch builds |
| `checklist/cve-response.md` | CVE triage, patch release SLA, security advisory, disclosure |
| **`install-best-practices.md`** | **epicsagas project standard install block, curl flags, Homebrew notation, Updating table order** |

### Step 3: Audit against the checklist

For each item in the loaded checklist:
- ✅ Mark items the project satisfies
- ❌ Flag missing or incomplete items
- Give concrete fix suggestions, not vague advice

### Step 4: Report findings

Structure the output as:

```
## OSS Readiness: <project name>

### [Domain] — PASS / WARN / FAIL
- ✅ ...
- ❌ ... → Fix: ...

### Score
| Domain | Status |
|--------|--------|
| Community files | ✅ |
| README | ⚠️ |
| ...
```

**Scoring guide:**
| community ✅ + readme ✅ | Minimum viable OSS |
| + promotion ✅ | Launch ready |
| + release ✅ | Distribution ready |
| + governance ✅ | Sustainable OSS |

## Language / Platform Routing

When the user asks about packaging or install methods, load `checklist/release.md` first (has the routing table), then follow the relevant sub-file:

| Keywords | Sub-file |
|----------|----------|
| rust, cargo, cargo-dist | `languages/rust.md` |
| go, golang, goreleaser | `languages/go.md` |
| node, nodejs, npm, npx | `languages/node.md` |
| deno | `languages/deno.md` |
| bun | `languages/bun.md` |
| python, pip, uv, pipx | `languages/python.md` |
| java, jvm, kotlin, graalvm | `languages/java.md` |
| c, c++, zig | `languages/systems.md` |
| swift, spm, mint | `languages/swift.md` |
| mise, asdf | `tools/mise.md` |
| uv, uvx | `tools/uv.md` |
| pkgx, nix, flox | `tools/universal.md` |
| curl security, sigstore, sbom, sha pinning | `tools/security.md` |
| macos, homebrew, dmg, pkg, notarization, gatekeeper | `platforms/macos.md` |
| windows, winget, scoop | `platforms/windows.md` |
| linux, apt, dnf, snap | `platforms/linux.md` |
| update, upgrade, self-update | `checklist/update.md` |

## Agent Instructions

### Answering "is this ready to ship?"

Never answer from memory. Always load the relevant checklist file(s) first, then audit systematically.

1. Start with `checklist/community.md` — missing Tier 1 files are blockers
2. Then `checklist/readme.md` — README quality determines first impressions
3. Load others based on user's concern or explicit request

### Answering "how do I distribute this?"

1. Load `checklist/release.md` — find the project type in the routing table
2. Follow the pointer to the language-specific file
3. Give the exact commands, not generic advice

### Answering "how do I launch this?"

1. Load `checklist/promotion.md`
2. Check pre-launch gate items first — don't discuss channels if README is incomplete
3. Tailor channel advice to the language/ecosystem (e.g., Rust → r/rust + This Week in Rust)

### Security review

1. Load `checklist/governance.md`
2. Check SECURITY.md, secret scanning, SBOM, Pwn-request config, and Actions SHA pinning
3. Flag any missing items as blockers before recommending launch

### Answering "how do I update / upgrade this?"

1. Load `checklist/update.md` — the update readiness audit checklist
2. Audit the project's README: does it have an "Updating" section matching every install method?
3. Check each install method in "Installation" has a corresponding update command in "Updating"
4. Verify version check command (`--version`), CHANGELOG format, and migration guide exist
5. If missing, generate the correct update section using the template from §6.6

### Badge Style Selection

When generating or polishing badges (README generate/polish scope):

**If the user passes a style option explicitly** — use it directly:

| Option | Preset |
|--------|--------|
| `--badge bold` | `for-the-badge` + `labelColor=0d1117` (default) |
| `--badge classic` | `flat`, no labelColor |
| `--badge modern` | `flat-square`, no labelColor |
| `--badge social` | `social`, no labelColor |
| `--badge plastic` | `plastic`, no labelColor |

**If no style option is given** — ask interactively before generating badges:

```
배지 스타일을 선택해주세요:

1. bold (기본값) — for-the-badge, 다크 배경 — epicsagas 표준 스타일
2. classic       — flat, GitHub 기본 느낌
3. modern        — flat-square, 미니멀
4. social        — social, 커뮤니티 스타 카운트용
5. plastic       — plastic, 클래식 입체감

선택하지 않으면 bold(1)로 진행합니다.
```

Once a style is selected (or defaulted), apply the corresponding template from `checklist/readme.md § Badge Design Style`.

### README Language Selection

When generating a new README (GENERATE mode):

**If the user passes a language option explicitly:**
| Option | Coverage |
|--------|----------|
| `--lang en` | English only (default) |
| `--lang en,ko` | English + Korean |
| `--lang en,ko,ja,zh` | Full multilingual (i18n checklist applies) |

**If no language option is given — ask interactively:**

```
README 언어 전략을 선택해주세요:

1. 영어만 (기본값) — 글로벌 OSS 표준
2. 영어 + 한국어  — epicsagas 권장 (Korean dev community 타겟)
3. 영어 + 한+일+중 — 전체 다국어 (i18n 체크리스트 적용)

선택하지 않으면 영어만(1)으로 진행합니다.
```

For options 2–3, load `checklist/i18n.md` and apply the multilingual README structure.

### License Selection

When generating community files or README and no LICENSE exists:

**If the user specifies a license — use it directly.**

**If no license specified — ask interactively:**

```
라이선스를 선택해주세요:

1. Apache-2.0 (기본값) — epicsagas 표준, 특허 조항 포함
2. MIT           — 최소 제약, 최대 호환성
3. GPL-3.0       — Copyleft, 파생물 공개 강제
4. BSL-1.1       — Business Source License (상용 제한)

선택하지 않으면 Apache-2.0(1)으로 진행합니다.
```

### Answering "pre-release / beta / nightly"
1. Load `checklist/prerelease.md`
2. Identify the project language — check for cargo-dist or goreleaser config
3. Give concrete tag pattern and config snippet

### Answering "Docker / container image"
1. Load `checklist/docker.md`
2. Default registry: GHCR for epicsagas projects
3. Give the complete GitHub Actions workflow for multi-arch build

### Answering "CVE / security vulnerability"
1. Load `checklist/cve-response.md`
2. Assess severity tier — give SLA deadline
3. Walk through patch release + advisory steps in order

### Do not

- Do not load all sub-files unless the user requests a full audit
- Do not recommend channels before checking community file completeness
- Do not give generic "write a good README" advice — cite specific checklist items
- Do not generate badges without resolving the style (option or interactive prompt)
- Do not generate badges, README language selection, or license without resolving the style/choice (option or interactive prompt)
