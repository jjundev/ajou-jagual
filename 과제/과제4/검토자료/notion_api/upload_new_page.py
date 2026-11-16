"""Upload 과제4/보고서_노션.md as a NEW native Notion page (2026-11-16).

RETIRED (2026-11-16): the author now edits the Notion page directly, so Notion is canonical.
Do not run this or patch_rows.py; start Notion work from a fresh pull. Its 5-screenshot check
also fails now that cases 03-05 were removed.
"""
import json, re, sys, mimetypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / ".claude/skills/notion-report-sync/scripts"))
from notion_report import NotionAPI          # noqa: E402
from notion_images import send_upload       # noqa: E402

EVID = Path(__file__).resolve().parent
REPORT = ROOT / "과제/과제4/보고서_노션.md"
SHOTS = sorted((ROOT / "과제/과제4/터미널_스크린샷").glob("0[1-5]-*.png"))
PARENT = "3e2b06d2-63bc-803a-bbc0-fb62531e78e0"
TITLE = "HW4: 타이머 관리 보고서"
MANIFEST = EVID / "manifest.json"
NBSP = " "


def unesc(s):
    return re.sub(r"\\(.)", r"\1", s)


def rt(text, bold=False):
    out = []
    for i in range(0, len(text), 2000):
        item = {"type": "text", "text": {"content": text[i:i + 2000]}}
        if bold:
            item["annotations"] = {"bold": True}
        out.append(item)
    return out


def inline(md):
    items = []
    for k, part in enumerate(re.split(r"(?<!\\)\*\*", md)):
        if part:
            items += rt(unesc(part), bold=(k % 2 == 1))
    return items


def para(md=""):
    return {"type": "paragraph", "paragraph": {"rich_text": inline(md) if md else []}}


def cell_text(raw, source):
    text = unesc(raw.replace("<br>", "\n"))
    if source:
        text = re.sub(r"^ +", lambda m: NBSP * len(m.group(0)), text, flags=re.M)
    return rt(text)


def table(lines, source_table):
    body = "\n".join(lines)
    rows = re.findall(r"<tr>\n(.*?)\n</tr>", body, re.S)
    parsed = [re.findall(r"<td>(.*?)</td>", r, re.S) for r in rows]
    width = len(parsed[0])
    children = []
    for ri, cells in enumerate(parsed):
        assert len(cells) == width
        children.append({"type": "table_row", "table_row": {"cells": [
            cell_text(c, source_table and ri > 0 and ci == 0) for ci, c in enumerate(cells)]}})
    return {"type": "table", "table": {"table_width": width, "has_column_header": True,
                                       "has_row_header": False, "children": children}}


def build():
    lines = REPORT.read_text().split("\n")
    blocks, i, shot = [], 0, 0
    while i < len(lines):
        ln = lines[i]
        if ln == "":
            i += 1; continue
        if ln.startswith("<table_of_contents"):
            blocks.append({"type": "table_of_contents", "table_of_contents": {"color": "gray"}})
        elif ln == "<empty-block/>":
            blocks.append(para())
        elif ln.startswith("## "):
            blocks.append({"type": "heading_2", "heading_2": {"rich_text": inline(ln[3:])}})
        elif ln.startswith("# "):
            blocks.append({"type": "heading_1", "heading_1": {"rich_text": inline(ln[2:])}})
        elif ln.startswith("```"):
            lang = ln[3:].strip() or "plain text"
            j = i + 1
            while lines[j] != "```":
                j += 1
            code = "\n".join(lines[i + 1:j])
            blocks.append({"type": "code", "code": {"language": lang, "rich_text": rt(code)}})
            i = j
        elif ln.startswith("<table"):
            j = i
            while lines[j] != "</table>":
                j += 1
            src = "<td>소스코드</td>" in "\n".join(lines[i:j])
            blocks.append(table(lines[i:j + 1], src))
            i = j
        elif ln.startswith("!["):
            blocks.append({"type": "image", "_shot": str(SHOTS[shot])})
            shot += 1
        else:
            blocks.append(para(ln))
        i += 1
    assert shot == 5 == len(SHOTS), (shot, SHOTS)
    return blocks


def upload_image(api, path):
    data = Path(path).read_bytes()
    name = Path(path).name.encode("ascii", "ignore").decode() or "shot.png"
    name = f"hw4-case-{Path(path).name[:2]}.png"
    up = api.request("POST", "file_uploads", {"mode": "single_part", "filename": name,
                                             "content_type": "image/png"})
    send_upload(api, up["id"], name, data, "image/png")
    return {"type": "image", "image": {"type": "file_upload", "file_upload": {"id": up["id"]}}}


REMOTE = EVID / "remote-blocks.json"


def cell_texts(row):
    return ["".join(t["plain_text"] for t in c) for c in row["table_row"]["cells"]]


def replace_body(api, man):
    """Archive the uploaded body so main() can append the rewritten one into the same page.

    Refuses when the live page differs from remote-blocks.json (the post-upload readback),
    i.e. when the author may already have edited it in Notion.
    """
    pid = man["page_id"]
    old = json.loads(REMOTE.read_text())
    old_by_id = {b["id"]: b for b in old}
    cur = api.children(pid)
    archived = set(man.get("archived", []))
    if man.get("pending") != "replace-archive":
        if [b["id"] for b in cur] != [b["id"] for b in old]:
            raise SystemExit("live block ids differ from remote-blocks.json; inspect before replacing")
        for b in cur:
            o = old_by_id[b["id"]]
            if b["last_edited_time"] != o["last_edited_time"]:
                raise SystemExit(f"block {b['id']} edited since upload; inspect before replacing")
            if b["type"] == "table":
                rows = api.children(b["id"])
                if [cell_texts(r) for r in rows] != [cell_texts(r) for r in o["_rows"]]:
                    raise SystemExit(f"table {b['id']} rows edited since upload; inspect")
        man["pending"] = "replace-archive"
        man["archived"] = []
        MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2))
    else:  # resuming an interrupted archive: only blocks from the old body may remain
        stray = [b["id"] for b in cur if b["id"] not in old_by_id]
        if stray:
            raise SystemExit(f"unexpected blocks while resuming archive: {stray[:3]}")
    for b in cur:
        api.request("DELETE", f"blocks/{b['id']}")
        archived.add(b["id"])
        man["archived"] = sorted(archived)
        MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2))
    left = api.children(pid)
    if left:
        raise SystemExit(f"{len(left)} blocks remain after archive; inspect")
    man.update(done=0, planned=None)
    man.pop("pending")
    MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2))
    print("archived", len(archived), "old blocks")


def main():
    api = NotionAPI()
    blocks = build()
    man = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    if "--replace" in sys.argv:
        replace_body(api, man)
        man["planned"] = len(blocks)
        MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2))
    if not man.get("page_id"):
        page = api.request("POST", "pages", {
            "parent": {"page_id": PARENT},
            "properties": {"title": {"title": rt(TITLE)}}})
        man = {"page_id": page["id"], "url": page["url"], "done": 0,
               "planned": len(blocks), "shots": [str(s) for s in SHOTS]}
        MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2))
    pid = man["page_id"]
    print("page", pid, man["url"], "blocks", len(blocks))
    while man["done"] < len(blocks):
        batch = blocks[man["done"]:man["done"] + 8]
        payload = [upload_image(api, b["_shot"]) if b["type"] == "image" else b for b in batch]
        man["pending"] = [man["done"], man["done"] + len(batch)]
        MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2))
        before = len(api.children(pid))
        if before != man["done"]:
            raise SystemExit(f"remote has {before} children, manifest says {man['done']}; inspect")
        try:
            api.request("PATCH", f"blocks/{pid}/children", {"children": payload})
        except Exception as e:  # timeout may still have inserted
            print("write uncertain:", e)
        after = len(api.children(pid))
        if after != man["done"] + len(batch):
            raise SystemExit(f"after={after}, expected {man['done'] + len(batch)}; inspect")
        man["done"] = after
        man.pop("pending")
        MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2))
        print("done", after, "/", len(blocks))


if __name__ == "__main__":
    main()
