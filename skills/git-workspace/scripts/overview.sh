#!/usr/bin/env bash
set -euo pipefail

# overview.sh — Workspace-wide project health dashboard
# Shows: open issues, open PRs, main vs latest tag diff for each repo
# Works in submodule monorepos, flat multi-repo, and single projects
#
# Usage:
#   overview.sh                # full dashboard
#   overview.sh --json         # machine-readable JSON output
#   overview.sh --repo <name>  # single repo detail with PR/issue lists
#   overview.sh --root <path>  # use specified workspace root

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

parse_common_args "$@"
init_workspace

# ── Help ──

if [[ " ${REMAINING_ARGS[*]} " == *" --help "* ]] || [[ " ${REMAINING_ARGS[*]} " == *" -h "* ]]; then
  echo "Usage: $(basename "$0") [options]"
  echo ""
  echo "Options:"
  echo "  --json          Output JSON for programmatic use"
  echo "  --repo <name>   Show single repo detail"
  echo "  --root <path>   Use specified workspace root"
  echo "  -h, --help      Show this help"
  exit 0
fi

enumerate_repos

# ── GitHub data collection ──

# Query GitHub API (with simple in-memory cache)
declare -A _gh_cache
gh_cached() {
  local key="$1"
  if [[ -v "_gh_cache[$key]" ]]; then
    echo "${_gh_cache[$key]}"
    return
  fi
  local val
  val=$(gh api "$key" --jq '.open_issues_count' 2>/dev/null || echo "0")
  _gh_cache["$key"]="$val"
  echo "$val"
}

# ── Single repo data collection ──

collect_repo_data() {
  local idx="$1"
  local name="${REPO_NAMES[$idx]}"
  local path="${REPO_PATHS[$idx]}"
  local remote="${REPO_REMOTES[$idx]}"

  local github_repo
  github_repo=$(to_github_repo "$remote")

  DATA_OPEN_ISSUES=0
  DATA_OPEN_PRS=0
  DATA_LATEST_TAG=""
  DATA_COMMITS_AHEAD=0
  DATA_HEAD=""
  DATA_HAS_GITHUB=false

  if [ -n "$github_repo" ]; then
    DATA_HAS_GITHUB=true

    # Issues count (GitHub open_issues_count includes PRs, so we subtract)
    local raw_issues
    raw_issues=$(gh api "repos/$github_repo" --jq '.open_issues_count' 2>/dev/null || echo "0")
    DATA_OPEN_PRS=$(gh pr list -R "$github_repo" --state open --json number --jq 'length' 2>/dev/null || echo "0")
    if [ "$raw_issues" -ge "$DATA_OPEN_PRS" ] 2>/dev/null; then
      DATA_OPEN_ISSUES=$((raw_issues - DATA_OPEN_PRS))
    else
      DATA_OPEN_ISSUES=0
    fi
  fi

  DATA_LATEST_TAG=$(git -C "$path" describe --tags --abbrev=0 2>/dev/null || echo "")
  DATA_HEAD=$(git -C "$path" rev-parse --short HEAD 2>/dev/null || echo "?")

  if [ -n "$DATA_LATEST_TAG" ]; then
    DATA_COMMITS_AHEAD=$(git -C "$path" rev-list --count "${DATA_LATEST_TAG}..HEAD" 2>/dev/null || echo "0")
  else
    DATA_COMMITS_AHEAD=$(git -C "$path" rev-list --count HEAD 2>/dev/null || echo "0")
  fi
}

# ── Renderers ──

render_json_line() {
  local name="$1" github="$2" issues="$3" prs="$4" tag="$5" ahead="$6" head="$7"
  local tag_json="null"
  [ -n "$tag" ] && tag_json="\"$tag\""
  printf '{"name":"%s","github":"%s","open_issues":%d,"open_prs":%d,"latest_tag":%s,"commits_ahead":%d,"head":"%s"}' \
    "$name" "$github" "$issues" "$prs" "$tag_json" "$ahead" "$head"
}

render_pretty_line() {
  local name="$1" github="$2" issues="$3" prs="$4" tag="$5" ahead="$6" head="$7"
  local has_gh="$8"

  # Status icon
  local icon="${green}✓${reset}"
  [ "$prs" -gt 0 ] 2>/dev/null && icon="${yellow}⬥${reset}"
  [ "$ahead" -gt 10 ] 2>/dev/null && icon="${red}↑${reset}"

  printf "  ${icon} ${bold}%-18s${reset}" "$name"

  # GitHub activity
  if $has_gh; then
    if [ "$issues" -gt 0 ] || [ "$prs" -gt 0 ]; then
      printf " "
      [ "$issues" -gt 0 ] && printf "${red}issues:%d${reset} " "$issues"
      [ "$prs" -gt 0 ] && printf "${yellow}PRs:%d${reset}" "$prs"
    else
      printf " ${dim}clean${reset}"
    fi
  else
    printf " ${dim}(local)${reset}"
  fi

  # Tag vs HEAD
  if [ -n "$tag" ]; then
    if [ "$ahead" -eq 0 ]; then
      printf "  ${green}%s${reset}" "$tag"
    elif [ "$ahead" -le 5 ]; then
      printf "  ${yellow}%s+%d${reset}" "$tag" "$ahead"
    else
      printf "  ${red}%s+%d${reset}" "$tag" "$ahead"
    fi
  else
    printf "  ${dim}(no tag)${reset} %s commits" "$ahead"
  fi

  printf "\n"
}

# ── Single-repo detail renderer ──

render_single_detail() {
  local name="$1" path="$2"
  local github_repo
  github_repo=$(to_github_repo "${REPO_REMOTES[0]}")

  echo -e "${bold}Detail: $name${reset}"
  echo ""

  if [ -n "$github_repo" ]; then
    echo -e "  ${bold}Open PRs:${reset}"
    gh pr list -R "$github_repo" --state open \
      --json number,title,author,updatedAt \
      --jq '.[] | "    #\(.number) \(.title) (\(.author.login))"' 2>/dev/null \
      || echo "    (none)"
    echo ""

    echo -e "  ${bold}Open Issues:${reset}"
    gh issue list -R "$github_repo" --state open \
      --json number,title,author,updatedAt \
      --jq '.[] | "    #\(.number) \(.title) (\(.author.login))"' 2>/dev/null \
      || echo "    (none)"
    echo ""
  fi

  collect_repo_data 0
  render_pretty_line "$name" "$github_repo" "$DATA_OPEN_ISSUES" "$DATA_OPEN_PRS" \
    "$DATA_LATEST_TAG" "$DATA_COMMITS_AHEAD" "$DATA_HEAD" "$DATA_HAS_GITHUB"
  echo ""

  echo -e "  ${dim}Commits since tag:${reset}"
  if [ -n "$DATA_LATEST_TAG" ]; then
    git -C "$path" log --oneline "${DATA_LATEST_TAG}..HEAD" 2>/dev/null | head -15 | sed 's/^/    /'
  else
    git -C "$path" log --oneline -15 2>/dev/null | sed 's/^/    /'
  fi
}

# ── Main ──

if [ "$WORKSPACE_MODE" = "single" ]; then
  # Single repo: always show detail view
  if $flag_json; then
    collect_repo_data 0
    render_json_line "${REPO_NAMES[0]}" "$(to_github_repo "${REPO_REMOTES[0]}")" \
      "$DATA_OPEN_ISSUES" "$DATA_OPEN_PRS" "$DATA_LATEST_TAG" "$DATA_COMMITS_AHEAD" "$DATA_HEAD"
    echo
  else
    render_single_detail "${REPO_NAMES[0]}" "${REPO_PATHS[0]}"
  fi
  exit 0
fi

# ── Single repo detail mode (--repo flag) ──

if [ -n "$flag_repo" ]; then
  found_idx=-1
  for i in "${!REPO_NAMES[@]}"; do
    [ "${REPO_NAMES[$i]}" = "$flag_repo" ] && found_idx=$i && break
  done

  if [ "$found_idx" -eq -1 ]; then
    echo -e "${red}Repo not found: $flag_repo${reset}" >&2
    echo -e "Available: ${REPO_NAMES[*]}" >&2
    exit 1
  fi

  if $flag_json; then
    collect_repo_data "$found_idx"
    gh_repo=$(to_github_repo "${REPO_REMOTES[$found_idx]}")
    render_json_line "$flag_repo" "$gh_repo" "$DATA_OPEN_ISSUES" "$DATA_OPEN_PRS" \
      "$DATA_LATEST_TAG" "$DATA_COMMITS_AHEAD" "$DATA_HEAD"
    echo
  else
    echo -e "${bold}Detail: $flag_repo${reset}"
    echo ""

    gh_repo=$(to_github_repo "${REPO_REMOTES[$found_idx]}")
    if [ -n "$gh_repo" ]; then
      echo -e "  ${bold}Open PRs:${reset}"
      gh pr list -R "$gh_repo" --state open \
        --json number,title,author,updatedAt \
        --jq '.[] | "    #\(.number) \(.title) (\(.author.login))"' 2>/dev/null \
        || echo "    (none)"
      echo ""

      echo -e "  ${bold}Open Issues:${reset}"
      gh issue list -R "$gh_repo" --state open \
        --json number,title,author,updatedAt \
        --jq '.[] | "    #\(.number) \(.title) (\(.author.login))"' 2>/dev/null \
        || echo "    (none)"
      echo ""
    fi

    collect_repo_data "$found_idx"
    render_pretty_line "$flag_repo" "$gh_repo" "$DATA_OPEN_ISSUES" "$DATA_OPEN_PRS" \
      "$DATA_LATEST_TAG" "$DATA_COMMITS_AHEAD" "$DATA_HEAD" "$DATA_HAS_GITHUB"
    echo ""

    echo -e "  ${dim}Commits since tag:${reset}"
    if [ -n "$DATA_LATEST_TAG" ]; then
      git -C "${REPO_PATHS[$found_idx]}" log --oneline "${DATA_LATEST_TAG}..HEAD" 2>/dev/null | head -15 | sed 's/^/    /'
    else
      git -C "${REPO_PATHS[$found_idx]}" log --oneline -15 2>/dev/null | sed 's/^/    /'
    fi
  fi
  exit 0
fi

# ── Full dashboard ──

# Collect all data first (sequential to avoid race conditions)
declare -a ALL_ISSUES=() ALL_PRS=() ALL_TAGS=() ALL_AHEAD=() ALL_HEADS=() ALL_HAS_GH=() ALL_GH_REPOS=()

for i in "${!REPO_NAMES[@]}"; do
  collect_repo_data "$i"
  ALL_ISSUES+=("$DATA_OPEN_ISSUES")
  ALL_PRS+=("$DATA_OPEN_PRS")
  ALL_TAGS+=("$DATA_LATEST_TAG")
  ALL_AHEAD+=("$DATA_COMMITS_AHEAD")
  ALL_HEADS+=("$DATA_HEAD")
  ALL_HAS_GH+=("$DATA_HAS_GITHUB")
  ALL_GH_REPOS+=("$(to_github_repo "${REPO_REMOTES[$i]}")")
done

if $flag_json; then
  echo "["
  for i in "${!REPO_NAMES[@]}"; do
    [ "$i" -gt 0 ] && printf ","
    render_json_line "${REPO_NAMES[$i]}" "${ALL_GH_REPOS[$i]}" \
      "${ALL_ISSUES[$i]}" "${ALL_PRS[$i]}" "${ALL_TAGS[$i]}" \
      "${ALL_AHEAD[$i]}" "${ALL_HEADS[$i]}"
  done
  echo ""
  echo "]"
else
  echo -e "${bold}─────────────────────────────────────────────────────────────${reset}"
  echo -e "${bold}  $(workspace_name) Workspace Overview${reset}"
  echo -e "${bold}─────────────────────────────────────────────────────────────${reset}"
  echo ""

  for i in "${!REPO_NAMES[@]}"; do
    render_pretty_line "${REPO_NAMES[$i]}" "${ALL_GH_REPOS[$i]}" \
      "${ALL_ISSUES[$i]}" "${ALL_PRS[$i]}" "${ALL_TAGS[$i]}" \
      "${ALL_AHEAD[$i]}" "${ALL_HEADS[$i]}" "${ALL_HAS_GH[$i]}"
  done

  # Aggregate
  total_issues=0 total_prs=0 unreleased=0
  for i in "${!REPO_NAMES[@]}"; do
    total_issues=$((total_issues + ALL_ISSUES[$i]))
    total_prs=$((total_prs + ALL_PRS[$i]))
    [ "${ALL_AHEAD[$i]}" -gt 0 ] && unreleased=$((unreleased + 1))
  done

  echo ""
  echo -e "${bold}─────────────────────────────────────────────────────────────${reset}"
  printf "  ${bold}Total:${reset} %d repos" "${#REPO_NAMES[@]}"
  [ "$total_issues" -gt 0 ] && printf "  |  ${red}Issues: %d${reset}" "$total_issues"
  [ "$total_prs" -gt 0 ] && printf "  |  ${yellow}PRs: %d${reset}" "$total_prs"
  [ "$unreleased" -gt 0 ] && printf "  |  ${cyan}Unreleased: %d${reset}" "$unreleased"
  printf "\n"
  echo -e "${bold}─────────────────────────────────────────────────────────────${reset}"
fi
