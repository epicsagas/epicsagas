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

Format for each routine:

```
### Routine N: [Name]
- **Corrects**: [which bias/weakness]
- **Action**: [concrete behavior, 1-3 steps]
- **Frequency**: [daily / weekly / per-incident]
- **Success criterion**: [objective, measurable criterion]
```

### 6. Overall Assessment

One paragraph. Cold. No hedging. Direct statement of the user's most impactful thinking pattern — the one that, if corrected, would yield the highest ROI.

---

## Agent Instructions

### Do
- Use actual conversation topics and patterns as evidence
- Be specific — "user consistently abandons testing phases" not "user sometimes skips testing"
- Name biases by their recognized names
- Provide counter-examples when the user breaks their own pattern (this reveals what triggers the exception)
- Link each routine to a specific finding — no orphan recommendations

### Do Not
- Use any form of praise, encouragement, or softening language
- Start sentences with hedging qualifiers followed by compliments
- Use personality frameworks (MBTI, Big Five, Enneagram) — behavioral evidence only
- Make claims without citing conversation patterns
- Suggest generic advice ("get more sleep", "exercise regularly", "meditate")
- Output filler or hedging — every sentence must carry information
- Diagnose medical or psychological conditions
