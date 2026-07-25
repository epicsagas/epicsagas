---
name: korean-verbosity
description: "Trims Korean 만연체 (verbosity): splits overlong multi-clause sentences, turns empty-verb nominalizations (~에 대한 검토를 수행한다) back into verbs (~을 검토한다), and removes 겹말/redundancy. Preserves meaning and protected spans. Triggers on: '만연체', '문장이 길어', '문장 분할', '간결하게', '군더더기', 'wordy Korean', 'concise Korean', '명사화 풀어'."
---

# korean-verbosity — 만연체·명사화 정리

Readability collapses when clauses nest and empty verbs pad sentences. This skill
shortens without losing content: split long sentences, convert nominalizations to
verbs, and cut redundancy. Meaning stays; only length changes.

Regex detection: `../korean-polish/references/regex-pack.md` (만연체 block).

## When to Trigger

**Explicit** (`/korean-verbosity`): "make this Korean more concise", "이 문장 너무 길어", "군더더기 빼줘".

**Auto** (inside `korean-polish` Stage 2): before translationese.

## Constraints (NON-NEGOTIABLE)

1. **Content invariant.** Splitting/trimming must not drop any proposition or qualifier.
2. **Protected spans frozen** — never split inside `$...$`, a citation, or a list item that must stay atomic.
3. **Don't over-split.** Two short sentences that read as one thought can stay; the target is clarity, not minimum length.
4. **Keep logical connectives** when splitting — the second sentence must still carry the causal/adversative link.
5. **Answer in Korean** unless the user writes in English.

## Process

### Pass A — 만연체 분할
Flag sentences with **45+ 어절 or 4+ commas** (or 3+ nested clauses). Split at
clause boundaries, promoting embedded 삽입절 (원문 콤마: `, 앞서 언급했듯,`) to their
own sentence or moving them to the front. Re-supply the connective.

> 원문: 본 연구는, 앞서 언급했듯, 여러 요인을 고려했을 뿐 아니라, 그것들이 상호작용하는 방식에 대한 분석을 수행함으로써, 기존 연구와 차별화되는 기여를 가진다.
> 고침: 이 연구는 여러 요인을 고려하였다. 나아가 그 요인들이 상호작용하는 방식까지 분석하였다. 이 점에서 기존 연구와 차별화된다.

### Pass B — 명사화 → 동사화
Empty verb (하다/수행하다/진행하다/이루어지다) + 동작명사 → main verb.

| 나쁜 예 | 고친 예 |
|---|---|
| A에 대한 분석을 수행하였다 | A를 분석하였다 |
| ~에 대한 검토가 이루어질 필요가 있다 | ~을 검토해야 한다 |
| B의 증가를 야기하는 결과를 초래한다 | B를 증가시킨다 |
| ~라는 점에 있어서 문제가 존재한다 | ~은 문제이다 |
| 결과에 대한 해석에 있어 주의가 요구된다 | 결과를 해석할 때 주의해야 한다 |

### Pass C — 겹말·군더더기
미리 예측 → 예측 · 다시 재검토 → 재검토 · 서로 상호작용 → 상호작용 ·
약 30% 정도 → 약 30% · 남은 여생 → 여생 · `~이 존재한다` → `~이 있다/~이다`.

### Output
Diff per edit with `(A/B/C)` code + the 어절/comma count that triggered a split.

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|---|---|---|
| "Shorter is always better" | Choppy 단문 나열 also hurts readability. | split for clarity, not for length |
| "Nominalization sounds academic" | Empty-verb padding is *less* precise, not more. | prefer the main verb |
| "Splitting drops the connective" | Then re-add it. | carry 따라서/그러나 into the split |
| "Cut the qualifier to shorten" | Qualifiers carry the claim's scope. | keep every hedge/scope word |

## Evidence Required

- [ ] Long-sentence candidates flagged with their metric (어절/comma)
- [ ] Nominalizations converted where an empty verb was present
- [ ] No proposition or qualifier dropped in any split
- [ ] Protected spans intact

## Red Flags

- A split sentence lost its 따라서/그러나 → broken logic
- A qualifier ("대략", "일부", "~에 한하여") vanished → scope changed
- Over-splitting turned one argument into staccato fragments
- A number or citation landed on the wrong side of a split

## Agent Instructions

### Do
- Report the metric that flagged each long sentence
- Re-supply connectives after splitting
- Keep every hedge and scope qualifier

### Do Not
- Split inside `$...$`, citations, or atomic list items
- Drop qualifiers to hit a length target
- Nominalize *back* — always toward the verb
