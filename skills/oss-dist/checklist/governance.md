# OSS Governance & Security Checklist

> Compressed from OSS-PROJECT-GUIDELINES.md §3.5, §3.8, §3.9
> English only. AI-auditable. Under 120 lines.

---

## §3.5 Security

### SECURITY.md Required Fields

| Field | Requirement |
|---|---|
| Supported versions table | List versions with support status |
| Vulnerability reporting contact | Email + PGP key OR GitHub Private Vulnerability Reporting URL |
| Acknowledgement SLA | 48 hours |
| Patch target SLA | 90 days |

### Dependency Vulnerability Scanning

| Tool | Integration | Scope |
|---|---|---|
| GitHub Dependabot | Auto (free) | Auto PRs for vulnerable deps |
| GitHub CodeQL | Actions workflow | Static source analysis |
| Snyk | CI integration | Containers, IaC included |
| cargo audit | `cargo audit` | Rust (RustSec DB) |
| npm audit | `npm audit` | Node.js deps |
| pip-audit | `pip-audit` | Python (OSV DB) |

### Required CI Steps (GitHub Actions)

- [ ] `gitleaks/gitleaks-action@v2` — secret scanning
  - Personal repos: free
  - Org repos: requires `GITLEAKS_LICENSE` key (free tier available); v2+ is NOT MIT (as of 2024)
- [ ] Language-specific audit: `cargo audit` / `npm audit` / `pip-audit`
- [ ] `github/codeql-action/analyze@v3` — static analysis (`languages: javascript, python`)

### Actions Version Freshness

- [ ] All pinned GitHub Actions are within 1 major version of latest release
- [ ] No action older than 6 months without a justified reason
- [ ] Automated freshness check configured (Dependabot `github-actions` ecosystem or `pinact`)
- [ ] SHA pins include a version comment (`@<sha> # v<tag>`) for human readability

> **How to check:** Run `git ls-remote https://github.com/<owner>/<repo> refs/tags/v<X.Y.Z>` to verify pinned SHA matches the claimed version. Use [pinact](https://github.com/suzuki-shunsuke/pinact) to automate SHA pinning.

### SBOM (Software Bill of Materials) — Required since 2024

- [ ] Generate SBOM in CI using `anchore/sbom-action@v0` (`format: spdx-json`)
- [ ] Attach `sbom.spdx.json` to GitHub Release via `softprops/action-gh-release@v3`
- [ ] Pin all Actions to full commit SHA (version tags are mutable — repointing attack vector)
  - Use Dependabot `github-actions` ecosystem or `pinact` to automate

| Language | SBOM Tool |
|---|---|
| Rust | `cargo cyclonedx` |
| Python | `cyclonedx-bom` |
| Node.js | `@cyclonedx/cyclonedx-npm` |

### Pwn-Request Prevention

| Trigger | Rule |
|---|---|
| Fork PR | Use `pull_request` event — no secrets exposed |
| `pull_request_target` | Never checkout PR code — secrets are exposed |
| Secret isolation | Use Environment Protection Rules to gate secrets from fork PRs |

> GitHub 2025.12: Environment Protection Rules enforcement strengthened.

---

## §3.8 Governance

### GOVERNANCE.md Minimum Structure

> Note: Projects under 5K stars may use a CONTRIBUTING.md section instead of a full GOVERNANCE.md.

#### Roles

| Role | Rights | Qualification |
|---|---|---|
| Contributor | Submit PRs | Open to all |
| Committer | Merge PRs | 5+ PRs merged, voted in by maintainers |
| Maintainer | Release rights | Long-term contributors, see promotion criteria |

#### Decision Making

| Change Type | Threshold |
|---|---|
| Normal change | 1 reviewer approval |
| Breaking change | 2+ maintainer approvals |
| Governance change | 2/3 maintainer vote |

#### RFC Process

- [ ] `rfcs/` folder at repo root
- [ ] File naming: `YYYY-MM-DD-feature-name.md`
- [ ] 2-week public comment period
- [ ] Maintainer decision recorded in RFC file

### Maintainer Promotion Criteria

- [ ] 6+ months of sustained activity
- [ ] 5+ substantial PR contributions
- [ ] Code of Conduct adherence (no violations)
- [ ] 2+ nominations from existing maintainers

---

## §3.9 Sustainability

### Funding Options

- [ ] GitHub Sponsors — add `.github/FUNDING.yml`
- [ ] Open Collective — organization-friendly, transparent finances
- [ ] Buy Me a Coffee / Ko-fi — lightweight individual support
- [ ] Corporate sponsorship — logo placement in README
- [ ] Paid support / consulting — SLA-backed commercial offering
- [ ] Cloud version — OSS core + paid hosted tier (open-core model)

---
