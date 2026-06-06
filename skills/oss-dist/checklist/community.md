# OSS Community Files — Audit Checklist (§1)

## §1.1 File Priority Tiers

**Tier 1 — Must**
- [ ] `README.md`
- [ ] `LICENSE`
- [ ] `.gitignore`

**Tier 2 — Strongly Recommended**
- [ ] `CONTRIBUTING.md`
- [ ] `CODE_OF_CONDUCT.md`
- [ ] `SECURITY.md`
- [ ] `.github/ISSUE_TEMPLATE/` (directory with at least one template)
- [ ] `.github/workflows/` (CI pipeline)

**Tier 3 — Recommended**
- [ ] `CHANGELOG.md`
- [ ] `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] `.github/dependabot.yml`
- [ ] `CODEOWNERS`
- [ ] `SUPPORT.md`
- [ ] `.editorconfig`

**Tier 4 — Optional**
- [ ] `.github/FUNDING.yml`
- [ ] `GOVERNANCE.md`

---

## §1.2 License Selection

| SPDX ID | Type | Disclosure | Best For | Examples |
|---|---|---|---|---|
| MIT | Permissive | None | Max adoption | Babel, Rails |
| Apache-2.0 | Permissive | None | Enterprise / patent clauses | Android, K8s |
| GPL-3.0 | Strong copyleft | Modified → same license | Ecosystem protection | Bash, GIMP |
| AGPL-3.0 | Strongest copyleft | Incl. network use | Force SaaS open-source | Mastodon |
| LGPL-3.0 | Weak copyleft | Library only | Library distribution | GNU C Library |
| MPL-2.0 | File-level copyleft | Modified files only | Granular file control | Firefox |

**Compatibility rules**
- MIT: compatible with MIT, BSD, Apache-2.0, ISC; GPL dep propagates GPL
- Apache-2.0: compatible with MIT, BSD, Apache-2.0; incompatible with GPL-2.0
- GPL-3.0: compatible with MIT, BSD, Apache-2.0, GPL-2.0-or-later; GPL-2.0-only incompatible
- AGPL-3.0: compatible with most permissive licenses; most commercial libs incompatible

**Audit tooling**
- [ ] Rust: `cargo deny`
- [ ] Node: `license-checker`
- [ ] Python: `pip-licenses`
- [ ] Commercial / polyglot: FOSSA

---

## §1.3 CHANGELOG.md Format (Keep a Changelog)

- [ ] Follows [Keep a Changelog](https://keepachangelog.com) format
- [ ] Sections used: `Added`, `Changed`, `Fixed`, `Security`
- [ ] Latest release at the top
- [ ] Dates in ISO 8601 (`YYYY-MM-DD`)
- [ ] Versions follow SemVer

---

## §1.4 GitHub Repo Settings

- [ ] Description set (non-empty)
- [ ] Topics/tags set (at least 3 relevant tags)
- [ ] Social preview image set (1280×640 px)
- [ ] Discussions enabled (if community Q&A is in scope)
- [ ] GitHub Pages configured (if docs are published)

**Docs tooling reference**

| Tool | Stack | Strengths | Best For |
|---|---|---|---|
| VitePress | Vue/JS | Fast build | JS/TS projects |
| Docusaurus | React/JS | i18n, versioning | Large projects |
| MkDocs + Material | Python | YAML config, rich plugins | Python projects |
| Starlight | Astro | Perf, a11y | Modern stack |
| GitBook | SaaS | GUI editing | Internal wikis |
| Rustdoc | Rust | `cargo doc` auto-gen | Rust libraries |

---

## §1.5 GitHub Community Profile (Insights > Community)

- [ ] README present
- [ ] LICENSE present
- [ ] Code of Conduct present
- [ ] Contributing guide present
- [ ] Issue templates present
- [ ] Pull request template present
- [ ] Security policy present
- [ ] Description set
- [ ] Topics set

**Org-level `.github` repo**: health files (CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, ISSUE_TEMPLATE, PULL_REQUEST_TEMPLATE) placed here auto-inherit to all sub-repos.
**Exception**: `LICENSE` must exist per-repo — org-level does not propagate it.
