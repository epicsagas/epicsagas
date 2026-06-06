# Swift — One-Line Install

> Primary: **mint** (Swift CLI tool manager) + Homebrew. Linux server via Docker.

## Runtime Install

```bash
# macOS: Xcode Command Line Tools (includes Swift)
xcode-select --install

# Homebrew (specific version)
brew install swiftlang

# mise
mise use swift@6.0

# Linux
wget -q https://download.swift.org/swift-6.0-release/ubuntu2204/swift-6.0-RELEASE-ubuntu22.04.tar.gz
# or use Docker → see below
```

## Tool Distribution

```bash
# mint (Swift CLI package manager)
brew install mint
mint install user/tool
mint run user/tool

# Homebrew (macOS — most common for end users)
brew install tool

# Swift Package Manager (SPM) — build from source
git clone https://github.com/user/tool && cd tool
swift build -c release
.build/release/tool

# Direct binary release (GitHub Releases)
curl -L https://github.com/user/tool/releases/latest/download/tool-macos.zip -o tool.zip
unzip tool.zip && sudo mv tool /usr/local/bin/
```

## Mint Distribution (Package.swift)

```swift
// Package.swift
let package = Package(
    name: "tool",
    targets: [
        .executableTarget(name: "tool", path: "Sources")
    ]
)
```

```bash
# Users install via mint
mint install user/tool@1.0.0
```

## Linux / Server Deployment (Docker)

```dockerfile
FROM swift:6.0-slim AS builder
WORKDIR /app
COPY . .
RUN swift build -c release

FROM ubuntu:22.04
COPY --from=builder /app/.build/release/tool /usr/local/bin/
ENTRYPOINT ["tool"]
```

## OS Support

| Platform | Method | Notes |
|----------|--------|-------|
| macOS | mint, Homebrew, SPM | Native |
| Linux | Docker, SPM | Swift Linux toolchain available |
| Windows | ❌ | Not officially supported |
