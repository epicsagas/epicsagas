---
name: non-tech-feedback
description: "Generates a plain-language project explanation for non-technical audiences and collects comprehension gaps. Identifies complexity that shouldn't exist in the product itself. Triggers on: 'explain simply', 'for non-tech', 'mom test', 'plain language', 'too complex to explain'."
---

# Non-Tech Feedback — External Comprehension Gate

Translate the current project into language a non-technical person can understand. The parts they can't understand are the parts that are probably over-engineered.

## When to Trigger

**Auto-trigger**: Project description contains >3 layers of technical abstraction, or the user struggles to explain what they're building without technical terms.

**Explicit** (`/non-tech-feedback`): User wants to prepare for a pitch, simplify their product, or find unnecessary complexity.

## Constraints (NON-NEGOTIABLE)

1. **Zero technical terms** in the plain-language version — no "API", "pipeline", "agent", "vector", "RAG"
2. **Real audience** — the user must present this to an actual non-technical person within 7 days
3. **Confusion = complexity signal** — if a non-tech person can't understand it, the product is too complex
4. **Answer in Korean** unless user writes in English

## Process

### Step 1: Project translation

Ask the user to describe their project. Then generate a plain-language version using this template:

> **{Project name}** helps **{who}** solve **{what problem}** by **{how, in everyday terms}**.
>
> Example: "Wavexa helps music lovers enjoy better sound quality by cleaning up audio files automatically."

Rules for translation:
- **Who**: A specific person, not a segment ("my friend who likes music" not "audiophile market")
- **What problem**: A pain they feel, not a technical gap ("songs sound bad on good headphones" not "audio quantization noise")
- **How**: An action anyone understands ("cleans up", "organizes", "finds", "connects")

### Step 2: Comprehension test script

Generate a script the user can use with a real person:

```markdown
## Comprehension Test Script

### Opening
"I'm working on a project and I want to make sure I can explain it clearly. Can I describe it to you and tell me what's unclear?"

### Pitch
{plain-language description from Step 1}

### Questions to ask
1. "What do you think this does?"
2. "Who do you think would use this?"
3. "Would you use this? Why or why not?"
4. "What's confusing about what I just said?"
5. "If you had to explain this to someone else, how would you say it?"
```

### Step 3: Gap analysis template

After the user conducts the test, help them analyze:

| Non-tech response | What it reveals | Action |
|-------------------|----------------|--------|
| Gets the core idea immediately | Product concept is clear | ✅ Good — focus on execution |
| Understands the problem, not the solution | Solution is overcomplicated | Simplify the "how" |
| Doesn't understand the problem | Building for yourself, not users | Validate the problem exists for others |
| "That sounds like {existing product}" | No differentiation | Sharpen the unique value |
| "Why would anyone need that?" | No real market need | Go back to problem discovery |
| Eyes glaze over mid-explanation | Too many concepts | Cut features until it's one idea |

### Step 4: Record

```bash
mkdir -p non-tech-feedback
```

Write to `non-tech-feedback/FEEDBACK-{timestamp}.md`:

```markdown
---
project: {project name}
created: {ISO-8601}
test_conducted: {yes/no — date if yes}
---

# Non-Tech Feedback: {project}

## Plain Language Description
{translation from Step 1}

## Comprehension Test Results
{To be filled after real person test}

### Response Summary
- "What does it do?": {their answer}
- "Who would use it?": {their answer}
- "Would you use it?": {their answer}
- "What's confusing?": {their answer}

## Gap Analysis
| Confusion point | Complexity signal | Recommended action |
|-----------------|-------------------|-------------------|
| {what confused them} | {what it reveals} | {what to simplify} |

## Key Insight
{One sentence: the most important thing learned from this exercise}
```

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|--------|----------|-----------|
| "My users ARE technical" | Technical users still need to understand the value in 10 seconds. | Even engineers buy with emotions, justify with logic. Explain the value, not the architecture. |
| "I can't simplify this without losing accuracy" | If you can't simplify it, you don't understand it deeply enough. | Feynman technique: if you can't explain it simply, you don't understand it. |
| "I don't know any non-technical people" | Family, friends, neighbors, coffee shop barista. | Pick anyone. The exercise works with any non-expert. |
| "This doesn't apply to developer tools" | Developer tools are sold to teams with non-technical decision makers. | The CTO understands. The CFO needs to. |
| "It's too early to explain" | If you can't explain the idea, you can't validate it. | If you can't explain it, you're not ready to build it. |

## Evidence Required

- [ ] Plain-language description generated (zero tech terms)
- [ ] Comprehension test script prepared
- [ ] Test conducted with real non-technical person within 7 days
- [ ] Gap analysis completed based on real responses
- [ ] Key insight extracted
- [ ] Feedback recorded to file

## Red Flags

- Can't generate plain-language description without tech terms
- Refuses to test with real people
- Dismisses non-tech feedback as irrelevant
- Plain-language version is longer than 2 sentences
- "How" part requires background knowledge to understand

## Agent Instructions

### Do
- Strip ALL technical language — be aggressive about this
- Generate the test script immediately so the user has it ready
- Follow up on whether the test was actually conducted
- Treat confusion as a product signal, not an audience limitation
- Keep the plain-language version to 2 sentences max

### Do Not
- Let technical terms slip into the plain-language version
- Accept "I'll do it later" without a specific date
- Dismiss the exercise because the product is "for developers"
- Generate the gap analysis without real test results
- Let the user skip the real-person test entirely
