#!/usr/bin/env bash
# common.sh — Shared utilities for git-workspace scripts
# Provides: ROOT auto-detection, repo enumeration, color codes, shared arg parsing
#
# Source from any script:
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "$SCRIPT_DIR/common.sh"

set -euo pipefail

# ── Color codes ──

green="\033[32m"
yellow="\033[33m"
red="\033[31m"
cyan="\033[36m"
dim="\033[2m"
bold="\033[1m"
reset="\033[0m"

# ── Global state ──

ROOT=""
WORKSPACE_MODE=""  # submodule | flat | single
declare -a REPO_NAMES=()
declare -a REPO_PATHS=()
declare -a REPO_REMOTES=()

# Shared parsed flags (set by parse_common_args)
flag_dry_run=false
flag_verbose=false
flag_json=false
flag_repo=""
flag_root=""

# ── ROOT detection ──

# _has_git_subdirs: true if any immediate subdirectory contains .git (file or dir)
_has_git_subdirs() {
  local dir="$1"
  local sub
  for sub in "$dir"/*/; do
    [ -d "$sub" ] || continue
    [ -e "$sub.git" ] || [ -d "$sub/.git" ] && return 0
  done
  return 1
}

# detect_root: walk up from start_dir to find workspace root
# Sets ROOT and WORKSPACE_MODE globals
detect_root() {
  local start_dir="${1:-$(pwd)}"

  # Normalize
  start_dir="$(cd "$start_dir" && pwd)"

  local dir="$start_dir"
  while true; do
    # Submodule monorepo: has .gitmodules
    if [ -f "$dir/.gitmodules" ]; then
      ROOT="$dir"
      WORKSPACE_MODE="submodule"
      return 0
    fi

    # Has .git (file = submodule, dir = regular repo)
    if [ -e "$dir/.git" ]; then
      if _has_git_subdirs "$dir"; then
        ROOT="$dir"
        WORKSPACE_MODE="flat"
        return 0
      fi
      # This is a standalone repo — keep walking to check for parent workspace
      # unless we already walked up from it
      if [ "$dir" = "$start_dir" ]; then
        ROOT="$dir"
        WORKSPACE_MODE="single"
        return 0
      fi
    fi

    # Reached filesystem root
    if [ "$dir" = "/" ]; then
      ROOT="$start_dir"
      WORKSPACE_MODE="single"
      return 0
    fi

    # Go up one level
    dir="$(dirname "$dir")"
  done
}

# ── Repo enumeration ──

# _parse_gitmodules: fill REPO_* arrays from .gitmodules
_parse_gitmodules() {
  local current_name=""
  local temp_names=() temp_paths=() temp_remotes=()

  while IFS= read -r line; do
    if [[ "$line" =~ ^\[submodule\ \"([^\"]+)\"\] ]]; then
      current_name="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^[[:space:]]*path[[:space:]]*=[[:space:]]*(.+)$ ]]; then
      temp_names+=("$current_name")
      temp_paths+=("$ROOT/${BASH_REMATCH[1]}")
      temp_remotes+=("")  # filled in next pass
    elif [[ "$line" =~ ^[[:space:]]*url[[:space:]]*=[[:space:]]*(.+)$ ]]; then
      temp_remotes[-1]="${BASH_REMATCH[1]}"
    fi
  done < "$ROOT/.gitmodules"

  REPO_NAMES=("${temp_names[@]}")
  REPO_PATHS=("${temp_paths[@]}")
  REPO_REMOTES=("${temp_remotes[@]}")
}

# _scan_flat_repos: fill REPO_* arrays from */.git directories
_scan_flat_repos() {
  REPO_NAMES=()
  REPO_PATHS=()
  REPO_REMOTES=()

  for dir in "$ROOT"/*/; do
    [ -d "$dir" ] || continue
    [ -e "$dir.git" ] || [ -d "$dir/.git" ] || continue

    local name
    name="$(basename "$dir")"
    REPO_NAMES+=("$name")
    REPO_PATHS+=("$dir")
    # Resolve remote for GitHub data
    REPO_REMOTES+=("$(git -C "$dir" remote get-url origin 2>/dev/null || echo "")")
  done
}

# enumerate_repos: dispatch to the right enumeration method
enumerate_repos() {
  case "$WORKSPACE_MODE" in
    submodule) _parse_gitmodules ;;
    flat)      _scan_flat_repos ;;
    single)
      REPO_NAMES=("$(basename "$ROOT")")
      REPO_PATHS=("$ROOT")
      REPO_REMOTES+=("$(git -C "$ROOT" remote get-url origin 2>/dev/null || echo "")")
      ;;
  esac
}

# ── Utility functions ──

workspace_name() {
  basename "$ROOT"
}

# Convert git URL → owner/repo (for gh CLI)
to_github_repo() {
  local url="$1"
  local repo="$url"
  repo="${repo#git@github.com:}"
  repo="${repo#https://github.com/}"
  repo="${repo#http://github.com/}"
  repo="${repo%.git}"
  if [[ "$repo" == *"://"* ]] || [[ "$repo" == "."/* ]]; then
    echo ""
    return
  fi
  echo "$repo"
}

# ── Shared argument parsing ──

# parse_common_args: extracts --root, --dry-run, --verbose, --json, --repo
# Remaining positional args are left for the caller
REMAINING_ARGS=()

parse_common_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --root)      flag_root="$2"; shift 2 ;;
      -n|--dry-run) flag_dry_run=true; shift ;;
      -v|--verbose) flag_verbose=true; shift ;;
      --json)      flag_json=true; shift ;;
      --repo)      flag_repo="$2"; shift 2 ;;
      -h|--help)
        # Caller should handle --help after calling parse_common_args
        REMAINING_ARGS+=("$1")
        shift
        ;;
      *)
        REMAINING_ARGS+=("$1")
        shift
        ;;
    esac
  done
}

# ── Initialization ──

# init_workspace: call after parse_common_args to set up ROOT + repos
init_workspace() {
  if [ -n "$flag_root" ]; then
    # Explicit --root: determine mode directly
    ROOT="$(cd "$flag_root" && pwd)"
    if [ -f "$ROOT/.gitmodules" ]; then
      WORKSPACE_MODE="submodule"
    elif _has_git_subdirs "$ROOT"; then
      WORKSPACE_MODE="flat"
    else
      WORKSPACE_MODE="single"
    fi
  else
    detect_root
  fi
}
