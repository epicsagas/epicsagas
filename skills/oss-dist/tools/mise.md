# mise — Universal Runtime Manager

> asdf successor. Manages Node, Python, Go, Rust, Java, and more in a single tool.

## Install

```bash
curl https://mise.run | sh      # macOS/Linux
brew install mise               # Homebrew
cargo install mise              # via cargo
# Windows: partial support via Scoop
```

## Core Usage

```bash
mise use node@22                # install + activate
mise use python@3.13
mise use java@21
mise use -g cargo:ripgrep@14    # install Rust binary tool globally
mise install                    # install all from .mise.toml
```

## .mise.toml (commit to repo root)

```toml
[tools]
node    = "22"
python  = "3.13"
rust    = "1.87"
go      = "1.24"
java    = "21"
```

## mise vs asdf

| | mise | asdf |
|--|------|------|
| Speed | ~5ms | ~120ms |
| Implementation | Rust | Bash |
| Windows | partial | none |
| Security | GPG·Cosign·SLSA·Attestations | limited |
| `.tool-versions` compat | ✅ | ✅ |

## Supported Backends

`asdf`, `cargo`, `npm`, `pipx`, `ubi`, `go`, `aqua` — usable directly without plugins.
