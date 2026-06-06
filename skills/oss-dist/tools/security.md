# Install Script Security

## curl | sh Trust Ladder

```
Low  ←──────────────────────────────────────── High
curl URL | sh
curl --proto '=https' --tlsv1.2 URL | sh        ← minimum
download → sha256 verify → execute
GPG signature verify → execute
Sigstore/Cosign + GitHub Attestations            ← 2025 standard
```

## Command Reference

```bash
# Unix minimum
curl --proto '=https' --tlsv1.2 -LsSf URL | sh

# Windows minimum
powershell -ExecutionPolicy ByPass -c "irm URL | iex"

# Sigstore verification
cosign verify-blob tool.tar.gz \
  --certificate tool.tar.gz.pem \
  --signature tool.tar.gz.sig \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

## GitHub Actions Security Scanning

```yaml
# Secret scanning
- uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
# ⚠️ Organization repos require GITLEAKS_LICENSE key (personal repos free)

# Static analysis
- uses: github/codeql-action/analyze@v3
  with:
    languages: javascript, python

# Rust audit
- run: cargo audit

# SBOM generation + release upload
- uses: anchore/sbom-action@v0
  with:
    format: spdx-json
    output-file: sbom.spdx.json
- uses: softprops/action-gh-release@v3
  with:
    files: sbom.spdx.json
```

## Action SHA Pinning

Pin actions to full commit SHA — version tags are mutable and can be repointed:

```yaml
# ❌ mutable tag — repointing attack possible
- uses: anchore/sbom-action@v0

# ✅ immutable SHA pin with version comment
- uses: anchore/sbom-action@d94f46e13dff70106a72dd1edfd81536da9f7a2  # v0.17.x
```

Automate with Dependabot `github-actions` ecosystem or [`pinact`](https://github.com/suzuki-shunsuke/pinact).

## Actions Version Freshness Audit

When auditing a project's CI/CD, verify that pinned actions are not severely outdated:

```bash
# Check the latest version of an action
git ls-remote https://github.com/actions/checkout refs/tags/v6.0.2
# → de0fac2e4500dabe0009e67214ff5f5447ce83dd  refs/tags/v6.0.2

# Verify pinned SHA matches the version comment
# If SHA != ls-remote output, the comment is stale or the pin is wrong
```

### Freshness Rules

| Signal | Action |
|--------|--------|
| Pinned version is 2+ major versions behind latest | Flag as NEEDS UPDATE |
| Pinned version is 1+ year old | Flag as STALE |
| SHA has no version comment | Flag as UNREADABLE — add `# vX.Y.Z` |
| Version comment doesn't match SHA | Flag as MISMATCH — verify and fix |

### Recommended Update Process

1. Identify latest stable version for each action (GitHub Releases / `git ls-remote`)
2. Get the commit SHA: `git ls-remote <repo-url> refs/tags/v<X.Y.Z>`
3. Replace old SHA + comment with new SHA + updated comment
4. Verify: `grep -c 'old-sha' .github/workflows/*.yml` returns 0
5. Automate: configure Dependabot for `github-actions` ecosystem

## Pwn-Request Prevention

```yaml
on:
  pull_request:         # fork PR: no secrets (safe)
  pull_request_target:  # runs base branch code only (caution)
# NEVER checkout PR code under pull_request_target — secrets exposed
# 2025.12: GitHub tightened Environment Protection Rules for pull_request_target
```

## Dependency Audit Tools

| Language | Tool | Command |
|----------|------|---------|
| Rust | cargo-audit | `cargo audit` |
| Node | npm audit | `npm audit` |
| Python | pip-audit | `pip-audit` |
| Multi | Dependabot | auto PR on vulnerability |
| Multi | Snyk | CI integration, container + IaC |
