# Pre-release Channel Strategy Checklist

> §PR of OSS-PROJECT-GUIDELINES. Alpha/beta/rc/nightly channel decisions,
> toolchain config, announcement, and stable graduation criteria.
> English only. AI-auditable.

---

## §PR.1 Pre-release Channel Decision Matrix

| Channel | Tag Pattern | When to Use | Audience | Stability Promise |
|---------|------------|-------------|----------|-------------------|
| `nightly` | `v0.0.0-nightly.YYYYMMDD` | Daily HEAD snapshot, automated | CI consumers, power users | None — may break any day |
| `alpha` | `v1.0.0-alpha.N` | API still changing, core incomplete | Internal / invited testers | No API stability |
| `beta` | `v1.0.0-beta.N` | Feature-complete, bugs expected | Opt-in community testers | Feature-stable, API locked |
| `rc` | `v1.0.0-rc.N` | Release candidate, blocking bugs only | All early adopters | Stable unless blocker found |

**Decision rules:** Skip alpha for CLI-only tools. Use `rc` ≥ 7 days before stable. Nightly must be automated — never manual.

---

## §PR.2 cargo-dist Pre-release Config

**Tag patterns** — `Cargo.toml` version field drives the tag; use SemVer pre-release suffixes:

```
v1.0.0-alpha.1   v1.0.0-beta.1   v1.0.0-rc.1   v1.0.0-nightly.20260608
```

**`dist-workspace.toml` snippet:**

```toml
[dist]
allow-dirty = ["cargo"]   # nightly snapshots only
pr-run-mode = "upload"    # pre-release artifacts isolated from stable manifest
```

**CI tag trigger:**

```yaml
on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"     # stable only
      - "v[0-9]+.[0-9]+.[0-9]+-*"   # pre-release (separate job)
```

- [ ] `prerelease-repo-manifests` set if using a dedicated tap/channel repo
- [ ] Pre-release job does NOT publish to Homebrew stable tap
- [ ] Nightly tag script: `git tag v0.0.0-nightly.$(date +%Y%m%d) && git push origin --tags`

---

## §PR.3 npm / PyPI Pre-release Channels

### npm

`package.json` version: `"1.0.0-beta.1"` — SemVer pre-release suffix prevents auto-install.

```bash
npm publish --tag next                        # "next" dist-tag, never "latest"
npm dist-tag add my-pkg@1.0.0 latest          # promote to stable
```

- [ ] `latest` dist-tag never points to a pre-release version
- [ ] `beta` dist-tag for beta series; `next` for rc
- [ ] `npm deprecate my-pkg@"1.0.0-*"` after graduation

### PyPI

```bash
uv publish --publish-url https://test.pypi.org/legacy/ dist/*  # validate first
uv publish dist/*   # version 1.0.0b1 — PyPI auto-flags as pre-release
```

- [ ] PEP 440 suffixes: `1.0.0a1`, `1.0.0b1`, `1.0.0rc1`
- [ ] `pip install my-pkg` never resolves pre-release without `--pre`
- [ ] `test.pypi.org` upload passes before production publish

---

## §PR.4 Announcement Strategy

| Channel | Action | Timing |
|---------|--------|--------|
| GitHub Release | Check **"Set as a pre-release"** — prevents `latest` API pointer updating | Every pre-release tag |
| GitHub Discussion | Post in `Announcements` with `[beta]` prefix | beta.1 and rc.1 |
| Discord `#beta` | Pin install command + feedback form link | beta.1 only |
| Opt-in mailing list | Notify subscribers of "pre-release" opt-in | rc.1 only |
| README badge | `![beta](https://img.shields.io/badge/channel-beta-orange)` | During beta series |

- [ ] Announcement includes explicit opt-in command (`cargo install my-crate --version 1.0.0-beta.1`)
- [ ] Known limitations listed in release notes
- [ ] Feedback issue template linked (`?template=beta_feedback.yml`)

---

## §PR.5 Graduation Checklist (Pre-release → Stable)

**Minimum criteria — all must pass before promoting:**

| Criterion | Threshold | How to Verify |
|-----------|-----------|---------------|
| Soak time | ≥ 7 days since last rc tag | `git log --tags --simplify-by-decoration` |
| Open blocking issues | 0 issues labeled `blocker` or `rc-blocker` | GitHub Issues filter |
| Open regressions | 0 issues labeled `regression` opened after beta.1 | GitHub Issues filter |
| Download / install count | ≥ 50 unique installs of rc (signal of real-world exposure) | crates.io stats / npm insights |
| CI green | All matrix targets pass on rc tag commit | GitHub Actions status |

**Promotion steps:**
- [ ] Create stable tag: `git tag v1.0.0 && git push origin v1.0.0`
- [ ] GitHub Release: uncheck "Set as a pre-release", set as **"Set as the latest release"**
- [ ] npm: `npm dist-tag add my-pkg@1.0.0 latest`
- [ ] PyPI: stable version (`1.0.0`) published — PyPI auto-promotes as stable
- [ ] Homebrew tap formula updated to stable version
- [ ] Deprecate all pre-release versions: `npm deprecate my-pkg@"1.0.0-*" "Use 1.0.0 stable"`
- [ ] CHANGELOG.md: collapse all pre-release entries under `## [1.0.0]`
- [ ] Discord `#beta` pinned message updated to stable announcement

---
