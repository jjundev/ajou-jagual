import json
from pathlib import Path
import shutil
import subprocess
import sys
import unicodedata

import pytest

from concept_util import SCRIPTS, copy_fixture, nfd_path, playwright_available
import _paths
import build


RANGE = "9999"
SOURCE = ".pack/자료_확인문제_9999_Mini"
HTML = "확인문제_9999_Mini.html"
SHARED = Path("복습노트/_assets/problem-explain/v1")


def json_file(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def pack_files(root):
    from hashlib import sha256
    return {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def fixture(tmp_path, kind="legacy-html"):
    repo, run = tmp_path / "repo", tmp_path / "run"
    live = copy_fixture(repo / "복습노트", nfd=kind == "nfd-archive")
    (live / ".pack/정리노트_9999_Mini.md").write_text("Mini topic", encoding="utf-8")
    shutil.copytree(_paths.REPO / SHARED, repo / SHARED)
    note = live / "정리노트_9999_Mini.html"
    note.write_text(note.read_text() + '<link rel="stylesheet" href=".pack/extra.css">')
    (live / ".pack/extra.css").write_text('div { background:url("graphic.svg"); }')
    (live / ".pack/graphic.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    review = live / "복습문제_9999_Mini.html"
    if kind == "nfd-archive":
        note.rename(note.with_name(unicodedata.normalize("NFD", note.name)))
        name = unicodedata.normalize("NFD", review.with_suffix(".json").name)
        json_file(nfd_path(live, ".pack/자료_복습팩") / name,
                  {"version": 1, "name": review.name, "sections": [review.read_text()], "scripts": []})
    if kind != "legacy-html":
        review.unlink()
    (live / HTML).write_text("previous concept page")
    return repo, run, live


def seed(src, live):
    for name in ("objectives.json", "items.json"):
        shutil.copyfile(nfd_path(live, SOURCE) / name, src / name)


@pytest.mark.parametrize("kind", ["legacy-html", "nfd-archive", "zero-cards"])
def test_prepare_mirrors_pack(tmp_path, kind):
    from concept_release import prepare
    from review_source import review_paths, source_file

    repo, run, live = fixture(tmp_path, kind)
    before = pack_files(live)
    src = prepare(repo, RANGE, run)
    stage = src.parent.parent
    assert src.is_relative_to(run / "stage")
    assert not list(src.iterdir())
    assert not (stage / HTML).exists()
    assert pack_files(live) == before
    assert len(review_paths(stage)) == (kind != "zero-cards")
    for built, original in zip(review_paths(stage), review_paths(live)):
        assert source_file(built).read_bytes() == source_file(original).read_bytes()
    assert (stage / ".pack/graphic.svg").is_file()
    assert (run / "stage" / SHARED / "pretendard/pretendard.css").is_file()
    recorded = json.loads((run / "prepare.json").read_text())
    assert recorded["version"] == 1 and recorded["range"] == RANGE and recorded["slug"] == "Mini"
    assert recorded["owned_before"][(live / HTML).relative_to(repo).as_posix()] == before[HTML]


@pytest.mark.parametrize("missing", [
    "정리노트_9999_Mini.html", ".pack/정리노트_9999_Mini.md", ".pack/자료_복습팩/stt-summary.md",
])
def test_prepare_requires_pack_evidence(tmp_path, missing):
    from concept_release import prepare

    repo, run, live = fixture(tmp_path)
    nfd_path(live, missing).unlink()
    before = pack_files(live)
    with pytest.raises(ValueError):
        prepare(repo, RANGE, run)
    assert pack_files(live) == before


def test_staged_build_uses_final_relative_urls(tmp_path):
    from concept_release import prepare
    from urllib.parse import unquote
    import re

    repo, run, live = fixture(tmp_path)
    src = prepare(repo, RANGE, run)
    seed(src, live)
    work = build.build(src, assets_dir=run / "stage" / SHARED)
    assert work.read_bytes() == build.render_page(nfd_path(live, SOURCE), assets_dir=repo / SHARED).encode()
    page = work.read_text()
    ref = re.search(r'href="([^"]+/pretendard/pretendard.css)"', page)[1]
    assert (work.parent / unquote(ref)).is_file()
    assert "정리노트_9999_Mini.html#" in page


@pytest.mark.skipif(not playwright_available(), reason="playwright·chromium 없음")
def test_browser_cli_accepts_stage_root(tmp_path):
    from concept_release import write_review_request

    repo, run, _, src, html = staged(tmp_path, kind="nfd-archive")
    stage = run / "stage"
    request = write_review_request(repo, RANGE, run)
    attempt = json.loads(request.read_text())["attempt"]
    report = run / "browser" / attempt / "browser.json"
    result = subprocess.run([sys.executable, str(SCRIPTS / "browser_check.py"), str(html),
                             "--src", str(src), "--out", str(report), "--serve-root", str(stage),
                             "--shots", str(report.parent / "shots"), "--request", str(request)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(report.read_text())
    assert data["html"] == html.relative_to(stage).as_posix()
    assert data["status"] == "pass" and len(data["runs"]) == 4
    assert data["attempt"] == attempt
    note = nfd_path(html.parent, "정리노트_9999_Mini.html")
    assert f'href="{note.name}#s0-a"' in html.read_text()


def staged(tmp_path, kind="legacy-html", *, had_html=True):
    from concept_release import prepare
    import blind

    repo, run, live = fixture(tmp_path, kind)
    if not had_html:
        (live / HTML).unlink()
    src = prepare(repo, RANGE, run)
    seed(src, live)
    answers = []
    for item in build.load_source(src)["items"]:
        answer = item["answer"] if item["format"] == "mcq" else item["answer"]["canonical"]
        answers.append(f"| {item['id']} | {answer} | fixture only | |")
    answer_file = run / "fixture-answers.md"
    answer_file.write_text("\n".join(answers))
    blind.record(src, answer_file, src / "blind-ledger.json", 1)
    page = build.build(src, assets_dir=run / "stage" / SHARED)
    return repo, run, live, src, page


def approved(repo, run, src, page):
    from concept_release import write_review_request
    from browser_check import sha256
    from hashlib import sha256 as hash_bytes
    import base64

    request_file = write_review_request(repo, RANGE, run)
    request = json.loads(request_file.read_text())
    attempt = run / "browser" / request["attempt"]
    (attempt / "shots").mkdir(parents=True)
    first, *rest = build.load_source(src)["items"]
    report = attempt / "browser.json"
    manual = attempt / "visual-review.json"
    cases, hashes = {}, {}
    png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jJ1sAAAAASUVORK5CYII=")
    for case in request["cases"]:
        tag = case.replace("/", "-")
        shots = [f"shots/{tag}-{suffix}.png" for suffix in (first["id"], first["id"] + "-hint", "last")]
        for rel in shots:
            (attempt / rel).write_bytes(png)
            hashes[rel] = hash_bytes(png).hexdigest()
        cases[case] = {"status": "pass", "observation": "test fixture", "screenshots": shots}
    result = {
        "status": "pass", "html": page.relative_to(run / "stage").as_posix(), "sha256": sha256(page),
        "attempt": request["attempt"], "request_sha256": sha256(request_file),
        "failures": [], "transport": "file://, offline=True",
        "viewports": ["1280x900", "375x812"], "themes": ["light", "dark"],
        "screenshots": hashes,
        "runs": [{"label": case.replace("/", " "), "failures": [], "external_blocked": [],
                  "detail": dict(items=len(rest)+1, items_checked=len(rest)+1, hints_checked=len(rest)+1)}
                 for case in request["cases"]],
    }
    json_file(report, result)
    json_file(manual, {"version": 1, "request_sha256": sha256(request_file), "browser_report_sha256": sha256(report),
                       "reviewer": "unit test", "status": "pass", "cases": cases})
    return request_file, report, manual


def edit_json(path, edit):
    value = json.loads(path.read_text())
    edit(value)
    json_file(path, value)


def test_publish_writes_only_owned_bytes(tmp_path):
    from concept_release import publish

    repo, run, live, src, page = staged(tmp_path)
    (live / "복습문제_9999_Mini-문제.pdf").write_bytes(b"leave PDF in place")
    (live / "문제설명_9999_Mini.html").write_bytes(b"leave explain in place")
    (live.parent / "8888").mkdir()
    (live.parent / "8888/page.html").write_bytes(b"another pack")
    _, report, _ = approved(repo, run, src, page)
    before = pack_files(repo)
    assert publish(repo, RANGE, run) == live / HTML
    assert (live / HTML).read_bytes() == page.read_bytes()
    assert (nfd_path(live, SOURCE) / "browser.json").read_bytes() == report.read_bytes()
    for name in ("objectives.json", "items.json", "blind-ledger.json"):
        assert (nfd_path(live, SOURCE) / name).read_bytes() == (src / name).read_bytes()
    owned = {(live / HTML).relative_to(repo).as_posix()}
    owned.update((nfd_path(live, SOURCE) / name).relative_to(repo).as_posix()
                 for name in ("objectives.json", "items.json", "blind-ledger.json", "browser.json"))
    assert {k: v for k, v in pack_files(repo).items() if k not in owned} == {
        k: v for k, v in before.items() if k not in owned}


@pytest.mark.parametrize("fault", ["missing-record", "machine-only", "manual-fail", "old-attempt",
                                  "missing-case", "duplicate-case", "duplicate-manual", "missing-shot", "changed-shot",
                                  "objection", "round-4", "bad-layout"])
def test_publish_refuses_review(tmp_path, fault):
    from browser_check import sha256
    from concept_release import publish, write_review_request

    repo, run, live, src, page = staged(tmp_path)
    request, report, manual = approved(repo, run, src, page)
    if fault == "missing-record":
        request.unlink()
    elif fault == "machine-only":
        manual.unlink()
    elif fault == "manual-fail":
        edit_json(manual, lambda d: d.update(status="fail"))
    elif fault == "old-attempt":
        write_review_request(repo, RANGE, run)
        new_attempt = json.loads(request.read_text())["attempt"]
        new_dir = report.parent.with_name(new_attempt)
        shutil.copytree(report.parent, new_dir)
        edit_json(new_dir / manual.name, lambda d: d.update(request_sha256=sha256(request)))
    elif fault == "missing-case":
        edit_json(manual, lambda d: d["cases"].pop("375x812/dark"))
    elif fault == "duplicate-case":
        edit_json(report, lambda d: d["runs"].append(d["runs"][0]))
        edit_json(manual, lambda d: d.update(browser_report_sha256=sha256(report)))
    elif fault == "duplicate-manual":
        raw = manual.read_text()
        manual.write_text(raw.replace('"1280x900/light":', '"1280x900/light": {"status":"fail"}, "1280x900/light":'))
    elif fault == "missing-shot":
        next((report.parent / "shots").glob("*.png")).unlink()
    elif fault == "changed-shot":
        next((report.parent / "shots").glob("*.png")).write_bytes(b"changed")
    elif fault in ("objection", "round-4"):
        key, val = ("round", 4) if fault == "round-4" else ("objection", "unresolved")
        edit_json(src / "blind-ledger.json", lambda d: next(iter(d.values())).update({key: val}))
    elif fault == "bad-layout":
        (page.parent / "stray.txt").touch()
    before = pack_files(repo)
    with pytest.raises(ValueError):
        publish(repo, RANGE, run)
    assert pack_files(repo) == before


@pytest.mark.parametrize("fault", ["staged-html", "items", "ledger", "browser-report",
                                  "live-manifest", "new-review-input", "shared-font",
                                  "note-local-asset", "live-owned"])
def test_publish_refuses_changes(tmp_path, fault):
    from concept_release import publish

    repo, run, live, src, page = staged(tmp_path)
    _, report, _ = approved(repo, run, src, page)
    paths = {
        "staged-html": page, "items": src / "items.json", "ledger": src / "blind-ledger.json",
        "browser-report": report, "live-manifest": nfd_path(live, ".pack/자료_복습팩/manifest.json"),
        "new-review-input": live / "복습문제_9999_Extra.html",
        "shared-font": next((repo / SHARED).rglob("*.woff2")), "note-local-asset": live / ".pack/graphic.svg",
        "live-owned": live / HTML,
    }
    target = paths[fault]
    with target.open("ab") as file:
        file.write(b"changed")
    before = pack_files(repo)
    with pytest.raises(ValueError):
        publish(repo, RANGE, run)
    assert pack_files(repo) == before


def test_review_request_rejects_unbuilt_items(tmp_path):
    from concept_release import write_review_request

    repo, run, _, src, _ = staged(tmp_path)
    edit_json(src / "items.json", lambda d: d["items"][0].update(hint="첫 단계에서 노트를 다시 읽어 봐요."))
    with pytest.raises(ValueError, match="빌드"):
        write_review_request(repo, RANGE, run)


def test_browser_refuses_changed_stage_dependency(tmp_path):
    import browser_check
    from concept_release import write_review_request

    repo, run, _, src, html = staged(tmp_path)
    request = write_review_request(repo, RANGE, run)
    attempt = json.loads(request.read_text())["attempt"]
    out = run / "browser" / attempt / "browser.json"
    (html.parent / ".pack/graphic.svg").write_text("<svg/>")
    with pytest.raises(ValueError, match="근거가 바뀌었어요"):
        browser_check.check(html, out, out.parent / "shots",
                            src=src, serve_root=run / "stage", request=request)
    assert not out.exists()


@pytest.mark.parametrize("had_html", [True, False])
def test_publish_rolls_back_second_replace(tmp_path, monkeypatch, had_html):
    import os
    from concept_release import publish

    repo, run, _, src, page = staged(tmp_path, had_html=had_html)
    approved(repo, run, src, page)
    before = pack_files(repo)
    replace = os.replace
    calls = []
    def fail_second(source, dest):
        calls.append(dest)
        if len(calls) == 2:
            raise OSError("test second replace")
        replace(source, dest)
    monkeypatch.setattr(os, "replace", fail_second)
    with pytest.raises(OSError, match="second replace"):
        publish(repo, RANGE, run)
    assert len(calls) == 2 and pack_files(repo) == before


@pytest.mark.parametrize("location", ["stage", "destination"])
def test_publish_rejects_stage_or_destination_symlink(tmp_path, location):
    from concept_release import publish

    repo, run, live, src, page = staged(tmp_path)
    approved(repo, run, src, page)
    path = src if location == "stage" else nfd_path(live, SOURCE)
    moved = path.with_name("moved")
    path.rename(moved)
    path.symlink_to(moved, target_is_directory=True)
    before = pack_files(repo)
    with pytest.raises(ValueError, match="심볼릭 링크"):
        publish(repo, RANGE, run)
    assert pack_files(repo) == before
