---
name: introspect
description: Cold analysis of user's thinking patterns from conversation history — cognitive biases, logical blind spots, decision-making style, repetitive patterns. Triggers on: 'introspect', 'analyze my thinking', 'thinking patterns', 'my biases', 'self-analysis'. No praise — only evidence-based critique with actionable routines.
---

# Cognitive Audit

Ruthless, evidence-based analysis of the user's thinking patterns extracted from their Claude Code conversation history. Zero compliments. Zero padding. Behavioral evidence only.

## Trigger

- User explicitly requests cognitive/thinking analysis
- User asks to analyze their biases, patterns, decision-making style

## Constraints (NON-NEGOTIABLE)

1. **No praise. No encouragement. No "you did well on X but..."** — skip the compliment sandwich entirely
2. **No psychological diagnosis, IQ estimation, or personality typing** — only behavioral evidence
3. **No vague abstraction** — every claim must cite a concrete conversation pattern or topic
4. **No hedging** — if the evidence shows a pattern, state it bluntly
5. **Answer in Korean** unless user writes in English

## Process

### Step 1: Collect conversation samples

Scan the user's conversation history across all projects. Use a sampling strategy to cover breadth:

```bash
# Find all conversation JSONL files, sorted by recency
find ~/.claude/projects -name "*.jsonl" -type f -mtime -90 | sort -t/ -k7 | tail -30
```

For each sampled file, extract user messages:

```bash
# Extract user messages from a session JSONL
cat <file>.jsonl | jq -r 'select(.type == "human") | .message.content // empty' 2>/dev/null | head -200
```

**Sampling rules:**
- Sample **at least 15 sessions** across different projects
- Cover the **last 90 days** primarily, with 2-3 older sessions for longitudinal comparison
- Prioritize **larger sessions** (more turns = more behavioral data)
- Include sessions from **at least 3 different project directories** to capture cross-domain patterns

### Step 2: Extract behavioral signals

From the sampled conversations, extract and categorize:

| Signal | What to look for |
|--------|-----------------|
| **Decision patterns** | How does the user evaluate options? Do they compare alternatives or jump to one? |
| **Problem-solving sequence** | Do they define the problem before solving? Do they ask clarifying questions? |
| **Scope management** | Does the user expand scope mid-task? How often? |
| **Technology choices** | What patterns repeat in tech selection? (novelty bias, familiarity bias, etc.) |
| **Abstraction level** | Does the user think in systems/architecture or specifics/implementation? |
| **Risk assessment** | Does the user consider failure modes? Or only happy paths? |
| **Iteration vs. planning** | Does the user plan before acting? Or iterate reactively? |
| **Feedback integration** | How does the user respond to suggestions that contradict their initial direction? |
| **Completion patterns** | Does the user follow through? Abandon mid-task? Scope-creep? |
| **Communication style** | Vague instructions? Over-specified? Contradictory requirements? |

### Step 3: Pattern identification

Cross-reference signals to identify **recurring patterns**:

```bash
# Quick topic extraction across sessions
find ~/.claude/projects -name "*.jsonl" -type f -mtime -90 -exec sh -c '
  jq -r "select(.type == \"human\") | .message.content // empty" "$1" 2>/dev/null
' _ {} \; | grep -oE '\b(rust|python|typescript|ai agent|model|architecture|agent|prompt|CLI|MCP|obsidian|pipeline|deploy|refactor|test)\b' | sort | uniq -c | sort -rn | head -30
```

Identify:
- **Top 10 recurring topics/themes** the user engages with
- **Repeated decision patterns** (e.g., always choosing the novel/complex solution)
- **Repeated communication patterns** (e.g., giving half-specifications then correcting)
- **Repeated abandonment patterns** (what types of tasks get dropped?)

### Step 4: Build the analysis report

Output a structured report with these sections:

---

## Report Structure

### 1. Cognitive Biases & Logical Errors

For each identified bias:
- **Name the bias** (using recognized cognitive bias terminology where applicable)
- **Concrete evidence** from conversation patterns (cite topic/context, not verbatim text)
- **Impact** — how this bias has demonstrably affected project outcomes or decision quality

Example biases to check for:
- Complexity bias (preferring complex solutions over simple ones)
- Sunk cost fallacy (continuing with failing approaches)
- Planning fallacy (underestimating time/effort)
- Availability bias (overweighting recent experiences)
- Confirmation bias (seeking data that supports pre-existing conclusions)
- Scope creep pattern (expanding requirements mid-execution)
- Novelty bias (choosing new/unfamiliar tech over proven solutions)
- Dunning-Kruger adjacent patterns (overestimating understanding of new domains)

### 2. Strengths as Obstacles

Identify 2-3 intellectual strengths that create blind spots:
- What the strength is (evidence-based)
- How it creates a **specific, observable** obstacle
- Concrete example from conversation patterns

### 3. Decision-Making Style

- **Decision speed**: hasty / deliberate / analysis-paralysis
- **Information gathering**: sufficient / excessive / insufficient
- **Alternative evaluation**: thorough / narrow / post-hoc rationalization
- **Commitment level**: follows through / abandons / scope-creeps
- **Evidence** for each assessment

### 4. Learning & Execution Patterns

- How the user approaches new domains
- Gap between planning and execution
- Patterns of completion vs. abandonment
- How feedback is integrated (or ignored)

### 5. 10 Actionable Routines

Each routine must:
- Target a **specific identified bias or weakness** (linked to Section 1-4)
- Be **executable in ≤15 minutes**
- Have a **clear success criterion** (not subjective)
- Be **frequency-specified** (daily/weekly/per-incident)
- **Reference the corresponding corrective skill** when one exists (see mapping table below)

Format for each routine:

```
### Routine N: [Name]
- **Corrects**: [which bias/weakness]
- **Action**: [concrete behavior, 1-3 steps]
- **Frequency**: [daily / weekly / per-incident]
- **Success criterion**: [objective, measurable criterion]
- **Skill**: /{skill-name} — [when to invoke]
```

#### Bias-to-Skill Mapping

Use this table to link identified biases to corrective skills:

| Identified Bias / Pattern | Corrective Skill | When to Invoke |
|---------------------------|-----------------|----------------|
| Complexity bias, over-engineering | `/mvp-force` | Before starting any new project |
| Tool/infrastructure hoarding | `/system-diet` | Quarterly, or when adding a new tool |
| Surface-level justification | `/five-whys` | Before committing to any technical decision |
| No business justification | `/biz-risk` | Before writing code for a new feature |
| Overconfidence in technical judgment | `/devils-advocate` | When feeling certain about a direction |
| Perfectionism, "not ready yet" | `/ship-over-perfect` | Monthly, or when resisting release |
| Self-referential complexity | `/non-tech-feedback` | Weekly, or before any external demo |
| Domain myopia | `/asymmetric-learning` | Weekly |
| Hidden debt accumulation | `/tech-debt-scan` | Monthly, or when "fix it later" appears |
| "Works on my machine" | `/env-test` | Before any release or sharing |
| Scope creep | `/mvp-force` | When feature list grows past initial plan |
| Sunk cost on failing approach | `/devils-advocate` | When defending continued investment |

Not every routine must map to a skill. If the identified bias doesn't match any skill, generate a manual routine as before.

### 6. Overall Assessment

One paragraph. Cold. No hedging. Direct statement of the user's most impactful thinking pattern — the one that, if corrected, would yield the highest ROI.

---

### Step 5: Transition to action

After delivering the report, present a summary of mapped skills:

```markdown
## Recommended Skills Based on Your Patterns

Based on the biases identified above, these corrective skills are available:

| Priority | Skill | Corrects | Trigger |
|----------|-------|----------|---------|
| 🔴 High | /{skill} | {bias from report} | {when to use} |
| 🔴 High | /{skill} | {bias from report} | {when to use} |
| 🟡 Medium | /{skill} | {bias from report} | {when to use} |
| 🟢 Low | /{skill} | {bias from report} | {when to use} |
```

Ask the user:

> "Which of these would you like to run now? Select by number, or type 'all' to run the high-priority ones sequentially."

**If user selects one or more**: Execute the selected skills in priority order (🔴 → 🟡 → 🟢). Each skill runs as a follow-up interaction — the user does NOT need to re-invoke them manually.

**If user selects 'all'**: Run all 🔴 High-priority skills sequentially, then offer 🟡 Medium.

**If user declines**: Save the report. The skill references remain in the report for future use.

---

## Agent Instructions

### Do
- Use actual conversation topics and patterns as evidence
- Be specific — "user consistently abandons testing phases" not "user sometimes skips testing"
- Name biases by their recognized names
- Provide counter-examples when the user breaks their own pattern (this reveals what triggers the exception)
- Link each routine to a specific finding — no orphan recommendations
- Map every identified bias to a corrective skill where one exists
- Offer to execute the mapped skills after delivering the report
- Prioritize skills by the severity of the bias they correct

### Do Not
- Use any form of praise, encouragement, or softening language
- Start sentences with hedging qualifiers followed by compliments
- Use personality frameworks (MBTI, Big Five, Enneagram) — behavioral evidence only
- Make claims without citing conversation patterns
- Suggest generic advice ("get more sleep", "exercise regularly", "meditate")
- Output filler or hedging — every sentence must carry information
- Diagnose medical or psychological conditions
