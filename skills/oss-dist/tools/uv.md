# uv — Python Toolchain Manager

> Replaces pip + pyenv + virtualenv + pipx in one tool. Rust-based, 10–100x faster.
> **Key:** Install Python tools without Python installed.

## Install

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# CI (no shell profile modification)
curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="/usr/local" sh
```

## Tool Install & Run

```bash
uv tool install ruff            # isolated install
uvx ruff check .                # run without install (npx equivalent)
uvx black --check src/
```

## Project Workflow

```bash
uv init my-project
uv add requests
uv sync
uv build
uv publish
```

## GitHub Actions (Trusted Publishers — no token needed)

```yaml
environment: pypi
permissions:
  id-token: write
  contents: read
steps:
  - uses: astral-sh/setup-uv@v4
  - run: uv build
  - run: uv publish
```

## uv vs pipx vs pip

| Feature | uv | pipx | pip |
|---------|----|----|-----|
| Isolated tool install | ✅ | ✅ | ❌ |
| Run without install (uvx) | ✅ | ✅ (pipx run) | ❌ |
| Python version management | ✅ | ❌ | ❌ |
| Speed | ⚡⚡⚡ | ⚡ | ⚡ |
| Works without Python | ✅ | ❌ | ❌ |
