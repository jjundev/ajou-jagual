"""Pull and safely edit a selected Notion report page."""
from __future__ import annotations

import argparse
import copy
import difflib
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import json
from datetime import datetime
from pathlib import Path




NOTION_VERSION = "2026-03-11"


def markdown_from_response(response: dict) -> str:
    if response.get("truncated") or response.get("unknown_block_ids"):
        raise ValueError("Notion Markdown response is incomplete")
    markdown = response.get("markdown")
    if not isinstance(markdown, str):
        raise ValueError("Notion Markdown response has no content")
    return markdown


def save_pulled_markdown(markdown: str, output: Path, backup_dir: Path | None = None) -> Path | None:
    output.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if output.exists():
        previous = output.read_text()
        if previous == markdown:
            return None
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup_dir = backup_dir or output.parent / "검토자료" / "노션_백업"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / f"{output.stem}-backup-{stamp}{output.suffix}"
        backup.write_bytes(output.read_bytes())
    output.write_text(markdown)
    return backup


def pull_markdown(api, page_id: str, output: Path, report: Path,
                  backup_dir: Path | None = None) -> tuple[str, str | None, Path | None]:
    if output.resolve() == report.resolve():
        raise ValueError("Notion output and local report must differ")
    markdown = markdown_from_response(api.request("GET", f"pages/{page_id}/markdown"))
    source = report.read_text()
    previous = output.read_text() if output.exists() else None
    backup = save_pulled_markdown(markdown, output, backup_dir)
    local_diff = "".join(difflib.unified_diff(source.splitlines(keepends=True),
                                              markdown.splitlines(keepends=True),
                                              fromfile=str(report), tofile=str(output)))
    previous_diff = None if previous is None else "".join(difflib.unified_diff(
        previous.splitlines(keepends=True), markdown.splitlines(keepends=True),
        fromfile=str(backup or output), tofile=str(output)))
    return local_diff, previous_diff, backup


class NotionAPI:
    def __init__(self) -> None:
        token = os.environ.get("NOTION_TOKEN")
        if not token:
            raise RuntimeError("NOTION_TOKEN is not set")
        self.headers = {"Authorization": f"Bearer {token}",
                        "Notion-Version": NOTION_VERSION,
                        "Content-Type": "application/json"}

    def request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = "https://api.notion.com/v1/" + path
        data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
        request = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        for attempt in range(5):
            try:
                with urllib.request.urlopen(request, timeout=35) as response:
                    return json.load(response)
            except urllib.error.HTTPError as error:
                detail = json.loads(error.read().decode())
                if method == "GET" and error.code in (429, 500, 502, 503, 504, 529) and attempt < 4:
                    delay = int(error.headers.get("Retry-After", min(2 ** attempt, 30)))
                    time.sleep(delay)
                    continue
                raise RuntimeError(f"Notion {method} {path}: HTTP {error.code} "
                                   f"{detail.get('code')}: {detail.get('message')}") from None
        raise RuntimeError("Notion GET retry limit reached")

    def children(self, block_id: str) -> list[dict]:
        result = []
        cursor = None
        while True:
            query = f"blocks/{block_id}/children?page_size=100"
            if cursor:
                query += "&start_cursor=" + urllib.parse.quote(cursor)
            response = self.request("GET", query)
            result.extend(response["results"])
            cursor = response.get("next_cursor")
            if not cursor:
                return result

    def tree(self, block_id: str) -> list[dict]:
        result = self.children(block_id)
        for block in result:
            if block.get("has_children"):
                block["_children"] = self.tree(block["id"])
        return result


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


def apply_edits(api, page_id: str, edits: list[dict], evidence: Path) -> list[str]:
    if not isinstance(edits, list) or not edits:
        raise ValueError("edits must be a nonempty list")
    keys = [edit.get("block_id") for edit in edits]
    if len(keys) != len(set(keys)):
        raise ValueError("Each block may be edited once per batch")
    tree = api.tree(page_id)
    members = set(_ids(tree))
    prepared = []
    for edit in edits:
        key = edit["block_id"]
        if key not in members:
            raise ValueError(f"Block {key} is outside the selected page")
        before = api.request("GET", f"blocks/{key}")
        body = build_update(before, edit)
        prepared.append((key, before, body))
    markdown = markdown_from_response(api.request("GET", f"pages/{page_id}/markdown"))
    evidence.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    prefix = evidence / f"before-targeted-{stamp}"
    prefix.with_suffix(".json").write_text(
        json.dumps({"page_id": page_id, "tree": tree,
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
    commands = parser.add_subparsers(dest="command", required=True)
    pull = commands.add_parser("pull")
    pull.add_argument("--page-id", required=True)
    pull.add_argument("--report", type=Path, required=True)
    pull.add_argument("--output", type=Path, required=True)
    pull.add_argument("--backup-dir", type=Path)
    edit = commands.add_parser("edit")
    edit.add_argument("--page-id", required=True)
    edit.add_argument("--plan", type=Path, required=True)
    edit.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    api = NotionAPI()
    if args.command == "pull":
        local_diff, previous_diff, backup = pull_markdown(
            api, args.page_id, args.output, args.report, args.backup_dir)
        if backup:
            print(f"Previous download saved: {backup}")
        print(f"Downloaded Notion Markdown: {args.output}")
        print("\n=== Previous Notion download -> current Notion download ===")
        if previous_diff is None:
            print("No previous download at this output path")
        else:
            print(previous_diff or "No change from previous download")
        print("\n=== Local report -> current Notion download ===")
        print(local_diff or "No difference from local report")
    else:
        document = json.loads(args.plan.read_text())
        if document.get("page_id") != args.page_id:
            raise ValueError("Edit plan page_id differs from --page-id")
        print("Verified blocks:", apply_edits(api, args.page_id, document["edits"], args.evidence))


if __name__ == "__main__":
    main()
