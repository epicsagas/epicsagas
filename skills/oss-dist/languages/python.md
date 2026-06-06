# Python — One-Line Install

> Primary: **uv** (replaces pip+pyenv+pipx). Python-free install possible.

## Install Commands

```bash
# uv (recommended — no Python required)
uv tool install tool
uvx tool                        # run without install

# pipx (isolated install)
pipx install tool

# pip (universal fallback)
pip install tool
```

## pyproject.toml (PEP 621)

```toml
[project]
name = "my-tool"
version = "1.0.0"
requires-python = ">=3.11"
license = "MIT"
dependencies = ["click>=8.0", "rich>=13.0"]

[project.scripts]
my-tool = "my_tool.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.backend"
```

## PyPI Publish

```bash
# uv (recommended)
uv build && uv publish

# traditional
pip install build twine && python -m build && twine upload dist/*
```

## GitHub Actions (Trusted Publishers — no token)

```yaml
environment: pypi
permissions:
  id-token: write
  contents: read
steps:
  - uses: astral-sh/setup-uv@v4
  - run: uv build && uv publish
```

## Runtime-Free Binary Options

| Tool | Best For | Notes |
|------|----------|-------|
| **PyInstaller** | general CLI/GUI | most widely used |
| **Nuitka** | performance + obfuscation | compiles to C |
| **PyOxidizer** | Rust ecosystem integration | embeds Python |
