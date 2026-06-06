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

### Do not

- Do not load all sub-files unless the user requests a full audit
- Do not recommend channels before checking community file completeness
- Do not give generic "write a good README" advice — cite specific checklist items
