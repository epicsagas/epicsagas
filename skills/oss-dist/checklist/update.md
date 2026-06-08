# Update Readiness — Audit Checklist (§6)

> Audits whether the project provides proper update/upgrade guidance for all supported install methods.
> Complements `checklist/release.md` (install) — this covers the upgrade lifecycle.

---

## §6.1 README Update Section

- [ ] README has a dedicated "Updating" or "Upgrade" section (separate from "Installation")
- [ ] Every install method listed in "Installation" has a corresponding update command
- [ ] Update commands are exact copy-paste ready (not vague descriptions)

**Common mistake:** README lists 5 install methods but only shows `brew upgrade`.

---

## §6.2 Update Commands by Install Method

For each install method the project supports, verify the correct update command is documented:

| Install Method | Expected Update Command | Notes |
|---|---|---|
| Homebrew (`brew install`) | `brew upgrade tool` | |
| cargo (`cargo install`) | `cargo install tool@latest` | Recompiles from source |
| cargo-binstall | `cargo binstall tool@latest` | Binary, fast |
| npm global | `npm update -g tool` | |
| pnpm global | `pnpm update -g tool` | |
| yarn global | `yarn global upgrade tool` | |
| bun global | `bun update -g tool` | |
| pipx | `pipx upgrade tool` | |
| pip | `pip install --upgrade tool` | |
| uv tool | `uv tool upgrade tool` | |
| go install | `go install github.com/user/tool@latest` | Always pulls latest |
| scoop | `scoop update tool` | |
| winget | `winget upgrade --id Publisher.ToolName` | |
| choco | `choco upgrade tool` | |
| apt repo | `sudo apt update && sudo apt install --only-upgrade tool` | |
| dnf repo | `sudo dnf upgrade tool` | |
| pacman / AUR | `sudo pacman -Syu tool` or `yay -Syu tool` | |
| snap | `sudo snap refresh tool` | Auto-update by default |
| flatpak | `flatpak update com.example.Tool` | |
| mint | `mint install user/tool@latest` | Overwrites previous |
| mise | `mise upgrade tool` | |
| curl \| sh (static binary) | Re-run the same installer script | cargo-dist / goreleaser generated |
| PowerShell `irm \| iex` | Re-run the same installer script | |

### Audit check

```
For each install method in README "Installation" section:
  → Is there a matching update command in "Updating" section?
  → Is the command correct for that package manager?
  → Is it copy-paste ready?
```

---

## §6.3 Version Verification

- [ ] `--version` / `-V` / `version` subcommand works
- [ ] Version check command documented in README (e.g., `tool --version`)
- [ ] Version output includes semver (`X.Y.Z`) — not just commit hash

---

## §6.4 Breaking Changes & Migration

- [ ] CHANGELOG follows [Keep a Changelog](https://keepachangelog.com) format
- [ ] Major version bumps include migration guide
- [ ] Breaking changes are called out in GitHub Release notes
- [ ] Deprecation notices appear at least 1 minor version before removal

---

## §6.5 Self-Updating Support

If the tool supports in-place self-update, document it:

| Mechanism | Example | Audit |
|---|---|---|
| Built-in self-update | `tool self update` or `tool update` | [ ] Documented in README |
| Auto-update check | Deno: auto-checks on first run | [ ] Documented, with opt-out flag |
| Package manager auto | snap: auto-updates by default | [ ] Noted in README if applicable |

---

## §6.6 Update Command Reference Template

Use this template when generating update sections for README:

```markdown
## Updating

| Method | Command |
|--------|---------|
| Homebrew | `brew upgrade tool` |
| cargo | `cargo install tool@latest` |
| npm | `npm update -g tool` |
| pipx | `pipx upgrade tool` |
| uv | `uv tool upgrade tool` |
| go | `go install github.com/user/tool@latest` |
| scoop | `scoop update tool` |
| winget | `winget upgrade --id Publisher.ToolName` |
| choco | `choco upgrade tool` |
| Script (macOS/Linux) | Re-run install script |
| Script (Windows) | Re-run install command |
```

**Rules:**
- Only include rows for install methods the project actually supports
- Commands must match the install method — never mix (e.g., don't show `brew upgrade` for a cargo-installed tool)
- If only one install method exists, a single command line is sufficient (no table needed)

---

## §6.7 Language-Specific Update Patterns

When auditing, check the language-specific update conventions:

### Rust (`languages/rust.md`)
- cargo-dist generated installers: re-running the same `curl | sh` or `irm | iex` replaces the binary
- Homebrew: `brew upgrade tool`
- cargo-binstall: `cargo binstall tool@latest` (faster than `cargo install`)

### Go (`languages/go.md`)
- `go install ...@latest` always pulls latest — this IS the update command
- goreleaser installers: re-run the same script
- Homebrew: `brew upgrade tool`

### Node.js (`languages/node.md`)
- `npx tool@latest` always runs latest — no update needed
- Global installs: `npm update -g tool`
- Homebrew: `brew upgrade tool`

### Python (`languages/python.md`)
- uv: `uv tool upgrade tool` (or `uv tool upgrade --all`)
- pipx: `pipx upgrade tool`
- pip: `pip install --upgrade tool`
- uvx: always latest, no update needed

### Java (`languages/java.md`)
- SDKMAN: `sdk install java <version>` (replaces previous)
- Homebrew: `brew upgrade tool`
- GraalVM binary: re-download from Releases

### Deno (`languages/deno.md`)
- `deno upgrade` (built-in self-update)
- Homebrew: `brew upgrade deno`
- Compiled binary: re-run `deno compile`

### Bun (`languages/bun.md`)
- `bun upgrade` (built-in self-update)
- Global installs: `bun update -g tool`
- Compiled binary: re-run `bun build --compile`

### C/C++/Zig (`languages/systems.md`)
- Homebrew: `brew upgrade tool`
- apt: `sudo apt update && sudo apt install --only-upgrade tool`
- dnf: `sudo dnf upgrade tool`
- Static binary: re-download from Releases

### Swift (`languages/swift.md`)
- mint: `mint install user/tool@latest`
- Homebrew: `brew upgrade tool`
- SPM: `git pull && swift build -c release`

---

## See Also

- `checklist/release.md` — install commands and distribution pipeline
- `languages/<lang>.md` — language-specific install and release details
- `platforms/<platform>.md` — platform-specific package managers
