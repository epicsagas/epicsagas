---
name: korean-cohesion
description: "Checks Korean sentence/paragraph cohesion: subject-predicate agreement across long relative clauses, overuse of demonstratives (이/그/이러한/해당) and connective adverbs (그러나/따라서/또한), 라는 사실/점 padding, and parallelism in enumerations. Paragraph-level, statistical + suggestion. Triggers on: '호응', '결속', '지시어 남용', '접속부사', '병렬', '주술 호응', 'cohesion', 'Korean flow'."
---

# korean-cohesion — 호응·결속

Even clean sentences read poorly if subjects and predicates drift apart, every
sentence opens with 그러나/따라서, demonstratives point at nothing definite, or
enumerations break parallel form. This skill works at the paragraph level: it
measures these patterns and proposes fixes.

Regex/thresholds: `../korean-polish/references/regex-pack.md` (결속·호응 block).

## When to Trigger

**Explicit** (`/korean-cohesion`): "호응 봐줘", "지시어 너무 많아", "접속부사 정리", "병렬 맞춰".

**Auto** (inside `korean-polish` Stage 6): last, with the meaning-regression pass.

## Constraints (NON-NEGOTIABLE)

1. **Referent safety.** When resolving a demonstrative (이것/그것/이러한) to a noun, use the *actual* referent from context; never guess.
2. **Don't strip meaningful connectives.** 그러나/따라서 that carry real logic stay; only the reflexive, every-sentence ones go.
3. **Meaning invariant**, protected spans frozen.
4. **Answer in Korean** unless the user writes in English.

## Process

### Pass A — 주술 호응
Flag sentences where subject→predicate distance is **20+ 어절** (long 관형절). Split
the relative clause so the subject and its verb sit close, or restate the subject.

> 원문: 이 변수가 다른 변수들과 상호작용하면서 나타나는 복잡한 양상은 예측이 어렵다.
> 고침: 이 변수는 다른 변수와 상호작용하며 복잡한 양상을 보인다. 그 양상은 예측하기 어렵다.

### Pass B — 지시어 남용
Count 이것/그것/이러한/그러한/해당 per paragraph. Above threshold, replace vague
ones with the actual noun; collapse `~라는 사실/점을` → `~음을`.

| 나쁜 예 | 고친 예 |
|---|---|
| 이러한 사실은 이것이 그것에 영향을 준다는 것을 의미한다. | 이는 A가 B에 영향을 준다는 뜻이다. |
| ~라는 사실을 발견하였다는 점을 강조한다. | ~을 발견하였음을 강조한다. |

### Pass C — 접속부사 과다
Flag runs where consecutive sentences open with 그러나/따라서/또한/그리고. Keep the
logically necessary ones; drop the reflexive ones.

### Pass D — 병렬 구조
Enumerated items must share part-of-speech/form.

| 나쁜 예 | 고친 예 |
|---|---|
| 이 정책은 효율적이고 공평성을 높인다. | 이 정책은 효율성을 높이고 공평성을 개선한다. |

### Output
A paragraph-level report (지시어/접속부사 counts, 주술 거리 outliers) + diffs.

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|---|---|---|
| "Resolve 그것 to the nearest noun" | Nearest ≠ correct referent. | use the real antecedent; if unclear, flag |
| "Delete all connective adverbs" | Some carry the argument. | drop only reflexive ones |
| "Long relative clauses are fine in Korean" | Past 20 어절 the subject is lost. | split the 관형절 |
| "Parallelism is pedantic" | Broken parallelism reads as a category error. | unify item form |

## Evidence Required

- [ ] 주술 거리 outliers (20+ 어절) flagged/split
- [ ] Demonstrative counts per paragraph; vague ones resolved to real nouns
- [ ] Reflexive connective adverbs trimmed; logical ones kept
- [ ] Enumerations made parallel
- [ ] Referents verified against context

## Red Flags

- A demonstrative resolved to the wrong noun → meaning drift
- A logically necessary 그러나/따라서 deleted → argument break
- Splitting a 관형절 dropped a modifier
- "Parallelizing" changed an item's meaning to fit the form

## Agent Instructions

### Do
- Report per-paragraph counts before editing
- Verify each referent against context
- Keep connectives that carry logic

### Do Not
- Guess referents
- Strip connectives wholesale
- Force parallelism at the cost of meaning
