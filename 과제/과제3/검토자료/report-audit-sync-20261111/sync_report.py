"""Targeted, backed-up synchronization of the approved HW3 report wording."""
import copy
import difflib
import html
import importlib.util
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[3]
REPORT = ROOT / "과제/과제3/보고서_노션.md"
MANIFEST = ROOT / "과제/과제3/검토자료/notion_api/manifest.json"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


notion = module("notion_report", ".agents/skills/notion-report-sync/scripts/notion_report.py")
audit = module("report_md", ".claude/skills/report-audit/scripts/report_md.py")


def save(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def walk(tree):
    for block in tree:
        yield block
        yield from walk(block.get("_children", []))


def plain(items):
    return "".join(item.get("text", {}).get("content", "") for item in items)


def decode(text):
    text = re.sub(r"<br\s*/?>", "\n", text)
    return html.unescape(audit._ESCAPE.sub(r"\1", text))


def mask_urls(text):
    return audit._IMAGE.sub(lambda m: m[1] + "<URL>" + m[3], text)


def image_body(block, old, new):
    surrogate = {
        "id": block["id"], "type": "paragraph",
        "paragraph": {"rich_text": block["image"].get("caption", [])},
    }
    body = notion.build_update(surrogate, {
        "block_id": block["id"], "type": "paragraph",
        "old_text": old, "new_text": new,
    })
    return {"image": {"caption": body["paragraph"]["rich_text"]}}


def prepare(api, page_id):
    page = api.request("GET", f"pages/{page_id}")
    title = plain(page["properties"]["title"]["title"])
    assert title == "HW3: CPU 및 인터럽트 스케줄러 보고서", title
    remote = notion.markdown_from_response(api.request("GET", f"pages/{page_id}/markdown"))
    local = REPORT.read_text()
    protected = audit.compare_protected(remote, local)
    assert all(name == "image URLs" for name, detail in protected), protected
    tree = api.tree(page_id)
    save("remote-before.json", {"page": page, "tree": tree})
    (EVIDENCE / "remote-before.md").write_text(remote)
    blocks = list(walk(tree))
    old_lines, new_lines = remote.splitlines(), local.splitlines()
    assert len(old_lines) == len(new_lines)
    edits, images = [], []
    for line_no, (old_line, new_line) in enumerate(zip(old_lines, new_lines), 1):
        if mask_urls(old_line) == mask_urls(new_line):
            continue
        candidates = []
        if old_line.startswith("<td>") and new_line.startswith("<td>"):
            old, new = decode(old_line[4:-5]), decode(new_line[4:-5])
            for block in blocks:
                if block["type"] == "table_row":
                    for index, cell in enumerate(block["table_row"]["cells"]):
                        if plain(cell) == old:
                            candidates.append((block, index))
        elif old_line.startswith("![") and new_line.startswith("!["):
            old = decode(audit._IMAGE.fullmatch(old_line)[0].split("](", 1)[0][2:])
            new = decode(audit._IMAGE.fullmatch(new_line)[0].split("](", 1)[0][2:])
            candidates = [(b, None) for b in blocks if b["type"] == "image"
                          and plain(b["image"].get("caption", [])) == old]
        else:
            old, new = decode(old_line), decode(new_line)
            candidates = [(b, None) for b in blocks if b["type"] == "paragraph"
                          and plain(b["paragraph"].get("rich_text", [])) == old]
        assert len(candidates) == 1, (line_no, len(candidates))
        block, cell_index = candidates[0]
        edit = {"block_id": block["id"], "type": block["type"],
                "old_text": old, "new_text": new, "report_line": line_no}
        if cell_index is not None:
            assert cell_index == 1, "A source cell must never be changed"
            edit["cell_index"] = cell_index
        if block["type"] == "image":
            image_body(block, old, new)
            images.append(edit)
        else:
            notion.build_update(block, edit)
            edits.append(edit)
    ids = [e["block_id"] for e in edits + images]
    assert len(ids) == len(set(ids))
    plan = {"page_id": page_id, "page_url": page["url"], "title": title,
            "edits": edits, "images": images}
    save("sync-plan.json", plan)
    print(f"Prepared {len(edits)} text/table edits and {len(images)} caption edits", flush=True)
    for edit in sorted(edits + images, key=lambda e: e["report_line"]):
        print(f"  line {edit['report_line']}: {edit['type']} {edit['block_id']}", flush=True)


def apply(api, page_id):
    plan = json.loads((EVIDENCE / "sync-plan.json").read_text())
    assert page_id == plan["page_id"]
    before = json.loads((EVIDENCE / "remote-before.json").read_text())
    saved_blocks = {b["id"]: b for b in walk(before["tree"])}
    # Preflight every approved target before the first mutation.
    for edit in plan["edits"] + plan["images"]:
        current = api.request("GET", "blocks/" + edit["block_id"])
        saved = saved_blocks[edit["block_id"]]
        kind = edit["type"]
        # Hosted-image signatures refresh on GET without changing the attachment.
        assert stable(current[kind]) == stable(saved[kind]), f"Target changed: {edit['block_id']}"
        assert current.get("last_edited_time") == saved.get("last_edited_time")
    completed = notion.apply_edits(api, page_id, plan["edits"], EVIDENCE / "text-edits")
    save("completed.json", {"text_blocks": completed, "image_captions": []})
    image_ids = []
    for edit in plan["images"]:
        key = edit["block_id"]
        live = api.request("GET", f"blocks/{key}")
        saved = saved_blocks[key]
        assert live["type"] == "image" and stable(live["image"]) == stable(saved["image"])
        assert live.get("last_edited_time") == saved.get("last_edited_time")
        body = image_body(live, edit["old_text"], edit["new_text"])
        save("pending-image.json", {"block_id": key, "body": body})
        try:
            api.request("PATCH", f"blocks/{key}", body)
        except Exception:
            observed = api.request("GET", f"blocks/{key}")
            save("uncertain-image.json", observed)
            raise
        actual = api.request("GET", f"blocks/{key}")
        assert plain(actual["image"].get("caption", [])) == edit["new_text"]
        image_ids.append(key)
        save("completed.json", {"text_blocks": completed, "image_captions": image_ids})
        (EVIDENCE / "pending-image.json").unlink()
        print(f"Caption verified: {key}", flush=True)
    print(f"Applied and read back {len(completed)} text blocks and {len(image_ids)} captions", flush=True)


def stable(value):
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items()
                if k not in {"created_time", "last_edited_time", "created_by", "last_edited_by", "expiry_time"}}
    if isinstance(value, list):
        return [stable(v) for v in value]
    if isinstance(value, str) and value.startswith("https://"):
        u = urlsplit(value)
        if "amazonaws.com" in u.netloc or "notion-static.com" in u.netloc:
            return urlunsplit((u.scheme, u.netloc, u.path, "", ""))
    return value


def verify(api, page_id):
    plan = json.loads((EVIDENCE / "sync-plan.json").read_text())
    before = json.loads((EVIDENCE / "remote-before.json").read_text())
    tree = api.tree(page_id)
    save("remote-after.json", {"page": api.request("GET", f"pages/{page_id}"), "tree": tree})
    old_blocks, new_blocks = list(walk(before["tree"])), list(walk(tree))
    assert [(b["id"], b["type"]) for b in old_blocks] == [(b["id"], b["type"]) for b in new_blocks]
    by_id = {b["id"]: b for b in new_blocks}
    expected_tree = copy.deepcopy(before["tree"])
    expected_by_id = {b["id"]: b for b in walk(expected_tree)}
    for edit in plan["edits"] + plan["images"]:
        expected = expected_by_id[edit["block_id"]]
        if edit["type"] == "image":
            body = image_body(expected, edit["old_text"], edit["new_text"])
        else:
            body = notion.build_update(expected, edit)
        kind = edit["type"]
        if kind == "table_row":
            assert notion._editable_state(kind, by_id[edit["block_id"]][kind]) == notion._editable_state(kind, body[kind])
        elif kind == "image":
            assert plain(by_id[edit["block_id"]][kind].get("caption", [])) == edit["new_text"]
        else:
            assert notion._editable_state(kind, by_id[edit["block_id"]][kind]) == notion._editable_state(kind, body[kind])
        # Ignore server-derived plain_text/href by retaining the original item metadata
        # and applying only the approved literal change for the full-tree comparison.
        field = "cells" if kind == "table_row" else ("caption" if kind == "image" else "rich_text")
        groups = expected[kind][field] if kind == "table_row" else [expected[kind][field]]
        for group in groups:
            for item in group:
                if item.get("type") == "text" and edit["old_text"] in item["text"]["content"]:
                    item["text"]["content"] = item["text"]["content"].replace(edit["old_text"], edit["new_text"], 1)
                    if "plain_text" in item:
                        item["plain_text"] = item["plain_text"].replace(edit["old_text"], edit["new_text"], 1)
    assert stable(expected_tree) == stable(tree), "Unexpected native block change"
    output = ROOT / "과제/과제3/검토자료/노션_pull/current.md"
    local_diff, previous_diff, backup = notion.pull_markdown(api, page_id, output, REPORT)
    (EVIDENCE / "previous-download.diff").write_text(previous_diff or "")
    (EVIDENCE / "local-report.diff").write_text(local_diff)
    downloaded = output.read_text()
    assert mask_urls(downloaded).rstrip() == mask_urls(REPORT.read_text()).rstrip(), "Downloaded text differs from approved local report"
    print("Previous download comparison:", "no prior download" if previous_diff is None else ("changed; backup saved" if previous_diff else "unchanged"))
    print("Local report comparison: identical except signed image URLs")
    root = tree
    toc = [b for b in root if b["type"] == "table_of_contents"]
    assert len(toc) == 1 and toc[0]["table_of_contents"].get("color") == "gray"
    images = [b for b in root if b["type"] == "image"]
    assert len(images) == 5
    checks = {
        "text_sync": "verified", "approved_local_replacements": 7,
        "text_blocks_updated": len(plan["edits"]), "image_captions_updated": len(plan["images"]),
        "block_ids_types_and_order": "unchanged", "all_changes_match_plan": "verified",
        "code_outputs_table_structure_headings": "unchanged", "original_image_blocks": "unchanged",
        "gray_toc_count": 1, "download_matches_local_except_signed_urls": True,
        "previous_download_changed": bool(previous_diff), "previous_download_backup": str(backup) if backup else None,
        "fresh_download": str(output), "live_page_settings_and_table_widths": "not verified in this text-only sync",
        "pdf_export": "not requested", "commit": "not requested",
    }
    save("verification.json", checks)
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    page_id = json.loads(MANIFEST.read_text())["page_id"]
    assert page_id == "408b06d2-63bc-8184-8464-e0f3a3bbd8e5"
    {"prepare": prepare, "apply": apply, "verify": verify}[sys.argv[1]](notion.NotionAPI(), page_id)
