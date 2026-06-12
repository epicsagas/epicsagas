---
name: git-workspace
description: "Git workspace manager — sync repos, bump versions, project health dashboard. Works in submodule monorepos, flat multi-repo, and single projects. Triggers: sync repos, pull all, bump version, git tags, overview, dashboard, project status."
---

# Git Workspace Manager

Manage git repositories in any workspace layout — submodule monorepo, flat multi-repo, or single project. Auto-detects workspace type from CWD.

$ARGUMENTS

## Actions

### sync — Fetch & pull all repos
When the user says "sync", "pull all", "sync repos":
```bash
bash "$(find ~/.claude/plugins/cache -path '*/git-workspace/scripts/sync.sh' -print -quit 2>/dev/null || echo '.claude/skills/git/scripts/sync.sh')"
```
Flags: `-v` verbose, `-n` dry-run, `--root <path>` override workspace root

### bump — Version bump, tag & push
When the user mentions a version bump with a target repo and type (major/minor/patch):
```bash
bash "$(find ~/.claude/plugins/cache -path '*/git-workspace/scripts/bump.sh' -print -quit 2>/dev/null || echo '.claude/skills/git/scripts/bump.sh')" <repo-name> <major|minor|patch>
bash "$(find ~/.claude/plugins/cache -path '*/git-workspace/scripts/bump.sh' -print -quit 2>/dev/null || echo '.claude/skills/git/scripts/bump.sh')" all <major|minor|patch>
```

Before bumping, ALWAYS:
1. Show the current latest tag for the target repo(s): `git -C <repo> describe --tags --abbrev=0`
2. Show what the new version will be
3. Ask the user to confirm before executing the bump

### overview — Project health dashboard
When the user says "overview", "dashboard", "project status", "issues/PRs", "release needed":
```bash
bash "$(find ~/.claude/plugins/cache -path '*/git-workspace/scripts/overview.sh' -print -quit 2>/dev/null || echo '.claude/skills/git/scripts/overview.sh')"
```

Single repo detail (lists PR titles, issue titles, commits since tag):
```bash
bash "$(find ~/.claude/plugins/cache -path '*/git-workspace/scripts/overview.sh' -print -quit 2>/dev/null || echo '.claude/skills/git/scripts/overview.sh')" --repo <name>
```

JSON output for programmatic use:
```bash
bash "$(find ~/.claude/plugins/cache -path '*/git-workspace/scripts/overview.sh' -print -quit 2>/dev/null || echo '.claude/skills/git/scripts/overview.sh')" --json
```

Shows per-repo:
- Open issues & PRs (via `gh` CLI)
- Latest tag vs HEAD commit count (unreleased commits)
- 🔴 red `↑` = 10+ unreleased, 🟡 yellow `⬥` = open PRs, 🟢 green `✓` = clean

### tags — Show latest tags
When the user asks about current versions/tags:
```bash
for dir in */; do
  tag=$(git -C "$dir" describe --tags --abbrev=0 2>/dev/null) && echo "$(basename $dir): $tag" || echo "$(basename $dir): (no tags)"
done
```

### commit — Commit changes
Use the git-cc skill or epic:commit for commits. Do NOT handle commits in this skill.

## Rules
- Always confirm before executing destructive actions (bump, push)
- Never force-push
