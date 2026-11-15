"""Persist authored review sections independently of the browser document."""
import argparse
import hashlib
import json
from pathlib import Path

from update_review import Spans, extract_cards
from review_input import (
    archive_path, archived_markup, read_archive, read_review, review_path, review_paths,
    source_file, source_digest, nfc, NAME, problem_href, problem_pdf_pages,
)

SHELL_SCRIPTS = {"theme-ui", "panels-ui", "pager-ui"}


def archive_review(source: Path) -> Path:
    """Store exact problem/solution spans and authored scripts, excluding the page shell."""
    source = review_path(source)
    raw = source.read_text(encoding="utf-8")
    spans = sorted(Spans(raw).spans, key=lambda row: row[2])
    main = next((row for row in spans if row[0] == "main"), None)
    sections = [raw[start:end] for tag, _, start, end in spans
                if tag == "section" and (main is None or main[2] < start < end < main[3])
                and not any(parent[0] == "section" and parent[2] < start < end < parent[3] for parent in spans)]
    if not sections and extract_cards(raw):
        sections = [card["raw"] for card in extract_cards(raw)]
    scripts = [raw[start:end] for tag, attrs, start, end in spans if tag == "script"
               and attrs.get("id") not in SHELL_SCRIPTS and "src" not in attrs
               and not any(raw[start:end] in section for section in sections)
               and not raw[start:end].startswith("<script>document.documentElement.classList.add")]
    if extract_cards(raw) != extract_cards("\n".join(sections)):
        raise ValueError(f"보존 카드의 내용 또는 순서가 달라졌어요: {source}")
    value = {
        "version": 1,
        "name": nfc(source.name),
        "html_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "sections": sections,
        "scripts": scripts,
    }
    path = archive_path(source)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path)
    args = parser.parse_args()
    print(archive_review(args.review))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
