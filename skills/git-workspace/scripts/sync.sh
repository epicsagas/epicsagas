#!/usr/bin/env bash
set -euo pipefail

# sync.sh — Fetch & pull all repos in a workspace
# Works in submodule monorepos, flat multi-repo, and single projects
#
# Usage:
#   sync.sh [options]
#   sync.sh --root /path/to/workspace

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

parse_common_args "$@"
init_workspace

# ── Help ──

if [[ " ${REMAINING_ARGS[*]} " == *" --help "* ]] || [[ " ${REMAINING_ARGS[*]} " == *" -h "* ]]; then
  echo "Usage: $(basename "$0") [options]"
  echo ""
  echo "Fetch & pull all repos in the workspace."
  echo ""
  echo "Options:"
  echo "  --root <path>   Use specified workspace root (auto-detected by default)"
  echo "  -n, --dry-run   Show what would happen without executing"
  echo "  -v, --verbose   Show detailed output including 'git status'"
  echo "  -h, --help      Show this help"
  exit 0
fi

# ── Single-repo mode ──

if [ "$WORKSPACE_MODE" = "single" ]; then
  echo -e "${bold}Syncing single repo: $(workspace_name)${reset}"
  echo ""

  if $flag_dry_run; then
    echo -e "${cyan}~ $(workspace_name)${reset} — would fetch & pull"
    exit 0
  fi

  has_changes=false
  git -C "$ROOT" diff --quiet HEAD 2>/dev/null || has_changes=true
  git -C "$ROOT" diff --cached --quiet 2>/dev/null || has_changes=true

  if $has_changes; then
    echo -e "${yellow}! $(workspace_name)${reset} — dirty working tree (skipping pull)"
    exit 0
  fi

  git -C "$ROOT" fetch --all --prune 2>&1 || true

  branch=$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "HEADLESS")
  if [ "$branch" = "HEADLESS" ]; then
    echo -e "${yellow}! $(workspace_name)${reset} — detached HEAD (skipping pull)"
    exit 0
  fi

  ahead=$(git -C "$ROOT" rev-list --count "@{upstream}..HEAD" 2>/dev/null || echo "0")
  behind=$(git -C "$ROOT" rev-list --count "HEAD..@{upstream}" 2>/dev/null || echo "0")

  if [ "$behind" -eq 0 ] && [ "$ahead" -eq 0 ]; then
    echo -e "${green}✓ $(workspace_name)${reset} — up to date ($branch)"
  elif [ "$behind" -gt 0 ]; then
    if pull_output=$(git -C "$ROOT" pull --ff-only 2>&1); then
      echo -e "${green}✓ $(workspace_name)${reset} — pulled $behind commit(s) ($branch)"
      if $flag_verbose; then
        echo "$pull_output" | sed 's/^/    /'
      fi
    else
      echo -e "${red}✗ $(workspace_name)${reset} — pull failed"
      echo "$pull_output" | head -3 | sed 's/^/    /'
      exit 1
    fi
  elif [ "$ahead" -gt 0 ]; then
    echo -e "${cyan}↑ $(workspace_name)${reset} — $ahead ahead of remote ($branch)"
  fi
  exit 0
fi

# ── Multi-repo mode (submodule or flat) ──

enumerate_repos

mode_label=$([ "$WORKSPACE_MODE" = "submodule" ] && echo "submodules" || echo "repositories")
echo -e "${bold}Syncing ${#REPO_NAMES[@]} ${mode_label} in $(workspace_name)${reset}"
echo ""

success=0
up_to_date=0
failed=0
skipped=0

for i in "${!REPO_NAMES[@]}"; do
  repo="${REPO_PATHS[$i]}"
  name="${REPO_NAMES[$i]}"

  has_changes=false
  git -C "$repo" diff --quiet HEAD 2>/dev/null || has_changes=true
  git -C "$repo" diff --cached --quiet 2>/dev/null || has_changes=true
  if $has_changes; then
    echo -e "${yellow}! $name${reset} — dirty working tree (skipping pull)"
    if $flag_verbose; then
      git -C "$repo" status --short | sed 's/^/    /'
    fi
    echo ""
    skipped=$((skipped + 1))
    continue
  fi

  if $flag_dry_run; then
    echo -e "${cyan}~ $name${reset} — would fetch & pull"
  else
    fetch_output=$(git -C "$repo" fetch --all --prune 2>&1) || true

    branch=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "HEADLESS")

    if [ "$branch" = "HEADLESS" ]; then
      # Submodule detached HEAD: update to remote tracking commit
      if [ "$WORKSPACE_MODE" = "submodule" ]; then
        before=$(git -C "$repo" rev-parse HEAD 2>/dev/null)
        if update_output=$(git -C "$ROOT" submodule update --remote --merge -- "$name" 2>&1); then
          after=$(git -C "$repo" rev-parse HEAD 2>/dev/null)
          if [ "$before" != "$after" ]; then
            count=$(git -C "$repo" rev-list --count "$before..$after" 2>/dev/null || echo "?")
            echo -e "${green}✓ $name${reset} — merged $count new commit(s) (detached → updated)"
            if $flag_verbose; then
              git -C "$repo" log --oneline "$before..$after" | sed 's/^/    /'
            fi
            success=$((success + 1))
          else
            echo -e "${green}✓ $name${reset} — up to date (detached HEAD)"
            up_to_date=$((up_to_date + 1))
          fi
        else
          echo -e "${red}✗ $name${reset} — submodule update failed"
          echo "$update_output" | head -3 | sed 's/^/    /'
          failed=$((failed + 1))
        fi
      else
        echo -e "${yellow}! $name${reset} — detached HEAD (skipping pull)"
        skipped=$((skipped + 1))
      fi
      echo ""
      continue
    fi

    ahead=$(git -C "$repo" rev-list --count "@{upstream}..HEAD" 2>/dev/null || echo "0")
    behind=$(git -C "$repo" rev-list --count "HEAD..@{upstream}" 2>/dev/null || echo "0")

    if [ "$behind" -eq 0 ] && [ "$ahead" -eq 0 ]; then
      echo -e "${green}✓ $name${reset} — up to date ($branch)"
      up_to_date=$((up_to_date + 1))
    elif [ "$behind" -gt 0 ]; then
      if pull_output=$(git -C "$repo" pull --ff-only 2>&1); then
        echo -e "${green}✓ $name${reset} — pulled $behind commit(s) ($branch)"
        if $flag_verbose; then
          echo "$pull_output" | sed 's/^/    /'
        fi
        success=$((success + 1))
      else
        echo -e "${red}✗ $name${reset} — pull failed"
        echo "$pull_output" | head -3 | sed 's/^/    /'
        failed=$((failed + 1))
      fi
    elif [ "$ahead" -gt 0 ]; then
      echo -e "${cyan}↑ $name${reset} — $ahead ahead of remote ($branch)"
      skipped=$((skipped + 1))
    fi
  fi

  if $flag_verbose && ! $flag_dry_run; then
    st=$(git -C "$repo" status --short 2>/dev/null)
    if [ -n "$st" ]; then
      echo "$st" | sed 's/^/    /'
    fi
  fi

  echo ""
done

echo -e "${bold}─────────────────────────────${reset}"
total=${#REPO_NAMES[@]}
echo -e "  Total: $total | ${green}Pulled: $success${reset} | ${cyan}Up to date: $up_to_date${reset} | ${red}Failed: $failed${reset} | Skipped: $skipped"
