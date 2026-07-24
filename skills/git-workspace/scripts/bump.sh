#!/usr/bin/env bash
set -euo pipefail

# bump.sh — Semantic version bump, tag & push
# Works in submodule monorepos, flat multi-repo, and single projects
#
# Usage:
#   bump.sh <repo-name> <major|minor|patch>
#   bump.sh all <major|minor|patch>
#   bump.sh --root /path/to/workspace <repo-name> <major|minor|patch>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

parse_common_args "$@"
init_workspace

# ── Positional args (after common flags are stripped) ──

args=("${REMAINING_ARGS[@]}")

usage() {
  echo "Usage: $(basename "$0") [options] <repo-name|all> <major|minor|patch>"
  echo ""
  echo "Options:"
  echo "  --root <path>   Use specified workspace root"
  echo ""
  echo "Examples:"
  echo "  $(basename "$0") my-repo patch     # v1.2.3 -> v1.2.4"
  echo "  $(basename "$0") my-repo minor     # v1.2.3 -> v1.3.0"
  echo "  $(basename "$0") my-repo major     # v1.2.3 -> v2.0.0"
  echo "  $(basename "$0") all patch         # bump all repos"
  echo "  $(basename "$0") . patch           # bump current (single-repo mode)"
}

if [ ${#args[@]} -lt 2 ]; then
  usage
  exit 1
fi

target="${args[0]}"
bump_type="${args[1]}"

if [[ "$bump_type" != "major" && "$bump_type" != "minor" && "$bump_type" != "patch" ]]; then
  echo -e "${red}Invalid bump type: $bump_type. Use major, minor, or patch.${reset}"
  exit 1
fi

# ── Bump logic ──

bump_version() {
  local repo="$1"
  local name
  name=$(basename "$repo")

  # Get latest tag
  local latest_tag
  latest_tag=$(git -C "$repo" describe --tags --abbrev=0 2>/dev/null) || {
    echo -e "${yellow}! $name${reset} — no tags found, starting at v0.0.0"
    latest_tag="v0.0.0"
  }

  # Strip leading 'v' if present
  local version="${latest_tag#v}"

  # Parse semver
  local major minor patch
  IFS='.' read -r major minor patch <<< "$version"

  # Ensure numeric
  major=${major:-0}
  minor=${minor:-0}
  patch=${patch:-0}

  local old_version="v${major}.${minor}.${patch}"

  # Bump
  case "$bump_type" in
    major) major=$((major + 1)); minor=0; patch=0 ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    patch) patch=$((patch + 1)) ;;
  esac

  local new_version="v${major}.${minor}.${patch}"

  echo -e "${cyan}$name${reset}  $old_version → ${green}$new_version${reset}  ($bump_type)"

  # Rust repos: the release tooling (cargo-dist) rejects a tag whose version
  # does not match Cargo.toml, so bump the manifest and commit a release
  # commit BEFORE tagging. Tagging without this produced a failed release
  # (claudy v0.6.0, 2026-07-24). Non-Rust repos skip this block unchanged.
  if [ -f "$repo/Cargo.toml" ]; then
    local plain_version="${major}.${minor}.${patch}"
    if grep -qE '^version = "' "$repo/Cargo.toml"; then
      # Bump only the first (package) version line.
      perl -pi -e 'if (!$done && s/^version = "[^"]+"/version = "'"$plain_version"'"/) { $done = 1 }' "$repo/Cargo.toml"
      # Refresh Cargo.lock so the workspace member entry matches.
      (cd "$repo" && cargo update --workspace --quiet 2>/dev/null || cargo check --quiet 2>/dev/null || true)
      git -C "$repo" add Cargo.toml
      [ -f "$repo/Cargo.lock" ] && git -C "$repo" add Cargo.lock
      git -C "$repo" commit -m "release: $new_version" 2>&1 | sed 's/^/    /'
      git -C "$repo" push origin HEAD 2>&1 | sed 's/^/    /'
    fi
  fi

  # Tag
  git -C "$repo" tag "$new_version"

  # Push tag
  git -C "$repo" push origin "$new_version" 2>&1 | sed 's/^/    /'

  return 0
}

# ── Execute ──

if [ "$WORKSPACE_MODE" = "single" ]; then
  # Single repo: any target means "this repo"
  echo -e "${bold}Bumping ${bump_type} version for $(workspace_name)${reset}"
  echo ""
  bump_version "$ROOT"
else
  enumerate_repos

  if [ "$target" = "all" ]; then
    echo -e "${bold}Bumping ${bump_type} version for all repositories${reset}"
    echo ""

    success=0
    failed=0

    for i in "${!REPO_NAMES[@]}"; do
      if bump_version "${REPO_PATHS[$i]}"; then
        success=$((success + 1))
      else
        failed=$((failed + 1))
      fi
      echo ""
    done

    echo -e "${bold}─────────────────────────────${reset}"
    echo -e "  ${green}Bumped: $success${reset} | ${red}Failed: $failed${reset}"
  else
    # Find named repo
    found=-1
    for i in "${!REPO_NAMES[@]}"; do
      [ "${REPO_NAMES[$i]}" = "$target" ] && found=$i && break
    done

    if [ "$found" -eq -1 ]; then
      echo -e "${red}Repository not found: $target${reset}"
      echo ""
      echo -e "Available repos:"
      for i in "${!REPO_NAMES[@]}"; do
        echo "  ${REPO_NAMES[$i]}"
      done
      exit 1
    fi

    bump_version "${REPO_PATHS[$found]}"
  fi
fi
