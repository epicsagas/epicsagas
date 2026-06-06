# Windows — Package Managers

## Comparison

| | winget | Scoop | Chocolatey |
|--|--------|-------|------------|
| Pre-installed | Windows 11 ✅ | ❌ | ❌ |
| Admin required | some | ❌ | some |
| Package count | 8,000+ | medium | 10,000+ |
| Dev tool focus | general | ✅ | partial |
| Enterprise DSC | ❌ | ❌ | ✅ |
| Best for | end users | developers | enterprise |

## winget

```powershell
winget install tool                           # by name
winget install --id Publisher.ToolName        # by exact ID
winget upgrade --all                          # update all
```

## Scoop (recommended for developers — no admin)

```powershell
# Install Scoop
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

# Add custom bucket and install
scoop bucket add user https://github.com/user/scoop-bucket
scoop install tool
scoop update tool
```

## Chocolatey

```powershell
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

choco install tool
choco upgrade tool
```

## irm | iex Security

```powershell
# Standard pattern (de facto standard)
powershell -ExecutionPolicy ByPass -c "irm https://example.com/install.ps1 | iex"

# ByPass is explicit and transparent — preferred over hidden policy bypass
# Script runs in-memory (no disk write) — verify URL source before running
```

## Scoop Bucket Setup (for publishers)

```json
// bucket/tool.json
{
  "version": "1.0.0",
  "description": "Tool description",
  "homepage": "https://github.com/user/tool",
  "license": "MIT",
  "architecture": {
    "64bit": {
      "url": "https://github.com/user/tool/releases/download/v1.0.0/tool-windows-x64.zip",
      "hash": "sha256:..."
    }
  },
  "bin": "tool.exe"
}
```
