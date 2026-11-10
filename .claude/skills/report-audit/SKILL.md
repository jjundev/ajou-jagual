---
name: report-audit
description: Use when asked to read one Notion-exported course report Markdown (보고서_노션.md) for [2026-2] 자료구조 및 알고리즘 이해 and fix what is wrong in that file — captions or analysis that disagree with the printed outputs, contradictions, claims about cases never run, instructions left in result sections, references to headings that do not exist, or awkward Korean sentences. Not for cross-source rubric review (assignment-report-audit), detector-score or style-signal rewriting, Notion upload, or PDF export (notion-report-sync).
---

# Report audit (one Markdown file)

Find and fix errors **inside one report Markdown file**, change only what the user approves, and prove that code, tables, headings and image URLs did not move. The file itself is the evidence: its "실제 출력" blocks and its full-source block are what claims are checked against.

## Read scope

Read the target file only. Everything else is a separate source the user must name first: assignment PDFs, `.c` files, other reports, **and git history or other commits**. When the user says "이 파일만", do not run `git log`, `git show` or open neighbouring files to settle a doubt; list the doubt as an open question instead.

Allowed without asking, because it is the same content: extracting the file's own full-source block to the scratchpad, compiling it, and running the file's own inputs through it.

## Workflow

1. `python3 .claude/skills/report-audit/scripts/report_md.py prose FILE` — numbered prose; code cells, code blocks and image URLs are hidden. Read all of it.
2. Fill **every** row of the findings table below. A category with nothing found gets the row `없음` with what you checked, so a skipped category is visible.
3. Present the table and ask once for the scope to fix (AskUserQuestion, recommended answer first). If no question tool exists, ask in chat and stop. Do not edit before the answer.
4. Edit approved rows with exact-string replacements. Change only the defective words; do not add new claims, examples or sentences while fixing one.
5. Verify:
   - `python3 .claude/skills/report-audit/scripts/report_md.py check FILE --before HEAD` (or `--before <backup file>` outside git) must print `protected spans identical`. Image alt text is editable; URLs are not.
   - `grep -c` each removed phrase → 0 (or the count you intended to keep).
6. Report: rows fixed, rows left, verification output, and what was not done (Notion, PDF, commit — those belong to `notion-report-sync` and the user).

## Findings table (all categories required)

| 범주 | What to check | Example from this course |
|---|---|---|
| 사실: 출력 대조 | Every T number, order and count in each image caption and 결과 분석 against the nearest preceding "실제 출력" block. **Each image caption gets its own row**, `일치` included, so none is skipped — also check words like "끝나지 않은" vs. "도착하지 않은". pop/restore happens after the tick that finishes, so the restored task shows on the next T. | "T6·T7에서 I1 → P1 순서로 스택이 풀린다" when output shows T4 I1, T5 P1 |
| 사실: 문서 안 모순 | An example that the same document says cannot occur, or a description that contradicts the code it sits beside. | "인접 FREE 블록이 남지 않는다" next to an example of three adjacent FREE blocks |
| 사실: 실행하지 않은 단정 | Results stated for an algorithm or case the report never implemented or ran. | "Best-Fit은 가장 작은 10칸을 선택한다" with no Best-Fit run |
| 결과 칸의 지시문 | 결과 분석 must state what was observed. Instructions ("~같아야 한다", "~확인한다", "검사한다") there are wrong tense for a result. A one-line purpose sentence before a case is fine. | "실패 명령 실행 전후의 메모리 지도가 같아야 한다." inside 결과 분석 |
| 참조 | Every "(… 사례 n)", "앞 절", "표 n" points to a heading or item that exists with that name. | "(실행 사례 5)" while headings are 공식 예시 / 추가 사례 1~4 |
| 문장 | Endings whose meaning does not fit (셈이다 for something literally true), colloquial fragments (꼴이다, 가득이다), mismatched pairs (…결과이고, …때문이다), a predicate inside parentheses, a subheading narrower than its content — in-cell subheadings are the short segments between `¶` marks in `prose` output; compare each with the branch or paragraphs under it (e.g. "프로세스가 다 돈 경우." heading a branch that also covers quantum expiry). Scan: `… prose FILE \| grep -n '셈이다\|꼴이다\|가득이다\|때문이다\|)'` then read each hit. | "IDLE_CONTEXT와 같은 셈이다" (they are exactly equal) |
| 소스 대조 (opt-in) | Only when the user names a `.c` file: `report_md.py code-compare FILE --source X.c`. Blank lines vanish in Notion export and are not a difference. | report Allman/4-space vs submitted K&R/2-space |
| 경고 (보고만) | `report_md.py warnings FILE` — expired signed image URLs carrying security tokens. Do not edit them; re-export replaces them. | `X-Amz-Expires=3600` issued 2026-10-29 |

Columns of the table you present: `행 | 범주 | 현재 문구 | 문제 | 수정안 | 근거`. 근거 is the output line, code line or heading that proves the row.

## Out of scope: style signals

Do not rewrite text to look less AI-written or to pass a detector: repeated templates, symmetric case layouts, "정상 입력이라면…" repetition, rubric-compliance sentences, prose length, comment density. These are not errors, and rewriting them hides assistance (same rule as `assignment-report-audit`). If asked, say this skill fixes factual and language errors only, and that AI assistance should be disclosed under the course policy. Fix genuine errors in the same pass as usual.

## Common mistakes

| Mistake | Instead |
|---|---|
| Checking git history to guess intent ("최근 커밋이 번호를 바꿨으니…") | Outside read scope unless named; ask which numbering the user wants |
| Rewriting a terse cell into three sentences with new claims | Replace the defective words with one plain sentence of the same content |
| Fixing captions but skipping the 문장 category | Every category row is filled, `없음` included |
| Verifying only that code compiles | `check --before` also covers table structure, headings and URLs |
| Editing a Notion page or regenerating the PDF | Stop at the Markdown; point to `notion-report-sync` |
