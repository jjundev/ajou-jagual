---
name: programming-assignment-report
description: Use when preparing, reviewing, or finishing a programming assignment report from assignment instructions, source code, and execution results. Applies to 코딩 과제 보고서; not to general essays or implementing the assignment code itself.
---

# Programming assignment reports

Help the author produce a report whose requirements, code explanations, and execution analysis agree with the actual assignment and program. Work from the current artifacts rather than replaying a fixed sequence from an earlier assignment.

## Choose the needed work

Identify what the user has requested and which artifacts exist: assignment prompt or rubric, supplied starter code, implemented code, author-written explanation, execution evidence, and final-format file. Do the relevant work below. A request to review a draft does not require recreating it; a Markdown draft does not imply that a required PDF has been checked.

Keep a compact requirement record with `requirement | source and page | evidence | status`. Include scoring weights, hard-fail conditions, submission format, and deadline only when the sources state them. Use statuses that distinguish **confirmed**, **needs author input**, **source conflict**, **not executed**, and **format not verified**. Do not turn an unknown into a pass.

## Use specialist skills when needed

Read and follow a specialist skill only when its task is within the requested scope; these are conditional routes, not a checklist to execute for every report. Keep assignment requirements, code and execution analysis, and final-format verification here. A report request does not by itself authorize external editing or uploads.

- For actual terminal execution screenshots needed as report evidence, use [terminal-evidence-capture](../terminal-evidence-capture/SKILL.md). Capture the current source and cases, with input, observed output, and exit status recorded alongside the images. Do not force screenshots when text logs suffice. If capture is unavailable, report the concrete limitation and distinguish an actual text log from a screenshot; do not fabricate an image or reuse stale evidence as current.
- For user-requested Notion comparisons, targeted edits, or image slots, use [notion-report-sync](../notion-report-sync/SKILL.md). Keep synchronization separate from PDF export and final PDF verification. Capturing a screenshot alone does not authorize uploading it.
- For a cover-only deliverable, use [assignment-cover](../assignment-cover/SKILL.md). For combining a finished report PDF with its cover, use [assignment-report-merge](../assignment-report-merge/SKILL.md); let that skill handle a missing cover rather than creating it twice. Include these tasks only when the requested deliverable calls for them, and follow the specialist's conditions for replacing existing files.
- Use [assignment-report-audit](../assignment-report-audit/SKILL.md) as a separate entry point for a requested comprehensive review, not an automatic step during drafting. When that audit refers here for code and execution analysis, perform that analysis and return to the audit; do not restart the audit or either full workflow recursively.

## Establish the assignment contract

- Read the relevant prompt, rubric, and supplied code before deciding the report's scope. For PDFs, inspect relevant rendered pages as well as extracted text when layout, images, or extraction artifacts could matter.
- For programming reports in this workspace's **[2026-2] 자료구조 및 알고리즘 이해** course, first read [the common course rubric](references/course-rubric.md), then the current assignment instructions, [the course report format](references/data-structures-course-format.md), and the HW1 case study below. The user confirmed that this rubric applies to all assignments in that course and semester. Apply its confirmed grading and submission requirements; check for explicit official changes and record unresolved contradictions. The format reference supplies author preferences within mandatory requirements. Neither source applies automatically to other courses or semesters.
- For those follow-up reports, also read [the HW1 case study](references/hw1-case-study.md) for the preserved final PDF and source, concrete analysis examples, and their evidence. Use its explanation depth and evidence presentation as a reference after establishing the current assignment contract. The full-mark outcome is user-reported; it does not establish grading causality, resolve new source conflicts, or validate a later report. Keep the preserved copies unchanged and analyze the current code and runs afresh.
- If visible content, extracted text, announcements, or files disagree, record the exact conflict and its sources. Do not silently treat an extraction-only instruction or the visible page as authoritative. Check accessible official updates and ask the user about provenance when the difference changes implementation or grading; state any provisional choice. Do not contact teaching staff without explicit user instruction.
- Separate requirements for code, report content, document layout, and submission. Reuse the confirmed common rubric within its stated scope; do not carry HW1-specific examples, counts, deadlines, or earned scores into another assignment. Author preferences cannot waive official requirements, and a new instruction that does not address a common rule does not cancel it. Keep unresolved source conflicts distinct from explicit official changes.

## Anchor analysis in code and execution

- Compare supplied code with the student's current implementation. Describe a function's inputs, outputs, changed state, and reason for its key conditions or state transitions. Analyze supplied declarations and functions when the rubric requires them. Do not attribute a provided design choice to the student or claim an optimization without measurements or another source.
- Use actual runs for result analysis: record the input, observed output, environment when relevant, and a short trace that explains the result. Choose cases from the assignment examples and material boundaries or errors; never prescribe a fixed test count. Compute reported case totals from the record instead of retyping them.
- If asked to change only comments, preserve executable code and verify that preservation by an appropriate source or token comparison. Re-run focused checks when code changed, evidence became stale, or a required gate needs it. A successful compile, a matching example, and broad correctness are different claims.
- When a current report includes code, compare its code text with the current source after edits. Check every numerical result, return value, and limitation against code or execution evidence. In particular, distinguish a possible future failure from an observed failure.

## Confirm the author's understanding before drafting

- Before writing a new report or substantially rewriting its explanations, inspect the assignment requirements, supplied code, current implementation, and available execution evidence. Then identify the author's understanding needed for the report's core explanations. Code can establish behavior without establishing how the author understands it.
- Ask about key conditions and state changes, a small input trace, or the author's own implementation choices and reasons. Do not present a supplied design as the author's choice. Reuse sufficient explanations already given in conversation or the author's draft; ask only about missing essentials, without a fixed question count or an interview for every function. Routine review, proofreading, and formatting do not require an interview; revisit only understanding affected by substantive changes.
- Use an available question tool to send **one substantive question at a time**, with multiple-choice options, a recommended answer first, and free-text input allowed. In Codex Default mode use `request_user_input_async`; use `request_user_input` only when actually available in Plan mode. Follow the tool's schema, label the recommendation as such, and allow the author to explain in their own words. Ground technical recommendations in the code; recommendations about personal intent are possible suggestions, not established author intent. If no question tool is available, explain that limitation and ask in chat using the same one-question, options-and-recommendation format.
- Wait for the answer before sending the next understanding question or completing the explanation that depends on it. Independent source inspection and execution checks may continue. Elapsed time and a preselected recommendation are not answers.
- Compare the answer with code and execution evidence. If a selection alone leaves a necessary causal explanation unclear, ask for its reason or a small execution example. Follow-up questions also include options and a recommendation while inviting a concrete explanation through free text. Narrow ambiguous answers to one concrete state; explain a misconception briefly, then check another small example. Do not turn this into an endless exam: leave unresolved understanding unconfirmed.
- Reflect the meaning and level of the author's confirmed answers in the relevant report explanation, subject to the assignment's authorship rules. Do not invent intent, understanding, or reflections, copy an incorrect answer into the report, or portray understanding reached after explanation as something the author knew from the start. A suggested option selection alone does not establish independent understanding or authorship.
- If the author skips a question, keep that understanding unconfirmed and defer only the claims that depend on it; verified factual content may proceed. Do not automatically adopt the recommendation. Keep interview working notes separate from the report and do not automatically save verbatim question-and-answer logs to a separate file.

## Keep authorship and evidence clear

- Read the assignment's authorship rules. If it requires the student's own writing, use factual notes, focused questions, and feedback on the student's draft; treat assistant-written prose as provisional material, not proof of direct authorship. Do not promise that a style is undetectable or introduce deliberate mistakes to change its appearance.
- Follow the pre-drafting understanding check above for missing author explanations. Selecting a suggested answer or approving a drafted paragraph does not by itself establish independent understanding or authorship.
- Write in a clear, specific level appropriate to the author. Prefer a small state trace and causal explanation over generic praise, line-by-line paraphrase, speculative intent, or polished but unsupported claims.
- Keep working notes, conflict records, and submission checklists separate from the report body. If an author asks for a review, report concrete issues with locations and repair directions; do not infer the writer from prose style alone.

## Verify the deliverable that actually exists

- For the course above, check the common rubric's mandatory text code and separate report/`.c` submission requirements: code screenshots cannot replace source text in the report (assignment zero), and ZIP submission is treated as non-submission. Run screenshots remain valid execution evidence. Keep the rubric's deferred items out of confirmed checks.
- If the rubric requires a final PDF, verify the exported PDF itself: layout, readable text, code text selection or extraction, and required sections. A Markdown draft, a Notion page, or a successful export command alone does not prove PDF compliance.
- Use an external editor or Notion only when the user requests it. Treat synchronization and export as separate operations and verify their actual outputs. Never claim submission, upload, or completion based on a local draft.
- Finish with the report's confirmed requirements, unresolved conflicts, missing author work, test scope, and format status. State the exact next step needed for completion. Avoid claiming a grade or that all possible inputs were validated.

## Skill check before reuse

When revising this skill, test it against at least these distinct situations: conflicting PDF render/extraction; a report that invents a performance rationale for supplied code or miscounts recorded tests; and a sound Markdown draft whose required PDF has not been rendered or checked. Keep assignment-specific fixtures and service adapters outside this skill unless repetition demonstrates a need for a reusable resource.

Also check the interview flow: a new report with missing core understanding prompts one tool question with options and a recommendation before the dependent explanation; a selection without sufficient reasoning receives a focused follow-up; incorrect or ambiguous answers receive explanation and rechecking; no response stays pending and a skipped question stays unconfirmed without automatic recommendation adoption; sufficient prior answers and formatting-only requests do not trigger repeated interviews; and a missing question tool produces an explicit chat fallback with the same question format. Distinguish simulated behavior checks from live question-tool UI verification.

Also check specialist routing: text-log-only and local-draft requests do not trigger screenshots or unrelated Notion, upload, cover, or merge work; needed terminal screenshots use the capture skill with current evidence and an honest unavailable-capture fallback; requested Notion work uses its specialist without claiming PDF export; cover-only work and a finished-PDF merge with a missing cover take their respective routes without duplicate cover creation; and an audit-originated analysis returns without recursive workflow invocation. Distinguish simulated routing checks from actual terminal, Notion, and PDF operations.
