# Release Checklist — Cross-Platform Distribution & CI/CD Automation

> §4 of OSS-PROJECT-GUIDELINES. Routing table referenced by `../SKILL.md` (Targeted Lookup).
> Load sub-files on demand; do not load all at once.

---

## One-Line Install Router

| Keywords | File |
|----------|------|
| rust, cargo, cargo-dist | `../languages/rust.md` |
| go, golang, goreleaser | `../languages/go.md` |
| node, nodejs, npm, npx | `../languages/node.md` |
| deno | `../languages/deno.md` |
| bun | `../languages/bun.md` |
| python, pip, uv, pipx, uvx | `../languages/python.md` |
| java, jvm, kotlin, graalvm, sdkman | `../languages/java.md` |
| c, cpp, zig, systems | `../languages/systems.md` |
| swift, spm, mint | `../languages/swift.md` |
| mise, asdf, runtime manager | `../tools/mise.md` |
| uv, uvx, pipx | `../tools/uv.md` |
| pkgx, nix, flox, universal | `../tools/universal.md` |
| curl, security, sigstore, sbom, attestations | `../tools/security.md` |
| macos, homebrew, dmg, pkg, notarization, gatekeeper | `../platforms/macos.md` |
| windows, winget, scoop, chocolatey | `../platforms/windows.md` |
| linux, apt, dnf, pacman, snap | `../platforms/linux.md` |
| update, upgrade, self-update | `../checklist/update.md` |

---

## Project Type → Recommended Distribution Tool

| Project | Primary | Secondary | Notes |
|---------|---------|-----------|-------|
| Rust CLI | cargo-dist | cargo binstall | Auto SBOM + Attestations |
| Go CLI | goreleaser + Homebrew | eget | Auto apt/dnf repo |
| Node.js | npx + npm publish | Bun compile | — |
| Deno | deno compile | Homebrew | Runtime-free binary |
| Bun | bun build --compile | npm publish | Built-in cross-compile |
| Python CLI | uv tool install | pipx | No Python required for users |
| JVM/Kotlin | GraalVM native-image | Homebrew | JVM-free binary, 10ms startup |
| C/C++ | Homebrew + apt/dnf | vcpkg | — |
| Zig | mise + cross-compile | Homebrew | Single cmd all platforms |
| Swift | mint + Homebrew | SPM | Linux via Docker |
| Team env | mise (.mise.toml) | flox | All runtimes unified |
| Enterprise | Nix / flox | mise | Reproducible builds |
| Windows only | winget + Scoop | Chocolatey | No admin rights (Scoop) |
| CI one-shot | pkgx / uvx / npx | Docker | Zero system side effects |

---

## Core Install Principles

1. Provide multiple install paths simultaneously: curl + brew + package manager
2. `curl | sh` minimum security: `--proto '=https' --tlsv1.2`
3. Windows minimum: `powershell -ExecutionPolicy ByPass -c "irm ... | iex"`
4. Supply chain (2025+): include SBOM, Attestations, or Sigstore signatures
5. CI one-shot tools: pkgx / uvx / npx (no system pollution)

---

## Version Automation Tool Selection

| Tool | Trigger style | Language fit | Monorepo |
|------|--------------|-------------|---------|
| release-please | PR-based, manual merge | multi-language | manifest mode |
| semantic-release | fully automated, plugin | JS-centric | plugin support |
| cargo-dist | tag-triggered | Rust | workspace support |

Conventional Commits → auto bump rules:
- `feat:` → minor
- `fix:` → patch
- `feat!:` or `BREAKING CHANGE:` → major

---

## Release Pipeline Checklist

- [ ] Commit pushed → CI passes (check + test + audit + sbom)
- [ ] Tag created (`vX.Y.Z`)
- [ ] Release workflow triggered
- [ ] Parallel build matrix: Linux x86_64, Linux ARM64, macOS Intel, macOS Apple Silicon, Windows x86_64
- [ ] Artifacts collected and archived
- [ ] Installers generated: shell installer, PowerShell installer, Homebrew formula
- [ ] Code signing applied: macOS `codesign` signing ✅ (notarization not implemented in cargo-dist — irrelevant for CLI distribution)
- [ ] Artifacts uploaded to GitHub Releases
- [ ] Published to package managers: Homebrew tap, crates.io (as applicable)
- [ ] Release notes auto-generated from commit log

---

## CI Pipeline Standard (Rust)

Apply the 4-job structure uniformly across all projects:

| Job | Tool | Notes |
|-----|------|------|
| `check` | `cargo check` + `clippy` + `fmt` | `Swatinem/rust-cache@v2` required |
| `test` | `cargo test` | `Swatinem/rust-cache@v2` required |
| `audit` | `cargo audit --locked` | Run on every PR |
| `sbom` | `cargo cyclonedx -f json` | Upload `*.cdx.json` artifact |

> ⚠️ `cargo cyclonedx -f json` — use the `-f json` flag. `--format json` is an invalid flag.

---

## Language-Specific Release Strategy

| Language | Toolchain | Key notes |
|----------|-----------|-----------|
| Rust | cargo-dist 0.31.0 | `dist-workspace.toml` SSOT; when excluding musl, glibc-linked native lib comment required; macOS signing via `CODESIGN_*` Secrets |
| Node.js | npm publish + release-please | Binary: Bun compile or Node.js SEA; versioning via release-please |
| Python | uv build + uv publish | pyproject.toml PEP 621; PyPI Trusted Publishers (OIDC — no API token needed) |
| Go | goreleaser | Homebrew formula auto-generated; apt/dnf repo via goreleaser-pro or nfpm |
| All | GitHub Actions matrix | Parallel builds per platform; macOS signing required |
