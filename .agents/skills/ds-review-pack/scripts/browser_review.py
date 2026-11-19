"""Bind browser review of the working pack to its current render inputs."""
import hashlib
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from uuid import uuid4

from browser_layout import expected_scopes, has_layout_defect, needs_visual_check
from manifest import load
from pack_layout import nfc, normalized_child
from pdf_cards import digest
from review_source import review_paths

MEASUREMENTS = "layout-measurements.json"
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


def browser_paths(stage: Path) -> tuple[Path, Path, Path]:
    reviews = review_paths(stage)
    if len(reviews) != 1 or not reviews[0].is_file():
        raise ValueError("브라우저 검토에 작업용 복습문제 HTML 하나가 필요해요")
    review = reviews[0]
    note = normalized_child(stage, nfc(review.name).replace("복습문제_", "정리노트_", 1))
    manifest = normalized_child(stage / ".pack", "자료_복습팩") / "manifest.json"
    return note, review, manifest


def render_inputs(repo: Path, stage: Path) -> dict[str, str]:
    note, review, manifest = browser_paths(stage)
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


def snapshot(repo: Path, stage: Path, mode: str, attempt: str, *, version: int | None = None) -> dict:
    if version is None:
        version = 2 if mode == "new" else 1
    if type(version) is not int or version not in (1, 2) or (version == 2 and mode != "new"):
        raise ValueError("브라우저 검토 요청 버전이 모드와 맞지 않아요")
    cases = required_cases(mode)
    request = {
        "version": version, "attempt": attempt, "mode": mode, "stage": str(stage),
        "cases": list(cases), "inputs": render_inputs(repo.resolve(), stage),
    }
    if version == 2:
        manifest = load(browser_paths(stage)[2])
        scopes = {kind: [list(pair) for pair in expected_scopes(manifest, kind)] for kind in ("note", "review")}
        request["expected_scopes"] = {case: scopes[case.split("/")[0]] for case in cases}
    return request


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


def attempt_directory(run: Path, request: dict) -> Path:
    attempt = request.get("attempt")
    if not isinstance(attempt, str) or not re.fullmatch(r"[0-9a-f]{32}", attempt):
        raise ValueError("브라우저 검토 요청 번호가 잘못됐어요")
    browser = run / "browser"
    directory = browser / attempt
    if browser.is_symlink() or directory.is_symlink() or not directory.is_dir():
        raise ValueError("브라우저 검토 시도 폴더를 확인할 수 없어요")
    return directory


def request_matches(repo: Path, stage: Path, mode: str, request: dict) -> None:
    try:
        current = snapshot(repo, stage, mode, request["attempt"], version=request.get("version"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"브라우저 검토 입력 오류: {exc}") from exc
    if current != request:
        raise ValueError("브라우저 검토 요청 후 입력이 변경됐어요")


def finite(value) -> bool:
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def scope_key(row) -> tuple[str, str] | None:
    if isinstance(row, dict) and has_text(row.get("id")) and has_text(row.get("area")):
        return row["id"], row["area"]
    return None


def valid_layout_row(row) -> bool:
    if scope_key(row) is None or row.get("state") not in ("measured", "no-figure", "visual-only"):
        return False
    overflow = row.get("overflow_px")
    count = row.get("svg_text_count")
    if not finite(overflow) or overflow < 0 or type(count) is not int or count < 0:
        return False
    if "min_svg_text_height_px" not in row or (row["state"] == "no-figure" and count != 0):
        return False
    height = row["min_svg_text_height_px"]
    if count == 0 and height is not None or count > 0 and (not finite(height) or height <= 0):
        return False
    widgets = row.get("widget_min_svg_text_height_px")
    return isinstance(widgets, dict) and all(
        has_text(key) and (value is None or (height is not None and finite(value) and value >= height))
        for key, value in widgets.items()
    )


def require_measurements(directory: Path, request: dict, request_sha: str, approval: dict) -> None:
    path = directory / MEASUREMENTS
    if path.is_symlink():
        raise ValueError("브라우저 검토 측정 파일에 심볼릭 링크를 사용할 수 없어요")
    data, raw = read_record(path)
    if (hashlib.sha256(raw).hexdigest() != approval.get("measurements_sha256")
            or data.get("request_sha256") != request_sha
            or type(data.get("version")) is not int or data["version"] != 1):
        raise ValueError("브라우저 검토 측정 기록이 현재 승인 또는 요청과 달라요")
    cases = data.get("cases")
    if not isinstance(cases, dict) or set(cases) != set(request["cases"]):
        raise ValueError("브라우저 검토 측정의 필수 화면 조합이 맞지 않아요")
    for case, result in cases.items():
        if not isinstance(result, dict) or result.get("errors") != [] or not isinstance(result.get("rows"), list):
            raise ValueError(f"브라우저 검토 측정 오류: {case}")
        required = {tuple(pair) for pair in request["expected_scopes"][case]}
        measured = set()
        review_needed = set()
        for row in result["rows"]:
            key = scope_key(row)
            if key not in required or key in measured or not valid_layout_row(row):
                raise ValueError(f"브라우저 검토 측정 영역 또는 수치 오류: {case} {key}")
            if has_layout_defect(row):
                raise ValueError(f"브라우저 검토 레이아웃 결함: {case} {key}")
            measured.add(key)
            if needs_visual_check(row):
                review_needed.add(key)
        if measured != required:
            raise ValueError(f"브라우저 검토 측정 영역 누락: {case} {sorted(required - measured)}")

        notes = approval["cases"][case].get("visual_notes")
        if not isinstance(notes, list):
            raise ValueError(f"브라우저 검토 실화면 관찰 목록 오류: {case}")
        observed = set()
        for note in notes:
            key = scope_key(note)
            if key not in required or key in observed or not has_text(note.get("observation")):
                raise ValueError(f"브라우저 검토 실화면 관찰 영역 또는 내용 오류: {case} {key}")
            observed.add(key)
        if not review_needed <= observed:
            raise ValueError(f"브라우저 검토 실화면 관찰 누락: {case} {sorted(review_needed - observed)}")


def require_pass(repo: Path, stage: Path, run: Path, mode: str) -> None:
    request, raw = read_record(run / "browser-request.json")
    directory = attempt_directory(run, request)
    version = request.get("version")
    request_sha = hashlib.sha256(raw).hexdigest()
    approval, _ = read_record(directory / "browser-review.json")
    if (type(version) is not int or version not in (1, 2)
            or type(approval.get("version")) is not int or approval["version"] != version
            or approval.get("request_sha256") != request_sha):
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
    request_matches(repo, stage, mode, request)
    if version == 2:
        require_measurements(directory, request, request_sha, approval)
