# Bun — One-Line Install

> Key advantage: `bun build --compile` produces a **single binary** with built-in cross-compile.

## Runtime Install

```bash
# macOS/Linux
curl -fsSL https://bun.sh/install | bash

# Windows
powershell -ExecutionPolicy ByPass -c "irm bun.sh/install.ps1 | iex"

# Homebrew
brew install bun

# npm
npm install -g bun
```

## Tool Distribution

```bash
# Global install (npm-compatible)
bun install -g tool

# Compile to standalone binary (no Bun/Node needed at runtime)
bun build ./src/cli.ts --compile --outfile tool

# Cross-compile (single command, no toolchain setup)
bun build ./src/cli.ts --compile --target bun-linux-x64   --outfile tool-linux
bun build ./src/cli.ts --compile --target bun-linux-arm64 --outfile tool-linux-arm
bun build ./src/cli.ts --compile --target bun-windows-x64 --outfile tool.exe
bun build ./src/cli.ts --compile --target bun-darwin-x64  --outfile tool-mac-intel
bun build ./src/cli.ts --compile --target bun-darwin-arm64 --outfile tool-mac-arm
```

## npm Publish (Bun project)

```bash
bun publish   # publishes to npm registry
```

## GitHub Actions

```yaml
- uses: oven-sh/setup-bun@v2
  with:
    bun-version: latest
- run: bun install && bun test
- run: |
    bun build ./src/cli.ts --compile --target bun-linux-x64   --outfile dist/tool-linux
    bun build ./src/cli.ts --compile --target bun-windows-x64 --outfile dist/tool.exe
    bun build ./src/cli.ts --compile --target bun-darwin-arm64 --outfile dist/tool-mac
```
