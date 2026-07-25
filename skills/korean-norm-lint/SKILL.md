---
name: korean-norm-lint
description: "Deterministic Korean orthography linter (국립국어원 어문규범): 띄어쓰기 (의존명사/조사/관형사/-어지다), 조사 호응 (로써/로서, 에/에게, 와/과), 문장부호 (colon/semicolon→마침표, 강조 작은따옴표), and 맞춤법. High-confidence, near-automatic fixes. Triggers on: '띄어쓰기', '맞춤법', '어문규범', '조사 오류', '문장부호', 'Korean orthography', 'Korean grammar lint', '국립국어원'."
---

# korean-norm-lint — 어문규범 린트 (결정론적)

Unlike the style skills, orthography has right answers. This skill applies the
국립국어원 어문규범 with high confidence: 띄어쓰기, 조사 호응, 문장부호, 맞춤법. Because
it is deterministic, fixes may be applied near-automatically — but math, code,
and citations are still frozen.

Regex detection: `../korean-polish/references/regex-pack.md` (어문규범 block).
Rules + 이중피동 list + 부호: `../korean-polish/references/academic-connectives.md`.

## When to Trigger

**Explicit** (`/korean-norm-lint`): "띄어쓰기 봐줘", "맞춤법 검사", "문장부호 고쳐".

**Auto** (inside `korean-polish` Stage 5): after register, before cohesion.

## Constraints (NON-NEGOTIABLE)

1. **Protected spans frozen** — never re-space inside `$...$`, code, URLs, or reference strings.
2. **Ambiguous 띄어쓰기 → suggest, not auto.** `-ㄴ데`(어미, 붙임) vs `데`(의존명사, 띄움) depends on meaning; when the test is ambiguous, flag don't apply.
3. **Standard is 국립국어원.** Not personal preference. Cite the rule for non-obvious fixes.
4. **Answer in Korean** unless the user writes in English.

## Process

### Pass A — 띄어쓰기
- 의존명사 띄움: `진것`→`진 것`, `할수 있다`→`할 수 있다`, 관형형+`것/수/바/지/채`.
- 판별 요령: 뒤에 조사 `에`가 붙을 수 있으면 의존명사(띄움). `-ㄴ데/-는지/-ㄴ지`는 어미(붙임).
- 경과의 `지`·`만`은 띄움: `떠난 지 삼 년`, `십 년 만에`. 한정 조사 `만`은 붙임: `철수만`.
- 관형사 띄움: `각 가정`, `전 국민`, `매 회계 연도`. 접두사 `제-`는 붙임: `제2차`.
- `-어지다/-어하다`는 붙임: `이루어진다`, `예뻐한다`.

### Pass B — 조사 호응
- **로써(수단)** vs **로서(자격)**: 실험으로써→실험으로 · 경제학자로써→경제학자로서.
- **에(무정물)** vs **에게(유정물)**.
- **와/과**, `뿐/밖에/만큼` 붙임 여부.

### Pass C — 문장부호
- 콜론 `:` / 세미콜론 `;` in Korean sentence position → **마침표** (한국어 규범에 영어식 용법 없음). `…다음과 같다:` → `…다음과 같다.`
- 강조는 **작은따옴표** `'…'`; 큰따옴표는 직접 인용.

### Pass D — 맞춤법·오탈자
Standard spelling + 이중피동 (`되어지→되다`, list in references). Final proofread.

### Output
Diff per fix with a rule tag: `[띄어쓰기·의존명사]`, `[조사·로서]`, `[부호·콜론]`.
Deterministic fixes may be batch-applied; ambiguous ones listed for confirm.

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|---|---|---|
| "띄어쓰기 is subjective" | 국립국어원 has explicit rules; most cases are decidable. | apply the rule, cite it |
| "Colon looks cleaner before a list" | Not a Korean convention. | 마침표 |
| "Double-space fixes inside the equation too" | Math is protected. | skip `$...$` |
| "-ㄴ데 vs 데, just pick붙임" | Meaning decides it. | test with 조사 `에`; if ambiguous, flag |

## Evidence Required

- [ ] 띄어쓰기 fixes tagged with the rule
- [ ] 조사 호응 (로써/로서, 에/에게) checked
- [ ] Colons/semicolons in sentence position → 마침표
- [ ] Ambiguous cases flagged, not force-applied
- [ ] Protected spans un-respaced

## Red Flags

- A `-ㄴ데/데` "fix" changed the meaning (concession vs place/case)
- Re-spacing altered a token inside `$...$` or a URL
- A citation string got "corrected"
- Applying 부호 rules deleted a legitimate colon inside a title/quote

## Agent Instructions

### Do
- Tag every fix with its 규범 rule
- Batch-apply only the unambiguous, deterministic fixes
- Cite 국립국어원 for non-obvious calls

### Do Not
- Re-space inside math, code, URLs, citations
- Force ambiguous 띄어쓰기 without the meaning test
- Impose personal preference as a "rule"
