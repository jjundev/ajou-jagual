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
        if kind == "code":
            payload["language"] = block["code"]["language"]
    return {kind: payload}
