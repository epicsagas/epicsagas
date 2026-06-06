# Plugin Distribution — AI Coding Tool Integration & Auto-Update

> Install/update automation checklist for CLI tools integrated as plugins into AI coding tools
> (Claude Code, Cursor, Codex, etc.). Assumes a Rust CLI distributed via cargo-dist.

---

## §P.1 Plugin Manifest (.claude-plugin/plugin.json)

Claude Code plugins are defined by placing `plugin.json` in the `.claude-plugin/` directory.

```json
{
  "name": "plugin-id",
  "version": "x.y.z",
  "description": "One-line description",
  "author": { "name": "org", "url": "https://github.com/org" },
  "homepage": "https://github.com/org/repo",
  "repository": "https://github.com/org/repo",
  "license": "Apache-2.0",
  "keywords": ["harness", "automation"],
  "skills": "./registry/skills/",
  "commands": "./registry/commands/",
  "agents": ["./registry/agents/builder.md"],
  "hooks": "./hooks/hooks.json"
}
```

### Audit

- [ ] `name` is unique and distinguishable from the CLI binary name
- [ ] `version` matches `Cargo.toml`, `package.json`, and git tag
- [ ] `skills`/`commands`/`agents` path exists and content is valid
- [ ] `hooks` path contains valid JSON `hooks.json`

---

## §P.2 SessionStart Bootstrap (Cross-Platform Node.js)

Claude Code is Node.js-based, so the SessionStart hook uses a `node` script to
automate binary install/update/seed.

### hooks.json structure

```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "node \"${CLAUDE_PLUGIN_ROOT}/hooks/install.js\"; binary-name resume",
        "async": false
      }]
    }]
  }
}
```

### install.js design principles

1. **No dependencies**: uses built-in modules only (`child_process`, `fs`, `https`, `os`, `path`)
2. **3-step behavior**:
   - Binary not installed → download installer from GitHub Releases and execute
   - Binary exists + plugin version > binary version → auto-update
   - After install/update, run `seed()` (skills/agents/commands/MCP sync)
3. **Non-fatal**: all errors output warnings only and do not halt the session
4. **Platform branching**: `os.platform()` for `darwin`/`linux` → `.sh`, `win32` → `.ps1`

### Semver comparison (inside install.js)

```javascript
function semverGt(a, b) {
  const pa = a.split(".").map(Number);
  const pb = b.split(".").map(Number);
  for (let i = 0; i < 3; i++) {
    if (pa[i] > pb[i]) return true;
    if (pa[i] < pb[i]) return false;
  }
  return false;
}
```

### Audit

- [ ] `install.js` uses built-in Node.js modules only
- [ ] Auto-installs from GitHub Releases when binary is not installed
- [ ] Auto-updates when plugin version > binary version
- [ ] On install/update failure, outputs warnings only without halting session
- [ ] Supports all 3 platforms: macOS/Linux/Windows
- [ ] `async: false` ensures SessionStart waits until completion

---

## §P.3 Hook System — Quality Automation Ring

Configures a code quality automation ring (Ring 0) via plugin hooks.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `SessionStart` | Session start | Binary install/update + session restore |
| `PreToolUse(Bash)` | Before Bash execution | Dangerous command blocking (force push, rm -rf, etc.) |
| `PostToolUse(Edit)` | After file edit | Auto format + typecheck + lint |
| `PostToolUse(*)` | After every tool use | Observation log recording (async, 5s timeout) |
| `PreCompact` | Before context compaction | Save work state snapshot |
| `SessionEnd` | Session end | Observation analysis → skill evolution → gate |

### Audit

- [ ] SessionStart is blocking (`async: false`)
- [ ] PostToolUse observe is async (`async: true`, `timeout: 5`)
- [ ] Dangerous command guard blocks force push, rm -rf, prod DB drop, etc.
- [ ] PreCompact snapshot enables state restorable without context loss

---

## §P.4 Multi-Tool Installation System

A single Rust binary is installed across 7 AI coding tools, each with a different config format.

| Tool | Config Location | Install Target |
|------|----------------|----------------|
| Claude Code | `~/.claude/settings.json` | hooks + MCP + plugin cache |
| Codex | `~/.codex/` | hooks + skills |
| Gemini | `~/.gemini/` | GEMINI.md + skills + commands |
| Cursor | `~/.cursor/` | hooks + commands + agents |
| OpenCode | `~/.config/opencode/` | commands + agents + plugin |
| Cline | `~/Documents/Cline/Rules/` | rules |
| Aider | `~/` | .aider.conf.yml + CONVENTIONS.md |

### Design principles

1. **Interactive TUI**: crossterm-based arrow/space tool selection menu
2. **Non-destructive merge**: preserves existing settings.json keys, adds new keys only
3. **Symlink protection**: traversal attack prevention (canonical path verification)
4. **Dry-run**: preview changes via `--dry-run` flag
5. **Uninstall**: clean removal via `--uninstall` flag

### Audit

- [ ] `install <tool>` subcommand exists
- [ ] Supports all 7 tools as install targets
- [ ] Preserves existing config files (non-destructive merge)
- [ ] `--dry-run` and `--uninstall` both supported
- [ ] Interactive TUI or CLI flag selection both supported

---

## §P.5 Binary Auto-Update (Rust)

The binary's own auto-update logic (`src/update.rs`).

### Behavior flow

1. Fetch latest release version from GitHub API
2. Compare with current binary version via semver
3. 1-hour cooldown (`~/.harness/.last-binary-sync` marker file)
4. Detect install method and run appropriate upgrade:
   - Homebrew → `brew upgrade`
   - cargo-binstall → `cargo binstall`
   - fallback → `cargo install`

### Audit

- [ ] GitHub API-based version check
- [ ] Cooldown mechanism to rate-limit API calls
- [ ] Auto-detect install method (brew / binstall / cargo)
- [ ] On update failure, continues with existing binary

---

## §P.6 Version Bump Checklist

On release, you must synchronize versions across 4 locations.

| File | Field |
|------|-------|
| `Cargo.toml` | `version = "x.y.z"` |
| `package.json` | `"version": "x.y.z"` |
| `.claude-plugin/plugin.json` | `"version": "x.y.z"` |
| Git tag | `vx.y.z` |

### Audit

- [ ] All 4 locations have the same version
- [ ] `plugin.json` version is used as the install.js auto-update trigger
- [ ] Git tag push triggers CI/CD pipeline

---

## §P.7 Plugin Distribution Architecture

```
GitHub Release (cargo-dist)
  ├── epic-harness-installer.sh      ← curl | sh
  ├── epic-harness-installer.ps1     ← irm | iex
  ├── epic-harness-{target}.tar.xz  ← binary
  └── SHA256 checksums

.claude-plugin/                      ← plugin metadata
  ├── plugin.json
  └── marketplace.json

hooks/                               ← SessionStart automation
  ├── hooks.json                     ← hook definitions
  └── install.js                     ← cross-platform bootstrap

registry/                            ← seed resources (embedded in binary)
  ├── skills/    (15)
  ├── commands/  (10)
  ├── agents/    (4)
  └── presets/   (4)
```

### Audit

- [ ] Plugin metadata and binary managed in same repository
- [ ] install.js locates plugin.json via `CLAUDE_PLUGIN_ROOT` environment variable
- [ ] Registry resources are compile-time embedded via `include_str!`
- [ ] Marketplace metadata (`marketplace.json`) exists

---

## See Also

- `checklist/release.md` — cargo-dist pipeline, CI/CD
- `languages/rust.md` — Rust CLI distribution overview
- `checklist/governance.md` — security policy, supply chain
- [[project-guidelines/project-guidelines]]
