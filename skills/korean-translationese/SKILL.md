---
name: korean-translationese
description: "Detects and repairs English→Korean translation interference (번역투) in Korean prose: inanimate subjects with cognitive verbs, we/우리 and pronoun padding, ~의 그것, passive/double-passive, have/there-is/사동 make calques, idiom calques, ~에 대하여/~을 통해, 하나의, and 무정물 plural ~들. Detect→suggest→confirm; never blind-replace. Triggers on: '번역투', '번역체 고쳐', 'translationese', '어색한 한국어', '직역투', '영어 번역 다듬어'."
---

# korean-translationese — 번역투 제거

Korean text translated (or LLM-generated) from English carries repeated *traces*
of English: subjects, pronouns, passives, and idioms that are grammatical in
English but awkward or ungrammatical in Korean. This skill finds those traces and
proposes native Korean. It is **context-sensitive** — many candidates are
legitimate — so it always suggests with a diff and reason code, never auto-replaces.

Full candidate tables: `../korean-polish/references/translationese-table.md`.
Regex detection: `../korean-polish/references/regex-pack.md` (번역투 block).

## When to Trigger

**Explicit** (`/korean-translationese`): user asks to fix 번역투/번역체/직역투, or "make this Korean less like a translation".

**Auto** (inside `korean-polish` Stage 3): after verbosity, before register.

## Constraints (NON-NEGOTIABLE)

1. **Suggest, don't auto-apply.** Every hit is a candidate; the fix depends on context.
2. **Meaning invariant.** A less-번역투 sentence that changes the claim is wrong.
3. **Protected spans frozen** — `$...$`, numbers, citations, code, proper nouns.
4. **Legitimacy check before flagging.** `하나의` meaning "single/one" stays; `~들` on animate nouns stays; a neutral 서술 ("표 3은 …을 나타낸다") may be fine. Flag only real interference.
5. **Answer in Korean** unless the user writes in English.

## Process

Run these passes, each producing diffs with a `(§n)` reason code:

| Pass | Detect | Fix direction |
|---|---|---|
| ① 무생물 주어 | 사물 주어 + 인지/주장 동사 (주장/제시/보여주다) | `~은/는` → `~에서(는)` or 필자 주어 |
| ② 대명사·we·우리 | 서술어에 정보 있는데 남은 we/우리/그들/it | 생략 |
| ③ ~의 그것 | `의 그것(들)` | 명사 반복 or 재구성 |
| ④ 피동·이중피동 | `되어지/불려지/…에 의해 …되어진`, 감정 피동 | 능동으로; `-되어지다`→`-되다` |
| ⑤ have | `~을 가진다/가지고 있다` | `~에(게) ~가 있다` |
| ⑥ there-is/위치/free-from | 문말 `~이 있다` 남발, `위치해 있다`, `~로부터 자유` | 서술 재구성 / `~에 없다` |
| ⑦ 사동 make | `~게 만들다` | `~으로 …하다` |
| ⑧ 숙어 직역 | 고려에 넣다, …중 하나, sound robust | 관용 한국어 |
| ⑨ 연결·수식 | `~에 대하여/~에 있어서/~을 통해`, `하나의`(a/an), 무정물 `~들` | 삭제/축약 — 단, 정당한 용법은 유지 |

### Output
```
line 42 · ①무생물주어
- 이 논문은 A가 B를 유발한다고 주장한다.
+ 이 논문에서는 A가 B를 유발한다고 주장한다.
```
Summarize: N flagged, M applied, K left (legitimate).

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|---|---|---|
| "Replace every 하나의" | Many mean "single" and are correct. | check sense before flagging |
| "All passives are 번역투" | Korean passive is fine when the agent is unknown/irrelevant. | flag only agent-recoverable passives |
| "무생물 주어 is always wrong" | Neutral 서술 (표/그림 주어) can be idiomatic. | flag only cognitive/assertive verbs |
| "Just auto-fix, it's faster" | Context-free replacement mistranslates. | detect→suggest→confirm |

## Evidence Required

- [ ] Each pass run with reason-coded diffs
- [ ] Legitimate hits explicitly excluded (not silently kept)
- [ ] Meaning preserved per edit
- [ ] Protected spans untouched

## Red Flags

- A passive→active flip invents an agent not in the source → meaning drift
- Deleting `우리` changes a genuine first-person authorial stance
- `하나의` removed where it meant "single/one" → altered claim
- Auto-applied edits with no diff

## Agent Instructions

### Do
- Mask protected spans before matching
- Give a reason code per edit
- Keep legitimate uses; say why you kept them

### Do Not
- Blind find-replace
- Invent agents to un-passivize
- Touch math, numbers, citations, proper nouns
