---
name: korean-polish
description: "Orchestrates a staged Korean prose-polishing (윤문) pass over a document, coordinating the translationese, verbosity, register, norm-lint, and cohesion specialists in top-down order with a term glossary and a meaning-preserving diff report. Use for academic/technical Korean, especially English→Korean translations. Triggers on: '윤문', '한국어 다듬어', '문장 다듬어', '번역투 고쳐', '한국어 교정', 'polish Korean', 'Korean prose'."
---

# korean-polish — 한국어 윤문 오케스트레이터

Run a disciplined, staged polishing pass over Korean prose. Polishing is **top-down** (logic → sentence → translationese → register → norms → regression) and **suggest-then-confirm**, because Korean style edits rarely have a single correct answer and blind find-replace over-corrects. This skill sequences the five specialists and enforces the meaning-preserving contract.

Companion specialists (invoke in this order):
1. **korean-translationese** — English→Korean interference (무생물 주어, we/우리, ~의 그것, 피동·이중피동, have/there-is, 사동 make, 숙어, ~에 대하여/~을 통해, 하나의, 무정물 ~들)
2. **korean-verbosity** — 만연체 분할, 명사화→동사화, 겹말·군더더기
3. **korean-register** — 서술체·시제·구어체 제거, 용어 일관성
4. **korean-norm-lint** — 띄어쓰기·조사·문장부호·맞춤법 (deterministic)
5. **korean-cohesion** — 주술 호응, 지시어·접속부사 남용, 병렬, 조사

Shared reference packs live in `references/` and are loaded on demand.

## When to Trigger

**Explicit** (`/korean-polish`): user asks to polish/edit Korean prose, fix 번역투, or improve a Korean translation of a document.

**Auto**: a Korean document (especially one translated from English, or LLM-generated) is about to be shipped, submitted, or published.

## Constraints (NON-NEGOTIABLE)

1. **Meaning is invariant.** Polishing changes *form*, never *content*. If a rewrite alters what a sentence asserts, it is wrong — discard it.
2. **Protected spans are frozen.** Never touch: inline/display math (`$...$`, `$$...$$`), numbers, units, code, citations/references, proper nouns, URLs, section/heading structure, or defined technical terms. Treat them as opaque tokens.
3. **Translation fidelity.** If the document is a translation, every edit must stay faithful to the source; do not "improve" the argument, only the Korean.
4. **Suggest → confirm for context-dependent fixes.** Translationese, verbosity, register, cohesion are context-sensitive → propose with a diff; only norm-lint (어문규범) is deterministic enough for near-automatic application.
5. **One defect class per pass.** Do not mix stages — it multiplies false positives and cascading errors.
6. **Parity check on structured docs.** For bilingual or math-bearing documents, count protected spans before and after; the counts MUST match, or the edit broke something.
7. **Answer in Korean** unless the user writes in English.

## Intensity dial

Ask (or infer) the intensity before editing:

| Level | What it does | Expected edits / 1000 words |
|---|---|---|
| **conservative** | Fix only genuine defects; preserve already-good sentences. Default for polished text. | few, surgical |
| **assertive** | Also rework sentence rhythm, vocabulary, and connectives for flow. Higher reward, higher risk. | many; re-verify parity |
| **diagnostic-only** | Report findings as a diff/checklist; change nothing. | 0 |

Higher intensity ⇒ mandatory parity re-check and a per-sentence meaning review.

## Process

### Stage 0 — Prepare
- Build/load a **term glossary** (source term → single Korean equiv). This is the #1 defect source in translations. Load `references/economics-glossary.md` for economics; extend per document.
- Fix the document's **종결체** (‘~한다’ 서술체 for papers) and **시제** policy (general statements → 현재형).
- Snapshot protected-span counts (math, citations, numbers).

### Stage 1 — Structure/logic (developmental)
Check argument flow and paragraph/sentence connection *before* touching wording. Do not line-edit yet.

### Stage 2 — Sentence (korean-verbosity)
Split 만연체 (45+ 어절 or 4+ commas), turn nominalizations back into verbs, cut 겹말.

### Stage 3 — Translationese (korean-translationese)
Run the §1 translationese passes. Detect → suggest → confirm.

### Stage 4 — Register + terminology (korean-register)
Enforce 서술체·시제, strip 구어체/담화표지, and check every glossary term for variant spellings.

### Stage 5 — Norms (korean-norm-lint)
띄어쓰기, 조사 호응 (로써/로서, 에/에게, 와/과), 문장부호 (콜론·세미콜론→마침표, 강조 작은따옴표), 맞춤법. Deterministic → near-automatic.

### Stage 6 — Cohesion + regression (korean-cohesion)
주술 호응, 지시어·접속부사 남용, 병렬. Then **regression**: re-read every edited sentence against the original for meaning drift, and re-run the Stage-0 parity snapshot.

### Deliverable
A per-stage diff report:
```
[Stage 3 · translationese] line 42
- 이 논문은 A가 B를 유발한다고 주장한다.
+ 이 논문에서는 A가 B를 유발한다고 주장한다.
  reason: 무생물 주어 + 인지동사 (§1①)
```
End with: edits applied / suggested-only, protected-span parity (before=after), and any meaning-risk flags.

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|---|---|---|
| "Just find-replace the 번역투 patterns" | Context-free replacement over-corrects — many hits are legitimate (하나의 생산함수 = a *single* function). | detect → suggest → confirm |
| "Polish everything in one sweep" | One sweep blends defect classes and hides meaning drift. | one stage per pass, top-down |
| "The prose reads awkwardly, rewrite it freely" | Freedom breaks translation fidelity and parity. | edit form, not content; keep protected spans |
| "It's already good, skip the checks" | Then run diagnostic-only and prove it — don't guess. | diagnostic pass |
| "Fixing the math spacing while I'm here" | Math is a protected span. | never touch `$...$` |

## Evidence Required

- [ ] Term glossary loaded/created
- [ ] Protected-span counts snapshotted (before)
- [ ] Stages run top-down, one defect class each
- [ ] Diff report with per-edit reason codes
- [ ] Protected-span parity verified (before == after)
- [ ] Meaning-drift regression pass on every edited sentence

## Red Flags

- A "fix" changes a number, term, or claim → stop, revert
- Protected-span count changed → an edit ate math/citation
- Same concept rendered by two Korean terms → glossary violation
- Edits pile up in one paragraph while the rest is untouched → over-editing a single spot
- Aggressive rewrites with no diff → unauditable

## Agent Instructions

### Do
- Load only the reference pack the current stage needs
- Show a diff with a reason code for every edit
- Keep the source meaning; when unsure, suggest don't apply
- Re-verify math/citation parity after the run

### Do Not
- Auto-apply translationese/register/cohesion edits without confirm at assertive intensity on high-stakes docs
- Touch `$...$`, numbers, citations, headings, or defined terms
- Blend stages
- "Improve" the argument of a translation
