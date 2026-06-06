# macOS — Package Managers & Distribution

## Package Manager Comparison

| | Homebrew | MacPorts | mas | Direct binary |
|--|----------|----------|-----|--------------|
| Install required | `brew` | `port` | pre-installed | none |
| Admin required | ❌ | ✅ | ❌ | ❌ |
| Package count | 7,000+ formulae / 12,000+ casks | 30,000+ | Mac App Store only | — |
| Dev tool focus | ✅ | ✅ | ❌ | — |
| GUI apps | ✅ (cask) | partial | ✅ | ✅ (DMG/pkg) |
| Best for | developers | power users / reproducible | App Store apps | zero-dep CLI |

---

## Homebrew (recommended)

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install from official formula
brew install tool

# Install from a custom tap (third-party)
brew tap user/tap
brew install user/tap/tool

# Update
brew upgrade tool

# Uninstall
brew uninstall tool
```

### Homebrew Tap Setup (for publishers)

```ruby
# Formula/tool.rb
class Tool < Formula
  desc "Short description of the tool"
  homepage "https://github.com/user/tool"
  version "1.0.0"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/user/tool/releases/download/v1.0.0/tool-aarch64-apple-darwin.tar.gz"
      sha256 "<sha256>"
    else
      url "https://github.com/user/tool/releases/download/v1.0.0/tool-x86_64-apple-darwin.tar.gz"
      sha256 "<sha256>"
    end
  end

  def install
    bin.install "tool"
  end

  test do
    assert_match "tool", shell_output("#{bin}/tool --version 2>&1")
  end
end
```

Auto-generate via: **cargo-dist** (Rust), **goreleaser** (Go) — both write formula and push to tap on tag.

---

## MacPorts

```bash
# Install MacPorts from https://www.macports.org/install.php

sudo port install tool
sudo port upgrade tool
sudo port uninstall tool
```

MacPorts is less common than Homebrew for CLI tools. Target it only if your users are power users with reproducibility requirements.

---

## mas (Mac App Store CLI)

```bash
# Install mas
brew install mas

# Search
mas search "App Name"

# Install by App Store ID
mas install 1234567890

# Update
mas upgrade 1234567890
```

Only applicable for apps distributed through the Mac App Store.

---

## Direct Binary Distribution

### curl installer (cargo-dist / goreleaser generated)

```bash
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/user/tool/releases/latest/download/tool-installer.sh | sh
```

Re-run the same script to update.

### Manual download

```bash
# Apple Silicon
curl -L https://github.com/user/tool/releases/latest/download/tool-aarch64-apple-darwin.tar.gz | tar xz
sudo mv tool /usr/local/bin/

# Intel
curl -L https://github.com/user/tool/releases/latest/download/tool-x86_64-apple-darwin.tar.gz | tar xz
sudo mv tool /usr/local/bin/
```

---

## Architecture Coverage

| Arch | Target triple | Hardware |
|------|--------------|----------|
| Apple Silicon | `aarch64-apple-darwin` | M1 / M2 / M3 / M4 |
| Intel | `x86_64-apple-darwin` | 2020 and earlier Intel Macs |

Always ship **both targets**. Rosetta 2 lets Apple Silicon run Intel binaries, but native ARM is significantly faster and preferred.

---

## Code Signing & Notarization (required for distribution)

macOS Gatekeeper blocks unsigned/unnotarized binaries by default. Users see "app can't be opened" without this.

### Developer ID signing

```bash
# Sign the binary
codesign --sign "Developer ID Application: Your Name (TEAMID)" \
  --options runtime \
  --timestamp \
  ./tool

# Verify
codesign --verify --verbose ./tool
```

### Notarization (required for Gatekeeper on macOS 10.15+)

```bash
# Zip the binary for submission
dzip tool.zip tool

# Submit for notarization
xcrun notarytool submit tool.zip \
  --apple-id "you@example.com" \
  --team-id "TEAMID" \
  --password "@keychain:AC_PASSWORD" \
  --wait

# Staple the ticket (for DMG/pkg; binaries use online check)
xcrun stapler staple tool.dmg
```

**Cost:** Apple Developer Program — $99/yr.

### cargo-dist auto-notarization

cargo-dist v0.14+ can handle signing + notarization automatically via GitHub Actions when secrets are configured:

```toml
# dist-workspace.toml
[workspace.metadata.dist]
macos-sign = true
```

Required GitHub Secrets: `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_NOTARIZATION_PASSWORD`, `APPLE_TEAM_ID`.

---

## DMG Distribution

DMG (Disk Image) is the conventional format for macOS GUI app distribution.

```bash
# Create a simple DMG
hdiutil create -volname "Tool" \
  -srcfolder ./dist \
  -ov -format UDZO \
  tool.dmg

# Sign the DMG
codesign --sign "Developer ID Application: Your Name (TEAMID)" tool.dmg

# Notarize
xcrun notarytool submit tool.dmg \
  --apple-id "you@example.com" \
  --team-id "TEAMID" \
  --password "@keychain:AC_PASSWORD" \
  --wait

xcrun stapler staple tool.dmg
```

For CLI tools, DMG is rarely needed — prefer Homebrew + direct binary.

---

## .pkg Installer

`.pkg` is macOS's native installer format, suitable for tools needing system-level installation.

```bash
# Build with pkgbuild
pkgbuild --root ./payload \
  --identifier "com.example.tool" \
  --version "1.0.0" \
  --install-location /usr/local \
  tool.pkg

# Sign
productsign --sign "Developer ID Installer: Your Name (TEAMID)" \
  tool.pkg tool-signed.pkg

# Notarize
xcrun notarytool submit tool-signed.pkg \
  --apple-id "you@example.com" \
  --team-id "TEAMID" \
  --password "@keychain:AC_PASSWORD" \
  --wait

xcrun stapler staple tool-signed.pkg
```

---

## Gatekeeper Bypass (for unsigned binaries — development only)

```bash
# Remove quarantine attribute (dev/testing only — never instruct users to do this)
xattr -d com.apple.quarantine ./tool

# Allow in System Settings → Privacy & Security → "Open Anyway"
```

Never document quarantine bypass as an install method. Ship properly signed binaries instead.

---

## Audit Checklist

- [ ] Both `aarch64-apple-darwin` and `x86_64-apple-darwin` targets built
- [ ] Homebrew formula/tap exists and is auto-updated on release
- [ ] Binary is code-signed with Developer ID
- [ ] Binary/installer is notarized (required for macOS 10.15+)
- [ ] SHA256 checksums published alongside release artifacts
- [ ] README documents `brew upgrade tool` as the update command

## See Also
- `checklist/release.md` — CI/CD pipeline, version automation
- `languages/rust.md` — cargo-dist notarization config
- `platforms/windows.md` — Windows Authenticode signing
- `tools/security.md` — SBOM, attestations, sigstore
