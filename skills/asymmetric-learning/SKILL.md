---
name: asymmetric-learning
description: "Recommends and structures learning from a field completely outside the user's expertise. Generates a weekly reading plan with summary template for cross-pollination of ideas. Triggers on: 'learn something new', 'asymmetric learning', 'weekly learning', 'outside my field', 'cross-pollination'."
---

# Asymmetric Learning — Cross-Domain Knowledge Injection

Force weekly engagement with a field completely outside the user's expertise. Innovation happens at the intersection of domains, not in the depth of one.

## When to Trigger

**Auto-trigger**: User has been working exclusively in their primary domain (Rust, AI agents, systems engineering) for >2 weeks without mentioning any other field.

**Explicit** (`/asymmetric-learning`): User wants a reading recommendation outside their field, or wants to structure their cross-domain learning.

## Constraints (NON-NEGOTIABLE)

1. **Zero overlap with user's primary domain** — if it relates to programming, AI, or systems engineering, it doesn't count
2. **One book per week** — not articles, not papers, not blog posts. A complete book.
3. **Structured summary required** — not "I read it", but a specific template filled out
4. **Actionable extraction** — what idea from this field applies to the user's work?
5. **Answer in Korean** unless user writes in English

## Process

### Step 1: Domain selection

Generate 3 book recommendations from 3 different non-technical fields. Select from:

| Domain | Why it matters for engineers |
|--------|------------------------------|
| **Behavioral psychology** | Decision-making patterns, cognitive biases, habit formation |
| **Marketing / positioning** | How products are perceived, not just how they work |
| **Organizational behavior** | Team dynamics, communication failure modes |
| **Negotiation / sales** | Understanding what people actually want vs. what they say |
| **Design thinking** | User-centered problem solving beyond technical optimization |
| **Economics / game theory** | Incentive structures, system-level thinking |
| **Storytelling / narrative** | How to communicate complex ideas simply |
| **Biology / evolution** | Adaptation, emergence, complex systems |
| **Education / pedagogy** | How people learn, which applies to documentation and onboarding |

Present 3 options from different domains. User picks one.

### Step 2: Reading plan

Generate a 7-day reading schedule:

```markdown
# Weekly Reading Plan

## Book: {title} by {author}
## Domain: {domain}

| Day | Task |
|-----|------|
| Mon | Read chapters {N-N}. Note: key concepts only. |
| Tue | Read chapters {N-N}. Note: one idea that connects to your work. |
| Wed | Read chapters {N-N}. Note: what surprises you. |
| Thu | Read chapters {N-N}. Note: what contradicts your assumptions. |
| Fri | Read chapters {N-N}. Note: actionable insight. |
| Sat | Complete summary template. |
| Sun | Write cross-pollination note: how does this apply to {user's project}? |
```

### Step 3: Summary template

Provide the template to fill after reading:

```markdown
---
book: {title}
author: {author}
domain: {domain}
date_completed: {ISO-8601}
---

# Book Summary: {title}

## One-sentence thesis
{What is the book's core argument?}

## 3 key ideas
1. {idea}: {one-paragraph explanation}
2. {idea}: {one-paragraph explanation}
3. {idea}: {one-paragraph explanation}

## Surprising insight
{What challenged your existing beliefs?}

## Cross-pollination
{How does one idea from this book apply to your current work/project?}

## Concrete action
{One specific thing you will do differently based on this book}
```

### Step 4: PARA integration

Guide the user to save the summary:

```bash
# Save to PARA structure
# Projects/ if directly applicable to active work
# Areas/ if general professional development
# Resources/ if reference material for future use
```

### Step 5: Record

```bash
mkdir -p asymmetric-learning
```

Write the reading plan to `asymmetric-learning/PLAN-{timestamp}.md`.

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|--------|----------|-----------|
| "I don't have time to read" | You spent 40 hours this week on technical work. 3 hours for a book is 7.5%. | Read 30 min/day. That's a book a week. |
| "This won't help my work" | You don't know that. That's the point. | The connections become obvious after reading, not before. |
| "I prefer technical books" | Your technical depth is already high. That's not the bottleneck. | Read what you're BAD at, not what you're good at. |
| "I learn from articles instead" | Articles are pre-digested thinking. Books force sustained engagement. | One book > ten articles. Depth beats breadth. |
| "I'll do it when I'm less busy" | You will never be less busy. | Schedule it now. Same time every week. |

## Evidence Required

- [ ] Book selected from non-technical domain
- [ ] 7-day reading plan generated
- [ ] Summary template provided
- [ ] Book read within 7 days
- [ ] Summary completed using template
- [ ] Cross-pollination note written
- [ ] Summary saved to PARA structure

## Red Flags

- User consistently picks books adjacent to their field (avoiding discomfort)
- Summary is superficial ("it was interesting")
- Cross-pollination note can't connect to real work (didn't engage deeply)
- "I'll start next week" repeated multiple weeks
- User abandons the book mid-week without replacement

## Agent Instructions

### Do
- Pick genuinely non-technical books — no "soft engineering" books
- Make the reading plan concrete with chapter assignments
- Follow up on completion — ask for the summary
- Help connect ideas across domains when the user struggles
- Rotate domains — don't recommend the same domain twice in a row

### Do Not
- Recommend books about programming, AI, or systems
- Accept "I read the summary online" as completion
- Let the user skip the cross-pollination step
- Recommend books the user has already read
- Generate more than 3 options (decision paralysis)
