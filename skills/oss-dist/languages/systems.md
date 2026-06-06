# C / C++ / Zig — One-Line Install

## C / C++

### Install Commands

```bash
# Homebrew (macOS/Linux)
brew install tool

# apt (Debian/Ubuntu)
sudo apt install tool

# dnf (RHEL/Fedora)
sudo dnf install tool

# vcpkg (cross-platform package manager)
git clone https://github.com/microsoft/vcpkg
./vcpkg/bootstrap-vcpkg.sh
./vcpkg/vcpkg install tool

# Windows
winget install tool
choco install tool
```

### Distribution

- Provide pre-built binaries via GitHub Releases for each OS/arch
- Use CMake + CPack to generate platform installers (.deb, .rpm, .msi)
- Static linking (`-static`) eliminates runtime dependency issues

---

## Zig

> Key advantage: single command cross-compile to all platforms, zero toolchain setup.

### Install

```bash
mise use zig@0.14          # recommended (version management)
brew install zig            # Homebrew
```

### Cross-Compile (all targets from one machine)

```bash
zig build -Dtarget=x86_64-linux-musl      # Linux static binary
zig build -Dtarget=aarch64-linux-musl     # Linux ARM64 static
zig build -Dtarget=x86_64-windows-gnu     # Windows binary
zig build -Dtarget=aarch64-macos          # macOS ARM
zig build -Dtarget=x86_64-macos           # macOS Intel
```

### GitHub Actions

```yaml
- uses: mlugg/setup-zig@v1
  with:
    version: 0.14.0
- run: zig build -Dtarget=x86_64-linux-musl -Doptimize=ReleaseFast
```

### OS/Arch Matrix

| Target | OS | Arch | Notes |
|--------|----|------|-------|
| `x86_64-linux-musl` | Linux | x86_64 | static, no glibc dep |
| `aarch64-linux-musl` | Linux | ARM64 | static |
| `x86_64-windows-gnu` | Windows | x86_64 | |
| `x86_64-macos` | macOS | Intel | |
| `aarch64-macos` | macOS | Apple Silicon | |
