---
name: discover
description: "Problem discovery for individuals, teams, and startups. Reframes vague ideas, solution-first thinking, and systemic complaints into structured problem definitions. Triggers on: 'discover', 'problem discovery', 'define the problem', 'what should we build', 'unclear requirements'."
---

# Discover — Problem Discovery

Help the user articulate **the real problem** before jumping to solutions. No spec without a problem statement.

## When to Trigger

**Auto-trigger**: Request lacks clear problem/goal, names a solution without why, lists symptoms without root cause, says "I don't know where to start", or is so broad it could mean 3+ things.

**Explicit** (`/discover`): User wants formal problem exploration for a new project/feature, re-exploration of a prior problem, or team alignment on "what are we solving?"

## Process

### Step 1: Listen

Repeat the request back. Ask: "Is that the core, or is there more?" Categorize:

| Category | Signal | Example |
|----------|--------|---------|
| Solution-first | Names tech/approach first | "Add Redis caching", "Build an app" |
| Feature-no-context | Describes output, not why | "Build a dashboard", "Need a landing page" |
| Systemic complaint | Broad negative without specifics | "Everything is slow", "Customers aren't coming" |
| Vague ambition | Goal with no boundaries | "Make it better", "Want to grow" |
| Clear problem | Observable gap stated | "Mobile payment failure rate is 12%" |

### Step 2: Probe

Select technique by category. **Max 3 questions per round, max 3 rounds**. If user can't answer or says "not sure", proceed to Frame with what you have.

| User signal | Technique | Core question |
|---|---|---|
| Names a solution | **5 Whys** | "What's happening that makes you need this?" → repeat, max 5 levels |
| Feature without why | **JTBD** | "What situation makes you need this? What does 'done' look like?" |
| "Everything is broken" | **Fishbone** | "Which area: People / Process / Technology / Data / Environment?" |
| Vague or contradictory | **Socratic** | "What specifically do you mean by 'X'?" |
| Vision, no path | **Done looks like** | "When this works perfectly, what do you see?" |
| Uncertain assumptions | **Assumption map** | "What must be true for this to work?" |

Extract from JTBD: "When [situation], I want [motivation], so I can [outcome]."

Skip round 3 if 2 rounds give enough to frame.

### Step 3: Frame

Synthesize into a structured problem statement:

> **[Who]** experiences **[observable problem]** when **[trigger condition]**, resulting in **[quantified impact]**. The desired state is **[measurable outcome]**.

Include: root cause / job story, constraints (timeline, resources, scale), assumptions (certain/uncertain), out-of-scope boundaries.

Show to user. Ask: "Does this capture the problem accurately?"

### Step 4: Save

```bash
mkdir -p discover
```

Write to `discover/PROBLEM-{timestamp}.md`. One problem per file — if multiple emerge, address sequentially.

### Step 5: Transition

"Problem defined. Next: execution plan, deeper exploration, or uncover more problems."

If user identifies additional problems, loop back to Step 2.

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|--------|----------|-----------|
| "Just start building" | Building without a problem is expensive guessing. | 5 minutes of framing saves hours of rework. |
| "The problem is obvious" | Then you'd have a spec, not a vague request. | Write it. If obvious, takes 30 seconds. |
| "No time for questions" | You have less time to build the wrong thing. | 2 focused rounds, not 10 open-ended ones. |
| "I already told you" | You told a solution. The problem is *why* you need it. | One "why" question. If answer reveals it, proceed. |
| "Figure it out from the code" | Code shows what exists, not what's missing or why it hurts. | Combine code exploration with user context. |
| "Let me show you the bug" | A bug is a symptom. Fixing symptoms is whack-a-mole. | Trace to root cause before jumping to fix. |

## Evidence Required

- [ ] Structured problem statement (Who / When / Problem / Impact / Desired state)
- [ ] Root cause or job story identified
- [ ] At least 1 measurable success criterion
- [ ] User confirmed the frame
- [ ] Scope boundaries stated
- [ ] Constraints and assumptions documented

## Red Flags

- Jumping to solutions/code during discovery
- >3 questions per round (overwhelming)
- >3 rounds without framing attempt (analysis paralysis)
- Ignoring "I'm not sure" — that IS information
- Producing unconfirmed problem statements
- Confusing symptoms with root causes
- Overly broad framing ("improve the system")
- Skipping discovery for non-trivial ambiguous work

## Output Format

`discover/PROBLEM-{timestamp}.md`:

```markdown
---
status: framed
created: {ISO-8601}
context: {one-line summary}
---

# Problem: {title}

## Problem Statement
{Who} experiences {observable problem} when {trigger condition}, resulting in {quantified impact}. The desired state is {measurable outcome}.

## Root Cause / Job Story
{5 Whys chain or JTBD job story}

## Constraints
- Timeline: {when needed}
- Resources: {stack, team, budget}
- Scale: {expected users, traffic, data}
- Compatibility: {existing system integration}

## Assumptions
- {assumption} — certain / uncertain

## Out of Scope
- {what this does NOT cover}
```
