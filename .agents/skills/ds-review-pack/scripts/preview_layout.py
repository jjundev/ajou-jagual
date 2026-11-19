#!/usr/bin/env python3
"""Preview author fragments and measure the staged review pack."""
from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from tempfile import mkdtemp, mkstemp
from typing import TypedDict
from urllib.parse import unquote, urlsplit

import assemble
import manifest
from browser_layout import CaseLayout, expected_scopes, has_layout_defect, measure_case, needs_visual_check
from browser_review import MEASUREMENTS, attempt_directory, browser_paths, read_record, render_urls, request_matches
from pack_layout import normalized_child
from pdf_cards import read_pack, to_payload
from pdf_layout import plan_pages
from pdf_publish import lock_handle
from pdf_render import render_session
from pdf_types import PdfError
from release_review import publication_lock, release_paths
from review_pdf import pages_for_mode


class LectureLayout(TypedDict):
    id: str
    question_pages: list[str]
    conditions_pages: list[str]
    ask_pages: list[str]
    split_ok: bool


def copy_fragment_assets(run: Path, output: Path, fragments: Sequence[Path]) -> None:
    pending = [(fragment, Path(".")) for fragment in fragments]
    copied = set()
    while pending:
        source, base = pending.pop()
        for url in sorted(render_urls(source)):
            parsed = urlsplit(url)
            if parsed.scheme == "data":
                continue
            if parsed.scheme or parsed.netloc or parsed.path.startswith("/"):
                raise ValueError(f"미리보기 자원은 RUN 상대 경로여야 해요: {url}")
            if not parsed.path:
                continue
            relative = Path(os.path.normpath(base / unquote(parsed.path)))
            asset = run
            for part in relative.parts:
                if part == ".." or relative.is_absolute():
                    raise ValueError(f"미리보기 자원이 RUN 밖에 있어요: {url}")
                asset = normalized_child(asset, part)
            if not asset.resolve().is_relative_to(run) or not asset.is_file():
                raise ValueError(f"미리보기 자원이 없거나 RUN 밖에 있어요: {url}")
            if relative in copied:
                continue
            copied.add(relative)
            dest = output / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(asset, dest)
            if asset.suffix.lower() in {".css", ".svg"}:
                pending.append((asset, relative.parent))


def build_author_page(
    run: Path, output: Path, *, section: str | None, cards: Sequence[str]
) -> tuple[Path, dict]:
    run = run.resolve()
    if (section is not None) == bool(cards):
        raise ValueError("섹션 하나 또는 카드 한 장 이상을 지정하세요")
    partial = manifest.load(run / "manifest.json")
    if section is not None:
        selected = [item for item in partial["sections"] if item["id"] == section]
        if not selected:
            raise ValueError(f"manifest에 없는 섹션: {section}")
        partial["sections"] = selected
        fragments = [run / "sections" / f"{section}.html"]
        name = manifest.note_name(partial)
        html = assemble.build_note(partial, run, output)
    else:
        selected = [item for item in partial["problems"] if item["id"] in cards]
        missing = set(cards) - {item["id"] for item in selected}
        if missing:
            raise ValueError(f"manifest에 없는 카드: {', '.join(sorted(missing))}")
        partial["problems"] = selected
        part_ids = {item["part"] for item in selected}
        partial["parts"] = [part for part in partial["parts"] if part["id"] in part_ids]
        fragments = [run / "cards" / f"{item['id']}.html" for item in selected]
        name = manifest.review_name(partial)
        html = assemble.build_review(partial, run, output)
    output.mkdir(parents=True, exist_ok=True)
    copy_fragment_assets(run, output, fragments)
    path = output / name
    path.write_text(html, encoding="utf-8")
    return path, partial


def probe_lecture_pages(review: Path, work: Path) -> list[LectureLayout]:
    pack = read_pack(review)
    cards = tuple(card for card in pack.cards if card.kind == "강의 코드")
    if not cards:
        return []
    pack = replace(pack, cards=cards)
    pages = pages_for_mode(plan_pages(pack, work), "problems")
    payload = to_payload(pack, "problems", pages, work / "assets")
    layouts: dict[str, LectureLayout] = {
        card.id: {"id": card.id, "question_pages": [], "conditions_pages": [], "ask_pages": [], "split_ok": False}
        for card in cards
    }
    for page, item in zip(pages, payload["problems"]):
        layout = layouts[page.logical_id]
        html = item["html"]
        layout["question_pages"].append(page.physical_id)
        if html["conditions"].strip():
            layout["conditions_pages"].append(page.physical_id)
        if html["ask"].strip():
            layout["ask_pages"].append(page.physical_id)
        if html["conditions"].strip() and ('class="ds-asks"' in html["ask"] or 'class="ds-asks ' in html["ask"]):
            layout["split_ok"] = True
    return list(layouts.values())


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def case_issues(case: str, result: CaseLayout) -> list[str]:
    issues = [f"{case}: {error}" for error in result["errors"]]
    for row in result["rows"]:
        label = f"{case} {row['id']}/{row['area']}"
        if has_layout_defect(row):
            height = row["min_svg_text_height_px"]
            issues.append(f"{label}: 넘침 {row['overflow_px']:.2f}px, SVG 글자 최소 {height}px")
        elif needs_visual_check(row):
            issues.append(f"{label}: 실화면 판독성 확인")
    return issues


def author_preview(run: Path, *, section: str | None, cards: Sequence[str]) -> int:
    run = run.resolve()
    preview = run / "work/preview"
    if not preview.resolve().is_relative_to(run):
        raise ValueError(f"미리보기 폴더가 RUN 밖에 있어요: {preview}")
    preview.mkdir(parents=True, exist_ok=True)
    kind = "note" if section is not None else "review"
    output = Path(mkdtemp(prefix=f"{kind}-", dir=preview))
    cases = {}
    issues = []
    lecture_pdf = []
    status, code = "pass", 0
    try:
        page, partial = build_author_page(run, output, section=section, cards=cards)
        scopes = expected_scopes(partial, kind)
        with render_session() as browser:
            for size in ("375x812", "1280x900"):
                case = f"{kind}/{size}/light"
                result = cases[case] = measure_case(browser, page, case, scopes)
                issues.extend(case_issues(case, result))
                if result["errors"] or any(map(has_layout_defect, result["rows"])):
                    status, code = "fail", 1
            lecture_ids = {card["id"] for card in partial["problems"] if card.get("source_kind") == "lecture-code"}
            if kind == "review" and lecture_ids:
                try:
                    lecture_pdf = probe_lecture_pages(page, output / "pdf-probe")
                    mismatch = lecture_ids ^ {layout["id"] for layout in lecture_pdf}
                    if mismatch:
                        raise PdfError(f"manifest와 조각의 lecture-code 표시 불일치: {', '.join(sorted(mismatch))}")
                except PdfError as exc:
                    issues.append(f"PDF 시험 배치 실패: {exc}")
                    status, code = "fail", 1
                for layout in lecture_pdf:
                    count = len(layout["question_pages"])
                    if count != 1 or not layout["split_ok"]:
                        split = "성공" if layout["split_ok"] else "실패"
                        issues.append(f"{layout['id']}: 문제지 {count}쪽 · 조건/질문 분리 {split}")
                        status, code = "fail", 1
    except PdfError as exc:
        issues.append(str(exc))
        status, code = "unavailable", 2
    except (ValueError, OSError, assemble.AssembleError) as exc:
        issues.append(str(exc))
        status, code = "fail", 1
    path = output / "layout.json"
    report = {"version": 1, "status": status, "cases": cases, "issues": issues}
    if kind == "review":
        report["lecture_pdf"] = lecture_pdf
    write_json(path, report)
    print(f"{kind} {status} · {len(cases)} cases · {len(issues)} issues")
    print(path)
    return code


def stage_preview(repo: Path, run: Path) -> int:
    run = run.resolve()
    record, stage, live = release_paths(repo, run)
    request_path = run / "browser-request.json"
    request, raw = read_record(request_path)
    directory = attempt_directory(run, request)
    mode = record.get("mode", "new")
    if type(request.get("version")) is not int or request["version"] != 2:
        raise ValueError("브라우저 검토 측정에는 v2 요청이 필요해요")
    request_matches(repo, stage, mode, request)
    note, review, _ = browser_paths(stage)
    pages = {"note": note, "review": review}
    results = {}
    code = 0
    try:
        with render_session() as browser:
            for case, required in request["expected_scopes"].items():
                result = results[case] = measure_case(
                    browser, pages[case.split("/")[0]], case, [tuple(pair) for pair in required],
                )
                if result["errors"] or any(map(has_layout_defect, result["rows"])):
                    code = 1
    except PdfError as exc:
        for case in request["cases"]:
            results.setdefault(case, {"rows": [], "errors": [str(exc)]})
        code = 2

    path = directory / MEASUREMENTS
    with publication_lock(live).open("a+") as handle:
        lock_handle(handle)
        if request_path.read_bytes() != raw:
            raise ValueError("측정 중 브라우저 검토 요청이 변경됐어요")
        request_matches(repo, stage, mode, request)
        attempt_directory(run, request)
        fd, pending = mkstemp(prefix=".layout-measurements-", dir=directory)
        os.close(fd)
        temporary = Path(pending)
        try:
            write_json(temporary, {"version": 1, "request_sha256": hashlib.sha256(raw).hexdigest(), "cases": results})
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    status = ("pass", "fail", "unavailable")[code]
    print(f"stage {status} · {len(results)} cases")
    print(path)
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("preflight", help="선택한 Python에서 설치된 Chrome을 실행")
    author = commands.add_parser("author", help="선택한 섹션 또는 카드 미리보기")
    author.add_argument("--run", required=True, type=Path)
    selection = author.add_mutually_exclusive_group(required=True)
    selection.add_argument("--section")
    selection.add_argument("--card", action="append")
    stage = commands.add_parser("stage", help="현재 v2 요청의 조립본 화면을 측정")
    stage.add_argument("--repo", required=True, type=Path)
    stage.add_argument("--run", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        if args.command == "preflight":
            with render_session() as browser:
                print(f"{sys.executable} · Chrome {browser.version}")
            return 0
        if args.command == "stage":
            return stage_preview(args.repo, args.run)
        return author_preview(args.run, section=args.section, cards=args.card or ())
    except PdfError as exc:
        print(exc, file=sys.stderr)
        return 2
    except (ValueError, OSError) as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
