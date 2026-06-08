---
name: readme
description: Generates or polishes a project README following OSS standards and conversion psychology. If a README exists → polish it. If not → generate from scratch. Covers hook copy, GIF demo, Quick Start, features, comparison, social proof, dark mode images, multilingual strategy, and star growth mechanics.
---

# README Generator & Polisher

## When to Use

- User says "write a README", "generate README", "make a README"
- User says "improve", "polish", "review", "fix my README"
- User shares a README and asks for feedback or rewrite
- User is about to launch OSS and README is missing or thin

## Process

### Step 0: Detect mode

```
README exists in CWD or provided by user → POLISH mode
No README found → GENERATE mode
```

Gather any missing context before writing:
- What does this project do? (one sentence)
- What language / stack?
- Who is the target user?
- What are the main alternatives?
- Does it have a website, docs, or existing demo?

---

## GENERATE Mode

Build in this exact section order. Every section below is required unless marked optional.

---

### Step 0.5: Detect Project Type

Adjust README structure based on project type before writing:

| Project type | Key differences |
|---|---|
| **CLI tool** | Quick Start = install + one command; demo GIF shows terminal interaction |
| **Library / crate / package** | Quick Start = add dependency + minimal code snippet; skip install section |
| **Framework** | Quick Start = scaffold command + directory tree; comparison table is critical |
| **Service / SaaS** | Quick Start = signup + API call; add pricing/tier section |

**Detection heuristics:**
- `Cargo.toml [[bin]]` or binary target → CLI tool
- `Cargo.toml [lib]` only, no binary → Library
- `package.json "main"` or `"exports"` without `"bin"` → Library
- `pyproject.toml` with no `[project.scripts]` → Library
- Ask user if ambiguous

**Library-specific adjustments:**
- Replace "Installation" heading with "Add to your project"
- Use `cargo add`, `npm install`, `pip install` — skip Homebrew/curl installer
- Add "API Reference" link section (docs.rs / pkg.go.dev / JSDoc)
- Quick Start must include a minimal working code example (≤10 lines)
- Skip demo GIF requirement (replace with code snippet)

---

### 1. Above the Fold (first screen — most critical)

Everything the visitor sees before scrolling must answer 3 questions:
1. What is this?
2. Why does it matter to me?
3. Who is it for?

**Template:**

```markdown
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="logo-light.png">
    <img alt="project-name logo" src="logo-light.png" width="200">
  </picture>

  # project-name

  > [10-word-max tagline that names the pain or the win]

  [![CI](badge-url)](link) [![Version](badge-url)](link) [![License](badge-url)](link) [![Downloads](badge-url)](link)
</div>

![Demo](demo.gif)
```

**Tagline rules (most important line in the file):**
- ≤10 words — if it needs more, cut it
- Name the user's pain OR the concrete win, not the feature
- Include the category so reader self-selects instantly
- Use "you" framing when possible

| Bad | Good |
|-----|------|
| `A tool for developers` | `The cd command that learns where you go` |
| `Fast JSON parser` | `Zero-allocation JSON parser — 8x faster than serde_json` |
| `Git UI` | `git is powerful. using it shouldn't be painful.` |

**Hook patterns (pick one):**
- **Category + differentiator:** `TypeScript-first schema validation with static type inference`
- **Problem-first (PAS):** `You've heard it before, git is powerful, but what good is that power when everything is so damn hard to do?` (lazygit)
- **Outcome:** `Open-source Notion alternative with real-time collaboration — 60k+ stars`
- **Comparison:** `A cat(1) clone with syntax highlighting and Git integration`

---

### 2. Demo GIF

Place immediately after badges — before any text explanation.

```markdown
![Demo](demo.gif)
```

GIF specs:
- Length: 15–30 seconds (8–10 seconds if showing one interaction)
- Frame rate: 15fps
- Size: ≤2MB
- Content: one core interaction, not a full feature tour
- Must convey value without reading any text

| Tool type | Asset | Tool to create |
|-----------|-------|----------------|
| CLI | Terminal recording | VHS, asciinema, terminalizer |
| GUI / web | Screen recording → GIF | LICEcap, Kap, ScreenToGif |
| Library | Before/After code block | (static markdown) |

Dark mode: use `<picture>` tag for images with white backgrounds — plain PNG breaks in dark mode:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="demo-dark.gif">
  <img alt="demo of project-name" src="demo-light.gif">
</picture>
```

---

### 3. Quick Start (2-minute rule)

User must go from zero to working in under 2 minutes. Tested on a fresh machine.

```markdown
## Quick Start

```bash
# macOS / Linux
curl -fsSL https://project.dev/install.sh | sh

# Windows
irm https://project.dev/install.ps1 | iex

# Homebrew
brew install project-name
```

```bash
project-name hello world   # verify it works
```
```

Rules:
- ≤3 commands total
- Copy-paste with zero modification
- State prerequisites explicitly (no hidden "you need Go 1.21")
- Show the first successful output

---

### 4. Features (scan-optimized)

Use a table, not a bullet list — tables are scanned, bullets are skipped.

```markdown
## Features

| | Feature | Why it matters |
|--|---------|----------------|
| ⚡ | Zero config | Works immediately after install |
| 🔍 | Respects .gitignore | No noise from build artifacts |
| 📦 | Single binary | No runtime, no dependencies |
| 🔄 | Git integration | See changed lines inline |
| 🌐 | Cross-platform | Mac, Linux, Windows |
```

Rules:
- 5–7 rows (not fewer, not more)
- Column 3 is the **benefit**, not a restatement of the feature
- Back performance claims with numbers: "8x faster" not "blazing fast"
- One emoji per row max

---

### 5. Usage

```markdown
## Usage

```bash
# Basic
project search "pattern" src/

# With context lines
project search -C 3 "pattern" src/

# Replace in place
project replace "old" "new" src/
```
```

Rules:
- Minimum working example — copy-paste and run
- Show 2–3 progressions (basic → intermediate)
- Must be CI-tested or include a "last verified" date if not

---

### 6. Comparison Table

```markdown
## Why project-name?

| | project-name | Alt A | Alt B |
|-|-------------|-------|-------|
| Speed | ⚡ 10x | baseline | 2x |
| Binary size | 2MB | 15MB | 8MB |
| Windows | ✅ | ❌ | ✅ |
| Zero config | ✅ | ❌ | ❌ |
| Maintained | ✅ | ⚠️ | ✅ |
```

Rules:
- ≥2 real alternatives (never invented ones)
- Include a row where an alternative wins — credibility requires honesty
- Keep factual — developers spot cherry-picking instantly
- Update when alternatives ship new features

---

### 7. Social Proof (optional, include if available)

```markdown
## Used By

<div align="center">
  <img src="company-a-logo.svg" height="40" alt="Company A">
  <img src="company-b-logo.svg" height="40" alt="Company B">
</div>

> "Replaced our entire X workflow and reduced CI time by 40%"
> — Jane Doe, CTO at Acme Corp

[![Star History Chart](https://api.star-history.com/svg?repos=user/repo&type=Date)](https://star-history.com/#user/repo)
```

Priority order:
1. Recognizable company logos ("Used by") — strongest trust signal
2. Specific testimonials with name + title + company + metric
3. Download/user count if large: `Trusted by 100,000+ developers`
4. Star history chart — shows growth momentum, not just total

Skip if: <100 stars, no notable adopters, no concrete testimonials.

---

### 8. Badges (4–6 max)

Order: CI status → version → license → downloads

Allowed:
- CI / build status
- Version (crates.io / npm / PyPI)
- License
- Downloads or users
- Discord / community (if active)

Forbidden:
- Code coverage (unless ≥90%)
- devDependencies status
- Unused platform badges
- Vanity badges with no meaning

#### Badge Design Style

**Default: `bold`** — same as epicsagas reference projects (epic-harness, alcove, etc.).
If not specified by the user, ask interactively (see SKILL.md § Badge Style Selection).

##### Style Presets

| Preset | `style=` | `labelColor` | Feel | When to use |
|--------|----------|--------------|------|-------------|
| **`bold`** *(default)* | `for-the-badge` | `0d1117` | Dark, high-contrast, branded | Serious OSS tools, CLIs, libraries |
| `classic` | `flat` | *(none)* | Minimal, GitHub-native | Lightweight libs, quick READMEs |
| `modern` | `flat-square` | *(none)* | Clean, no rounded corners | Developer tools, monorepos |
| `social` | `social` | *(none)* | Star/fork count display | Community-focused repos |
| `plastic` | `plastic` | *(none)* | Raised/3D look | Legacy projects, classic OSS feel |

Assign a distinct semantic color to each badge type — do not use shields.io defaults.

| Badge type | `color` | Notes |
|------------|---------|-------|
| CI / build | `58a6ff` | blue — neutral status |
| Version | `fc8d62` | orange — maps to crates.io / npm branding |
| License | `3fb950` | green — safe/permissive signal |
| Downloads | `3498db` | blue — usage/volume |
| Stars | `ffd700` | gold — community |
| Issues | `ff6b6b` | red — attention |

> For `classic` / `modern` / `social` / `plastic` presets, omit `labelColor` and `logoColor=white`.
> Colors above still apply via the `color=` param.

---

##### bold (default) — epicsagas standard

**Row 1 — activity stats** (stars, forks, issues, last-commit):

```html
<p align="center">
  <a href="https://github.com/user/repo/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/user/repo?style=for-the-badge&labelColor=0d1117&color=ffd700&logo=github&logoColor=white" /></a>
  <a href="https://github.com/user/repo/network/members"><img alt="Forks" src="https://img.shields.io/github/forks/user/repo?style=for-the-badge&labelColor=0d1117&color=2ecc71&logo=github&logoColor=white" /></a>
  <a href="https://github.com/user/repo/issues"><img alt="Issues" src="https://img.shields.io/github/issues/user/repo?style=for-the-badge&labelColor=0d1117&color=ff6b6b&logo=github&logoColor=white" /></a>
  <a href="https://github.com/user/repo/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/user/repo?style=for-the-badge&labelColor=0d1117&color=58a6ff&logo=git&logoColor=white" /></a>
</p>
```

**Row 2 — release metadata** (version, downloads, license):

```html
<p align="center">
  <a href="https://crates.io/crates/project"><img alt="Crates.io" src="https://img.shields.io/crates/v/project?style=for-the-badge&labelColor=0d1117&color=fc8d62&logo=rust&logoColor=white" /></a>
  <a href="https://crates.io/crates/project"><img alt="Downloads" src="https://img.shields.io/crates/d/project?style=for-the-badge&labelColor=0d1117&color=3498db&logo=rust&logoColor=white" /></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-3fb950?style=for-the-badge&labelColor=0d1117" /></a>
</p>
```

---

##### classic

```markdown
[![Stars](https://img.shields.io/github/stars/user/repo?style=flat&color=ffd700&logo=github)](link)
[![Version](https://img.shields.io/crates/v/project?style=flat&color=fc8d62&logo=rust)](link)
[![License](https://img.shields.io/badge/license-Apache--2.0-3fb950?style=flat)](link)
```

---

##### modern

```markdown
[![Stars](https://img.shields.io/github/stars/user/repo?style=flat-square&color=ffd700&logo=github)](link)
[![Version](https://img.shields.io/crates/v/project?style=flat-square&color=fc8d62&logo=rust)](link)
[![License](https://img.shields.io/badge/license-Apache--2.0-3fb950?style=flat-square)](link)
```

---

For npm: swap `logo=rust` → `logo=npm`, `color=fc8d62` → `color=cb3837`.
For PyPI: swap `logo=rust` → `logo=python`, `color=fc8d62` → `color=3776ab`.

---

### 9. User Convenience Sections (include based on tool type)

**Troubleshooting** — include for any CLI tool:

```markdown
## Troubleshooting

<details>
<summary>command not found after install</summary>

Add the install path to your PATH:
```bash
export PATH="$HOME/.cargo/bin:$PATH"  # Rust
export PATH="$HOME/.local/bin:$PATH"  # Python uv
```
</details>

<details>
<summary>Permission denied on macOS</summary>

macOS Gatekeeper may block unsigned binaries. Run:
```bash
xattr -d com.apple.quarantine /usr/local/bin/project-name
```
</details>
```

**Online playground** — include for libraries and frameworks:

```markdown
[![Open in StackBlitz](https://developer.stackblitz.com/img/open_in_stackblitz.svg)](stackblitz-url)
[![Open in CodeSandbox](https://codesandbox.io/static/img/play-codesandbox.svg)](codesandbox-url)
```

**FAQ** — include if ≥3 questions expected:

```markdown
## FAQ

<details>
<summary>Does this work on Windows?</summary>
Yes. See the Windows install command in Quick Start.
</details>

<details>
<summary>Is this production-ready?</summary>
Used in production at [Company A] and [Company B]. See CHANGELOG for stability history.
</details>
```

**Requirements** — include if non-trivial:

```markdown
## Requirements

- macOS 12+ / Ubuntu 20.04+ / Windows 10+
- No runtime required (statically linked binary)
```

---

### 10. Footer

```markdown
## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome — check open issues labeled `good first issue`.

## License

[MIT](LICENSE) © 2025 Your Name
```

---

### 11. Multilingual (optional — if targeting global audience)

Top of README.md:

```markdown
**[English](README.md)** | [Korean](README.ko.md) | [Japanese](README.ja.md) | [Chinese](README.zh-CN.md)
```

Rules:
- `README.md` is English — canonical source of truth
- Translations in separate files: `README.ko.md`, `README.zh-CN.md`
- Never let translations get ahead of English
- Use `help wanted` + `translation` labels for community contributions
- Chinese awesome lists have ~75% higher acceptance rate — good early target

---

## README Length

Target: **500–1,500 words** for the README itself.

- Simple library: 1–2 scrolls. Install + usage + API reference is enough.
- Complex framework: README is the onboarding gateway only — link to docs/ or external site for details.
- Use `<details>` collapsible for anything that doesn't fit the main flow.
- GitHub auto-generates an outline from headings — manual TOC only needed for 5+ major sections.

---

## POLISH Mode

When a README exists, score it and rewrite only failing sections.

### Scoring checklist

| Section | Pass condition |
|---------|---------------|
| Tagline | ≤10 words, names pain or win, above the fold |
| Demo visual | GIF exists, first screen, conveys value in ≤30s, dark mode safe |
| Quick Start | ≤3 commands, copy-paste ready, prerequisites stated |
| Features | Table format, 5–7 rows, benefit column, no fluff adjectives |
| Usage | Runnable example, not stale |
| Comparison | ≥2 real alternatives, includes a row they win |
| Badges | 4–6 max, correct order, no forbidden badges |
| Social proof | Company logos or concrete testimonials if available |
| Convenience | Troubleshooting / FAQ / playground if applicable |
| Footer | Contributing + License |
| Length | 500–1,500 words |
| Dark mode | `<picture>` tag for images with backgrounds |
| Multilingual | Language switcher at top if translations exist |

### Anti-patterns — fix immediately

| Anti-pattern | Signal | Fix |
|---|---|---|
| Wall of text | >3 paragraphs with no heading/list/visual | Break with headings, add visuals |
| Fluff adjectives | "blazing fast", "powerful", "revolutionary" without data | Add benchmark numbers or remove |
| No Quick Start | Install section missing or >5 steps | Write 3-command install |
| Stale examples | Obviously outdated, not CI-tested | Update + add CI test |
| Missing license | No LICENSE file or no mention | Add LICENSE + one-liner in footer |
| Information overload | Long blocks not wrapped in `<details>` | Collapse with `<details><summary>` |
| No visual above fold | Zero images before Quick Start | Add GIF or screenshot |
| Hidden prerequisites | Dependencies not listed | Add Requirements section |
| Feature bullets | Bullet list instead of table | Convert to 3-column table |
| Broken dark mode | White-background PNG on dark theme | Wrap in `<picture>` tag |
| Generic tagline | "A tool for developers" | Rewrite with 10-word rule |

---

## Output Format

```
## README [Generated / Polished]

### Changes (POLISH only)
- Tagline: rewrote — "A tool" → "X that does Y in one command"
- Features: converted bullet list to table, trimmed from 11 to 6, added benefit column
- Added GIF placement instruction (no GIF found — user must supply)
- Added Troubleshooting section with 2 common errors

---

[full markdown content]
```
