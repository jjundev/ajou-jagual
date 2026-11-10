"""Replace only the five approved HW3 image attachments, preserving captions."""
import copy
import hashlib
import importlib.util
import io
import json
import urllib.request
import uuid
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
EVIDENCE = ROOT / "이미지_재업로드"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


notion = load("notion_report", REPO / ".agents/skills/notion-report-sync/scripts/notion_report.py")
audit = load("report_md", REPO / ".claude/skills/report-audit/scripts/report_md.py")


def save(name, data):
    (EVIDENCE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def plain(items):
    return "".join(i.get("text", {}).get("content", "") for i in items)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def walk(tree):
    for block in tree:
        yield block
        yield from walk(block.get("_children", []))


def stable(value):
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items()
                if k not in {"last_edited_time", "last_edited_by", "created_time", "created_by", "expiry_time"}}
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value


def main():
    EVIDENCE.mkdir(exist_ok=False)
    (EVIDENCE / "교체_전_이미지").mkdir()
    (EVIDENCE / "업로드_원본").mkdir()
    (EVIDENCE / "업로드_확인").mkdir()
    manifest = json.loads((REPO / "과제/과제3/검토자료/notion_api/manifest.json").read_text())
    page_id = manifest["page_id"]
    assert page_id == "408b06d2-63bc-8184-8464-e0f3a3bbd8e5"
    api = notion.NotionAPI()
    page = api.request("GET", f"pages/{page_id}")
    assert plain(page["properties"]["title"]["title"]) == manifest["title"]
    tree = api.tree(page_id)
    markdown = notion.markdown_from_response(api.request("GET", f"pages/{page_id}/markdown"))
    local = (REPO / "과제/과제3/보고서_노션.md").read_text()
    mask = lambda s: audit._IMAGE.sub(lambda m: m[1] + "<URL>" + m[3], s).rstrip()
    assert mask(markdown) == mask(local), "Unexpected report wording difference"
    save("before.json", {"page": page, "tree": tree})
    (EVIDENCE / "before.md").write_text(markdown)
    images = [b for b in tree if b["type"] == "image"]
    assert len(images) == len(manifest["uploads"])
    records = []
    for index, (block, original) in enumerate(zip(images, manifest["uploads"]), 1):
        source = Path(original["path"])
        data = source.read_bytes()
        Image.open(io.BytesIO(data)).verify()
        snapshot = EVIDENCE / "업로드_원본" / source.name
        snapshot.write_bytes(data)
        with urllib.request.urlopen(block["image"]["file"]["url"], timeout=35) as response:
            old_data = response.read()
        (EVIDENCE / "교체_전_이미지" / source.name).write_bytes(old_data)
        records.append({"case": index, "block_id": block["id"], "source": str(source),
                        "snapshot": str(snapshot), "sha256": digest(data),
                        "old_sha256": digest(old_data), "caption": plain(block["image"].get("caption", [])),
                        "state": "prepared"})
    save("manifest.json", {"page_id": page_id, "page_url": page["url"], "images": records})
    for record, saved_block in zip(records, images):
        key = record["block_id"]
        current = api.request("GET", f"blocks/{key}")
        assert current["type"] == "image"
        assert current.get("last_edited_time") == saved_block.get("last_edited_time")
        assert current["image"].get("caption") == saved_block["image"].get("caption")
        data = Path(record["snapshot"]).read_bytes()
        filename = f"hw3-case-{record['case']:02}-20261111.png"
        record["state"] = "creating_upload"
        save("manifest.json", {"page_id": page_id, "page_url": page["url"], "images": records})
        created = api.request("POST", "file_uploads", {
            "mode": "single_part", "filename": filename, "content_type": "image/png"})
        uid = created["id"]
        record["upload_id"] = uid
        record["state"] = "sending_upload"
        save("manifest.json", {"page_id": page_id, "page_url": page["url"], "images": records})
        boundary = "HW3Image" + uuid.uuid4().hex
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                'Content-Type: image/png\r\n\r\n').encode() + data + f"\r\n--{boundary}--\r\n".encode()
        request = urllib.request.Request(f"https://api.notion.com/v1/file_uploads/{uid}/send",
            data=body, headers={**api.headers, "Content-Type": "multipart/form-data; boundary=" + boundary}, method="POST")
        with urllib.request.urlopen(request, timeout=60) as response:
            sent = json.load(response)
        assert sent["status"] == "uploaded"
        record["state"] = "attaching"
        save("manifest.json", {"page_id": page_id, "page_url": page["url"], "images": records})
        caption = [{k: copy.deepcopy(v) for k, v in item.items() if k in {"type", "text", "annotations"}}
                   for item in current["image"].get("caption", [])]
        try:
            api.request("PATCH", f"blocks/{key}", {
                "image": {"type": "file_upload", "file_upload": {"id": uid}, "caption": caption}})
        except Exception:
            save("uncertain-attachment.json", api.request("GET", f"blocks/{key}"))
            raise
        actual = api.request("GET", f"blocks/{key}")
        assert plain(actual["image"].get("caption", [])) == record["caption"]
        with urllib.request.urlopen(actual["image"]["file"]["url"], timeout=35) as response:
            attached = response.read()
        exact = attached == data
        pixels = Image.open(io.BytesIO(attached)).convert("RGBA").tobytes() == Image.open(io.BytesIO(data)).convert("RGBA").tobytes()
        assert exact or pixels
        (EVIDENCE / "업로드_확인" / filename).write_bytes(attached)
        record.update(state="verified", attached_sha256=digest(attached), exact_bytes=exact, identical_pixels=pixels)
        save("manifest.json", {"page_id": page_id, "page_url": page["url"], "images": records})
        print(f"Case {record['case']}: replaced attachment in existing block; caption preserved; bytes equal={exact}", flush=True)
    after = api.tree(page_id)
    save("after.json", {"page": api.request("GET", f"pages/{page_id}"), "tree": after})
    old_copy, new_copy = copy.deepcopy(tree), copy.deepcopy(after)
    for comparison in [old_copy, new_copy]:
        for block in walk(comparison):
            if block["type"] == "image":
                block["image"] = {"caption": block["image"].get("caption", [])}
    assert stable(old_copy) == stable(new_copy), "Unexpected change outside image attachments"
    output = REPO / "과제/과제3/검토자료/노션_pull/current.md"
    local_diff, previous_diff, backup = notion.pull_markdown(api, page_id, output, REPO / "과제/과제3/보고서_노션.md")
    assert mask(output.read_text()) == mask(local)
    save("verification.json", {"images": len(records), "original_blocks_order_and_captions_preserved": True,
         "all_attached_images_equal_local": True, "report_text_unchanged": True,
         "fresh_markdown": str(output), "previous_download_changed": bool(previous_diff),
         "previous_download_backup": str(backup) if backup else None})
    print("Verified all image replacements and unchanged report text/structure", flush=True)


if __name__ == "__main__":
    main()
