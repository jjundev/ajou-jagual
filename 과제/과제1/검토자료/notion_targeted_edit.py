"""Apply user-specified, narrow text replacements to the fixed HW1 Notion page."""
from __future__ import annotations

import copy
import argparse
import json
from datetime import datetime
from pathlib import Path

from notion_sync import EVIDENCE, PAGE_ID, NotionAPI, markdown_from_response


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
        if kind == "code":
            payload["language"] = block["code"]["language"]
    return {kind: payload}


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
