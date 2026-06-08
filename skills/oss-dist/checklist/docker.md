---
name: docker
description: Docker image distribution checklist — registry selection, multi-arch builds, Dockerfile best practices, tagging strategy, and GHCR setup.
tags: [docker, container, ghcr, multi-arch, buildx, oci]
---

# Docker Image Distribution — Checklist (§D)

---

## §D.1 Image Registry Decision Matrix

| Registry | Free Tier | Auth | Namespace | Best For |
|----------|-----------|------|-----------|----------|
| GHCR (`ghcr.io`) | Unlimited public; private tied to GitHub plan | `GITHUB_TOKEN` (OIDC, no secret needed) | `ghcr.io/org/repo` | OSS projects already on GitHub |
| Docker Hub | 1 private repo; public unlimited | PAT or OIDC | `org/repo` | Maximum discoverability |
| Self-hosted (Harbor) | Unlimited | LDAP / OIDC | custom | Air-gapped / enterprise |

**Recommendation**: GHCR for OSS CLI tools — zero token rotation, automatic visibility control, native GitHub Actions integration.

---

## §D.2 Multi-Arch Manifest (linux/amd64 + linux/arm64)

- [ ] QEMU + Buildx initialised: `setup-qemu-action@v3`, `setup-buildx-action@v3`
- [ ] Single `docker buildx build --platform linux/amd64,linux/arm64 --push` call
- [ ] Manifest verified: `docker buildx imagetools inspect ghcr.io/org/repo:latest`

```yaml
# multi-arch build step (excerpt from .github/workflows/docker.yml)
- uses: docker/setup-qemu-action@v3
- uses: docker/setup-buildx-action@v3
- name: Build and push
  uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

---

## §D.3 Dockerfile Best Practices for CLI Tools

- [ ] Multi-stage: `builder` compiles, final stage copies binary only
- [ ] Base: `gcr.io/distroless/static` (no shell) or `scratch`
- [ ] `USER nonroot:nonroot`; no package-manager cache in final layer
- [ ] Binary statically linked (Rust musl: `x86_64-unknown-linux-musl`)

```dockerfile
FROM rust:1.87-alpine AS builder
RUN apk add --no-cache musl-dev
WORKDIR /src
COPY . .
RUN cargo build --release --target x86_64-unknown-linux-musl

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /src/target/x86_64-unknown-linux-musl/release/mytool /mytool
USER nonroot:nonroot
ENTRYPOINT ["/mytool"]
```

---

## §D.4 Tagging Strategy

| Tag | Mutability | Updated on | Example |
|-----|-----------|-----------|---------|
| `latest` | Mutable | Every push to `main` | `ghcr.io/org/repo:latest` |
| `vX` | Mutable | Major release + patches | `ghcr.io/org/repo:v2` |
| `vX.Y` | Mutable | Minor release + patches | `ghcr.io/org/repo:v2.3` |
| `vX.Y.Z` | **Immutable** | Tag push only | `ghcr.io/org/repo:v2.3.1` |
| `sha-<commit>` | Immutable | Every build | `ghcr.io/org/repo:sha-a1b2c3d` |

**Policy**: pin production deployments to `vX.Y.Z` or `sha-*`. Never pin to `latest` in manifests.

---

## §D.5 GHCR Setup & Complete Workflow

- [ ] Package visibility set to **Public** in `github.com/org` → Packages → Settings
- [ ] `packages: write` permission + `GITHUB_TOKEN` — no external PAT required
- [ ] OCI labels populated via `docker/metadata-action` (`org.opencontainers.image.*`)

```yaml
# .github/workflows/docker.yml
name: Docker

on:
  push:
    branches: [main]
    tags: ["v*.*.*"]
jobs:
  build-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            type=sha,prefix=sha-,format=short
      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```
