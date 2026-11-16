"""Bind browser review of the working pack to its current render inputs."""
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from uuid import uuid4

from pack_layout import nfc, normalized_child
from pdf_cards import digest
from review_source import review_paths

MODES = ("new", "update-existing", "revise-existing")
ASSET_SUFFIXES = {
    ".avif", ".bmp", ".css", ".gif", ".ico", ".jpeg", ".jpg", ".js", ".mjs", ".otf", ".png",
    ".svg", ".ttf", ".webp", ".woff", ".woff2",
}
RENDER_ATTRIBUTES = {
    "audio": ("src",), "embed": ("src",), "image": ("href", "xlink:href"),
    "img": ("src",), "input": ("src",), "object": ("data",), "script": ("src",),
    "source": ("src",), "track": ("src",), "use": ("href", "xlink:href"),
    "video": ("src", "poster"),
}

CSS_URLS = re.compile(
    r"""/\*.*?\*/|url\(\s*(?:"([^"]+)"|'([^']+)'|([^\s)'"]+))\s*\)|@import\s+["']([^"']+)["']""",
    re.IGNORECASE | re.DOTALL,
)
SRCSET_URL = re.compile(r"[\s,]*([^\s,]\S*)")


def css_urls(text: str) -> set[str]:
    return {url for match in CSS_URLS.finditer(text) for url in match.groups() if url}


def srcset_urls(text: str) -> set[str]:
    urls = set()
    cursor = 0
    while match := SRCSET_URL.match(text, cursor):
        url = match[1]
        urls.add(url.rstrip(","))
        cursor = match.end()
        if not url.endswith(","):
            comma = text.find(",", cursor)
            cursor = len(text) if comma < 0 else comma + 1
    return urls


def required_cases(mode: str) -> tuple[str, ...]:
    if mode not in MODES:
        raise ValueError(f"브라우저 검토 모드 오류: {mode}")
    pages = ("note", "review") if mode == "new" else ("review",)
    return tuple(f"{page}/{size}/{theme}" for page in pages
                 for size in ("1280x900", "375x812") for theme in ("light", "dark"))


class RenderLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()
        self.style = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        keys = RENDER_ATTRIBUTES.get(tag, ())
        if tag == "link" and {"stylesheet", "icon", "preload", "modulepreload"}.intersection(
                (attrs.get("rel") or "").lower().split()):
            keys = ("href",)
        self.urls.update(attrs[key] for key in keys if attrs.get(key))
        if tag in {"img", "source"} and attrs.get("srcset"):
            self.urls.update(srcset_urls(attrs["srcset"]))
        if attrs.get("style"):
            self.urls.update(css_urls(attrs["style"]))
        if tag == "style":
            self.style = True

    def handle_endtag(self, tag):
        if tag == "style":
            self.style = False

    def handle_data(self, data):
        if self.style:
            self.urls.update(css_urls(data))


def render_urls(path: Path) -> set[str]:
    if path.suffix.lower() == ".css":
        return css_urls(path.read_text(encoding="utf-8"))
    parser = RenderLinks()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.urls


def local_asset(repo: Path, page: Path, url: str) -> Path | None:
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    relative = unquote(parsed.path)
    path = repo / relative.lstrip("/") if relative.startswith("/") else page.parent / relative
    path = Path(os.path.normpath(path))
    if not path.is_relative_to(repo):
        raise ValueError(f"브라우저 검토 자원이 저장소 밖에 있어요: {url}")
    actual = repo
    for part in path.relative_to(repo).parts:
        actual = normalized_child(actual, part)
    if not actual.resolve().is_relative_to(repo) or not actual.is_file():
        raise ValueError(f"브라우저 검토 자원이 없거나 저장소 밖에 있어요: {url}")
    return actual


def render_inputs(repo: Path, stage: Path) -> dict[str, str]:
    reviews = review_paths(stage)
    if len(reviews) != 1 or not reviews[0].is_file():
        raise ValueError("브라우저 검토에 작업용 복습문제 HTML 하나가 필요해요")
    review = reviews[0]
    note = normalized_child(stage, nfc(review.name).replace("복습문제_", "정리노트_", 1))
    manifest = normalized_child(stage / ".pack", "자료_복습팩") / "manifest.json"
    paths = {note, review, manifest}
    paths.update(p for p in stage.rglob("*") if p.is_file() and p.suffix.lower() in ASSET_SUFFIXES)
    paths.update(p for p in (stage.parent / "_assets").rglob("*") if p.is_file())
    pending = [note, review]
    scanned = set()
    while pending:
        origin = pending.pop()
        if origin in scanned:
            continue
        scanned.add(origin)
        for url in sorted(render_urls(origin)):
            asset = local_asset(repo, origin, url)
            if asset is not None:
                paths.add(asset)
                if asset.suffix.lower() in {".css", ".svg"}:
                    pending.append(asset)
    return {path.relative_to(repo).as_posix(): digest(path) for path in sorted(paths)}


def snapshot(repo: Path, stage: Path, mode: str, attempt: str) -> dict:
    return {
        "version": 1, "attempt": attempt, "mode": mode, "stage": str(stage),
        "cases": list(required_cases(mode)), "inputs": render_inputs(repo.resolve(), stage),
    }


def write_request(repo: Path, stage: Path, run: Path, mode: str) -> Path:
    attempt = uuid4().hex
    value = snapshot(repo, stage, mode, attempt)
    attempt_dir = run / "browser" / attempt
    attempt_dir.mkdir(parents=True)
    pending = run / f".browser-request-{attempt}.tmp"
    path = run / "browser-request.json"
    try:
        pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        pending.replace(path)
    finally:
        pending.unlink(missing_ok=True)
    return path


def read_record(path: Path) -> tuple[dict, bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise ValueError(f"브라우저 검토 기록을 읽을 수 없어요: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"브라우저 검토 기록 형식이 잘못됐어요: {path}")
    return value, raw


def has_text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_pass(repo: Path, stage: Path, run: Path, mode: str) -> None:
    request, raw = read_record(run / "browser-request.json")
    attempt = request.get("attempt")
    if not isinstance(attempt, str) or not re.fullmatch(r"[0-9a-f]{32}", attempt):
        raise ValueError("브라우저 검토 요청 번호가 잘못됐어요")
    approval, _ = read_record(run / "browser" / attempt / "browser-review.json")
    if approval.get("version") != 1 or approval.get("request_sha256") != hashlib.sha256(raw).hexdigest():
        raise ValueError("브라우저 검토 기록이 현재 요청과 달라요")
    if approval.get("status") != "pass" or not has_text(approval.get("reviewer")) or approval.get("issues") != []:
        raise ValueError("브라우저 검토가 통과하지 않았어요")
    cases = approval.get("cases")
    required = required_cases(mode)
    if not isinstance(cases, dict) or set(cases) != set(required):
        raise ValueError("브라우저 검토의 필수 화면 조합이 맞지 않아요")
    for case in required:
        row = cases[case]
        if not isinstance(row, dict) or row.get("status") != "pass" or not has_text(row.get("evidence")):
            raise ValueError(f"브라우저 검토의 확인 근거가 없거나 통과하지 않았어요: {case}")
    try:
        current = snapshot(repo, stage, mode, attempt)
    except OSError as exc:
        raise ValueError("브라우저 검토 후 입력을 읽을 수 없어요") from exc
    if current != request:
        raise ValueError("브라우저 검토 요청 후 입력이 변경됐어요")
