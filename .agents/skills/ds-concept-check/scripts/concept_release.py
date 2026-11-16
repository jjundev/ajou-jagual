#!/usr/bin/env python3
"""복습팩 후속 확인문제의 외부 작업본 준비 및 발행."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import sys
from uuid import uuid4

import blind
import browser_check
import build
import check

from browser_review import local_asset, render_urls
from pack_layout import RANGE_RE, check_layout, normalized_child
from pdf_cards import digest
from pdf_publish import lock_handle
from release_review import publication_lock
from review_source import review_paths, source_file
from update_review import publish_update


SHARED = Path("복습노트/_assets/problem-explain/v1")
SOURCE_FILES = ("objectives.json", "items.json", "blind-ledger.json")
SLUG_RE = re.compile(r"[A-Za-z0-9_]+")
CASES = tuple(f"{w}x{h}/{theme}" for w, h in browser_check.VIEWPORTS for theme in browser_check.THEMES)


def checked_path(root: Path, relative: Path) -> Path:
    """Resolve NFC/NFD names without following symbolic links."""
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"범위를 벗어난 경로: {relative}")
    path = root
    for part in relative.parts:
        path = normalized_child(path, part)
        if path.is_symlink():
            raise ValueError(f"심볼릭 링크를 사용할 수 없어요: {path}")
    return path


def require_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"팩이 없어 근거가 없습니다: {path}")
    return path


def roots(repo: Path, range_: str, run: Path) -> tuple[Path, Path, Path]:
    repo = repo.resolve(strict=True)
    if not RANGE_RE.fullmatch(range_) or not repo.is_dir():
        raise ValueError(f"복습팩 경로 또는 범위 오류: {repo} / {range_}")
    resolved_run = run.resolve()
    if run.is_symlink() or resolved_run.is_relative_to(repo) or repo.is_relative_to(resolved_run):
        raise ValueError(f"저장소 밖의 별도 RUN이 필요해요: {run}")
    live = checked_path(repo, Path("복습노트") / range_)
    if not live.is_dir():
        raise ValueError(f"팩이 없어 근거가 없습니다: {live}")
    return repo, live, resolved_run


def pack_slug(root: Path, live: Path, range_: str) -> str:
    manifest = require_file(checked_path(live, Path(".pack/자료_복습팩/manifest.json")))
    data = read_object(manifest)
    slug = data.get("slug")
    if data.get("range") != range_ or not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        raise ValueError(f"manifest range/slug 오류: {manifest.relative_to(root)}")
    return slug


def input_files(root: Path, pack: Path, range_: str, slug: str) -> dict[str, str]:
    note = require_file(checked_path(pack, Path(build.note_name(range_, slug))))
    paths = {note}
    for name in (".pack/자료_복습팩/manifest.json", ".pack/자료_복습팩/stt-summary.md",
                 f".pack/정리노트_{range_}_{slug}.md"):
        paths.add(require_file(checked_path(pack, Path(name))))
    for path in review_paths(pack):
        # Validate the logical HTML as well as the effective archive/HTML.
        checked_path(root, path.relative_to(root))
        paths.add(require_file(checked_path(root, source_file(path).relative_to(root))))

    shared = checked_path(root, SHARED)
    if not shared.is_dir():
        raise ValueError(f"공용 자원 없음: {shared}")
    build.assemble.asset_root(pack, assets_dir=shared)
    for path in shared.rglob("*"):
        checked_path(root, path.relative_to(root))
        if path.is_file():
            paths.add(path)

    pending, scanned = [note], set()
    while pending:
        origin = pending.pop()
        if origin in scanned:
            continue
        scanned.add(origin)
        for url in sorted(render_urls(origin)):
            asset = local_asset(root, origin, url)
            if asset is None:
                continue
            paths.add(checked_path(root, asset.relative_to(root)))
            if asset.suffix.lower() in {".css", ".svg"}:
                pending.append(asset)
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(paths)}


def owned_paths(root: Path, pack: Path, range_: str, slug: str) -> tuple[Path, ...]:
    src = Path(".pack") / f"자료_확인문제_{range_}_{slug}"
    return tuple(checked_path(root, pack.relative_to(root) / rel)
                 for rel in (Path(build.output_name(range_, slug)),
                             *(src / name for name in (*SOURCE_FILES, "browser.json"))))


def owned_snapshot(root: Path, paths: tuple[Path, ...]) -> dict[str, str | None]:
    result = {}
    for path in paths:
        if path.exists() and not path.is_file():
            raise ValueError(f"발행 대상이 파일이 아니에요: {path}")
        result[path.relative_to(root).as_posix()] = digest(path) if path.is_file() else None
    return result


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    data = dict(pairs)
    if len(data) != len(pairs):
        raise ValueError("검증 JSON에 중복 키가 있어요")
    return data


def read_object(path: Path, data: bytes | None = None) -> dict:
    value = json.loads(require_file(path).read_bytes() if data is None else data, object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise ValueError(f"JSON 객체가 필요해요: {path}")
    return value


def write_object(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def prepare(repo: Path, range_: str, run: Path) -> Path:
    repo, live, run = roots(repo, range_, run)
    run.mkdir(parents=True, exist_ok=True)
    if any(run.iterdir()):
        raise ValueError(f"비어 있는 RUN이 필요해요: {run}")
    stage = run / "stage"
    stage.mkdir()
    with publication_lock(live).open("a+") as handle:
        lock_handle(handle)
        slug = pack_slug(repo, live, range_)
        inputs = input_files(repo, live, range_, slug)
        before = owned_snapshot(repo, owned_paths(repo, live, range_, slug))
        for rel, checksum in inputs.items():
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repo / rel, target)
            if digest(target) != checksum:
                raise ValueError(f"작업본 복사 중 근거가 바뀌었어요: {rel}")
        stage_pack = stage / live.relative_to(repo)
        src = owned_paths(stage, stage_pack, range_, slug)[1].parent
        if src.exists() or (stage_pack / build.output_name(range_, slug)).exists():
            raise ValueError("작업본에 기존 확인문제 산출물이 포함됐어요")
        src.mkdir()
        write_object(run / "prepare.json", {
            "version": 1, "repo": str(repo), "range": range_, "slug": slug,
            "inputs": inputs, "owned_before": before,
        })
    return src


@dataclass(frozen=True)
class Candidate:
    stage: Path
    src: Path
    page: Path
    prepare_sha256: str
    artifacts: dict[str, str]
    files: dict[Path, bytes]
    ids: tuple[str, ...]


def candidate(repo: Path, live: Path, range_: str, run: Path) -> tuple[Candidate, tuple[Path, ...]]:
    prepare_file = require_file(checked_path(run, Path("prepare.json")))
    prepared_bytes = prepare_file.read_bytes()
    prepared = read_object(prepare_file, prepared_bytes)
    slug = pack_slug(repo, live, range_)
    if (prepared.get("version"), prepared.get("repo"), prepared.get("range"), prepared.get("slug")) != (
            1, str(repo), range_, slug):
        raise ValueError("요청한 저장소와 복습팩에 맞는 RUN이 필요해요")
    live_paths = owned_paths(repo, live, range_, slug)
    if owned_snapshot(repo, live_paths) != prepared.get("owned_before"):
        raise ValueError("기존 확인문제 산출물이 준비 이후 바뀌었어요")
    stage = checked_path(run, Path("stage"))
    stage_pack = checked_path(stage, live.relative_to(repo))
    if not stage_pack.is_dir():
        raise ValueError("확인문제 작업본 팩이 없어요")
    for pack in (live, stage_pack):
        layout = check_layout(pack)
        if layout:
            raise ValueError(layout[0])
    if (input_files(repo, live, range_, slug) != prepared.get("inputs")
            or input_files(stage, stage_pack, range_, slug) != prepared.get("inputs")):
        raise ValueError("공개 팩 또는 작업본의 근거가 준비 이후 바뀌었어요")

    page, objectives, items, ledger, _ = owned_paths(stage, stage_pack, range_, slug)
    src = objectives.parent
    files = {path: require_file(path).read_bytes() for path in (page, objectives, items, ledger)}
    try:
        problems = check.check(src)
        if problems:
            raise ValueError(f"확인문제 규칙 검사 실패 {len(problems)}건: {problems[0]}")
        rows = read_object(ledger, files[ledger])
        ids = tuple(item["id"] for item in build.load_source(src)["items"])
        if not ids or set(rows) != set(ids) or any(
                not isinstance(row, dict) or type(row.get("round")) is not int or row["round"] not in (1, 2, 3)
                for row in rows.values()):
            raise ValueError("블라인드 장부에는 문항별 r1~r3 판정이 필요해요")
        unresolved = blind.status(src, ledger)
        if unresolved:
            raise ValueError(f"블라인드 풀이 미해결 {len(unresolved)}건: {unresolved[0]}")
        rendered = build.render_page(src, assets_dir=checked_path(stage, SHARED)).encode("utf-8")
    except (build.BuildError, build.assemble.AssembleError, KeyError, TypeError, AttributeError) as error:
        raise ValueError(f"확인문제 검증 실패: {error}") from error
    if rendered != files[page]:
        raise ValueError("문항 또는 목표의 현재 데이터로 HTML을 다시 빌드하세요")
    artifacts = {path.relative_to(stage).as_posix(): sha256(data).hexdigest() for path, data in files.items()}
    if any(path.read_bytes() != data for path, data in files.items()):
        raise ValueError("검사 중 작업본 산출물이 바뀌었어요")
    return Candidate(stage, src, page, sha256(prepared_bytes).hexdigest(), artifacts, files, ids), live_paths


def request_record(work: Candidate, attempt: str) -> dict:
    return {"version": 1, "attempt": attempt, "prepare_sha256": work.prepare_sha256,
            "artifacts": work.artifacts, "cases": list(CASES)}


def write_review_request(repo: Path, range_: str, run: Path) -> Path:
    repo, live, run = roots(repo, range_, run)
    # The worker writes only in RUN. Publication rechecks the same inputs under the lock.
    work, _ = candidate(repo, live, range_, run)
    request = checked_path(run, Path("review-request.json"))
    return write_object(request, request_record(work, uuid4().hex))


def reviewed_browser(run: Path, work: Candidate) -> tuple[str, bytes]:
    request_file = require_file(checked_path(run, Path("review-request.json")))
    request_bytes = request_file.read_bytes()
    request = read_object(request_file, request_bytes)
    attempt = request.get("attempt")
    if (not isinstance(attempt, str) or not re.fullmatch(r"[0-9a-f]{32}", attempt)
            or request != request_record(work, attempt)):
        raise ValueError("현재 작업본과 브라우저 검토 요청이 달라요")
    browser_dir = checked_path(run, Path("browser") / attempt)
    browser_file = require_file(checked_path(browser_dir, Path("browser.json")))
    browser_bytes = browser_file.read_bytes()
    browser = read_object(browser_file, browser_bytes)
    page_rel = work.page.relative_to(work.stage).as_posix()
    labels = {case.replace("/", " ") for case in CASES}
    rows = browser.get("runs")
    total = len(work.ids)
    request_sha256 = sha256(request_bytes).hexdigest()
    if (browser.get("status") != "pass" or browser.get("failures") != []
            or browser.get("html") != page_rel or browser.get("sha256") != work.artifacts[page_rel]
            or browser.get("attempt") != attempt or browser.get("request_sha256") != request_sha256
            or browser.get("transport") != "file://, offline=True"
            or not isinstance(rows, list) or len(rows) != len(labels)
            or any(not isinstance(row, dict) or row.get("failures") != [] or row.get("external_blocked") != []
                   or row.get("detail") != dict(items=total, items_checked=total, hints_checked=total)
                   for row in rows)
            or not all(isinstance(row.get("label"), str) for row in rows)
            or {row["label"] for row in rows} != labels):
        raise ValueError("현재 HTML의 브라우저 검사 4조합이 모두 통과해야 해요")

    manual_file = checked_path(browser_dir, Path("visual-review.json"))
    manual = read_object(manual_file)
    cases = manual.get("cases")
    hashes = browser.get("screenshots")
    if (manual.get("version") != 1 or manual.get("status") != "pass"
            or manual.get("request_sha256") != request_sha256
            or manual.get("browser_report_sha256") != sha256(browser_bytes).hexdigest()
            or not isinstance(manual.get("reviewer"), str) or not manual["reviewer"].strip()
            or not isinstance(hashes, dict) or not isinstance(cases, dict) or cases.keys() != set(CASES)):
        raise ValueError("현재 요청과 브라우저 검사에 대한 수동 화면 검토가 필요해요")
    first = work.ids[0]
    if not re.fullmatch(r"q[0-9]+", first):
        raise ValueError(f"잘못된 첫 문항 ID: {first}")
    for case, row in cases.items():
        tag = case.replace("/", "-")
        shots = {f"shots/{tag}-{suffix}.png" for suffix in (first, first + "-hint", "last")}
        if (not isinstance(row, dict) or row.get("status") != "pass"
                or not isinstance(row.get("observation"), str) or not row["observation"].strip()
                or not isinstance(row.get("screenshots"), list) or len(row["screenshots"]) != len(shots)
                or not all(isinstance(path, str) for path in row["screenshots"])
                or set(row["screenshots"]) != shots
                or any(digest(require_file(checked_path(browser_dir, Path(path)))) != hashes.get(path)
                       for path in shots)):
            raise ValueError(f"화면 관찰 또는 캡처가 누락되거나 바뀌었어요: {case}")
    return attempt, browser_bytes


def _publish(repo: Path, range_: str, run: Path) -> tuple[Path, Path]:
    repo, live, run = roots(repo, range_, run)
    with publication_lock(live).open("a+") as handle:
        lock_handle(handle)
        work, targets = candidate(repo, live, range_, run)
        attempt, browser_bytes = reviewed_browser(run, work)
        backups = checked_path(run, Path("backups"))
        backup = checked_path(backups, Path(attempt))
        if backup.exists():
            backup = checked_path(backups, Path(f"{attempt}-{uuid4().hex}"))
        staged = [work.page, *(work.src / name for name in SOURCE_FILES)]
        files = {target: work.files[path] for target, path in zip(targets[:-1], staged)}
        files[targets[-1]] = browser_bytes
        publish_update(files, backup=backup)
    return targets[0], backup


def publish(repo: Path, range_: str, run: Path) -> Path:
    return _publish(repo, range_, run)[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "review-request", "publish"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--range", required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    try:
        inputs = (args.repo, args.range, args.run)
        if args.command == "publish":
            page, backup = _publish(*inputs)
            print(f"발행 {page} · 백업 {backup}")
        else:
            command = prepare if args.command == "prepare" else write_review_request
            print(command(*inputs))
    except (ValueError, OSError, build.assemble.AssembleError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
