---
name: tech-debt-scan
description: "Scans codebase for technical debt markers (TODO, FIXME, HACK, XXX) and quantifies risk by severity, age, and blast radius. Generates a prioritized remediation plan. Triggers on: 'tech debt', 'TODO scan', 'debt audit', 'code hygiene', 'fixme', 'technical debt'."
---

# Tech Debt Scan — Debt Visibility Engine

Make hidden technical debt visible, quantified, and prioritized. Debt that isn't tracked doesn't get paid — it compounds.

## When to Trigger

**Auto-trigger**: Codebase has >10 TODO/FIXME/HACK comments, or user says "I'll fix it later" more than twice in a session.

**Explicit** (`/tech-debt-scan`): User wants to audit their codebase for accumulated debt, or feels the codebase is becoming fragile.

## Constraints (NON-NEGOTIABLE)

1. **Scan everything** — no directory exemptions, no "that's third-party code" excuses
2. **Age matters** — a TODO from 6 months ago is worse than one from yesterday
3. **Blast radius matters** — debt in a hot path is worse than debt in a utility function
4. **Quantify risk** — every debt item gets a severity rating, not just a label
5. **Answer in Korean** unless user writes in English

## Process

### Step 1: Scan

Run the debt scanner across the codebase:

```bash
# Count debt markers by type
echo "=== Debt Count by Type ==="
grep -rn 'TODO\|FIXME\|HACK\|XXX\|WORKAROUND\|TEMP\|KLUDGE' --include='*.{rs,ts,js,py,go,rb,java,swift,kt}' . 2>/dev/null | \
  awk -F: '{print $1}' | sed "s/.*'\(TODO\|FIXME\|HACK\|XXX\|WORKAROUND\|TEMP\|KLUDGE\)'.*/\1/" | sort | uniq -c | sort -rn

# List all debt items with file, line, and content
echo "=== Full Debt Inventory ==="
grep -rn 'TODO\|FIXME\|HACK\|XXX\|WORKAROUND\|TEMP\|KLUDGE' --include='*.{rs,ts,js,py,go,rb,java,swift,kt}' . 2>/dev/null
```

### Step 2: Classify

For each debt item, determine:

| Dimension | Classification |
|-----------|---------------|
| **Type** | `TODO` (planned), `FIXME` (broken), `HACK` (working but wrong), `XXX` (dangerous), `WORKAROUND` (external dependency) |
| **Severity** | 🔴 **High** — causes data loss, security vulnerability, or production failure; 🟡 **Medium** — causes bugs under edge cases or slows development; 🟢 **Low** — cosmetic, non-critical optimization |
| **Age** | Recent (<30d), Stale (30-90d), Ancient (>90d) |
| **Blast radius** | Hot path (called on every request/event), Warm path (called regularly), Cold path (rarely executed) |

Priority formula:
```
priority = severity × (1 + age_multiplier) × blast_radius

Where:
  severity: High=3, Medium=2, Low=1
  age_multiplier: Recent=0, Stale=0.5, Ancient=1.0
  blast_radius: Hot=3, Warm=2, Cold=1
```

### Step 3: Risk report

Generate the debt report:

```markdown
# Tech Debt Report: {project}

## Summary
- **Total items**: {N}
- **🔴 High severity**: {N} ({percentage}%)
- **🟡 Medium severity**: {N} ({percentage}%)
- **🟢 Low severity**: {N} ({percentage}%)
- **Ancient debt (>90 days)**: {N}

## Top 10 by Priority Score
| # | File:Line | Type | Severity | Age | Blast Radius | Score | Description |
|---|-----------|------|----------|-----|--------------|-------|-------------|
| 1 | {path}:{line} | {type} | {🔴/🟡/🟢} | {age} | {hot/warm/cold} | {score} | {debt text} |
...

## Debt Hotspots (files with most debt)
| File | Count | Highest Severity |
|------|-------|-----------------|
| {path} | {N} | {severity} |

## Recommended Remediation
{Top 3 items to fix this week, with estimated effort}
```

### Step 4: Action plan

Generate a weekly remediation plan:

```markdown
## This Week's Debt Payment
1. **{debt item}** — {effort estimate} — {why it's first}
2. **{debt item}** — {effort estimate} — {why it's second}
3. **{debt item}** — {effort estimate} — {why it's third}

## Debt Trend
{Compare to previous scan if available — increasing or decreasing?}
```

### Step 5: Record

```bash
mkdir -p tech-debt-scan
```

Write to `tech-debt-scan/SCAN-{timestamp}.md`.

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|--------|----------|-----------|
| "I'll fix it when I refactor" | The refactor has been "next month" for 6 months. | Fix it now, or document why it can't be fixed now. |
| "It's not hurting anyone" | Until it does. Then it's an emergency fix at 2am. | Pay the debt on your schedule, not the bug's schedule. |
| "There are only a few TODOs" | Count them. You might be surprised. | Run the scan. The number is the number. |
| "The tests pass" | Tests test expected behavior. Debt is unexpected behavior waiting to happen. | Debt isn't about passing tests. It's about maintainability. |
| "I wrote that TODO for a reason" | Yes, to remind you to fix it later. It IS later. | Read what you wrote. Decide: fix it or delete the comment. |

## Evidence Required

- [ ] Full codebase scan completed
- [ ] Every debt item classified (type, severity, age, blast radius)
- [ ] Priority scores calculated
- [ ] Top 10 items identified
- [ ] Weekly remediation plan generated
- [ ] Scan recorded to file

## Red Flags

- Zero debt found (either the scan failed or the codebase is new)
- All debt classified as "low severity" (not being honest)
- More than 50 TODO items (systemic underinvestment in cleanup)
- Ancient debt in hot-path code ( ticking time bomb)
- User wants to "batch fix" everything instead of prioritizing

## Agent Instructions

### Do
- Count accurately — the number is data, not judgment
- Prioritize ruthlessly — high severity + hot path + ancient = fix NOW
- Track trends over time — is debt growing or shrinking?
- Be specific about remediation effort (hours, not "quick fix")
- Follow up on weekly remediation commitments

### Do Not
- Undercount by skipping directories or file types
- Let all debt be classified as "low"
- Generate a remediation plan larger than 3 items per week
- Accept "I'll do it all this weekend" as a plan
- Skip the blast radius analysis (it changes priority dramatically)
