"""Read review card archives and legacy review HTML."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote
import unicodedata

RANGE_RE = re.compile(r"\d{4}(?:-\d{4})?")


def nfc(s) -> str:
    return unicodedata.normalize("NFC", str(s))

def normalized_child(parent, name) -> Path:
    """Resolve a single NFC/NFD name; never silently choose ambiguous siblings."""
    parent=Path(parent)
    matches=[p for p in parent.iterdir() if nfc(p.name)==nfc(name)] if parent.is_dir() else []
    if len(matches)>1:raise ValueError(f'ambiguous normalized path: {parent / name}')
    return matches[0] if matches else parent/name


def pack_folders(repo) -> list[Path]:
    notes = normalized_child(repo, "복습노트")
    if not notes.is_dir():
        return []
    return sorted((d for d in notes.iterdir() if d.is_dir() and RANGE_RE.fullmatch(nfc(d.name))),
                  key=lambda d: nfc(d.name))


NAME = re.compile(r"복습문제_(\d{4}(?:-\d{4})?)_([A-Za-z0-9_]+)\.html")


def review_path(source: Path) -> Path:
    """Return the pack-relative anchor for either input format."""
    source = Path(source)
    if source.suffix == ".json" and nfc(source.parent.name) == "자료_복습팩" and source.parent.parent.name == ".pack":
        source = source.parents[2] / source.with_suffix(".html").name
    if not NAME.fullmatch(nfc(source.name)):
        raise ValueError(f"복습문제 입력 이름 오류: {source}")
    return normalized_child(source.parent, source.name)


def archive_path(source: Path) -> Path:
    source = review_path(source)
    data = normalized_child(source.parent / ".pack", "자료_복습팩")
    return normalized_child(data, nfc(source.stem) + ".json")


def source_file(source: Path) -> Path:
    source = review_path(source)
    if source.is_file():
        return source
    return archive_path(source)


def source_digest(source: Path) -> str:
    return hashlib.sha256(source_file(source).read_bytes()).hexdigest()


def review_paths(root: Path) -> tuple[Path, ...]:
    root = Path(root)
    html = [p for p in root.glob("*.html") if NAME.fullmatch(nfc(p.name))]
    data = normalized_child(root / ".pack", "자료_복습팩")
    paths = {nfc(p.name): p for p in html}
    for path in data.glob("*.json"):
        name = nfc(path.with_suffix(".html").name)
        if NAME.fullmatch(name):
            paths.setdefault(name, root / name)
    return tuple(paths[name] for name in sorted(paths))


def read_archive(path: Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    expected = nfc(Path(path).with_suffix(".html").name)
    if (not isinstance(value, dict) or value.get("version") != 1 or value.get("name") != expected
            or not isinstance(value.get("sections"), list) or not isinstance(value.get("scripts"), list)
            or not all(isinstance(item, str) for item in value["sections"] + value["scripts"])):
        raise ValueError(f"복습문제 원고 형식 오류: {path}")
    return value


def archived_markup(path: Path) -> str:
    document = read_archive(path)
    return "\n".join(document["sections"] + document["scripts"])


def read_review(source: Path) -> str:
    path = source_file(source)
    if path.suffix == ".json":
        return archived_markup(path)
    return path.read_text(encoding="utf-8")


def problem_pdf_pages(source: Path) -> dict[str, int]:
    """Use a published page map only when both the source and PDF match its hashes."""
    source = review_path(source)
    report = source.parent / ".pack/자료_PDF/pdf-validation.json"
    pdf = source.with_name(source.stem + "-문제.pdf")
    if not report.is_file() or not pdf.is_file():
        return {}
    value = json.loads(report.read_text(encoding="utf-8"))
    if value.get("status") != "published":
        return {}
    actual = source_file(source)
    archive = read_archive(actual) if actual.suffix == ".json" else {}
    sha = source_digest(source)
    pdf_sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if (value.get("source_sha256") in (sha, archive.get("html_sha256"))
            and value.get("artifact_hashes", {}).get(nfc(pdf.name)) == pdf_sha):
        pages = value.get("probes", {}).get("problems", {}).get("page_ids", [])
        return {pid: page for page, pid in enumerate(pages, 1) if re.fullmatch(r"p[1-9]\d*", pid)}
    verified = archive.get("verified_problem_pdf", {})
    return verified.get("pages", {}) if verified.get("sha256") == pdf_sha else {}


def problem_href(source: Path, problem_id: str, pages: dict[str, int]) -> str:
    source = review_path(source)
    name = quote(nfc(source.stem) + "-문제.pdf", safe="")
    return f"{name}#page={pages[problem_id]}" if problem_id in pages else name
