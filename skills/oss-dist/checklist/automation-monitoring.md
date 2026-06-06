# Release Automation & Monitoring Guide (2026)

> A comprehensive guide for managing release automation, deployment monitoring,
> security scanning, and update tracking for OSS projects.
> Based on the latest tools and patterns as of May 2026.

---

## §A.1 Release Automation Tool Comparison

| Criterion | cargo-dist | GoReleaser | release-please | release-plz | semantic-release |
|-----------|-----------|------------|----------------|-------------|-----------------|
| **Version** | v0.31.0 | v2.15.4 | v17.6.0 | v0.5 | v25.0.3 |
| **Language** | Rust | Go/Rust/Zig/Python | Multi-language (20+) | Rust only | JS/TS-centric |
| **Binary build** | Yes | Yes | No | No | No |
| **Deploy automation** | Yes (binary+installer) | Yes (binary+installer) | No (tagging only) | Yes (crates.io) | Yes (npm etc.) |
| **Monorepo** | Workspace | Partial release | Manifest config | Workspace | Limited |
| **CC-based** | Separate | Separate | Required | Required | Required |
| **GitHub Actions** | Dedicated Action | Dedicated Action | Dedicated Action | Dedicated Action | Custom |

### cargo-dist v0.31.0 (Axodotdev) — Default Rust CLI Tool

**v0.31.0 new features (2026-02-23):**
- Mirror hosting: Static file hosting as a fallback for GitHub Releases
- Homebrew tap mirror support (multi-urls)
- npm-shrinkwrap.json disable option
- Generic project build directory configuration
- Partial install prevention on interrupted installations

**5-stage pipeline:**
```
plan → build-local-artifacts → build-global-artifacts → host → announce
```

**dist-workspace.toml core configuration:**
```toml
[dist]
cargo-dist-version = "0.31.0"
ci = "github"
installers = ["shell", "powershell", "homebrew"]
targets = [
  "aarch64-apple-darwin",
  "x86_64-apple-darwin",
  "x86_64-unknown-linux-gnu",
  "aarch64-unknown-linux-gnu",
  "x86_64-pc-windows-msvc",
]
cache-builds = true
github-attestations = true
cargo-cyclonedx = true
cargo-auditable = true
tap = "epicsagas/homebrew-tap"
publish-jobs = ["homebrew", "./publish-crates"]
post-announce-jobs = ["./notify-discord"]
```

### GoReleaser v2.15.4 — Multi-language Alternative

Key changes in 2026:
- Rust/Zig/Python build support (v2.5+)
- Flatpak bundle, SRPM support
- Node SEA (Single Executable Application) builder (v2.16)
- Immutable release policy (prevents tag overwrites)
- Experimental MCP server (v2.10)

Rust support was added, but cargo-dist offers deeper integration within the Rust ecosystem.

### release-plz — Rust-exclusive Changelog Automation

Automatically generates changelogs and creates version bump PRs based on Conventional Commits.

```yaml
# .github/workflows/release-plz.yml
on:
  push:
    branches: [main]

jobs:
  release-plz:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - uses: dtolnay/rust-toolchain@stable
      - uses: release-plz/action@v0.5
        with:
          command: release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
```

**release-plz.toml changelog customization:**
```toml
[changelog]
body = """
## [{{ version }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for commit in commits %}
  - {% if commit.breaking %}[**breaking**] {% endif %}{{ commit.message }}
{% endfor %}
{% endfor %}
"""

commit_parsers = [
  { message = "^feat", group = "Features" },
  { message = "^fix", group = "Bug Fixes" },
  { message = "^perf", group = "Performance" },
  { message = "^refactor", group = "Refactor" },
  { message = "^doc", group = "Documentation" },
  { message = "^security", group = "Security" },
  { message = "^chore|^ci", skip = true },
]
```

### Changesets v3 (for JS/TS Monorepos)

v3.0.0-next.3 (2026-05-07):
- Node.js minimum version bumped (^22.11 || ^24 || >=26)
- Named export migration path
- micromatch → picomatch migration
- Bolt monorepo support removed, npm monorepo support added

Suitable for JS/TS projects (e.g., epiccounty.com).

---

## §A.2 CI/CD Pipeline Integration

### Reusable Workflow — Organization-wide CI Sharing

When each project uses the same CI patterns, define common workflows in the
`epicsagas/.github` repository and call them from all projects.

```yaml
# epicsagas/.github/.github/workflows/rust-ci.yml
on:
  workflow_call:
    inputs:
      toolchain:
        required: false
        type: string
        default: "stable"

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@master
        with:
          toolchain: ${{ inputs.toolchain }}
          components: rustfmt, clippy
      - uses: Swatinem/rust-cache@v2
      - run: cargo check --all-targets
      - run: cargo clippy -- -D warnings
      - run: cargo fmt --all -- --check

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@master
      - uses: Swatinem/rust-cache@v2
      - run: cargo test

  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@master
      - run: cargo install cargo-audit --locked
      - run: cargo audit

  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: dtolnay/rust-toolchain@master
      - run: cargo install cargo-cyclonedx --locked
      - run: cargo cyclonedx -f json
      - uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: "*.cdx.json"
```

```yaml
# Each project's ci.yml
jobs:
  rust-ci:
    uses: epicsagas/.github/.github/workflows/rust-ci.yml@v1
    secrets: inherit
```

### Composite Action — Encapsulating Repeated Steps

```yaml
# .github/actions/setup-rust-build/action.yml
name: 'Setup Rust Build'
inputs:
  toolchain:
    default: 'stable'
runs:
  using: "composite"
  steps:
    - uses: dtolnay/rust-toolchain@master
      with:
        toolchain: ${{ inputs.toolchain }}
        components: rustfmt, clippy
    - uses: Swatinem/rust-cache@v2
      with:
        cache-on-failure: "true"
```

### Build Caching Strategy

| Tool | Purpose | Use Case |
|------|---------|----------|
| Swatinem/rust-cache@v2 | GitHub Actions cache | Default (all Rust projects) |
| cargo-dist `cache-builds` | Release build cache | cargo-dist pipelines |
| Mozilla sccache | Cloud-backed cache | Large-scale/distributed builds |

Swatinem/rust-cache advanced configuration:
```yaml
- uses: Swatinem/rust-cache@v2
  with:
    cache-on-failure: "true"
    save-if: ${{ github.ref == 'refs/heads/main' }}
    cache-all-crates: "true"
```

---

## §A.3 Deployment Monitoring

### Download/Install Tracking

| Channel | Query Method | Notes |
|---------|-------------|-------|
| GitHub Releases | `GET /repos/{owner}/{repo}/releases` → `download_count` | Applies to assets only |
| crates.io | Webpage graphs, REST API, DB dumps | Per-version/period statistics |
| npm | `api.npmjs.org/downloads/point/{period}/{pkg}` | Daily/weekly/monthly/yearly |
| PyPI | `pypistats.org/api/packages/{pkg}/recent` | BigQuery public dataset |
| Homebrew | `formulae.brew.sh/api/formula/{f}.json` → `analytics` | 80-day aggregation, has opt-out |
| Unified | **libraries.io** | 32-registry integrated monitoring |

**GitHub Release statistics collection script:**
```bash
# Asset download counts for all releases
gh api repos/epicsagas/epic-harness/releases \
  --jq '.[] | .assets[] | "\(.name): \(.download_count)"'
```

### Release Notifications

| Method | Configuration | Notes |
|--------|--------------|-------|
| Discord Webhook | cargo-dist `post-announce-jobs` | Already in use by epic-harness |
| Slack Webhook | `slackapi/slack-github-action` | |
| RSS/Atom | `/{owner}/{repo}/releases.atom` | Universal feed |
| GitHub Watch | Repository Watch → Release event | Personal notifications |
| GitHub Discussions | `discussion_category_name` parameter | Links Releases with Discussions |

### Version Adoption Rate Tracking

Estimate approximate adoption rates by comparing download_count across assets:
```bash
# Total downloads per version
gh api repos/epicsagas/epic-harness/releases \
  --jq '.[] | {tag: .tag_name, total: (.assets | map(.download_count) | add)}'
```

### Update Check API (Built into CLI)

```json
// GET /api/v1/check?app={name}&version={current}&os={os}&arch={arch}
{
  "latest": "0.3.8",
  "current": "0.3.7",
  "update_available": true,
  "changelog_url": "https://github.com/{owner}/{repo}/releases/tag/v0.3.8"
}
```

epic-harness's `src/update.rs` already performs GitHub API-based version checking.

---

## §A.4 Security Monitoring

### Tool Comparison

| Tool | Scan Scope | CI Integration | Notes |
|------|-----------|----------------|-------|
| cargo audit | Known vulnerabilities (RustSec) | GitHub Actions | Already in use |
| cargo-deny | License + origin + vulnerabilities | GitHub Actions | Broader than audit |
| Dependabot | Dependency vulnerabilities + version updates | Auto PR | Already enabled |
| OpenSSF Scorecard | 18 security checks, 0-10 score | Auto PR checks | |
| Socket.dev | Supply chain security (npm/PyPI) | GitHub App | |
| Snyk | Comprehensive vulnerabilities + container/IaC | GitHub Actions | Free for public repos |

### SBOM & Provenance

```toml
# dist-workspace.toml
[dist]
cargo-cyclonedx = true     # CycloneDX SBOM → bom.xml
cargo-auditable = true     # Embed dependency info into binary
github-attestations = true # actions/attest-build-provenance@v2
```

- `cargo-cyclonedx`: Includes `bom.xml` in each tarball
- `cargo-auditable`: Enables `cargo audit` to scan the binary itself for vulnerabilities
- `github-attestations`: Automatically generates build provenance attestations

### OpenSSF Scorecard (Recommended Addition)

```yaml
# .github/workflows/scorecard.yml
name: Scorecard
on:
  push:
    branches: [main]

permissions:
  security-events: write

jobs:
  analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          persist-credentials: false
      - uses: ossf/scorecard-action@v2
        with:
          results_file: results.sarif
          results_format: sarif
          publish_results: true
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

18 automated checks: Vulnerabilities, Dependency-Update-Tool, Pinned-Dependencies,
Token-Permissions, CI-Tests, Signed-Releases, Branch-Protection, etc.

---

## §A.5 Windows Deployment Expansion

### MSI Installer (Built into cargo-dist)

```toml
[dist]
installers = ["shell", "powershell", "homebrew", "msi"]
```

1. `authors` field required in `Cargo.toml` (manufacturer name)
2. `dist init` → enable MSI option → `wix/main.wxs` auto-generated
3. WiX v3 is pre-installed on GitHub Actions Windows runners

### Winget Manifest Auto-submission

```yaml
# cargo-dist post-announce custom job
jobs:
  winget:
    runs-on: windows-latest
    steps:
      - shell: pwsh
        run: |
          wingetcreate update epicsagas.epic-harness `
            --version $version `
            --urls "https://github.com/epicsagas/epic-harness/releases/download/${version}/epic-harness-x86_64-pc-windows-msvc.msi" `
            --submit
```

### Scoop Manifest (autoupdate)

```json
{
  "version": "0.3.8",
  "description": "Self-evolving Claude Code harness",
  "homepage": "https://github.com/epicsagas/epic-harness",
  "license": "Apache-2.0",
  "architecture": {
    "64bit": {
      "url": "https://github.com/epicsagas/epic-harness/releases/download/v0.3.8/epic-harness-x86_64-pc-windows-msvc.zip"
    }
  },
  "bin": "epic-harness.exe",
  "checkver": "github",
  "autoupdate": {
    "architecture": {
      "64bit": {
        "url": "https://github.com/epicsagas/epic-harness/releases/download/v$version/epic-harness-x86_64-pc-windows-msvc.zip"
      }
    }
  }
}
```

Scoop's `autoupdate` automatically detects new versions without manual updates.

---

## §A.6 Recommended Adoption Roadmap

### Phase 1 (Immediate — Zero Cost)

| Task | Effect |
|------|--------|
| cargo-dist `cache-builds = true` | Faster release builds |
| cargo-dist `github-attestations = true` | Automatic build attestations |
| Add OpenSSF Scorecard Action | Security score visibility |
| Verify Dependabot is enabled | Automatic dependency vulnerability detection |

### Phase 2 (1 Week — Low Cost)

| Task | Effect |
|------|--------|
| Shared CI workflow in `epicsagas/.github` repo | CI consistency across 6 projects |
| Adopt release-plz | Automatic changelog generation |
| Discord release notifications (all projects) | Real-time release event tracking |
| GitHub Release download statistics collection script | Adoption rate monitoring |

### Phase 3 (1 Month — Medium Cost)

| Task | Effect |
|------|--------|
| Add MSI installer | Official Windows install support |
| Automate Winget/Scoop manifests | Windows user accessibility |
| cargo-dist `cargo-cyclonedx = true` | Include SBOM in release artifacts |
| Add `cargo-deny` to CI | License + origin checks |

### Phase 4 (Optional — Long-term)

| Task | Effect |
|------|--------|
| Update Check API service | Precise user version adoption tracking |
| Opt-in telemetry | Anonymous usage statistics (careful design required) |
| libraries.io integrated monitoring | Cross-platform download trends |
| GitHub MCP-based release management | AI agent-driven release note generation/review |

---

## See Also

- `checklist/release.md` — CI/CD pipeline, version automation
- `checklist/plugin.md` — AI tool plugin deployment automation
- `languages/rust.md` — Rust CLI deployment overview
- `checklist/governance.md` — Security policies, supply chain
