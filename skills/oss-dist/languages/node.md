# Node.js — One-Line Install

> Primary: **npx** (run without install). Publish via **npm**.

## Install Commands

```bash
# Run without install (recommended for CLI tools)
npx tool@latest

# Global install
npm install -g tool
pnpm add -g tool
yarn global add tool

# Homebrew (wraps npm binary)
brew install tool
```

## package.json Essentials

```json
{
  "name": "my-cli",
  "version": "1.0.0",
  "bin": { "my-cli": "./dist/cli.js" },
  "files": ["dist"],
  "engines": { "node": ">=18" }
}
```

## npm Publish (GitHub Actions)

```yaml
on:
  push:
    tags: ['v*']
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci && npm test && npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Runtime-Free Binary Options

| Tool | Method | Notes |
|------|--------|-------|
| **Bun** | `bun build --compile` | cross-compile built-in → `languages/bun.md` |
| **Node SEA** | `node --experimental-sea-config` | Node 20+, experimental |
| **pkg** | `pkg .` | maintenance uncertain |
