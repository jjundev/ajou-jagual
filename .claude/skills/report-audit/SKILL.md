---
name: report-audit
description: Use when asked to review or fix one Notion-exported course report Markdown (보고서_노션.md) for [2026-2] 자료구조 및 알고리즘 이해 for output mismatches, contradictions, unsupported execution claims, instructions left in result sections, broken references, or awkward Korean sentences. Not for cross-source rubric review (assignment-report-audit), detector-score or style-signal rewriting, Notion upload, or PDF export (notion-report-sync).
---

# Report audit (one Markdown file)

Find and fix errors **inside one report Markdown file**, change only what the user approves, and prove that code, tables, headings and image URLs did not move. The file itself is the evidence: its "실제 출력" blocks and its full-source block are what claims are checked against.

## Read scope

Read the target file only. Everything else is a separate source the user must name first: assignment PDFs, `.c` files, other reports, **and git history or other commits**. When the user says "이 파일만", do not run `git log`, `git show` or open neighbouring files to settle a doubt; list the doubt as an open question instead.

Allowed without asking, because it is the same content: extracting the file's own full-source block to the scratchpad, compiling it, and running the file's own inputs through it.

## Workflow

1. `python3 .claude/skills/report-audit/scripts/report_md.py prose FILE` — numbered prose; code cells, code blocks and image URLs are hidden. Read all of it.
2. `python3 .claude/skills/report-audit/scripts/report_md.py signals FILE [--source X.c]` — 과제2에서 밝혀낸 AI 작성 신호 10종을 보고한다. 자동 수정하지 않는다.
3. For each candidate, return to the relevant raw code, input and output in the **same file**; `prose` hides those blocks and cannot establish a factual error by itself. Apply the verdict rules below, then fill **every** category of the findings table. A checked category with no issue gets `없음` with what you checked; a category outside the supplied scope gets `대상 외` with the reason. Missing evidence is `판단 보류`, not `없음`.
3. Present the table and ask once for the scope to fix (AskUserQuestion, recommended answer first). If no question tool exists, ask in chat and stop. Do not edit before the answer.
4. Edit approved `오류 확정` or `설명 보완` rows with exact-string replacements. Change only the defective words; do not add new claims, examples or sentences while fixing one. Leave `정상` and `판단 보류` rows unchanged, including unsupported claims whose truth remains unknown. Do not delete a claim or replace it with a theoretical prediction merely because its execution evidence is absent.
5. Verify:
   - `python3 .claude/skills/report-audit/scripts/report_md.py check FILE --before HEAD` (or `--before <backup file>` outside git) must print `protected spans identical`. Image alt text is editable; URLs are not.
   - `grep -c` each removed phrase → 0 (or the count you intended to keep).
6. Report: rows fixed, rows left, verification output, and what was not done (Notion, PDF, commit — those belong to `notion-report-sync` and the user).

## Evidence and verdicts

For each candidate, record the claim's role (observed result, theoretical deduction, verification purpose, or requirement), its input/subject/conditions and time or processing stage, and the relevant lines of evidence. Test the strongest reading supported by that context before declaring an error. A keyword match only identifies a candidate.

| 판정 | When it applies | Action |
|---|---|---|
| 오류 확정 | The claim conflicts with code, output, another statement, or an unambiguous reference under the **same conditions and stage**; a definite language defect can also qualify. | Propose the smallest correction supported by the file. |
| 설명 보완 | The meaning is supportable, but an omitted condition, stage, or unclear sentence role makes it misleading. | Propose a short clarification using existing evidence only. If the clarification needs missing facts, use `판단 보류` instead. |
| 정상 | The claim is valid in context, including a sound theoretical prediction or a temporary intermediate state. | No correction. |
| 판단 보류 | The permitted material cannot establish the truth or supply facts needed for a correction. | State what evidence is missing; no correction or deletion. |

Absence of an implementation or output in the report does **not** establish that an experiment never happened. A new run of the file's own source and inputs is a **사후 재현**, not evidence of a historical run. Identify its provenance separately from the report's printed output.

## Findings table (all categories required)

| 범주 | What to check | Example from this course |
|---|---|---|
| 사실: 출력 대조 | Every T number, order and count in each image caption and 결과 분석 against the nearest preceding "실제 출력" block. **Each image caption gets its own row**, `일치` included, so none is skipped — also check words like "끝나지 않은" vs. "도착하지 않은". pop/restore happens after the tick that finishes, so the restored task shows on the next T. | "T6·T7에서 I1 → P1 순서로 스택이 풀린다" when output shows T4 I1, T5 P1 |
| 사실: 문서 안 모순 | Compare the subject, inputs, assumptions, and stage of both statements. Distinguish an invariant after an operation completes from a temporary state during it. Follow the relevant code before judging the example. | Three adjacent FREE blocks after marking the middle block FREE, **before merging**, are compatible with no adjacent FREE blocks **after release completes**. An output showing adjacent FREE blocks after completion would contradict that invariant. |
| 사실: 실행 주장과 근거 | First distinguish an asserted actual run from a deduction based on an algorithm's rules. Check an asserted run against the supplied implementation/input/output. Missing evidence alone means `판단 보류`; demonstrated conflict means `오류 확정`. | "이론상 Best-Fit은 가장 작은 적합 블록을 선택한다" can be `정상` without a run. "실제로 실행해 선택했다" without execution evidence is `판단 보류`, not proof of non-execution. |
| 결과 칸의 지시문 | Search for "~같아야 한다", "~확인한다", "검사한다", then determine the sentence's role. A purpose or criterion can accompany observed results. If instructions replace the result, distinguish a clarifiable role from missing observations; never invent the observations. | "두 출력이 같다. 이 출력으로 상태 보존을 확인한다" is `정상`. Instructions alone with no observed result require `판단 보류` for the missing result; an unclear role with sufficient evidence can be `설명 보완`. |
| 참조 | Every "(… 사례 n)", "앞 절", "표 n" points to a heading or item that exists with that name. | "(실행 사례 5)" while headings are 공식 예시 / 추가 사례 1~4 |
| 문장 | Endings whose meaning does not fit (셈이다 for something literally true), colloquial fragments (꼴이다, 가득이다), mismatched pairs (…결과이고, …때문이다), a predicate inside parentheses, a subheading narrower than its content — in-cell subheadings are the short segments between `¶` marks in `prose` output; compare each with the branch or paragraphs under it (e.g. "프로세스가 다 돈 경우." heading a branch that also covers quantum expiry). Scan: `… prose FILE \| grep -n '셈이다\|꼴이다\|가득이다\|때문이다\|)'` then read each hit. | "IDLE_CONTEXT와 같은 셈이다" (they are exactly equal) |
| 소스 대조 (opt-in) | Only when the user names a `.c` file: `python3 .claude/skills/report-audit/scripts/report_md.py code-compare FILE --source X.c`. Inspect the raw source before judging content; see the helper limitations below. | Allman/4-space vs K&R/2-space establishes a formatting difference, not a content error or authorship. |
| 경고 (보고만) | `report_md.py warnings FILE` — expired signed image URLs carrying security tokens. Do not edit them; re-export replaces them. | `X-Amz-Expires=3600` issued 2026-10-29 |
| AI 작성 신호 (보고만) | `signals` 10종. 양성 이름·위치·수치를 그대로 옮기고, 수정 제안은 쓰지 않는다. `source-out-of-scope-guards`는 `--source` 지정 시에만. | 과제2: `run-script-trace` 24건, `output-block-smushed-prompts` 6건, `caption-duplication` 6/6, `no-personal-voice` whole prose |

Columns of the table you present: `행 | 범주 | 판정 | 현재 문구 | 문제 | 수정안 | 근거`. 근거 identifies the claim role and conditions, cites the relevant output/code/heading lines, and explains why they support the verdict (or what is missing). Use `정상` for checked, matching captions. For a checked category with no issue, use `정상` and `없음`; for `대상 외`, use `—` as the verdict. `정상` and `판단 보류` rows have `—` as the correction. Signed-URL warnings remain report-only.

## Code-comparison helper limitations

`code-compare` is a comparison aid, not a C lexer or equivalence proof. Its regex tokenization ignores meaningful string whitespace and operator boundaries: `"A B"` vs `"A  B"`, or `x++ + y` vs `x + ++y`, can produce `tokens_equal: True`. A true value alone does not establish equal code behavior; a false value does not establish a behavioral difference either.

Exit code 1 can mean formatting alone differs. Read `tokens_equal`, `format_differs`, and the raw source rather than treating the exit code as a factual-error verdict. Blank-line loss, indentation, brace placement and line wrapping are formatting observations. Do not infer authorship, a content error, or an editing sequence from formatting or modification times alone.

## Out of scope: style signals

Do not rewrite text to look less AI-written or to pass a detector: repeated templates, symmetric case layouts, "정상 입력이라면…" repetition, rubric-compliance sentences, prose length, comment density. These are not errors, and rewriting them hides assistance (same rule as `assignment-report-audit`). If asked, say this skill fixes factual and language errors only, and that AI assistance should be disclosed under the course policy. Fix genuine errors in the same pass as usual.

다만 검출(`signals`)은 저자가 제출 전 공개·수정할 수 있도록 허용한다. 스킬 자체가 재작성하거나 신호 문구를 "자연스럽게" 바꾸지 않는다.

## Common mistakes

| Mistake | Instead |
|---|---|
| Checking git history to guess intent ("최근 커밋이 번호를 바꿨으니…") | Outside read scope unless named; ask which numbering the user wants |
| Calling a temporary state a contradiction of a completed-state invariant | Align the stages, then follow the code before deciding. |
| Deleting an execution claim because no output is supplied | Mark `판단 보류`; name the missing evidence and leave the claim unchanged. |
| Rewriting "확인한다" despite a concrete matching observation | Classify the sentence's role; valid result interpretation is `정상`. |
| Rewriting a terse cell into three sentences with new claims | Replace the defective words with one plain sentence of the same content |
| Fixing captions but skipping the 문장 category | Every category row is filled, `없음` included |
| Verifying only that code compiles | `check --before` also covers table structure, headings and URLs |
| Editing a Notion page or regenerating the PDF | Stop at the Markdown; point to `notion-report-sync` |
