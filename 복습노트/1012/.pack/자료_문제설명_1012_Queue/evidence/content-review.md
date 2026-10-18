# Actual source and content review — 1012
Reviewer: Codex main agent, 2026-10-12.

Original problem, note, bank and PDF/HWP files were read. Original HTML and source.json were not edited.

## Source visual
- P1/P8: 2019 recovered original TXT questions 6/4. The obvious Korean typo 스태 is retained; counts and final-result-stays-in-stack condition match. X is the intended answer to the false FIFO claim, not an editorial correction.
- P2/P4: native 2018 C024 HWP BodyText was independently decoded and pyhwp-rendered. Viewed hwp-question9.png and hwp-question1.png: P2 (1) infix `(2+4)*7-6*3+1`, (2) independent token table `5 6 * 4 2 / + 1 -`; P4 bracket-tool question. Source grid and 6 stack columns match.
- P3/P5/P7: visually viewed 2017 PDF page 1. P3 token sequence and four stack columns match; P5 asks postfix tool; P7 asks normal bank queue model.
- P6: visually viewed 2017 PDF pages 4–5. Source answer contains an extra `int op`, but explanation uses direct `push(&s, str[i]-'0')`, equivalent and confined to original blanks. Original scanf, empty-pop branch and variable declarations are retained.
- Viewed lecture S5 p26/p37 and S6 p3. Also read extracted relevant S5 p27/p28 and S6 p4 pages and current note topic text s0-array/pushpop, s1-matching/eval/convert, s2-fifo/buffer.

## Content and independent checks
- P1: numeric count rule follows one push per operand, two pop plus one push per binary operator. Nine pushes, eight pops; final31 remains. Does not count conversion stack or final retrieval.
- P2: source extractor labels entire legacy problem `main`; authoring still separates question (1) and question (2) in both solve/verify, never substitutes their inputs. (1) postfix corresponds to value25; (2) table is separate value31. Operator/output14-row table and six-column operand table checked.
- P3: every token state checked against independent expression reduction. First pop is right operand. Unused cells are not persistent stale array values. Final24.
- P4/P5: selection based on nesting/pending-subexpression invariants, not only numeric examples. Both stack.
- P6: three explicit function headings under extraction main marker; no question merged. Blank-only original code compiled C11 and run for four valid inputs. Warnings: missing nonvoid return for empty-pop branch and old `main()` prototype. No added safety changes. All calls in tested valid inputs have operands; length<=99; capacity and signed-int assumptions explicit. No UB result approved. Original-bank equivalent code answer is distinguished, not disputed numerical result.
- P7: normal FIFO service model explicitly stated, no VIP/priority assumption added. Queue.
- P8: separate feature/application judgments and actual A,B stack counterexample. X.
- All recall sections link exact question clue to definition/operation/condition/reason. Start is an actual first line, not duplicate general theory. Seven sections are ordered. Every answer is expanded, summary agrees with body; retries1–3. No new exam problem or out-of-scope advanced theory added.

## Approved template customization
Actual 375px P6 source-code block overflow was212px due to absence of pre overflow CSS. User explicitly approved on2026-10-12 the one-line `pre { max-width: 100%; overflow-x: auto; tab-size: 4; }` fix and final publication. Frozen upstream hash is unchanged in provenance; local override reconstructs original bytes and records current hash. Existing provenance/render checks were adapted to verify that reconstruction rather than falsely relabel original bytes.
