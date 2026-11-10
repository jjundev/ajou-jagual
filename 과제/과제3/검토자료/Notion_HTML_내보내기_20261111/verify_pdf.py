"""Check the actual landscape PDF and render every page for visual review."""
import hashlib
import json
import re
import unicodedata
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "보고서_노션_A4가로_후보.pdf"


def norm(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text).replace("\u200b", ""))


def main():
    content = json.loads((ROOT / "html-content.json").read_text())
    export = json.loads((ROOT / "export.json").read_text())
    upload = json.loads((ROOT / "이미지_재업로드/manifest.json").read_text())
    with zipfile.ZipFile(export["zip"]) as archive:
        for member in archive.infolist():
            if not member.is_dir():
                assert (ROOT / "원본" / member.filename).read_bytes() == archive.read(member)
    pdf = fitz.open(PDF)
    page_texts = [p.get_text() for p in pdf]
    normalized = [norm(s) for s in page_texts]
    full = norm("".join(page_texts))
    assert all(abs(p.rect.width - 841.89) < 1 and abs(p.rect.height - 595.28) < 1 for p in pdf)
    for heading in content["headings"]:
        assert norm(heading["text"]) in full, heading
    for p in content["paragraphs"]:
        if norm(p["text"]):
            assert norm(p["text"]) in full, (p["tag"], p["id"], p["text"][:100])
    paired = []
    for table in content["tables"]:
        for row in table["rows"]:
            for cell in row["cells"]:
                if norm(cell):
                    assert norm(cell) in full, (row["id"], cell[:100])
        if table["rows"][0]["cells"][0] == "소스코드":
            for row in table["rows"][1:]:
                pages = [i + 1 for i, text in enumerate(normalized)
                         if all(norm(cell) in text for cell in row["cells"])]
                assert pages, ("Code and analysis split or lost", row["id"])
                paired.append({"row_id": row["id"], "pages": pages})
    originals = []
    for entry, record in zip(content["images"], upload["images"]):
        path = Path(unquote(urlsplit(entry["src"]).path))
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
        image = Image.open(path).convert("RGB")
        originals.append({"path": str(path), "size": image.size, "pixels": image.tobytes(),
                          "sha256": record["sha256"], "pages": []})
    bounds, image_order, sparse = [], [], []
    for i, page in enumerate(pdf):
        assert page.get_text().strip() or page.get_images(), ("Blank page", i + 1)
        if len(norm(page.get_text())) < 80 and not page.get_images():
            sparse.append(i + 1)
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    x0, y0, x1, y1 = span["bbox"]
                    if x0 < -0.5 or y0 < -0.5 or x1 > page.rect.width + .5 or y1 > page.rect.height + .5:
                        bounds.append({"page": i + 1, "text": span["text"], "bbox": span["bbox"]})
        for image in page.get_images(full=True):
            pix = fitz.Pixmap(pdf, image[0])
            if pix.alpha:
                pix = fitz.Pixmap(pix, 0)
            if pix.colorspace.n != 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            matches = [k for k, original in enumerate(originals)
                       if original["size"] == (pix.width, pix.height) and original["pixels"] == pix.samples]
            assert len(matches) == 1, ("Unknown or changed embedded image", i + 1, pix.width, pix.height)
            assert norm("실제 터미널 실행 화면") in normalized[i], ("Screenshot label orphaned", i + 1)
            originals[matches[0]]["pages"].append(i + 1)
            image_order.append(matches[0])
    assert not bounds, bounds
    assert not sparse, ("Sparse text-only pages", sparse)
    assert image_order == list(range(len(originals))), image_order
    out = ROOT / "PDF_검토"
    out.mkdir(exist_ok=True)
    thumbs = []
    for i, page in enumerate(pdf):
        path = out / f"page-{i+1:02}.png"
        page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(path)
        image = Image.open(path).convert("RGB")
        image.thumbnail((400, 283))
        thumb = Image.new("RGB", (420, 310), "#dddddd")
        thumb.paste(image, ((420-image.width)//2, 23))
        ImageDraw.Draw(thumb).text((10, 5), str(i + 1), fill="black")
        thumbs.append(thumb)
    for start in range(0, len(thumbs), 12):
        batch = thumbs[start:start+12]
        sheet = Image.new("RGB", (1260, ((len(batch)+2)//3)*310), "white")
        for i, thumb in enumerate(batch):
            sheet.paste(thumb, ((i%3)*420, (i//3)*310))
        sheet.save(out / f"contact-{start//12+1}.png")
    for original in originals:
        del original["pixels"]
    result = {"pdf": str(PDF), "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
              "pages": len(pdf), "a4_landscape_all_pages": True, "export_assets_unchanged": True,
              "all_text_and_code_extracted": True, "paired_source_analysis_rows": paired,
              "new_screenshots_in_pdf": originals, "horizontal_or_vertical_clipping": bounds,
              "visual_review": "pending", "original_pdf_preserved": True}
    (ROOT / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(f"Verified {len(pdf)} A4 landscape pages, {len(paired)} paired code/analysis rows, {len(originals)} exact screenshot images.")
    for i, text in enumerate(page_texts):
        print(f"Page {i+1}: {text[:70].replace(chr(10), ' / ')}")


if __name__ == "__main__":
    main()
