# Universal Installer Tools (Language-Agnostic)

## Comparison Matrix

| Tool | macOS | Linux | Windows | Key Feature |
|------|-------|-------|---------|-------------|
| **Homebrew** | ✅ native | ✅ Linuxbrew | ❌ | 90k+ packages, dev standard |
| **mise** | ✅ | ✅ | partial | Runtime + tool manager → `tools/mise.md` |
| **uv** | ✅ | ✅ | ✅ | Python ecosystem unified → `tools/uv.md` |
| **pkgx** | ✅ | ✅ | WSL | Run without install, 4MB binary |
| **Nix** | ✅ | ✅ | WSL2 | Reproducible, 120k+ packages |
| **flox** | ✅ | ✅ | WSL2 | Nix + Homebrew-level UX |

## pkgx — Run Without Installing

```bash
curl https://pkgx.sh | sh       # bootstrap
pkgx node@20 script.js          # run without install
pkgx +python@3.12 -- python --version
```

Best for: CI one-shot, PoC, no system pollution.

## Nix — Reproducible Install

```bash
# Determinate Systems installer (recommended)
curl --proto '=https' --tlsv1.2 -sSf -L \
  https://install.determinate.systems/nix | sh -s -- install
nix profile install nixpkgs#ripgrep
```

Best for: reproducibility-critical env, ML projects, enterprise standardization.

## flox — Nix with Friendly UX

```bash
curl -sSf https://install.flox.dev | sh
flox init && flox install nodejs python
flox push       # share env with team
flox activate
```

Best for: team env sharing, AI/ML dev environments, reproducibility without Nix expertise.

