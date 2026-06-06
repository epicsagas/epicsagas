# Deno — One-Line Install

> Key advantage: `deno compile` produces a **single binary** — no runtime needed.

## Runtime Install

```bash
# macOS/Linux
curl -fsSL https://deno.land/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://deno.land/install.ps1 | iex"

# Homebrew
brew install deno

# mise
mise use deno@2
```

## Tool Distribution

```bash
# Run remote script directly
deno run --allow-net https://example.com/tool/cli.ts

# Global install
deno install --allow-net --allow-read \
  --name tool https://deno.land/x/tool/cli.ts

# Compile to standalone binary (no Deno needed at runtime)
deno compile --allow-net --output tool src/cli.ts

# Cross-compile
deno compile --target x86_64-unknown-linux-gnu --output tool-linux src/cli.ts
deno compile --target x86_64-pc-windows-msvc   --output tool.exe   src/cli.ts
deno compile --target aarch64-apple-darwin      --output tool-mac   src/cli.ts
```

## Cross-Compile Targets

| Target | OS | Arch |
|--------|----|------|
| `x86_64-unknown-linux-gnu` | Linux | x86_64 |
| `aarch64-unknown-linux-gnu` | Linux | ARM64 |
| `x86_64-pc-windows-msvc` | Windows | x86_64 |
| `x86_64-apple-darwin` | macOS | Intel |
| `aarch64-apple-darwin` | macOS | Apple Silicon |

## npm Publish (Deno → npm)

```bash
deno task build-npm   # uses dnt (Deno to Node Transform)
cd npm && npm publish
```
