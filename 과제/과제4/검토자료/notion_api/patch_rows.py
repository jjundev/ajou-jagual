"""Patch only the changed table rows of the HW4 Notion page (2026-11-16, comment reflection).

Compares the regenerated manuscript (upload_new_page.build()) with plan.json. Anything other than
table-row cell text must be identical, otherwise it refuses. Each changed row is patched only when its
live text still equals the post-upload readback (remote-blocks.json), so author edits are never
overwritten; a row already holding the new text is skipped, so the script can be re-run.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import upload_new_page as up  # noqa: E402

EVID = up.EVID
PLAN = EVID / "plan.json"
REMOTE = up.REMOTE
MANIFEST = up.MANIFEST


def plain(cells):
    return ["".join(t["text"]["content"] for t in c) for c in cells]


def changed_rows(old, new):
    if len(old) != len(new) or [b["type"] for b in old] != [b["type"] for b in new]:
        raise SystemExit("block structure differs from plan.json; refusing row patch")
    out = []
    for i, (o, n) in enumerate(zip(old, new)):
        if o["type"] != "table":
            if o != n:
                raise SystemExit(f"non-table block {i} differs; refusing row patch")
            continue
        orows, nrows = o["table"]["children"], n["table"]["children"]
        if len(orows) != len(nrows) or o["table"]["table_width"] != n["table"]["table_width"]:
            raise SystemExit(f"table {i} shape differs; refusing row patch")
        for r, (orow, nrow) in enumerate(zip(orows, nrows)):
            if plain(orow["table_row"]["cells"]) != plain(nrow["table_row"]["cells"]):
                out.append((i, r, nrow["table_row"]["cells"]))
    return out


def rich(block):
    return "".join(t["plain_text"] for t in block[block["type"]].get("rich_text", []))


def readback(api, pid):
    blocks = api.children(pid)
    for b in blocks:
        if b["type"] == "table":
            b["_rows"] = api.children(b["id"])
    return blocks


def main():
    api = up.NotionAPI()
    man = json.loads(MANIFEST.read_text())
    pid = man["page_id"]
    old = json.loads(PLAN.read_text())
    new = up.build()
    remote = json.loads(REMOTE.read_text())
    todo = changed_rows(old, new)
    print("rows to patch", len(todo), [(i, r) for i, r, _ in todo])
    patched = set(map(tuple, man.get("patched", [])))
    for i, r, cells in todo:
        saved = remote[i]["_rows"][r]
        live = api.request("GET", f"blocks/{saved['id']}")
        live_txt = up.cell_texts(live)
        if live_txt == plain(cells):
            patched.add((i, r))
            continue
        if live_txt != up.cell_texts(saved):
            raise SystemExit(f"row {i}/{r} ({saved['id']}) edited in Notion; not overwriting")
        api.request("PATCH", f"blocks/{saved['id']}", {"table_row": {"cells": cells}})
        patched.add((i, r))
        man["patched"] = sorted(patched)
        MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2))
        print("patched", i, r)

    after = readback(api, pid)
    if [b["id"] for b in after] != [b["id"] for b in remote]:
        raise SystemExit("top-level block ids changed; inspect")
    fails = []
    for i, (b, n) in enumerate(zip(after, new)):
        if b["type"] != "table":
            # the author may touch a block in the UI (e.g. code wrap) without changing its text
            if b["type"] != remote[i]["type"] or rich(b) != rich(remote[i]):
                fails.append(f"block {i} changed")
            continue
        want = [plain(row["table_row"]["cells"]) for row in n["table"]["children"]]
        got = [up.cell_texts(row) for row in b["_rows"]]
        if want != got:
            fails.append(f"table {i} text mismatch")
    if fails:
        raise SystemExit(f"verification failed: {fails}")
    REMOTE.write_text(json.dumps(after, ensure_ascii=False, indent=2))
    PLAN.write_text(json.dumps(new, ensure_ascii=False, indent=2))
    man["patched"] = sorted(patched)
    MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2))
    print("verified", len(after), "blocks;", len(todo), "rows patched")


if __name__ == "__main__":
    main()
