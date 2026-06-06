# Installation Section Best Practices — epicsagas Projects

> Cross-project standard for README installation sections.
> Applies to: epic-harness, alcove, obsidian-forge, llm-transpile, claudy, and all future Rust CLI projects.
> Last updated: 2026-05-11

---

## Design Principles

These principles are derived from widely adopted OSS projects (ripgrep, bat, fd, just, starship) and address what went wrong in the original epicsagas standard.

1. **Package manager first** — Homebrew / apt / winget are the canonical install path for most users. They handle PATH, updates, and uninstall cleanly. curl|sh is the fallback for users without a package manager.
2. **Platform sections over flat lists** — Separate macOS/Linux, Windows, and Rust toolchain sections eliminate the cognitive overhead of picking from 5+ options in one block.
3. **No fabricated options** — Only document install methods that exist in the current release. A broken install command is worse than a missing one.
4. **Minimal update guidance** — `brew upgrade <tool>` is self-evident to Homebrew users. A full Updating table is only needed when the update path is non-obvious (e.g., curl installers, built-in updaters).

---

## Standard Installation Template

```markdown
## Installation

### macOS / Linux

​```bash
brew install epicsagas/tap/<tool>
​```

No Homebrew? Use the installer script:

​```bash
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/epicsagas/<tool>/releases/latest/download/<tool>-installer.sh | sh
​```

### Windows

​```powershell
irm https://github.com/epicsagas/<tool>/releases/latest/download/<tool>-installer.ps1 | iex
​```

### Via Rust toolchain

​```bash
cargo binstall <tool>   # pre-built binary (fast)
cargo install <tool>    # build from source
​```

> `<tool> --version` to verify. Update with `brew upgrade <tool>` or re-run the installer script.
```

---

## Update Guidance Rules

### When a single inline hint suffices (preferred)

If all install methods have obvious update paths, append one line after the install block:

```
> `<tool> --version` to verify. Update with `brew upgrade <tool>` or re-run the installer script.
```

### When a `## Updating` table is needed

Only add a full Updating section when the tool has a **non-obvious update path**, such as:
- A built-in updater command (`<tool> update`)
- Multiple install methods with divergent update flows
- A plugin-based install (Claude Code plugin)

Template when a table is warranted:

```markdown
## Updating

| Method | Command |
|--------|---------|
| Homebrew | `brew upgrade <tool>` |
| curl / PowerShell installer | Re-run the install command above |
| cargo binstall | `cargo binstall <tool>@latest` |
| cargo install | `cargo install <tool>@latest` |

​```bash
<tool> --version
​```
```

---

## Rules

### Platform section order (mandatory)
1. macOS / Linux — Homebrew first, curl as fallback
2. Windows — PowerShell installer (only if `x86_64-pc-windows-msvc` target exists in release)
3. Via Rust toolchain — binstall before cargo install

### curl flags (mandatory exact form)
```
--proto '=https' --tlsv1.2 -LsSf
```
- `-L` follows redirects (required for GitHub releases)
- `-s` silent mode, `-S` show errors on failure, `-f` fail on HTTP errors
- Do NOT use `-sSf` (missing `-L`)

### Installer filename (must match actual release asset)
cargo-dist names the installer after the **binary name**, not the package name:
- Package `llm-transpile`, binary `transpile` → asset is `install.sh` / `install.ps1`
- Package `epic-harness`, binary `epic-harness` → asset is `epic-harness-installer.sh`

**Always verify the actual filename in the GitHub release before documenting.**

### Windows section — only if installer.ps1 exists
- alcove: macOS aarch64 only → **no Windows section**
- All others: include Windows section if `x86_64-pc-windows-msvc` target is in `dist-workspace.toml`

### Homebrew (mandatory one-line form)
```
brew install epicsagas/tap/<tool>
```
NOT the two-line form (`brew tap epicsagas/tap` + `brew install <tool>`).

### brew upgrade (short form, no tap prefix)
```
brew upgrade <tool>
```
NOT `brew upgrade epicsagas/tap/<tool>`.

### Scoop — only if repo exists
Do not document `scoop bucket add epicsagas/scoop-bucket` unless `https://github.com/epicsagas/scoop-bucket` actually exists and contains the formula.

---

## Per-Project Status (as of 2026-05-11)

| Project | Homebrew | curl installer | Windows installer | cargo binstall | Notes |
|---------|:--------:|:--------------:|:-----------------:|:--------------:|-------|
| epic-harness | ✅ | ✅ `epic-harness-installer.sh` | ✅ `epic-harness-installer.ps1` | ✅ | |
| alcove | ✅ | ✅ `alcove-installer.sh` | ❌ no Windows target | ✅ | aarch64-apple-darwin only |
| obsidian-forge | ✅ | ✅ `obsidian-forge-installer.sh` | ✅ `obsidian-forge-installer.ps1` | ✅ | |
| llm-transpile | ✅ | ✅ `install.sh` (binary: transpile) | ✅ `install.ps1` | ✅ | filename ≠ package name |
| claudy | ✅ | ✅ `claudy-installer.sh` | ✅ `claudy-installer.ps1` | ✅ | has `claudy update` built-in |

---

## Special Cases

### alcove
- Targets: aarch64-apple-darwin only (ort-sys/ONNX Runtime prebuilt binary limitation)
- No Windows installer — do not document `irm` command
- Linux users must build from source (`cargo install alcove`)

### llm-transpile
- Binary name is `transpile`, package name is `llm-transpile`
- cargo-dist generates `install.sh` / `install.ps1` (not `llm-transpile-installer.*`)
- Scoop bucket (`epicsagas/scoop-bucket`) does not exist — do not document Scoop

### claudy
- Has built-in updater: `claudy update`
- Include in update guidance as the primary method

---

## Audit Checklist

When reviewing a README for compliance:

- [ ] macOS/Linux: Homebrew is first, curl is the fallback (not the primary)
- [ ] curl flags: exactly `--proto '=https' --tlsv1.2 -LsSf`
- [ ] curl URL matches actual release asset filename (verify on GitHub releases page)
- [ ] Windows section: only present if `x86_64-pc-windows-msvc` target exists
- [ ] Windows: `irm ... | iex` short form (not `powershell -ExecutionPolicy ...`)
- [ ] Windows URL matches actual release asset filename
- [ ] Homebrew: one-line `brew install epicsagas/tap/<tool>`
- [ ] Scoop: only documented if `epicsagas/scoop-bucket` repo exists with formula
- [ ] Update guidance present (inline hint or `## Updating` table)
- [ ] `brew upgrade <tool>` without tap prefix
- [ ] Version verify: `<tool> --version`

---

## See Also
- `languages/rust.md` — cargo-dist pipeline, targets, installer generation
- `checklist/release.md` — CI/CD pipeline and release pipeline checklist
