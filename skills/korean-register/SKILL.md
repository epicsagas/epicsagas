---
name: korean-register
description: "Normalizes Korean academic register and terminology: enforces plain declarative 서술체 (~이다/~한다), strips 구어체/honorifics/담화표지 (되게, 좀, 아무튼), fixes tense (general statements → present, will-padding removed), and enforces one-term-per-concept against a glossary. Triggers on: '학술 문체', '격식', '문체 통일', '용어 일관성', '구어체 고쳐', 'academic tone', 'terminology consistency', '논문체'."
---

# korean-register — 학술 문체·용어 일관성

Papers must read in one consistent, formal, declarative voice, with each concept
named by exactly one term. Register errors and terminology drift are the most
visible defects in translated academic Korean. This skill enforces both.

Term map: `../korean-polish/references/economics-glossary.md`.
Connective/register sets: `../korean-polish/references/academic-connectives.md`.

## When to Trigger

**Explicit** (`/korean-register`): "make this academic/formal", "용어 통일해줘", "구어체 빼줘".

**Auto** (inside `korean-polish` Stage 4): after translationese, before norm-lint.

## Constraints (NON-NEGOTIABLE)

1. **One concept = one term.** Load the glossary; every variant of a defined term is a violation to flag.
2. **Protected terms frozen.** Symbols/abbreviations (EIC, W, C, X, PIM, LP) and first-occurrence `역어(English)` pairs are not "inconsistencies" — leave them.
3. **Register change ≠ meaning change.** 되게 중요하다 → 매우 중요하다 keeps the claim; a hedge must not be strengthened or weakened.
4. **Tense by convention**, not by the English source: general statements → 현재형; don't render every `will` as 미래형.
5. **Answer in Korean** unless the user writes in English.

## Process

### Pass A — 종결체·구어체
- Enforce plain declarative (`~이다/~한다`). Flag 경어체 (`~합니다/~습니다/~네요/~죠`).
- Strip 담화표지·구어 어휘: 되게/엄청→매우 · 좀→다소 · 그래서 결국→따라서 · 아무튼→요컨대 · ~인 것 같다→~로 보인다(근거 후).

### Pass B — 시제
General/theoretical statements → 현재형. Method/result description → 과거형.
Remove `will` padding: `~할 것이다` (일반 진술) → `~한다`.

### Pass C — 용어 일관성 (glossary-driven)
1. Scan the document; list every term that has a glossary entry.
2. For each, detect variant renderings (탄력도 vs 탄력성 vs 탄성).
3. Pick the glossary form (or the document's dominant form if not in glossary) and flag all others.
4. Extend the glossary with document-specific core terms.

### Output
Diff per edit with `(A/B/C)`; for Pass C, a **term-consistency table**: term →
chosen form → count of each variant → lines to fix.

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|---|---|---|
| "Variety of words reads better" | In papers, synonym-switching a *term* reads as a different concept. | one term per concept |
| "~인 것 같다 sounds humble" | Unsourced hedging weakens a claim. | ~로 보인다/판단된다 after evidence |
| "The English says will, so 미래형" | Korean marks general truth with 현재형. | present tense for general statements |
| "Fix the symbol to be consistent too" | Symbols are protected. | never rename EIC/W/C/X |

## Evidence Required

- [ ] 종결체 unified; 구어체/담화표지 removed
- [ ] Tense normalized (general → present)
- [ ] Term-consistency table produced; variants reconciled
- [ ] Protected symbols and 역어(English) pairs untouched
- [ ] No hedge strengthened or weakened

## Red Flags

- A term's meaning shifted because a "consistent" form was the wrong sense (마진 vs 마크업)
- A hedge ("~로 보인다") upgraded to an assertion ("~이다") → overclaim
- A defined symbol got "normalized"
- Present-tense rewrite changed a genuinely future/conditional statement

## Agent Instructions

### Do
- Build the term-consistency table first, then reconcile
- Keep hedges at their original strength
- Respect first-occurrence `역어(English)` conventions

### Do Not
- Touch symbols/abbreviations
- Turn a hedge into a claim (or vice versa) while formalizing
- Force present tense onto genuinely conditional/future statements
