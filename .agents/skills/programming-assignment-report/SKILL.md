---
name: programming-assignment-report
description: Use when preparing, reviewing, or finishing a programming assignment report from assignment instructions, source code, and execution results. Applies to 코딩 과제 보고서; not to general essays or implementing the assignment code itself.
---

# Programming assignment reports

Help the author produce a report whose requirements, code explanations, and execution analysis agree with the actual assignment and program. Work from the current artifacts rather than replaying a fixed sequence from an earlier assignment.

## Choose the needed work

Identify what the user has requested and which artifacts exist: assignment prompt or rubric, supplied starter code, implemented code, author-written explanation, execution evidence, and final-format file. Do the relevant work below. A request to review a draft does not require recreating it; a Markdown draft does not imply that a required PDF has been checked.

Keep a compact requirement record with `requirement | source and page | evidence | status`. Include scoring weights, hard-fail conditions, submission format, and deadline only when the sources state them. Use statuses that distinguish **confirmed**, **needs author input**, **source conflict**, **not executed**, and **format not verified**. Do not turn an unknown into a pass.

## Establish the assignment contract

- Read the relevant prompt, rubric, and supplied code before deciding the report's scope. For PDFs, inspect relevant rendered pages as well as extracted text when layout, images, or extraction artifacts could matter.
- For follow-up programming reports in this workspace's **[2026-2] 자료구조 및 알고리즘 이해** course, read [the course report format](references/data-structures-course-format.md). Treat it as the author's recurring format, then compare it with the new assignment's official instructions and explicit choices. Do not apply it to other courses or turn HW1-specific counts into defaults.
- If visible content, extracted text, announcements, or files disagree, record the exact conflict and its sources. Do not silently treat an extraction-only instruction or the visible page as authoritative. Check accessible official updates and ask the user about provenance when the difference changes implementation or grading; state any provisional choice. Do not contact teaching staff without explicit user instruction.
- Separate requirements for code, report content, document layout, and submission. Do not carry an assignment's page layout, point values, or examples into another assignment without checking its rubric; only the linked course format is a reusable layout default within its stated scope.

## Anchor analysis in code and execution

- Compare supplied code with the student's current implementation. Describe a function's inputs, outputs, changed state, and reason for its key conditions or state transitions. Analyze supplied declarations and functions when the rubric requires them. Do not attribute a provided design choice to the student or claim an optimization without measurements or another source.
- Use actual runs for result analysis: record the input, observed output, environment when relevant, and a short trace that explains the result. Choose cases from the assignment examples and material boundaries or errors; never prescribe a fixed test count. Compute reported case totals from the record instead of retyping them.
- If asked to change only comments, preserve executable code and verify that preservation by an appropriate source or token comparison. Re-run focused checks when code changed, evidence became stale, or a required gate needs it. A successful compile, a matching example, and broad correctness are different claims.
- When a current report includes code, compare its code text with the current source after edits. Check every numerical result, return value, and limitation against code or execution evidence. In particular, distinguish a possible future failure from an observed failure.

## Keep authorship and evidence clear

- Read the assignment's authorship rules. If it requires the student's own writing, use factual notes, focused questions, and feedback on the student's draft; treat assistant-written prose as provisional material, not proof of direct authorship. Do not promise that a style is undetectable or introduce deliberate mistakes to change its appearance.
- Ask only about choices or understanding that the files cannot settle. If the user requests stepwise teaching, ask one substantive question at a time and wait for the answer. Selecting a suggested answer or approving a drafted paragraph does not by itself establish independent understanding or authorship.
- Write in a clear, specific level appropriate to the author. Prefer a small state trace and causal explanation over generic praise, line-by-line paraphrase, speculative intent, or polished but unsupported claims.
- Keep working notes, conflict records, and submission checklists separate from the report body. If an author asks for a review, report concrete issues with locations and repair directions; do not infer the writer from prose style alone.

## Verify the deliverable that actually exists

- If the rubric requires a final PDF, verify the exported PDF itself: layout, readable text, code text selection or extraction, and required sections. A Markdown draft, a Notion page, or a successful export command alone does not prove PDF compliance.
- Use an external editor or Notion only when the user requests it. Treat synchronization and export as separate operations and verify their actual outputs. Never claim submission, upload, or completion based on a local draft.
- Finish with the report's confirmed requirements, unresolved conflicts, missing author work, test scope, and format status. State the exact next step needed for completion. Avoid claiming a grade or that all possible inputs were validated.

## Skill check before reuse

When revising this skill, test it against at least these distinct situations: conflicting PDF render/extraction; a report that invents a performance rationale for supplied code or miscounts recorded tests; and a sound Markdown draft whose required PDF has not been rendered or checked. Keep assignment-specific fixtures and service adapters outside this skill unless repetition demonstrates a need for a reusable resource.
