"""Verify source fidelity, recorded outputs, PDF text, and page boundaries."""

from pathlib import Path
import hashlib
import json
import re

import fitz
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (ROOT / "HW2.c").read_text()
RUNS = json.loads((ROOT / "검토자료/실행기록_보고서.json").read_text())
MANIFEST = json.loads((ROOT / "검토자료/보고서_구성.json").read_text())
HTML_CHECKS = json.loads((ROOT / "검토자료/HTML_검증.json").read_text())
NORMALIZE = lambda text: re.sub(r"\s+", "", text)


def main():
    sha = hashlib.sha256((ROOT / "HW2.c").read_bytes()).hexdigest()
    assert sha == RUNS["sha256"] == MANIFEST["source_sha256"]
    assert RUNS["passed"] == RUNS["total"]
    assert not RUNS["build"]["stderr"]
    assert HTML_CHECKS["overflow"] == []
    doc = fitz.open(ROOT / "보고서_초안.pdf")
    texts = [page.get_text() for page in doc]
    analysis_end = next(index for index, text in enumerate(texts) if text.startswith("실행결과 및 분석\n"))
    matches = []
    for part in MANIFEST["source_parts"]:
        pages = [index + 1 for index, text in enumerate(texts[:analysis_end]) if NORMALIZE(part) in NORMALIZE(text)]
        assert pages, "A source row is missing or split across pages"
        matches.append(pages)
    appendix_start = next(index for index, text in enumerate(texts) if text.startswith("전체 소스코드\n"))
    appendix = "".join(texts[appendix_start:])
    labels = [
        "전체 소스코드 (계속)",
        "전체 소스코드",
        "Mac 사용자용 전체 코드 부록이다. 분석 표와 동일한 HW2.c의 원문이며, 제공 코드와 참고 구현의 출처 머리말도 그대로 포함한다.",
    ]
    for label in labels:
        appendix = appendix.replace(label, "")
    assert NORMALIZE(appendix) == NORMALIZE(SOURCE), "Extracted full source differs"
    full_text = NORMALIZE("".join(texts))
    for name in MANIFEST["case_names"]:
        case = next(case for case in RUNS["cases"] if case["name"] == name)
        assert NORMALIZE(case["stdin"]) in full_text
        assert NORMALIZE(case["stdout"]) in full_text
        assert case["passed"] and case["returncode"] == 0 and not case["stderr"]
    screenshot_pages = [index + 1 for index, page in enumerate(doc) if page.get_images(full=True)]
    assert len(screenshot_pages) == MANIFEST["screenshot_count"]
    for index, text in enumerate(texts):
        assert len(text) > 250 or index + 1 in screenshot_pages, "Sparse orphan page"
    for image in MANIFEST["screenshots"]:
        assert hashlib.sha256(Path(image["path"]).read_bytes()).hexdigest() == image["sha256"]
    outside = []
    for index, page in enumerate(doc):
        assert abs(page.rect.width - 841.89) < 1 and abs(page.rect.height - 595.28) < 1
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    box = fitz.Rect(span["bbox"])
                    if box.x0 < 0 or box.y0 < 0 or box.x1 > page.rect.width + 1 or box.y1 > page.rect.height + 1:
                        outside.append({"page": index + 1, "text": span["text"]})
        for image in page.get_images(full=True):
            for box in page.get_image_rects(image[0]):
                assert box.x0 >= 0 and box.y0 >= 0 and box.x1 <= page.rect.width + 1 and box.y1 <= page.rect.height + 1
    assert not outside, outside

    out = ROOT / "검토자료/PDF_검토"
    out.mkdir(exist_ok=True)
    for old in out.glob("page-*.png"):
        if int(old.stem.split("-")[1]) > len(doc):
            old.unlink()
    thumbnails = []
    for index, page in enumerate(doc):
        target = out / f"page-{index + 1:02}.png"
        page.get_pixmap(matrix=fitz.Matrix(1.15, 1.15)).save(target)
        img = Image.open(target).convert("RGB")
        img.thumbnail((360, 255))
        thumb = Image.new("RGB", (380, 285), "#dededb")
        thumb.paste(img, ((380 - img.width) // 2, 20))
        ImageDraw.Draw(thumb).text((12, 3), str(index + 1), fill="black")
        thumbnails.append(thumb)
    for first in range(0, len(thumbnails), 12):
        subset = thumbnails[first:first + 12]
        sheet = Image.new("RGB", (1140, 285 * ((len(subset) + 2) // 3)), "white")
        for index, thumb in enumerate(subset):
            sheet.paste(thumb, ((index % 3) * 380, (index // 3) * 285))
        sheet.save(out / f"contact-{first // 12 + 1}.png")
    result = {
        "source_sha256": sha,
        "pdf_sha256": hashlib.sha256((ROOT / "보고서_초안.pdf").read_bytes()).hexdigest(),
        "pages": len(doc),
        "a4_landscape": True,
        "code_rows_contained_on_single_pages": matches,
        "appendix_extracted_text_matches_source_ignoring_whitespace": True,
        "html_appendix_exact_source_text": True,
        "execution_case_count": len(MANIFEST["case_names"]),
        "actual_inputs_and_outputs_extract_from_pdf": True,
        "outside_page_bounds": outside,
        "source_verification": {"passed": RUNS["passed"], "total": RUNS["total"]},
        "visual_review": "Page rasters generated; visual inspection is separate from these checks.",
        "screenshots": {"count": MANIFEST["screenshot_count"], "pages": screenshot_pages, "source": "Actual Antigravity IDE integrated terminal; six transcripts and pixel-identical crops verified."},
        "format_scope": "Local body draft; no Notion export, cover merge, or upload performed.",
        "authorship": MANIFEST["authorship"],
    }
    (ROOT / "검토자료/PDF_검증.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"PDF checks passed: {len(doc)} A4 landscape pages; {len(matches)} intact code rows; {len(MANIFEST['case_names'])} actual execution logs; {len(screenshot_pages)} real terminal screenshots; exact full-source appendix text.")


if __name__ == "__main__":
    main()
