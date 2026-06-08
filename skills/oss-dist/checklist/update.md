---
name: update
description: Update/upgrade readiness checklist for OSS projects. Covers per-install-method update commands, version check format, CHANGELOG requirements, migration guides, and a ready-to-paste README Updating section template for epicsagas projects.
tags: [layer/raw, project-guidelines]
project: projects
created: 2026-06-08
---

# Update & Upgrade Readiness — Checklist (§6)

> §6 of OSS-PROJECT-GUIDELINES. Referenced by `../SKILL.md` (Targeted Lookup, keyword: `update, upgrade, self-update`).
> For epicsagas install standard, see `../install-best-practices.md`.

---

## §6.1 Update Readiness Audit

For every install method documented in the README **Installation** section, a corresponding update path must exist — explicit or inline.

- [ ] List every install method currently in README (Homebrew, curl, cargo install, binstall, winget, scoop, mise, etc.)
- [ ] Confirm each has a documented update command or inline hint
- [ ] No install method is documented without a working, tested update path
- [ ] Update commands verified against actual released version (no placeholders)
- [ ] `--version` output tested after update to confirm version bumped
- [ ] If a built-in updater exists (`<tool> update / upgrade / self-update`), it is listed first

**Decision rule:** If all update paths are obvious (Homebrew, binstall, cargo install), a single inline hint suffices. Only add a full `## Updating` table when at least one path is non-obvious (curl installer, plugin-based install, built-in updater).

---

## §6.2 Per-Install-Method Update Commands

| Install Method | Update Command | Notes |
|----------------|---------------|-------|
| Homebrew | `brew upgrade <tool>` | Picks up new tap formula automatically |
| curl installer (macOS/Linux) | Re-run original `curl … \| sh` command | No state left; re-runs are idempotent |
| PowerShell installer (Windows) | Re-run original `irm … \| iex` command | Same as curl; overwrites binary in place |
| `cargo install` | `cargo install <tool>` | Rebuilds from latest crates.io version |
| `cargo binstall` | `cargo binstall <tool>@latest` | Downloads pre-built; faster than rebuild |
| winget | `winget upgrade <tool>` | Requires winget manifest on winget-pkgs |
| scoop | `scoop update <tool>` | Requires bucket manifest to be updated |
| mise | `mise upgrade <tool>` | Requires backend registry entry |

**epicsagas projects** — canonical update path priority (from `install-best-practices.md`):
1. `brew upgrade epicsagas/tap/<tool>`
2. Re-run curl / PowerShell installer
3. `cargo binstall <tool>@latest`
4. `cargo install <tool>` (source rebuild, slowest)

---

## §6.3 Version Check Verification

- [ ] `<tool> --version` exits 0
- [ ] Output format is exactly: `<tool> <semver>` on the first line (e.g., `alcove 0.4.1`)
- [ ] No extra noise before the version string (debug output, warnings, update nags)
- [ ] Version string matches the tag pushed to GitHub (strip leading `v` if present in output)
- [ ] CI smoke test runs `<tool> --version` after install step and asserts exit code 0
- [ ] If a built-in updater exists, `<tool> --version` after `<tool> self-update` reflects new version

**Canonical output contract:**
```
<tool> <major>.<minor>.<patch>
```

---

## §6.4 CHANGELOG Format Requirements

Follow [Keep a Changelog](https://keepachangelog.com) + [Semantic Versioning](https://semver.org).

- [ ] File is named `CHANGELOG.md` at repo root
- [ ] Latest release is at the top; oldest at the bottom
- [ ] Each version block: `## [<semver>] - YYYY-MM-DD`
- [ ] `[Unreleased]` section exists above latest release (updated continuously)
- [ ] Sections used only when non-empty: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`
- [ ] Breaking changes appear under `Changed` with a `**BREAKING:**` prefix
- [ ] Every entry is user-facing language, not commit messages
- [ ] Diff links at the bottom: `[0.4.1]: https://github.com/…/compare/v0.4.0…v0.4.1`
- [ ] `cargo-dist` / release-please changelog generation reviewed before publish — auto-generated entries must be human-edited for clarity

---

## §6.5 Migration Guide Checklist

Required whenever a release contains breaking changes (major bump or `feat!:` / `BREAKING CHANGE:` commit).

- [ ] `CHANGELOG.md` `Changed` section includes `**BREAKING:**` entries with before/after examples
- [ ] `MIGRATION.md` created (or version-specific section added) if migration steps exceed 3 lines
- [ ] Deprecated symbols emit a compile-time or runtime warning at least one minor version before removal
- [ ] Deprecation notice format: `@deprecated since <version> — use <replacement> instead`
- [ ] CLI flag renames: old flag still accepted with a deprecation warning for one release cycle
- [ ] Config file format changes: migration is automatic (with backup) or a `migrate` subcommand is provided
- [ ] GitHub Release body links to the relevant CHANGELOG section and migration steps
- [ ] Pinned GitHub Issue / Discussion opened for community questions on migration

---

## §6.6 README Updating Section Template

Use when `install-best-practices.md` inline hint is insufficient (see §6.1 decision rule).
Paste this block after `## Installation`, replacing `<tool>` with the binary name.

```markdown
## Updating

| Method | Command |
|--------|---------|
| Homebrew | `brew upgrade epicsagas/tap/<tool>` |
| curl / PowerShell installer | Re-run the install command above |
| cargo binstall | `cargo binstall <tool>@latest` |
| cargo install | `cargo install <tool>` |

Verify the update:

​```bash
<tool> --version
​```
```

**When the inline hint is sufficient** (preferred for epicsagas projects per `install-best-practices.md`):

```markdown
> `<tool> --version` to verify. Update with `brew upgrade epicsagas/tap/<tool>` or re-run the installer script.
```

This single line covers Homebrew and curl/PowerShell installer users — the two most common install paths.
Cargo users can infer `cargo binstall <tool>@latest` or `cargo install <tool>` without explicit guidance.
