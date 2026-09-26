# Notion Report Sync Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a project-local skill that compares the HW1 Notion report with local Markdown and safely applies user-requested edits to specified Notion blocks.

**Architecture:** Build on the existing `notion_sync.py` on `codex/course-report-format`. Keep the rich-text replacement and API update logic in one focused `notion_targeted_edit.py`; the skill routes ordinary review to the existing pull command and explicit edits to that helper. A plan JSON file is an ephemeral input, never a committed artifact.

**Tech Stack:** Python 3 standard library, Notion REST API (`Notion-Version: 2026-03-11`), `unittest`, Codex project-local `SKILL.md`.

**Spec:** `docs/superpowers/specs/2026-09-26-notion-report-sync-skill-design.md` (currently in the main checkout; copy it and this plan into the implementation worktree before starting Task 1). The implementation base is `codex/course-report-format`, which contains `notion_sync.py`; the current main checkout does not.

## Global Constraints

- Only the fixed HW1 page ID `4b5b06d263bc8255b539819393d50d19` and its descendant blocks are in scope.
- Ordinary use pulls and compares; it does not overwrite `보고서.md` or mutate Notion.
- A Notion edit requires an explicit user request naming the intended content. Never route routine edits through `push` or `layout-table`.
- Preflight every target, then save both a block-tree and Markdown backup before the first PATCH. Preserve rich-text annotations and links; reject unsupported rich-text shapes.
- After an uncertain PATCH result, do not retry automatically. Read the block and report its state. Verify every successful PATCH by GET.
- Keep `NOTION_TOKEN` in the environment only. PDF export and cover merging remain separate user workflows.

## Review Focus

1. An edit targets a block outside the HW1 page: reject all edits before PATCH (Task 2: `test_foreign_block`).
2. A requested phrase spans two rich-text items: reject it without dropping annotations (Task 1: `test_cross_item_rejected`).
3. One of several targets has stale text: reject the whole batch before PATCH (Task 2: `test_stale_batch`).
4. A PATCH times out after reaching Notion: GET the block once, report uncertain state, and never repeat PATCH (Task 2: `test_uncertain_patch`).
5. The live block changes between preflight and PATCH: compare `last_edited_time` immediately before that PATCH and stop (Task 2: `test_concurrent_change`).

## File Map

- `과제/과제1/검토자료/notion_targeted_edit.py`: validate edit JSON, preserve supported rich-text data, preflight all targets, back up, PATCH individually, and verify.
- `과제/과제1/검토자료/test_notion_targeted_edit.py`: pure replacement and fake-API workflow tests; no live Notion writes.
- `.agents/skills/notion-report-sync/SKILL.md`: trigger, read/compare process, explicit edit process, stop conditions, and PDF boundary.
- `과제/과제1/검토자료/노션_API_동기화.md`: one link to the new helper and a concise command example; keep existing historical notes.
- `docs/superpowers/specs/2026-09-26-notion-report-sync-skill-design.md`: the approved design, copied from the main checkout.

## Starting State

Use the `using-git-worktrees` skill and Codex managed worktree tool at execution time. Reuse an available checkout if suitable; otherwise create one from `codex/course-report-format`. Check `git status --short --branch`, confirm `notion_sync.py` and its tests exist, and copy the two design documents from the current main checkout into the new worktree. Do not move or delete the unrelated untracked cover and temporary files in main. Run baseline:

```bash
python3 -m unittest discover -s 과제/과제1/검토자료 -p 'test_notion_sync.py' -v
```

Expected: 8 passing tests. If the branch or baseline differs, inspect it before applying this plan.

---

### Task 1: Rich-text replacement with exact matching

**Files:**
- Create: `과제/과제1/검토자료/notion_targeted_edit.py`
- Create: `과제/과제1/검토자료/test_notion_targeted_edit.py`

**Interfaces:**
- Consumes: one Notion block dict and an edit dict: `block_id`, `type`, `old_text`, `new_text`, and optional zero-based `cell_index` for a `table_row`.
- Produces: `build_update(block: dict, edit: dict) -> dict`, returning the PATCH body keyed by block type. Task 2 calls this without changing its signature.

- [ ] **Step 1: Write failing tests for paragraph, table cell, annotation preservation, ambiguity, and cross-item text.**

```python
# test_notion_targeted_edit.py
import copy
import unittest
from notion_targeted_edit import build_update


def rich(content, **annotations):
    return {"type": "text", "text": {"content": content},
            "annotations": annotations}


class ReplacementTests(unittest.TestCase):
    def test_paragraph_preserves_annotations_and_link(self):
        item = rich("앞: 뒤", bold=True)
        item["text"]["link"] = {"url": "https://example.org"}
        block = {"id": "a", "type": "paragraph", "paragraph": {"rich_text": [item]}}
        original = copy.deepcopy(block)
        body = build_update(block, {"block_id": "a", "type": "paragraph",
                                    "old_text": "앞: 뒤", "new_text": "앞:  뒤"})
        self.assertEqual(body["paragraph"]["rich_text"][0]["text"]["content"], "앞:  뒤")
        self.assertEqual(body["paragraph"]["rich_text"][0]["annotations"], {"bold": True})
        self.assertEqual(body["paragraph"]["rich_text"][0]["text"]["link"],
                         {"url": "https://example.org"})
        self.assertEqual(block, original)

    def test_table_cell_updates_only_selected_cell(self):
        block = {"id": "b", "type": "table_row", "table_row": {"cells": [[rich("other")], [rich("old")]]}}
        body = build_update(block, {"block_id": "b", "type": "table_row",
                                    "cell_index": 1, "old_text": "old", "new_text": "new"})
        self.assertEqual(body["table_row"]["cells"][0][0]["text"]["content"], "other")
        self.assertEqual(body["table_row"]["cells"][1][0]["text"]["content"], "new")

    def test_cross_item_rejected(self):
        block = {"id": "a", "type": "paragraph", "paragraph": {"rich_text": [rich("ab"), rich("cd")]}}
        with self.assertRaisesRegex(ValueError, "one text item"):
            build_update(block, {"block_id": "a", "type": "paragraph",
                                 "old_text": "bc", "new_text": "BC"})

    def test_repeated_phrase_rejected(self):
        block = {"id": "a", "type": "code", "code": {"rich_text": [rich("x x")]}}
        with self.assertRaisesRegex(ValueError, "exactly once"):
            build_update(block, {"block_id": "a", "type": "code",
                                 "old_text": "x", "new_text": "y"})

    def test_bad_cell_index_rejected(self):
        block = {"id": "b", "type": "table_row", "table_row": {"cells": [[rich("x")]]}}
        with self.assertRaisesRegex(ValueError, "cell_index"):
            build_update(block, {"block_id": "b", "type": "table_row",
                                 "cell_index": 2, "old_text": "x", "new_text": "y"})
```

- [ ] **Step 2: Run the focused tests and confirm import failure.**

Run: `python3 -m unittest discover -s 과제/과제1/검토자료 -p 'test_notion_targeted_edit.py' -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'notion_targeted_edit'`.

- [ ] **Step 3: Implement the minimal pure replacement function.**

```python
# notion_targeted_edit.py
"""Apply user-specified, narrow text replacements to the fixed HW1 Notion page."""
from __future__ import annotations

import copy


def build_update(block: dict, edit: dict) -> dict:
    kind = block.get("type")
    if block.get("id") != edit.get("block_id") or kind != edit.get("type"):
        raise ValueError("Block identity or type changed")
    if kind not in {"paragraph", "heading_1", "heading_2", "heading_3",
                    "bulleted_list_item", "numbered_list_item", "code", "table_row"}:
        raise ValueError(f"Unsupported block type: {kind}")
    old, new = edit.get("old_text"), edit.get("new_text")
    if not isinstance(old, str) or not old or not isinstance(new, str):
        raise ValueError("old_text must be nonempty and new_text must be a string")
    if len(new) > 1900:
        raise ValueError("new_text exceeds the supported single-item length")
    payload = copy.deepcopy(block[kind])
    if kind == "table_row":
        index = edit.get("cell_index")
        cells = payload.get("cells", [])
        if type(index) is not int or not 0 <= index < len(cells):
            raise ValueError("Invalid cell_index")
        items = cells[index]
    else:
        if "cell_index" in edit:
            raise ValueError("cell_index is only valid for table_row")
        items = payload.get("rich_text", [])
    if any(item.get("type") != "text" for item in items):
        raise ValueError("Unsupported non-text rich-text item")
    matches = [(item, item["text"]["content"].count(old)) for item in items
               if item.get("type") == "text" and isinstance(item.get("text", {}).get("content"), str)]
    if sum(count for _, count in matches) != 1:
        raise ValueError("old_text must occur exactly once in one text item")
    item = next(item for item, count in matches if count)
    item["text"]["content"] = item["text"]["content"].replace(old, new, 1)
    if len(item["text"]["content"]) > 2000:
        raise ValueError("Updated Notion text item exceeds 2000 characters")
    # Notion GET fields such as plain_text, href, and block metadata are not writable.
    def writable(text_item):
        return {key: copy.deepcopy(value) for key, value in text_item.items()
                if key in {"type", "text", "annotations", "mention", "equation"}}
    if kind == "table_row":
        payload = {"cells": [[writable(item) for item in cell] for cell in payload["cells"]]}
    else:
        payload = {"rich_text": [writable(item) for item in items]}
    return {kind: payload}
```

Use `old_text` that fits wholly inside one text item. If Notion split it across items, stop and prepare a reviewed, case-specific edit; do not flatten all items. For `code`, preserve the existing `language` property by adding it to the body from the retrieved block when Notion requires it; pin that behavior with a test before using code-block edits live.

- [ ] **Step 4: Run the focused tests; add and run one code-language test.**

```python
def test_code_language_survives(self):
    block = {"id": "c", "type": "code", "code": {"rich_text": [rich("a: ")],
                                                   "language": "c"}}
    body = build_update(block, {"block_id": "c", "type": "code",
                                "old_text": "a: ", "new_text": "a:  "})
    self.assertEqual(body["code"]["language"], "c")
```

Update the non-table branch to retain `language` for `code`:

```python
payload = {"rich_text": [writable(item) for item in items]}
if kind == "code":
    payload["language"] = block["code"]["language"]
```

Run: `python3 -m unittest discover -s 과제/과제1/검토자료 -p 'test_notion_targeted_edit.py' -v`

Expected: all six tests PASS.

- [ ] **Step 5: Commit the pure edit builder and its tests.**

```bash
git add 과제/과제1/검토자료/notion_targeted_edit.py 과제/과제1/검토자료/test_notion_targeted_edit.py
git commit -m "feat(notion): preserve formatting in targeted text edits"
```

### Task 2: Preflight, backup, apply, and readback

**Files:**
- Modify: `과제/과제1/검토자료/notion_targeted_edit.py`
- Modify: `과제/과제1/검토자료/test_notion_targeted_edit.py`

**Interfaces:**
- Consumes: `build_update(block, edit)` from Task 1; `NotionAPI.request(method, path, body=None)` and `NotionAPI.tree(PAGE_ID)` from `notion_sync.py`.
- Produces: `apply_edits(api, edits: list[dict], evidence: Path) -> list[str]`; CLI `python3 과제/과제1/검토자료/notion_targeted_edit.py <edit-plan.json>`.

- [ ] **Step 1: Write fake-API tests for the five Review Focus risks.**

```python
# Append in test_notion_targeted_edit.py
import tempfile
from pathlib import Path
from notion_targeted_edit import apply_edits


class FakeAPI:
    def __init__(self, blocks, member_ids=None, fail_patch=False):
        self.blocks = copy.deepcopy(blocks)
        self.member_ids = set(member_ids or blocks)
        self.fail_patch = fail_patch
        self.patches = []

    def tree(self, page_id):
        return [copy.deepcopy(self.blocks[key]) for key in self.member_ids]

    def request(self, method, path, body=None):
        if method == "GET" and path.endswith("/markdown"):
            return {"markdown": "# snapshot\n", "truncated": False, "unknown_block_ids": []}
        key = path.removeprefix("blocks/")
        if method == "GET":
            return copy.deepcopy(self.blocks[key])
        self.patches.append((key, copy.deepcopy(body)))
        if self.fail_patch:
            raise TimeoutError("response lost")
        kind = self.blocks[key]["type"]
        self.blocks[key][kind].update(copy.deepcopy(body[kind]))
        self.blocks[key]["last_edited_time"] = "after"
        return copy.deepcopy(self.blocks[key])


def block(key, value="old"):
    return {"id": key, "type": "paragraph", "last_edited_time": "before",
            "paragraph": {"rich_text": [rich(value)]}}


class ApplyTests(unittest.TestCase):
    def test_foreign_block(self):
        api = FakeAPI({"a": block("a"), "foreign": block("foreign")}, {"a"})
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "outside"):
                apply_edits(api, [{"block_id": "foreign", "type": "paragraph",
                                   "old_text": "old", "new_text": "new"}], Path(directory))
        self.assertEqual(api.patches, [])

    def test_stale_batch(self):
        api = FakeAPI({"a": block("a"), "b": block("b", "changed")})
        edits = [{"block_id": key, "type": "paragraph", "old_text": "old", "new_text": "new"}
                 for key in ("a", "b")]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "exactly once"):
                apply_edits(api, edits, Path(directory))
        self.assertEqual(api.patches, [])

    def test_uncertain_patch(self):
        api = FakeAPI({"a": block("a")}, fail_patch=True)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "uncertain"):
                apply_edits(api, [{"block_id": "a", "type": "paragraph",
                                   "old_text": "old", "new_text": "new"}], Path(directory))
            self.assertTrue(list(Path(directory).glob("before-targeted-*.json")))
        self.assertEqual(len(api.patches), 1)

    def test_concurrent_change(self):
        class ChangingAPI(FakeAPI):
            def request(self, method, path, body=None):
                if method == "GET" and path == "blocks/a":
                    self.gets = getattr(self, "gets", 0) + 1
                    if self.gets == 2:
                        self.blocks["a"]["last_edited_time"] = "someone-else"
                return super().request(method, path, body)
        api = ChangingAPI({"a": block("a")})
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "changed"):
                apply_edits(api, [{"block_id": "a", "type": "paragraph",
                                   "old_text": "old", "new_text": "new"}], Path(directory))
        self.assertEqual(api.patches, [])

    def test_success_reads_back(self):
        api = FakeAPI({"a": block("a")})
        with tempfile.TemporaryDirectory() as directory:
            done = apply_edits(api, [{"block_id": "a", "type": "paragraph",
                                      "old_text": "old", "new_text": "new"}], Path(directory))
            self.assertEqual(done, ["a"])
            self.assertTrue(list(Path(directory).glob("before-targeted-*.md")))
        self.assertEqual(api.blocks["a"]["paragraph"]["rich_text"][0]["text"]["content"], "new")
```

- [ ] **Step 2: Run tests to verify `apply_edits` is missing.**

Run: `python3 -m unittest discover -s 과제/과제1/검토자료 -p 'test_notion_targeted_edit.py' -v`

Expected: FAIL because `apply_edits` cannot be imported.

- [ ] **Step 3: Implement preflight and backup before any PATCH.**

```python
# Append to notion_targeted_edit.py
import argparse
import json
from datetime import datetime
from pathlib import Path
from notion_sync import EVIDENCE, PAGE_ID, NotionAPI, markdown_from_response


def _ids(tree):
    for node in tree:
        yield node["id"]
        yield from _ids(node.get("_children", []))


def _editable_state(kind: str, data: dict):
    def core(items):
        return [(item.get("type"), item.get("text"), item.get("annotations"))
                for item in items]
    if kind == "table_row":
        return [core(cell) for cell in data["cells"]]
    result = core(data["rich_text"])
    return (result, data.get("language")) if kind == "code" else result


def apply_edits(api, edits: list[dict], evidence: Path) -> list[str]:
    if not isinstance(edits, list) or not edits:
        raise ValueError("edits must be a nonempty list")
    keys = [edit.get("block_id") for edit in edits]
    if len(keys) != len(set(keys)):
        raise ValueError("Each block may be edited once per batch")
    tree = api.tree(PAGE_ID)
    members = set(_ids(tree))
    prepared = []
    for edit in edits:
        key = edit["block_id"]
        if key not in members:
            raise ValueError(f"Block {key} is outside the HW1 page")
        before = api.request("GET", f"blocks/{key}")
        body = build_update(before, edit)
        prepared.append((key, before, body))
    markdown = markdown_from_response(api.request("GET", f"pages/{PAGE_ID}/markdown"))
    evidence.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    prefix = evidence / f"before-targeted-{stamp}"
    prefix.with_suffix(".json").write_text(
        json.dumps({"page_id": PAGE_ID, "tree": tree,
                    "blocks": {key: before for key, before, _ in prepared},
                    "edits": edits}, ensure_ascii=False, indent=2) + "\n")
    prefix.with_suffix(".md").write_text(markdown)
    print(f"Pre-edit snapshots: {prefix.with_suffix('.json')}, {prefix.with_suffix('.md')}")
    completed = []
    for key, before, body in prepared:
        try:
            live = api.request("GET", f"blocks/{key}")
        except Exception as error:
            raise RuntimeError(f"Pre-PATCH GET failed for {key}; completed={completed}") from error
        if (live.get("last_edited_time") != before.get("last_edited_time")
                or live[before["type"]] != before[before["type"]]):
            raise RuntimeError(f"Block {key} changed before PATCH; completed={completed}")
        try:
            api.request("PATCH", f"blocks/{key}", body)
        except Exception as error:
            try:
                current = api.request("GET", f"blocks/{key}")
            except Exception as recovery_error:
                raise RuntimeError(f"PATCH uncertain for {key}; completed={completed}; "
                                   "recovery GET failed; inspect before retry") from recovery_error
            observed = evidence / f"uncertain-{key}-{stamp}.json"
            observed.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n")
            kind = before["type"]
            if current.get("type") != kind:
                state = "diverged"
            else:
                current_state = _editable_state(kind, current[kind])
                if current_state == _editable_state(kind, body[kind]):
                    state = "matches expected"
                elif current_state == _editable_state(kind, before[kind]):
                    state = "unchanged"
                else:
                    state = "diverged"
            raise RuntimeError(f"PATCH uncertain for {key}; completed={completed}; "
                               f"state={state}; observed={observed}; inspect before retry") from error
        try:
            actual = api.request("GET", f"blocks/{key}")
        except Exception as error:
            raise RuntimeError(f"Readback uncertain for {key}; completed={completed}") from error
        kind = before["type"]
        same = _editable_state(kind, actual[kind]) == _editable_state(kind, body[kind])
        if not same:
            raise RuntimeError(f"Readback mismatch for {key}; completed={completed}")
        completed.append(key)
    return completed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    document = json.loads(args.plan.read_text())
    if document.get("page_id") != PAGE_ID:
        raise ValueError("Edit plan page_id differs from the fixed HW1 page")
    print("Verified blocks:", apply_edits(NotionAPI(), document["edits"], EVIDENCE))


if __name__ == "__main__":
    main()
```

Before marking this step done, restrict `build_update` to writable rich-text item fields and ensure `code.language` survives as Task 1 specified. For a Notion block type whose PATCH body is rejected by the live API, stop and report; do not fall back to page-wide replacement.

- [ ] **Step 4: Run all Notion unit tests and inspect backup contents.**

Run: `python3 -m unittest discover -s 과제/과제1/검토자료 -p 'test_notion*.py' -v`

Expected: existing 8 tests plus the new tests PASS. Inspect that the fake-API success test wrote both backup files before PATCH. Do not perform a live PATCH just to test the helper.

- [ ] **Step 5: Commit the API update workflow.**

```bash
git add 과제/과제1/검토자료/notion_targeted_edit.py 과제/과제1/검토자료/test_notion_targeted_edit.py
git commit -m "feat(notion): preflight and verify targeted block edits"
```

### Task 3: Project-local skill and usage note

**Files:**
- Create: `.agents/skills/notion-report-sync/SKILL.md`
- Modify: `과제/과제1/검토자료/노션_API_동기화.md`
- Add: `docs/superpowers/specs/2026-09-26-notion-report-sync-skill-design.md`

**Interfaces:**
- Consumes: `notion_sync.py pull`, `notion_targeted_edit.py <edit-plan.json>`, and the exact fixed paths from `notion_sync.py`.
- Produces: a discoverable project skill; no new runtime API.

- [ ] **Step 1: Draft the skill with the exact frontmatter and workflow.**

````markdown
---
name: notion-report-sync
description: Compare the project's HW1 Notion report with local Markdown and, when explicitly requested, update specified blocks while preserving formatting. Not for other Notion pages, databases, or PDF export.
---

# HW1 Notion report sync

The fixed page and paths live in `과제/과제1/검토자료/notion_sync.py`. Use its current `PAGE_ID`; do not substitute a page inferred from prose. Read `과제/과제1/검토자료/노션_API_동기화.md` before a live operation.

## Review a Notion edit

1. Run `python3 과제/과제1/검토자료/notion_sync.py pull` with `NOTION_TOKEN` in the environment. If the API says truncated or unknown blocks, stop; do not treat a partial download as a complete report.
2. Compare `과제/과제1/보고서_노션.md` with its preceding backup and with `과제/과제1/보고서.md`. Report actual wording, table-cell, code, heading, blank-line, and `<br>` differences separately. Do not normalize intentional spaces or blank blocks away. Distinguish Notion Markdown serialization from an actual content change.
3. For layout that Markdown cannot establish, inspect the live block tree or the PDF exported by the user. Do not claim to have verified the PDF from Markdown alone. Never overwrite `보고서.md` automatically.

## Edit specified blocks

Only after a user request to change specific Notion content: identify the exact block IDs and old text from a current API read. Prepare a temporary JSON edit plan with `page_id` and `edits`, each containing `block_id`, `type`, `old_text`, `new_text`, and `cell_index` for a table row. Review the plan against the requested change. Run `python3 과제/과제1/검토자료/notion_targeted_edit.py <edit-plan.json>`. The helper checks every target, saves a snapshot, patches one block at a time, and reads each back. Report the snapshot path and completed IDs. If preflight, PATCH, or readback fails, report the exact stage and any partial completion; do not blindly rerun an uncertain PATCH. Never use `push` or `layout-table` for ordinary edits.

`NOTION_TOKEN` stays in the environment. The user's final Notion PDF export and separate cover merge are outside this skill.
````

- [ ] **Step 2: Add this exact short command example to the existing sync note.**

````markdown
## 지정 블록만 수정할 때

`.agents/skills/notion-report-sync/SKILL.md`의 범위와 중단 조건을 따른다. 현재 블록 ID와 텍스트를 먼저 확인하고, 임시 JSON 파일에 `page_id`와 `edits`를 적은 뒤 다음을 실행한다.

```bash
python3 과제/과제1/검토자료/notion_targeted_edit.py /tmp/hw1-notion-edit.json
```

이 명령은 전체 보고서 재업로드가 아니라 지정 블록 수정에만 사용한다.
````

- [ ] **Step 3: Validate the skill and run the full Notion tests.**

```bash
python3 /Users/hyunjun_macbook_pro/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/notion-report-sync
python3 -m unittest discover -s 과제/과제1/검토자료 -p 'test_notion*.py' -v
git diff --check
```

Expected: skill validator reports `Skill is valid!`, all tests pass, and `git diff --check` is silent. Confirm the skill does not direct an automatic full-page push, automatic report overwrite, or PDF claim from Markdown.

- [ ] **Step 4: Commit the skill, spec, and usage note.**

```bash
git add .agents/skills/notion-report-sync/SKILL.md 과제/과제1/검토자료/노션_API_동기화.md docs/superpowers/specs/2026-09-26-notion-report-sync-skill-design.md
git commit -m "feat(skill): guide HW1 Notion report synchronization"
```

## Self-Review at Execution

Check every spec bullet against Tasks 1–3; verify the helper does not write a token or automatically run `push`. Inspect the final diff and branch status. The tests use a fake API and therefore prove local decisions and request shapes, not live Notion acceptance; an authorized real edit must still be verified by its GET readback and, where visual layout matters, the user's exported PDF.

## Scope amendment after implementation

The user clarified that the skill must serve other assignment reports. The shared pull/compare and targeted-edit code was moved to `.agents/skills/notion-report-sync/scripts/notion_report.py`; its CLI now accepts the page ID and assignment paths. The original task steps above document the first HW1-only implementation, not the current reusable interface. `과제/과제1/검토자료/notion_sync.py` remains solely for HW1's historical upload and table migration.
