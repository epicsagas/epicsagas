# Linux — Package Managers & Distribution

## Native Package Managers

| Manager | Distro | Format | Notes |
|---------|--------|--------|-------|
| apt | Debian/Ubuntu | .deb | Widest user base |
| dnf | RHEL/Fedora/CentOS | .rpm | Enterprise standard |
| pacman | Arch / Manjaro | pkg.tar | Rolling release, AUR |
| apk | Alpine | .apk | Container standard |
| zypper | openSUSE | .rpm | |

## APT Repository Setup (for publishers)

```bash
# User install after repo registration
curl -fsSL https://repo.example.com/gpg.key | \
  sudo gpg --dearmor -o /etc/apt/keyrings/tool.gpg
echo "deb [signed-by=/etc/apt/keyrings/tool.gpg] https://repo.example.com/apt stable main" | \
  sudo tee /etc/apt/sources.list.d/tool.list
sudo apt update && sudo apt install tool
```

Auto-generate via: **goreleaser** (Go), **cargo-dist** (Rust), **fpm** (any language).

## Universal Formats

| Format | Install | Sandbox | Best For |
|--------|---------|---------|---------|
| **AppImage** | `chmod +x tool.AppImage && ./tool.AppImage` | none | portable, no install |
| **Snap** | `sudo snap install tool` | AppArmor | auto-update, isolation |
| **Flatpak** | `flatpak install flathub com.example.Tool` | bubblewrap | desktop GUI apps |

## Static Binary (most portable)

```bash
# Download pre-built static binary
curl -L https://github.com/user/tool/releases/latest/download/tool-linux-x64 -o tool
chmod +x tool && sudo mv tool /usr/local/bin/

# Verify (if checksum provided)
curl -L .../tool-linux-x64.sha256 | sha256sum -c
```

Static binaries (musl-linked) run on any Linux without dependency issues.

## Architecture Coverage

| Arch | Tag | Common Use |
|------|-----|-----------|
| x86_64 | amd64 | servers, desktops |
| aarch64 | arm64 | AWS Graviton, Raspberry Pi 4, Apple M-series Linux VMs |
| armv7 | armhf | older Raspberry Pi |
