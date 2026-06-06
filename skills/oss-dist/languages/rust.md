# Rust — Cross-Platform CLI Distribution

> Primary tool: **cargo-dist 0.31.0**. Generates all installers automatically.
> Philosophy: Zero-dependency native binaries, SSOT pipeline, 95%+ ecosystem coverage.

---

## §R.1 Release Build Optimization

Before distribution, minimize binary size and maximize performance.

**`Cargo.toml`**

```toml
[package]
name = "your-cli-name"
version = "0.1.0"
edition = "2021"
description = "Ultra-lightweight high-performance Rust CLI"
repository = "https://github.com/username/your-cli-name"
license = "MIT OR Apache-2.0"
readme = "README.md"

[profile.release]
opt-level = "z"       # Binary size optimization ("3" for max speed)
lto = true            # Link-time optimization (performance + size)
codegen-units = 1     # Maximize optimization level
strip = true          # Strip debug symbols
panic = "abort"       # Reduce size further (optional)
```

### Audit

- [ ] `[profile.release]` has `lto = true` and `strip = true` at minimum
- [ ] `opt-level` set (either `"z"` for size or `"3"` for speed)
- [ ] `codegen-units = 1` set for maximum optimization
- [ ] Package metadata complete: `description`, `repository`, `license`, `readme`

---

## §R.2 Install Commands

**Standard one-line install block (epicsagas project standard):**

```bash
# macOS / Linux — pre-built binary, no Rust required
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/user/tool/releases/latest/download/tool-installer.sh | sh

# Windows — pre-built binary, no Rust required
irm https://github.com/user/tool/releases/latest/download/tool-installer.ps1 | iex

# Homebrew (macOS / Linux)
brew install user/tap/tool

# cargo-binstall — pre-built binary via Rust toolchain
cargo binstall tool

# cargo install — build from source (requires Rust toolchain)
cargo install tool
```

**Standard Updating table (includes all install methods, order unified):**

```markdown
## Updating

| Method | Command |
|--------|---------|
| curl installer (macOS/Linux) | Re-run the install script above |
| PowerShell installer (Windows) | Re-run the install command above |
| Homebrew | `brew upgrade tool` |
| cargo binstall | `cargo binstall tool@latest` |
| cargo install | `cargo install tool@latest` |

Verify the installed version:

​```bash
tool --version
​```
```

**Order rules (important):**
1. `curl | sh` — first (binary, no Rust required — maximum accessibility)
2. `irm | iex` (Windows) — immediately after curl
3. Homebrew — macOS/Linux package manager standard
4. Scoop — Windows-only, placed after Homebrew if present
5. `cargo binstall` — Rust users (binary, fast — recommended over `cargo install`)
6. `cargo install` — source compile fallback (last)

**curl flag standardization:**
- Must use `--proto '=https' --tlsv1.2 -LsSf` (do not mix `-sSf` or `-LsSf` inconsistently)
- Windows PowerShell: `irm ... | iex` (short form, no need for `Invoke-RestMethod`)

**Homebrew notation standardization:**
- `brew install user/tap/tool` (single line; avoid the two-line `brew tap` + `brew install` approach)

**Comment style standardization:**
- `# macOS / Linux — pre-built binary, no Rust required`
- `# Windows — pre-built binary, no Rust required`
- `# Homebrew (macOS / Linux)`
- `# cargo-binstall — pre-built binary via Rust toolchain`
- `# cargo install — build from source (requires Rust toolchain)`

**Scoop (add if Windows-only support exists):**

```bash
# Scoop (Windows, no admin required)
scoop bucket add user https://github.com/user/scoop-bucket && scoop install tool
```

**npm wrapper (add only when targeting the JS ecosystem):**

```bash
npx tool@latest
```

### Audit

- [ ] README install section order: curl → irm → brew → binstall → cargo (follow this order)
- [ ] curl flags: `--proto '=https' --tlsv1.2 -LsSf` (must match exactly)
- [ ] Windows installer: `irm ... | iex` single-line form
- [ ] Homebrew: `brew install user/tap/tool` single line (two-line format prohibited)
- [ ] `cargo binstall` comment: "pre-built binary via Rust toolchain"
- [ ] `cargo install` comment: "build from source (requires Rust toolchain)"
- [ ] Updating table exists and includes all install methods
- [ ] Updating table order: curl → irm → brew → scoop (if present) → binstall → cargo
- [ ] Version check command (`tool --version`) included in Updating section
- [ ] `brew upgrade tool` (full path `brew upgrade user/tap/tool` not needed)

---

## §R.3 cargo-dist Pipeline Setup

### dist-workspace.toml (SSOT — all cargo-dist config here, not Cargo.toml)

```toml
# dist-workspace.toml  ← must configure here, not in Cargo.toml
[workspace]
members = ["cargo:."]

[dist]
cargo-dist-version = "0.31.0"
ci = "github"
targets = [
  "aarch64-apple-darwin",
  "aarch64-unknown-linux-gnu",
  "aarch64-pc-windows-msvc",
  "x86_64-apple-darwin",
  "x86_64-unknown-linux-gnu",
  "x86_64-pc-windows-msvc",
]
installers = ["shell", "powershell", "homebrew"]
tap = "myorg/homebrew-tap"
create-release = true
install-path = "CARGO_HOME"
install-updater = false
publish-jobs = ["homebrew", "./publish-crates"]
macos-sign = true
# macos-notarize: not yet implemented in cargo-dist 0.31.0 — future support expected
# NOTE: musl targets omitted if crate uses glibc-linked native libs (e.g. fastembed/ONNX Runtime)
```

> ⚠️ **Warning**: `[workspace.metadata.dist]` in `Cargo.toml` is a deprecated pattern.
> Configure only in `dist-workspace.toml` and remove from `Cargo.toml`.

### Workflow Generation and Release

```bash
# Initial setup
dist init
dist generate --mode ci    # generates .github/workflows/release.yml

# Trigger release
git tag v1.0.0 && git push origin v1.0.0
```

### Audit

- [ ] `dist-workspace.toml` file exists, and no `[workspace.metadata.dist]` in `Cargo.toml`
- [ ] targets include Linux gnu, macOS Intel+ARM, Windows
- [ ] Installers include `shell`, `powershell`, `homebrew`
- [ ] `.github/workflows/release.yml` generated (`dist generate --mode ci`)
- [ ] Release triggered by git tag (`vX.Y.Z`)

---

## §R.4 CI Pipeline — Unified Structure

All Rust projects use the following 4-job structure as the standard.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

env:
  CARGO_TERM_COLOR: always
  CI: 1

jobs:
  check:
    name: Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - uses: Swatinem/rust-cache@v2
      - name: Check
        run: cargo check --all-targets
      - name: Clippy
        run: cargo clippy -- -D warnings
      - name: Format
        run: cargo fmt --all -- --check

  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - name: Test
        run: cargo test

  audit:
    name: Security Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - name: Install cargo-audit
        run: cargo install cargo-audit --locked
      - name: Run audit
        run: cargo audit

  sbom:
    name: Generate SBOM
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - name: Install cargo-cyclonedx
        run: cargo install cargo-cyclonedx --locked
      - name: Generate SBOM
        run: cargo cyclonedx -f json        # ← correct flag: -f json
      - uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: "*.cdx.json"
```

> ⚠️ **Warning**: `cargo cyclonedx --output-cdx --format json` uses incorrect flags.
> Must use `cargo cyclonedx -f json`.

### CI Audit

- [ ] 4-job structure: `check` / `test` / `audit` / `sbom`
- [ ] `Swatinem/rust-cache@v2` used (build cache)
- [ ] `cargo cyclonedx -f json` (flags must match exactly)
- [ ] `cargo install cargo-audit --locked` (`--locked` required)
- [ ] `cargo install cargo-cyclonedx --locked` (`--locked` required)
- [ ] `dtolnay/rust-toolchain@stable` with `components: rustfmt, clippy` (check job)

---

## §R.5 Release Pipeline — cargo-dist Success Pattern

Core structure of `release.yml` generated by cargo-dist:

```
plan → build-local-artifacts (matrix) → build-global-artifacts → host → announce
                                                                       ↓
                                                              publish-homebrew-formula
                                                              publish-crates (optional)
```

### macOS Code Signing (cargo-dist approach)

> **Signing scope**: `codesign` for binary signing only. Notarization (Apple notarization) is not yet implemented in cargo-dist 0.31.0.
> For CLI tools distributed as `.tar.gz`, signing alone is sufficient to pass Gatekeeper.

After setting `macos-sign = true` in `dist-workspace.toml`,
register the following 3 GitHub Secrets and cargo-dist will handle the rest automatically:

| Secret Name | Content |
|------------|---------|
| `CODESIGN_CERTIFICATE` | Base64-encoded .p12 file |
| `CODESIGN_CERTIFICATE_PASSWORD` | Password set during .p12 export |
| `CODESIGN_IDENTITY` | `Developer ID Application: Name (TEAM_ID)` |

For projects not using cargo-dist (manual builds), add the following step before packaging:

```yaml
- name: Sign macOS binary
  if: runner.os == 'macOS' && env.CODESIGN_CERTIFICATE != ''
  env:
    CODESIGN_CERTIFICATE: ${{ secrets.CODESIGN_CERTIFICATE }}
    CODESIGN_CERTIFICATE_PASSWORD: ${{ secrets.CODESIGN_CERTIFICATE_PASSWORD }}
    CODESIGN_IDENTITY: ${{ secrets.CODESIGN_IDENTITY }}
  run: |
    echo "$CODESIGN_CERTIFICATE" | base64 --decode > /tmp/cert.p12
    security create-keychain -p "" build.keychain
    security import /tmp/cert.p12 -k build.keychain \
      -P "$CODESIGN_CERTIFICATE_PASSWORD" -T /usr/bin/codesign
    security set-keychain-settings -lut 21600 build.keychain
    security unlock-keychain -p "" build.keychain
    security list-keychains -d user -s build.keychain \
      $(security list-keychains -d user | tr -d '"')
    security set-key-partition-list -S apple-tool:,apple: -s -k "" build.keychain
    codesign --force --sign "$CODESIGN_IDENTITY" --options runtime \
      target/${{ matrix.target }}/release/your-binary
    codesign --verify --deep --strict target/${{ matrix.target }}/release/your-binary
```

### musl Exclusion Condition

Crates that include glibc-linked native binaries such as fastembed or ONNX Runtime
cannot compile for musl targets. Remove musl from `dist-workspace.toml` targets:

```toml
# ❌ musl not possible (when including glibc-linked native lib)
# "x86_64-unknown-linux-musl"

# ✅ Use gnu only
targets = [
  "x86_64-unknown-linux-gnu",
  "aarch64-unknown-linux-gnu",
  ...
]
```

### Release Audit

- [ ] `build-local-artifacts` env includes `CODESIGN_CERTIFICATE` / `CODESIGN_CERTIFICATE_PASSWORD` / `CODESIGN_IDENTITY`
- [ ] macOS manual build projects: Sign step is placed before packaging
- [ ] Verify musl necessity (include if no native lib, exclude if present)
- [ ] Re-run `dist generate --mode ci` and commit (after each config change)

---

## §R.6 Distribution Channel Strategy (The Golden Stack)

| Channel | Target Users | Automation | Priority |
|---------|-------------|------------|----------|
| **cargo-binstall** | Rust developers | Auto (crates.io publish) | Primary |
| **Homebrew** | macOS / Linux standard | Auto (cargo-dist formula to tap) | Primary |
| **Scoop** | Windows power users | Auto (cargo-dist manifest) | Primary |
| **WinGet** | Windows general users | Manual PR to winget-pkgs repo | After stable |
| **npm wrapper** | JS/frontend ecosystem | Auto (cargo-dist npm package) | Optional |
| **curl \| sh** | Universal fallback | Auto (cargo-dist shell installer) | Always |
| **irm \| iex** | Windows fallback | Auto (cargo-dist PowerShell installer) | Always |

### Channel Decision Guide

- **Always include:** `curl | sh` + `irm | iex` + Homebrew + cargo-binstall
- **Windows dual-track:** Scoop (developers) + WinGet (general users)
- **npm wrapper only if:** target users are frontend/fullstack developers

### Audit

- [ ] Distribution channels match target user personas
- [ ] npm wrapper is only included if JS ecosystem reach is justified
- [ ] WinGet submission planned after first stable release
- [ ] Homebrew tap repository created (`username/homebrew-tap`)

---

## §R.7 Target Matrix

| Target | OS | Arch | Notes |
|--------|----|------|-------|
| `x86_64-unknown-linux-gnu` | Linux | x86_64 | glibc — include by default |
| `x86_64-unknown-linux-musl` | Linux | x86_64 | static — only when no native lib |
| `aarch64-unknown-linux-gnu` | Linux | ARM64 | AWS Graviton, Raspberry Pi |
| `x86_64-apple-darwin` | macOS | Intel | |
| `aarch64-apple-darwin` | macOS | Apple Silicon | M1/M2/M3/M4 |
| `x86_64-pc-windows-msvc` | Windows | x86_64 | |
| `aarch64-pc-windows-msvc` | Windows | ARM64 | Surface Pro, Copilot+ |

### Audit

- [ ] musl inclusion: include if no native lib (ONNX, SQLite, etc.), exclude if present
- [ ] ARM64 targets included: both macOS + Linux
- [ ] Windows MSVC target included (avoid GNU targets)

---

## §R.8 Supply Chain Security

- GitHub Attestations: automatically included in cargo-dist v0.26+
- SBOM: `cargo cyclonedx -f json` → upload `*.cdx.json` artifact
- Audit: `cargo audit` (runs on every PR in CI)
- Binary embeds dep tree: `cargo-auditable`

### Audit

- [ ] `cargo audit` runs in CI (detects known CVEs)
- [ ] SBOM artifact uploaded (`cargo cyclonedx -f json`)
- [ ] GitHub Attestations enabled (automatic with cargo-dist v0.26+)

---

## §R.9 Code Signing

| Platform | Method | Cost | Status |
|----------|--------|------|--------|
| macOS | Developer ID Application (`codesign`) | $99/yr | ✅ Signing complete (notarization not yet implemented in cargo-dist) |

- macOS: Register `CODESIGN_CERTIFICATE` / `CODESIGN_CERTIFICATE_PASSWORD` / `CODESIGN_IDENTITY` in GitHub Secrets

### Audit

- [ ] macOS: 3 `CODESIGN_*` secrets registered in GitHub Secrets
- [ ] macOS: cargo-dist uses `macos-sign = true` in dist-workspace.toml (notarization not implemented in 0.31.0)
- [ ] macOS: Manual builds include the `Sign macOS binary` step

---

## §R.10 Action Plan Checklist

Release readiness checklist by stage:

- [ ] Add `[profile.release]` optimization options (`Cargo.toml`)
- [ ] Complete package metadata (`description`, `repository`, `license`, `readme`)
- [ ] Create `dist-workspace.toml` (remove dist config from `Cargo.toml`)
- [ ] Run `dist generate --mode ci` → generates `release.yml`
- [ ] Unify CI pipeline to 4-job structure (`check/test/audit/sbom`)
- [ ] Register 3 `CODESIGN_*` secrets in GitHub Secrets
- [ ] Create test tag (`v0.1.0-alpha`) — verify Actions build succeeds
- [ ] Create Homebrew tap repo and link in `dist-workspace.toml`
- [ ] `cargo publish` → crates.io (enables `cargo binstall` support)
- [ ] WinGet manifest PR → `microsoft/winget-pkgs` (after stable release)

---

## §R.11 cargo-binstall Configuration — cargo-dist Alignment

`cargo-binstall` reads `Cargo.toml` metadata registered on crates.io to find pre-built binaries on GitHub Releases. If the assets generated by **cargo-dist 0.31.0+** do not match binstall metadata, it falls back to source builds.

### cargo-dist 0.31.0+ Asset Characteristics

| Property | Value |
|----------|-------|
| Archive format | `.tar.xz` (Unix), `.zip` (Windows) |
| Internal structure | Binary inside `{name}-{target}/` nested directory |
| Filename pattern | `{name}-{target}.tar.xz` |

> ⚠️ **cargo-dist 0.28 and below** used `.tar.gz` + flat structure. If you upgrade but miss the binstall metadata update, it falls back to source builds due to 404 errors.

### Required Cargo.toml Configuration

```toml
[package.metadata.binstall]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-{ target }.tar.xz"
pkg-fmt = "txz"
bin-dir = "{ name }-{ target }/{ bin }"

[package.metadata.binstall.overrides.x86_64-pc-windows-msvc]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-{ target }.zip"
pkg-fmt = "zip"
bin-dir = "{ bin }.exe"
```

### Important Notes

- **`pkg-fmt`**: Must be `txz` (not `tgz`). cargo-dist 0.31.0+ uses `.tar.xz` by default.
- **`bin-dir`**: Unix uses `{ name }-{ target }/{ bin }` (nested directory), Windows uses `{ bin }.exe` (flat structure).
- **When binary name ≠ package name**: Specify the actual binary name directly instead of `{ bin }`.
- **When using `.tar.gz`**: Explicitly set `archive-format = "tar.gz"` in cargo-dist config, and align binstall to `tgz`.

### Multi-Binary Projects

When there are multiple `[[bin]]` entries (e.g.: `epic-harness` + `epic` alias):

```toml
[package.metadata.binstall]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-{ target }.tar.xz"
pkg-fmt = "txz"
bin-dir = "{ name }-{ target }/{ bin }"  # { bin } is replaced with each binary name
```

The `{ bin }` template variable is individually replaced with each binary name declared in `[[bin]]`, so all binaries are installed without additional configuration.

### Verification Commands

```bash
# Install from crates.io metadata (after publishing)
cargo binstall <package-name>

# Install directly from GitHub releases (test before publishing)
cargo binstall <package-name> --repository https://github.com/<org>/<repo>

# Verify installed binary
which <binary-name>
<binary-name> --version
```

### Audit

- [ ] `[package.metadata.binstall]` section exists in Cargo.toml
- [ ] `pkg-fmt` matches actual asset format (`txz` for .tar.xz, `tgz` for .tar.gz)
- [ ] `pkg-url` matches actual GitHub Release asset name pattern
- [ ] `bin-dir` matches archive internal structure (nested vs flat)
- [ ] Windows override includes `zip` format + flat `bin-dir` setting
- [ ] Verify pre-built binary installation with `cargo binstall <pkg> --repository <url>`
- [ ] Version bump and crates.io publish required after metadata changes (existing version metadata cannot be modified)

---

## See Also
- `checklist/release.md` — CI/CD pipeline, version automation
- `checklist/update.md` — update commands for each install method
- `platforms/windows.md` — winget, Scoop, Chocolatey details
- `platforms/linux.md` — apt, dnf, snap, AppImage details
- [[project-guidelines/project-guidelines]]
