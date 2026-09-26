"""Upload the HW1 report as Notion blocks and retrieve Notion's Markdown."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


PAGE_ID = "4b5b06d263bc8255b539819393d50d19"
NOTION_VERSION = "2026-03-11"
REPORT = Path(__file__).resolve().parents[1] / "보고서.md"
EVIDENCE = Path(__file__).resolve().parent / "notion_api"
INLINE = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\$[^$]+\$)")


def _text_parts(text: str, annotations: dict | None = None) -> list[dict]:
    """Keep individual Notion rich-text items below its 2,000-char limit."""
    if not text:
        return []
    result = []
    for start in range(0, len(text), 1900):
        item = {"type": "text", "text": {"content": text[start : start + 1900]}}
        if annotations:
            item["annotations"] = annotations
        result.append(item)
    return result


def _rich(text: str) -> list[dict]:
    result = []
    position = 0
    for match in INLINE.finditer(text):
        result.extend(_text_parts(text[position : match.start()]))
        token = match.group(0)
        if token.startswith("**"):
            result.extend(_text_parts(token[2:-2], {"bold": True}))
        elif token.startswith("`"):
            result.extend(_text_parts(token[1:-1], {"code": True}))
        else:
            result.extend(_text_parts(token[1:-1]))
        position = match.end()
    result.extend(_text_parts(text[position:]))
    return result


def _block(kind: str, payload: dict) -> dict:
    return {"object": "block", "type": kind, kind: payload}


def _cell_text(text: str) -> list[dict]:
    return _rich(text.strip())


def _table(lines: list[str]) -> dict:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in lines]
    width = len(rows[0])
    if width < 1 or any(len(row) != width for row in rows):
        raise ValueError("Markdown table has inconsistent columns")
    if len(rows) < 3 or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
        raise ValueError("Markdown table separator is invalid")
    children = [_block("table_row", {"cells": [_cell_text(value) for value in row]})
                for row in [rows[0], *rows[2:]]]
    return _block("table", {"table_width": width, "has_column_header": True,
                            "has_row_header": False, "children": children})


def _starts_block(line: str) -> bool:
    return (line.startswith(("# ", "## ", "### ", "```", "- ", "> ", "|"))
            or line.strip() == "---")


def _parse_blocks(markdown: str) -> list[dict]:
    lines = markdown.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            language = line[3:].strip().lower()
            if language not in ("c", "text", ""):
                raise ValueError(f"Unsupported code language: {language}")
            end = i + 1
            while end < len(lines) and not lines[end].startswith("```"):
                end += 1
            if end == len(lines):
                raise ValueError("Unclosed code fence")
            content = "\n".join(lines[i + 1 : end])
            blocks.append(_block("code", {"rich_text": _text_parts(content),
                                          "language": "c" if language == "c" else "plain text"}))
            i = end + 1
            continue
        heading = re.match(r"^(#{1,3}) (.*)$", line)
        if heading:
            kind = f"heading_{len(heading.group(1))}"
            blocks.append(_block(kind, {"rich_text": _rich(heading.group(2))}))
            i += 1
            continue
        if line.strip() == "---":
            blocks.append(_block("divider", {}))
            i += 1
            continue
        if line.startswith("|"):
            end = i + 1
            while end < len(lines) and lines[end].startswith("|"):
                end += 1
            blocks.append(_table(lines[i:end]))
            i = end
            continue
        if line.startswith("- "):
            blocks.append(_block("bulleted_list_item", {"rich_text": _rich(line[2:])}))
            i += 1
            continue
        if line.startswith("> "):
            end = i + 1
            while end < len(lines) and lines[end].startswith("> "):
                end += 1
            text = " ".join(part[2:] for part in lines[i:end])
            blocks.append(_block("quote", {"rich_text": _rich(text)}))
            i = end
            continue
        end = i + 1
        while end < len(lines) and lines[end].strip() and not _starts_block(lines[end]):
            end += 1
        text = " ".join(lines[i:end])
        blocks.append(_block("paragraph", {"rich_text": _rich(text)}))
        i = end
    return blocks


def _plain(block: dict) -> str:
    kind = block["type"]
    return "".join(item["text"]["content"] for item in block[kind].get("rich_text", [])
                   if item["type"] == "text")


def _function_pair(group: list[dict]) -> list[dict]:
    heading = group[0]
    middle = group[1:]
    divider = middle[-1] if middle and middle[-1]["type"] == "divider" else None
    if divider:
        middle = middle[:-1]
    code = [block for block in middle if block["type"] == "code"]
    analysis = [block for block in middle if block["type"] != "code"]
    if len(code) != 1 or not analysis:
        raise ValueError(f"Function {_plain(heading)} needs one code block and analysis")
    columns = [
        _block("column", {"width_ratio": 0.5, "children": code}),
        _block("column", {"width_ratio": 0.5, "children": analysis}),
    ]
    result = [heading, _block("column_list", {"children": columns})]
    if divider:
        result.append(divider)
    return result


def build_blocks(markdown: str) -> list[dict]:
    """Convert the report to Notion blocks, pairing each function's code and analysis."""
    original = _parse_blocks(markdown)
    output = []
    i = 0
    in_source = False
    groups = 0
    while i < len(original):
        block = original[i]
        kind = block["type"]
        if kind == "heading_2":
            in_source = _plain(block).startswith("2. 소스코드 분석")
        if in_source and kind == "heading_3":
            end = i + 1
            while end < len(original) and original[end]["type"] not in ("heading_2", "heading_3"):
                end += 1
            output.extend(_function_pair(original[i:end]))
            groups += 1
            i = end
            continue
        output.append(block)
        i += 1
    return output


def markdown_from_response(response: dict) -> str:
    if response.get("truncated"):
        raise ValueError("Notion markdown response is truncated")
    if response.get("unknown_block_ids"):
        raise ValueError("Notion markdown contains unknown blocks")
    markdown = response.get("markdown")
    if not isinstance(markdown, str):
        raise ValueError("Notion markdown response has no content")
    return markdown


def table_from_columns(left_blocks: list[dict], right_blocks: list[dict]) -> dict:
    """Turn a live function's two Notion columns into one two-column table."""
    if len(left_blocks) != 1 or left_blocks[0]["type"] != "code":
        raise ValueError("Left Notion column must contain exactly one code block")
    code = _content(left_blocks[0])
    explanation = []
    for block in right_blocks:
        kind = block["type"]
        if kind not in ("paragraph", "bulleted_list_item"):
            raise ValueError(f"Unsupported function explanation block: {kind}")
        text = _content(block)
        explanation.append(("• " if kind == "bulleted_list_item" else "") + text)
    if not code.strip() or not explanation:
        raise ValueError("Function table needs code and explanation")
    rows = [
        _block("table_row", {"cells": [_rich("소스코드"), _rich("기능 명세와 분석")]}),
        _block("table_row", {"cells": [
            _text_parts(code, {"code": True}), _text_parts("\n".join(explanation))]}),
    ]
    return _block("table", {"table_width": 2, "has_column_header": True,
                            "has_row_header": False, "children": rows})


def save_pulled_markdown(markdown: str, output: Path) -> Path | None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        previous = output.read_text()
        if previous == markdown:
            return None
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = output.with_name(f"{output.stem}-backup-{stamp}{output.suffix}")
        backup.write_bytes(output.read_bytes())
    else:
        backup = None
    output.write_text(markdown)
    return backup


def assert_push_allowed(manifest_path: Path) -> None:
    if manifest_path.exists():
        status = json.loads(manifest_path.read_text()).get("status")
        if status == "complete":
            raise RuntimeError("This page was already uploaded; pull Notion edits before another push")
        raise RuntimeError("A previous push is incomplete; inspect its manifest before retrying")


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
                if error.code in (429, 529) or (method == "GET" and error.code in (500, 502, 503, 504)):
                    if attempt < 4:
                        delay = int(error.headers.get("Retry-After", min(2 ** attempt, 30)))
                        time.sleep(delay)
                        continue
                raise RuntimeError(f"Notion {method} {path}: HTTP {error.code} "
                                   f"{detail.get('code')}: {detail.get('message')}") from None
        raise RuntimeError("Notion request retry limit reached")

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


def _content(block: dict) -> str:
    return "".join(item.get("plain_text", item.get("text", {}).get("content", ""))
                   for item in block[block["type"]].get("rich_text", []))


def _check_remote_code(api: NotionAPI, new_blocks: list[dict], expected: list[str]) -> None:
    actual = []
    for block in new_blocks:
        if block["type"] != "column_list":
            continue
        columns = api.children(block["id"])
        if len(columns) != 2:
            raise RuntimeError("Notion did not create two columns")
        code_blocks = api.children(columns[0]["id"])
        if len(code_blocks) != 1 or code_blocks[0]["type"] != "code":
            raise RuntimeError("Notion left column has no code block")
        actual.append(_content(code_blocks[0]))
    if actual != expected:
        raise RuntimeError("Notion code text differs from the local C code blocks")


def _table_cell(block: dict, index: int) -> str:
    if block["type"] != "table_row":
        raise RuntimeError("Notion table does not contain table rows")
    return "".join(item.get("plain_text", item.get("text", {}).get("content", ""))
                   for item in block["table_row"]["cells"][index])


def locate_function_layout(root: list[dict], heading_id: str,
                           old_column_id: str) -> tuple[dict | None, dict | None]:
    """Find a function's live table and original columns after its heading."""
    index = next((i for i, block in enumerate(root) if block["id"] == heading_id), None)
    if index is None:
        raise RuntimeError("Function heading disappeared from Notion")
    following = root[index + 1 : index + 3]
    table = following[0] if following and following[0]["type"] == "table" else None
    old = next((block for block in following if block["id"] == old_column_id), None)
    if table is None and (old is None or following[0]["id"] != old_column_id):
        raise RuntimeError("Function layout has unexpected blocks after its heading")
    return table, old


def layout_table() -> None:
    """Replace each live code/analysis column pair with a two-column table."""
    EVIDENCE.mkdir(exist_ok=True)
    migration_path = EVIDENCE / "table-layout.json"
    api = NotionAPI()
    if migration_path.exists():
        manifest = json.loads(migration_path.read_text())
        if manifest["status"] == "complete":
            raise RuntimeError("Table layout was already completed")
        snapshot = json.loads(Path(manifest["snapshot"]).read_text())
        root = snapshot["blocks"]
    else:
        root = api.children(PAGE_ID)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        snapshot_path = EVIDENCE / f"before-table-{stamp}.json"
        snapshot_path.write_text(json.dumps({"blocks": api.tree(PAGE_ID)},
                                            ensure_ascii=False, indent=2) + "\n")
        source_markdown = api.request("GET", f"pages/{PAGE_ID}/markdown")
        (EVIDENCE / f"before-table-{stamp}.md").write_text(markdown_from_response(source_markdown))
        manifest = {"status": "converting", "snapshot": str(snapshot_path), "completed": []}
        migration_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    pairs = []
    for index, block in enumerate(root[:-1]):
        if block["type"] == "heading_3" and _content(block).startswith("2."):
            following = root[index + 1]
            if following["type"] != "column_list":
                raise RuntimeError(f"Function {_content(block)} is not followed by columns")
            pairs.append((block, following))
    if len(pairs) != 6:
        raise RuntimeError(f"Expected six function column groups; found {len(pairs)}")
    for heading, old_columns in pairs:
        if any(item["old_column_id"] == old_columns["id"] for item in manifest["completed"]):
            continue
        current_root = api.children(PAGE_ID)
        live_table, live_old = locate_function_layout(current_root, heading["id"], old_columns["id"])
        if live_old:
            columns = api.children(live_old["id"])
            if len(columns) != 2:
                raise RuntimeError(f"Function {_content(heading)} does not have two columns")
            left = api.children(columns[0]["id"])
            right = api.children(columns[1]["id"])
        else:
            snapshot_columns = old_columns.get("_children", [])
            if len(snapshot_columns) != 2 or not live_table:
                raise RuntimeError("Original columns are unavailable for recovery")
            left = snapshot_columns[0]["_children"]
            right = snapshot_columns[1]["_children"]
            columns = snapshot_columns
        table = table_from_columns(left, right)
        expected_code = _content(left[0])
        expected_explanation = "".join(item["text"]["content"]
                                       for item in table["table"]["children"][1]["table_row"]["cells"][1])
        if live_table is None:
            before_ids = {block["id"] for block in current_root}
            payload = {"children": [table],
                       "position": {"type": "after_block", "after_block": {"id": heading["id"]}}}
            api.request("PATCH", f"blocks/{PAGE_ID}/children", payload)
            current_root = api.children(PAGE_ID)
            live_table, live_old = locate_function_layout(current_root, heading["id"], old_columns["id"])
            if live_table is None or live_table["id"] in before_ids:
                raise RuntimeError("A new table did not appear after the function heading")
        table_id = live_table["id"]
        rows = api.children(table_id)
        if len(rows) != 2 or _table_cell(rows[1], 0) != expected_code or _table_cell(rows[1], 1) != expected_explanation:
            raise RuntimeError(f"Table content differs from live columns for {_content(heading)}")
        if live_old:
            for column, before in zip(columns, (left, right)):
                current = api.children(column["id"])
                if [(block["id"], block["last_edited_time"]) for block in current] != [
                    (block["id"], block["last_edited_time"]) for block in before
                ]:
                    raise RuntimeError(f"Notion content changed while converting {_content(heading)}; old columns remain")
            # A new table is verified before its old, recoverable column block is trashed.
            api.request("PATCH", f"blocks/{old_columns['id']}", {"in_trash": True})
        manifest["completed"].append({"heading": _content(heading),
                                      "old_column_id": old_columns["id"],
                                      "new_table_id": table_id})
        migration_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    final = api.children(PAGE_ID)
    if any(block["type"] == "column_list" for block in final) or sum(block["type"] == "table" for block in final) != 10:
        raise RuntimeError("Final Notion page does not have six function tables and four result tables")
    response = api.request("GET", f"pages/{PAGE_ID}/markdown")
    save_pulled_markdown(markdown_from_response(response), REPORT.with_name("보고서_노션.md"))
    manifest["status"] = "complete"
    migration_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print("Converted six function sections to two-column Notion tables")


def _expected_code(blocks: list[dict]) -> list[str]:
    return [_plain(block["column_list"]["children"][0]["column"]["children"][0])
            for block in blocks if block["type"] == "column_list"]


def preview(report: Path = REPORT) -> tuple[list[dict], str]:
    source = report.read_text()
    blocks = build_blocks(source)
    code = _expected_code(blocks)
    if len(code) != 6:
        raise ValueError(f"Expected six function groups; found {len(code)}")
    c_source = report.with_name("HW1.c").read_text()
    nonblank = lambda value: [line.rstrip() for line in value.splitlines() if line.strip()]
    if nonblank("\n".join(code)) != nonblank(c_source):
        raise ValueError("Report C code does not match HW1.c")
    if len(blocks) > 100:
        raise ValueError("More than 100 top-level blocks; split the upload")
    payload_size = len(json.dumps({"children": blocks}, ensure_ascii=False).encode())
    if payload_size > 500_000:
        raise ValueError("Notion append payload exceeds 500KB")
    print(f"Prepared {len(blocks)} root blocks, six code/analysis columns, {payload_size} bytes")
    return blocks, source


def push(report: Path = REPORT) -> None:
    blocks, source = preview(report)
    EVIDENCE.mkdir(exist_ok=True)
    manifest_path = EVIDENCE / "manifest.json"
    assert_push_allowed(manifest_path)
    api = NotionAPI()
    page = api.request("GET", f"pages/{PAGE_ID}")
    old = api.tree(PAGE_ID)
    backup_name = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = EVIDENCE / f"before-{backup_name}.json"
    backup.write_text(json.dumps({"page": page, "blocks": old}, ensure_ascii=False, indent=2) + "\n")
    old_markdown = api.request("GET", f"pages/{PAGE_ID}/markdown")
    (EVIDENCE / f"before-{backup_name}.md").write_text(markdown_from_response(old_markdown))
    manifest = {"status": "uploading", "page_id": PAGE_ID,
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "backup": str(backup), "old_ids": [block["id"] for block in old],
                "new_ids": [], "archived_old_ids": []}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    response = api.request("PATCH", f"blocks/{PAGE_ID}/children", {"children": blocks})
    manifest["new_ids"] = [block["id"] for block in response["results"]]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    if len(manifest["new_ids"]) != len(blocks):
        raise RuntimeError("Notion append returned an unexpected block count; old blocks remain")
    new_ids = set(manifest["new_ids"])
    current = api.children(PAGE_ID)
    new = [block for block in current if block["id"] in new_ids]
    _check_remote_code(api, new, _expected_code(blocks))
    if [block["id"] for block in new] != manifest["new_ids"]:
        raise RuntimeError("Notion block order changed; old blocks remain")
    old_current = {block["id"]: block for block in current if block["id"] in manifest["old_ids"]}
    if len(old_current) != len(old):
        raise RuntimeError("Existing Notion blocks changed during upload; old blocks remain")
    for original in old:
        if old_current[original["id"]]["last_edited_time"] != original["last_edited_time"]:
            raise RuntimeError("Existing Notion block was edited during upload; old blocks remain")
    manifest["status"] = "archiving_old"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    for block_id in manifest["old_ids"]:
        api.request("PATCH", f"blocks/{block_id}", {"in_trash": True})
        manifest["archived_old_ids"].append(block_id)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    final = api.children(PAGE_ID)
    if [block["id"] for block in final] != manifest["new_ids"]:
        raise RuntimeError("Final Notion block list differs from the uploaded blocks")
    _check_remote_code(api, final, _expected_code(blocks))
    manifest["status"] = "complete"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Uploaded {len(final)} root blocks to the existing Notion page")


def pull(output: Path) -> None:
    api = NotionAPI()
    response = api.request("GET", f"pages/{PAGE_ID}/markdown")
    markdown = markdown_from_response(response)
    backup = save_pulled_markdown(markdown, output)
    if backup:
        print(f"Previous Notion download saved: {backup}")
    print(f"Downloaded Notion Markdown: {output} ({len(markdown)} characters)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preview", "push", "pull", "layout-table"))
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--output", type=Path, default=REPORT.with_name("보고서_노션.md"))
    args = parser.parse_args()
    if args.command == "preview":
        preview(args.report)
    elif args.command == "push":
        push(args.report)
    elif args.command == "layout-table":
        layout_table()
    else:
        pull(args.output)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, urllib.error.URLError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
