# Go — One-Line Install

> Primary tool: **goreleaser**. Auto-generates Homebrew formula + apt/dnf repos.

## Install Commands

```bash
# Homebrew (macOS/Linux — recommended)
brew install tool

# go install (requires Go)
go install github.com/user/tool@latest

# eget (binary download, no Go needed)
eget user/tool

# Linux apt (goreleaser auto-generates repo)
echo 'deb [trusted=yes] https://repo.example.com/apt/ /' | \
  sudo tee /etc/apt/sources.list.d/tool.list
sudo apt update && sudo apt install tool

# Windows (Scoop)
scoop bucket add user https://github.com/user/scoop-bucket && scoop install tool
```

## goreleaser Config

```yaml
# .goreleaser.yaml
builds:
  - goos: [linux, darwin, windows]
    goarch: [amd64, arm64]

brews:
  - repository: { owner: user, name: homebrew-tap }

scoops:
  - repository: { owner: user, name: scoop-bucket }

nfpms:
  - formats: [deb, rpm, apk]
```

```bash
goreleaser release --clean
```

## GitHub Actions

```yaml
- uses: goreleaser/goreleaser-action@v6
  with:
    args: release --clean
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## OS/Arch Support

| OS | amd64 | arm64 |
|----|-------|-------|
| Linux | ✅ | ✅ |
| macOS | ✅ | ✅ |
| Windows | ✅ | ✅ |
| FreeBSD | ✅ | ✅ |
