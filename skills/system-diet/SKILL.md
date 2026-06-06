---
name: system-diet
description: "Forces removal of 20% of active tools, plugins, and automation pipelines to prevent complexity stagnation. Identifies unused, redundant, or low-value system components. Triggers on: 'system diet', 'too many tools', 'declutter', 'simplify setup', 'tool audit'."
---

# System Diet — Forced Complexity Reduction

Remove 20% of active tools, plugins, and automation pipelines every quarter. Systems that don't shrink rot from the inside.

## When to Trigger

**Auto-trigger**: User adds a new tool/plugin without removing an old one, or when tool configuration files grow beyond a manageable size.

**Explicit** (`/system-diet`): User wants to audit their toolchain, simplify their setup, or feels their system is slowing them down.

## Constraints (NON-NEGOTIABLE)

1. **20% minimum removal** — if you can't find 20% to cut, you're not looking hard enough
2. **No "I might need it"** — if you haven't used it in 30 days, it's gone
3. **One in, one out** — for every new tool added, one must be removed
4. **Measure before cutting** — document what each tool actually does for you
5. **Answer in Korean** unless user writes in English

## Process

### Step 1: Inventory

Scan the user's tool ecosystem. Collect from:

```bash
# Obsidian plugins
cat .obsidian/community-plugins.json 2>/dev/null

# Claude Code plugins and settings
cat ~/.claude/settings.json 2>/dev/null | jq '.enabledPlugins'

# Homebrew/cargo packages
brew list 2>/dev/null | wc -l
cargo install --list 2>/dev/null | grep -c '^-'

# Shell aliases/functions
grep -c 'alias\|function' ~/.zshrc 2>/dev/null

# Automation scripts
find ~ -name "*.sh" -path "*/bin/*" 2>/dev/null | wc -l
```

### Step 2: Usage audit

For each component, classify:

| Usage Level | Criteria | Action |
|-------------|----------|--------|
| **Active** | Used in the last 7 days | KEEP |
| **Situational** | Used in the last 30 days | PROBATION — justify or cut |
| **Dormant** | Not used in 30+ days | CUT |
| **Forgotten** | User doesn't remember installing it | CUT immediately |

### Step 3: Value classification

For each ACTIVE and SITUATIONAL tool, ask:

> "What concrete outcome does this produce that you couldn't achieve without it?"

| Value Level | Criteria | Action |
|-------------|----------|--------|
| **Critical** | Cannot do core work without it | KEEP |
| **Accelerator** | Saves measurable time daily | KEEP |
| **Convenience** | Nice to have, saves minor effort | Candidate for CUT |
| **Ritual** | Used out of habit, not necessity | CUT |

### Step 4: The 20% cut

Calculate: `total_components × 0.2 = minimum_removals`

Select cuts from this priority:
1. Forgotten components (free cuts)
2. Dormant components (free cuts)
3. Ritual-value components (easy cuts)
4. Convenience-value components on probation (harder cuts)

If forgotten + dormant < 20%, cut into convenience-value tools until the 20% threshold is met.

### Step 5: Record

```bash
mkdir -p system-diet
```

Write to `system-diet/AUDIT-{timestamp}.md`:

```markdown
---
date: {ISO-8601}
total_components: {N}
removed: {N} ({percentage}%)
---

# System Diet Audit: {date}

## Inventory
| Component | Usage | Value | Decision |
|-----------|-------|-------|----------|
| {name} | {active/situational/dormant/forgotten} | {critical/accelerator/convenience/ritual} | {KEEP/CUT/PROBATION} |

## Removed
- {component}: {reason for removal}

## Kept (with justification)
- {component}: {why it survived}

## New Rules
- {any one-in-one-out policies established}
```

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|--------|----------|-----------|
| "I might need it someday" | In 30 days you didn't. In 30 more you won't. | Cut it. If you truly need it, reinstalling takes 2 minutes. |
| "It doesn't hurt to keep it" | Every unused tool adds cognitive load, maintenance burden, and config noise. | Count the total. Then ask if 100 things is better than 80. |
| "This one is special" | They're all special. That's why you have so many. | Apply the same criteria. No exceptions. |
| "The setup took hours" | Sunk cost. Keeping it costs attention forever. | The hours are spent regardless. Future attention is the real cost. |
| "I just organized it perfectly" | Perfect organization of unused tools is still waste. | Organize the 80% you actually use. |

## Evidence Required

- [ ] Full inventory of tools/plugins/pipelines
- [ ] Usage classification for each component
- [ ] Value classification for active components
- [ ] 20% minimum removal achieved
- [ ] Each removal justified
- [ ] Audit recorded to file

## Red Flags

- Can't reach 20% removal (not being honest about usage)
- Everything is classified as "critical" (no discipline)
- User wants to "pause" removals instead of committing
- "I'll use it more next month" for dormant tools
- Inventory itself is overwhelming (already a sign of bloat)

## Agent Instructions

### Do
- Count components ruthlessly — the number itself is diagnostic
- Classify honestly — most "convenience" tools are actually "ritual"
- Make the 20% math explicit and enforce it
- Celebrate removals as progress, not loss
- Schedule the next quarterly diet

### Do Not
- Let everything be "critical"
- Accept "I'll think about it" as a decision
- Skip dormant/forgotten components in the count
- Let the user reclassify things to avoid cutting
- Forget to schedule the next audit
