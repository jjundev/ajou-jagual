#!/usr/bin/env python3
"""Prepare and publish a review pack with browser-only working HTML."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import sys

from browser_review import MODES, require_pass, required_cases, write_request

from pack_layout import RANGE_RE, nfc, normalized_child, pdf_report_path
from pdf_cards import digest, read_pack
from pdf_publish import lock_handle
from review_links import add_pdf_links, rewrite
from review_source import archive_review, archived_markup, review_paths, source_file, read_archive
from update_review import extract_cards, publish_update


def materialize(source: Path, stage: Path) -> Path:
    """Render the saved fragments in the same browser template used by new packs."""
    from assemble import ASSETS, asset_root, esc, fill
    from manifest import load, note_name
    from update_review import stamp_revision

    actual = source_file(source)
    target = stage / nfc(source.name)
    if actual.suffix == ".html":
        shutil.copy2(actual, target)
        return target
    data = read_archive(actual)
    manifest = load(stage / ".pack/자료_복습팩/manifest.json")
    used = {problem["part"] for problem in manifest["problems"]}
    page = fill((ASSETS / "review-template.html").read_text(encoding="utf-8"), {
        "ASSET_ROOT": asset_root(stage),
        "PAGE_TITLE": esc(manifest["review_title"]),
        "DESCRIPTION": esc(manifest["review_title"]),
        "TOC": "".join(f'<a href="#{p["id"]}">{esc(p["short"])}</a>'
                       for p in manifest["parts"] if p["id"] in used),
        "NOTE_HREF": note_name(manifest),
        "TITLE": esc(manifest["review_title"]),
        "INTRO": manifest["review_intro"],
        "PARTS": "\n".join(data["sections"]),
        "FOOTER": manifest["footer_review"],
        "SCRIPTS": "\n".join(data["scripts"]),
        "RANGE": manifest["range"],
    })
    cards = {card["id"]: card["raw"] for card in extract_cards(archived_markup(actual))}
    target.write_text(stamp_revision(page, manifest, cards), encoding="utf-8")
    return target


def prepare(repo: Path, range_: str, run: Path, *, mode: str = "new") -> Path:
    required_cases(mode)
    if not RANGE_RE.fullmatch(range_):
        raise ValueError("잘못된 복습팩 범위")
    notes = normalized_child(repo.resolve(), "복습노트")
    live = normalized_child(notes, range_)
    run.mkdir(parents=True, exist_ok=True)
    record = run / "release-stage.json"
    if record.exists():
        raise ValueError("새 발행 작업 폴더가 필요해요")
    stage = Path(tempfile.mkdtemp(prefix=f".review-build-{range_}-", dir=notes))
    try:
        baseline = {}
        if live.is_dir():
            if live.is_symlink() or any(p.is_symlink() for p in live.rglob("*")):
                raise ValueError("발행 팩에서 심볼릭 링크를 사용할 수 없어요")
            baseline = {p.relative_to(live).as_posix(): digest(p) for p in live.rglob("*") if p.is_file()}
            shutil.copytree(live, stage, dirs_exist_ok=True)
            copied = {p.relative_to(stage).as_posix(): digest(p) for p in stage.rglob("*") if p.is_file()}
            if copied != baseline:
                raise ValueError("작업본 복사 중 기존 복습팩이 변경됐어요")
            sources = review_paths(live)
            if len(sources) > 1:
                raise ValueError("날짜 폴더에 여러 복습문제 팩이 있어요")
            if sources and not (stage / sources[0].name).exists():
                materialize(sources[0], stage)
        record.write_text(json.dumps({"live": str(live), "stage": str(stage), "baseline": baseline, "mode": mode},
                                     ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except BaseException:
        shutil.rmtree(stage)
        raise
    return stage


def release_paths(repo: Path, run: Path) -> tuple[dict, Path, Path]:
    record = json.loads((run / "release-stage.json").read_text(encoding="utf-8"))
    stage, live = Path(record["stage"]), Path(record["live"])
    notes = normalized_child(repo.resolve(), "복습노트")
    if (stage.parent != notes or live.parent != notes or not stage.name.startswith(".review-build-")
            or stage.is_symlink() or live.is_symlink() or not RANGE_RE.fullmatch(live.name)):
        raise ValueError("발행 위치가 복습노트와 맞지 않아요")
    return record, stage, live


def publication_lock(live: Path) -> Path:
    # The pack release and PDF-only update use the same destination lock.
    lock_dir = Path(tempfile.gettempdir()) / "ds-pdf-locks"
    lock_dir.mkdir(exist_ok=True)
    return lock_dir / (hashlib.sha256(str(live).encode()).hexdigest() + ".lock")


def start_browser_review(repo: Path, run: Path) -> Path:
    record, stage, live = release_paths(repo, run)
    with publication_lock(live).open("a+") as handle:
        lock_handle(handle)
        return write_request(repo, stage, run, record.get("mode", "new"))


def release_files(stage: Path, record: dict) -> tuple[Path, dict[Path, bytes]]:
    if any(p.is_symlink() for p in stage.rglob("*")):
        raise ValueError("작업 폴더에서 심볼릭 링크를 사용할 수 없어요")
    reviews = review_paths(stage)
    if len(reviews) != 1 or not reviews[0].is_file():
        raise ValueError("검증을 끝낸 작업용 복습문제 HTML 하나가 필요해요")
    source = reviews[0]
    pack = read_pack(source)
    stored = archive_review(source)
    if extract_cards(source.read_text(encoding="utf-8")) != extract_cards(archived_markup(stored)):
        raise ValueError("복습문제 원고와 검증한 문항이 달라요")
    report_path = pdf_report_path(stage)
    pdfs = [source.with_name(source.stem + tail) for tail in ("-문제.pdf", "-답안.pdf")]
    pages = {}
    report = None
    if pack.cards:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if (report.get("status") != "published" or report.get("source_sha256") != pack.source_sha256
                or any(digest(p) != report["artifact_hashes"].get(nfc(p.name)) for p in pdfs)):
            raise ValueError("현재 원고의 검증·발행된 PDF 쌍이 필요해요")
        pages = {pid: page for page, pid in enumerate(report["probes"]["problems"]["page_ids"], 1)
                 if pid in {c.id for c in pack.cards}}
    data = stage / ".pack"
    note = stage / nfc(source.name).replace("복습문제_", "정리노트_", 1)
    if not note.is_file():
        raise ValueError("발행할 정리노트가 없어요")
    files = {
        p: p.read_bytes() for p in data.rglob("*") if p.is_file() and p != report_path
        and not any(c.startswith("자료_문제설명_") or c.startswith("자료_확인문제_")
                    for c in p.relative_to(data).parts)
        and record["baseline"].get(p.relative_to(stage).as_posix()) != digest(p)
    }
    manifest = data / "자료_복습팩/manifest.json"
    if manifest.is_file():
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        for link in payload.get("links", []):
            href = rewrite(f'href="{link["href"]}"', source, pages)
            if href != f'href="{link["href"]}"':
                link["href"] = href[6:-1]
        files[manifest] = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if report:
        files.update({p: p.read_bytes() for p in pdfs})
        # Build evidence is left intact. The published location is discoverable by the pack.
        files[report_path] = report_path.read_bytes()
    for p in (note, data / note.with_suffix(".md").name):
        if not p.is_file():
            raise ValueError(f"발행할 정리노트가 없어요: {p.name}")
        markdown = p.suffix == ".md"
        text = p.read_text(encoding="utf-8")
        if pack.cards:
            text = add_pdf_links(rewrite(text, source, pages, markdown=markdown), source, markdown=markdown)
        elif nfc(source.name) in text:
            raise ValueError("문항 0개에 복습문제 링크가 있어요")
        files[p] = text.encode("utf-8")
    return source, files


def publish(repo: Path, run: Path) -> Path:
    record, stage, live = release_paths(repo, run)
    with publication_lock(live).open("a+") as handle:
        lock_handle(handle)
        require_pass(repo, stage, run, record.get("mode", "new"))
        source, files = release_files(stage, record)
        targets = {live / p.relative_to(stage): data for p, data in files.items()}
        old_html = normalized_child(live, nfc(source.name))
        if old_html.is_file():
            targets[old_html] = None
        for path in targets:
            before = record["baseline"].get(path.relative_to(live).as_posix())
            if (digest(path) if path.is_file() else None) != before:
                raise ValueError(f"작업 중 기존 산출물이 변경됐어요: {path}")
        publish_update(targets, backup=run / ".release-backup")
        shutil.rmtree(stage)
    return live


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "browser-request", "publish", "discard"):
        command = commands.add_parser(name)
        command.add_argument("--repo", type=Path, required=True)
        command.add_argument("--run", type=Path, required=True)
        if name == "prepare":
            command.add_argument("--range", required=True)
            command.add_argument("--mode", choices=MODES, default="new")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            print(prepare(args.repo, args.range, args.run, mode=args.mode))
        elif args.command == "browser-request":
            print(start_browser_review(args.repo, args.run))
        elif args.command == "publish":
            print(publish(args.repo, args.run))
        else:
            _, stage, live = release_paths(args.repo, args.run)
            with publication_lock(live).open("a+") as handle:
                lock_handle(handle)
                shutil.rmtree(stage)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
