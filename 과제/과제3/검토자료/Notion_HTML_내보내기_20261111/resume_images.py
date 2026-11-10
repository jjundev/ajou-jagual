"""Resume the saved image plan using Notion's update-image request shape."""
import copy
import io
import json
import urllib.request
import uuid
import reupload_images as m
from pathlib import Path
from PIL import Image

api = m.notion.NotionAPI()
manifest = json.loads((m.EVIDENCE / "manifest.json").read_text())
before = json.loads((m.EVIDENCE / "before.json").read_text())
page_id = manifest["page_id"]
saved = {b["id"]: b for b in m.walk(before["tree"])}
for r in manifest["images"]:
    key = r["block_id"]
    current = api.request("GET", f"blocks/{key}")
    assert m.plain(current["image"].get("caption", [])) == r["caption"]
    data = Path(r["snapshot"]).read_bytes()
    assert m.digest(data) == r["sha256"]
    if r["state"] == "verified":
        with urllib.request.urlopen(current["image"]["file"]["url"], timeout=35) as response:
            assert response.read() == data
        continue
    assert current.get("last_edited_time") == saved[key].get("last_edited_time")
    if "upload_id" in r:
        uid = r["upload_id"]
        assert api.request("GET", f"file_uploads/{uid}")["status"] == "uploaded"
    else:
        filename = f"hw3-case-{r['case']:02}-20261111.png"
        r["state"] = "creating_upload"; m.save("manifest.json", manifest)
        result = api.request("POST", "file_uploads", {"mode": "single_part", "filename": filename, "content_type": "image/png"})
        uid = result["id"]; r["upload_id"] = uid
        r["state"] = "sending_upload"; m.save("manifest.json", manifest)
        boundary = "HW3Image" + uuid.uuid4().hex
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                'Content-Type: image/png\r\n\r\n').encode() + data + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(f"https://api.notion.com/v1/file_uploads/{uid}/send", data=body,
            headers={**api.headers, "Content-Type": "multipart/form-data; boundary=" + boundary}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as response:
            assert json.load(response)["status"] == "uploaded"
    caption = [{k: copy.deepcopy(v) for k, v in item.items() if k in {"type", "text", "annotations"}}
               for item in current["image"].get("caption", [])]
    r["state"] = "attaching"; m.save("manifest.json", manifest)
    try:
        api.request("PATCH", f"blocks/{key}", {"image": {"file_upload": {"id": uid}, "caption": caption}})
    except Exception:
        m.save("uncertain-attachment-resume.json", api.request("GET", f"blocks/{key}"))
        raise
    actual = api.request("GET", f"blocks/{key}")
    assert m.plain(actual["image"].get("caption", [])) == r["caption"]
    with urllib.request.urlopen(actual["image"]["file"]["url"], timeout=35) as response:
        attached = response.read()
    exact = attached == data
    a, b = Image.open(io.BytesIO(attached)).convert("RGBA"), Image.open(io.BytesIO(data)).convert("RGBA")
    pixels = a.size == b.size and a.tobytes() == b.tobytes()
    assert exact or pixels
    (m.EVIDENCE / "업로드_확인" / f"hw3-case-{r['case']:02}-20261111.png").write_bytes(attached)
    r.update(state="verified", attached_sha256=m.digest(attached), exact_bytes=exact, identical_pixels=pixels)
    m.save("manifest.json", manifest)
    print(f"Case {r['case']}: attachment and caption verified; exact bytes={exact}", flush=True)
after = api.tree(page_id)
m.save("after.json", {"page": api.request("GET", f"pages/{page_id}"), "tree": after})
old_copy, new_copy = copy.deepcopy(before["tree"]), copy.deepcopy(after)
for comparison in [old_copy, new_copy]:
    for block in m.walk(comparison):
        if block["type"] == "image":
            block["image"] = {"caption": block["image"].get("caption", [])}
assert m.stable(old_copy) == m.stable(new_copy), "Unexpected change outside image attachments"
report = m.REPO / "과제/과제3/보고서_노션.md"
output = m.REPO / "과제/과제3/검토자료/노션_pull/current.md"
local_diff, previous_diff, backup = m.notion.pull_markdown(api, page_id, output, report)
mask = lambda s: m.audit._IMAGE.sub(lambda x: x[1] + "<URL>" + x[3], s).rstrip()
assert mask(output.read_text()) == mask(report.read_text())
m.save("verification.json", {"images": len(manifest["images"]), "original_blocks_order_and_captions_preserved": True,
    "all_attached_images_equal_local": True, "report_text_unchanged": True, "fresh_markdown": str(output),
    "previous_download_changed": bool(previous_diff), "previous_download_backup": str(backup) if backup else None})
print("All 5 screenshot files reuploaded; report text, structure, captions and image order unchanged", flush=True)
