---
name: korean-register
description: "Normalizes Korean academic register to how Korean scholars actually write (grounded in real 경제학/CS journal conventions): lowers the speaker (본 논문은 → 본고에서는), demotes field/inanimate subjects (모형은 가정한다 → 이 모형에서는 …라고 가정한다; 결과는 보여준다 → 분석 결과 …로 나타난다), closes results/implications with field idioms (~로 나타났다/~을 보인다/~할 필요가 있다), enforces plain 서술체 and one-term-per-concept, and picks register by field (economics 한자어 vs CS 외래어). Triggers on: '학술 문체', '네이티브 한국어', '한국인이 쓴 것처럼', '격식', '문체 통일', '용어 일관성', 'academic tone', 'native Korean', '논문체'."
---

# korean-register — 학술 문체·용어 일관성

Papers must read in one consistent, formal, declarative voice, with each concept
named by exactly one term. Register errors and terminology drift are the most
visible defects in translated academic Korean. This skill enforces both.

Term map: `../korean-polish/references/economics-glossary.md`.
Connective/register sets: `../korean-polish/references/academic-connectives.md`.
Native academic register (한국 논문 실제 관행, 경제학/CS 대조): `../korean-polish/references/native-academic-register.md`.

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

### Pass A0 — Native academic register (foundational, 한국 논문 실제 관행)
Run first. The strongest "translated" tell is discourse-level, not lexical.
Retarget the prose to how Korean scholars actually write (full contrastive tables:
`../korean-polish/references/native-academic-register.md`):
- **Speaker**: `본 논문은/본 모델은 ~한다` (English "This paper…" as an agent) → `본고에서는/이 논문에서는 ~한다`, or drop the subject. Don't repeatedly stage the paper/model/section as an actor.
- **Field/inanimate subjects (highest value)**: `모형은 가정한다` → `이 모형에서는 …라고 가정한다`; `결과는/표 N은 …을 보여준다` → `분석 결과 …로 나타난다 / 표 N에서 보듯`; `산업경제학은 …모델링한다` → `산업경제학에서 …은 …모델링된다`. Demote the field to an adverbial background; state results impersonally.
- **Result/implication endings**: results → `~로 나타났다/추정된다/유의하다`; implications → `~할 필요가 있다/~을 시사한다`.
- **Field register**: economics → 한자어 개념어 (강건성·내생성·상충관계·후생; 프레임워크→분석틀, 프리미티브→기본 요소); CS → keep 외래어 (프레임워크·토큰·컨텍스트·에이전트). Don't over-purify CS terms.

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
