import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
import unicodedata

import pytest

from _util import MINI_RUN, REPO as ROOT
import assemble
from pdf_publish import dump, publish_stage, stage_hashes
from release_review import prepare, publish
from review_source import archive_review, read_review, review_paths
from update_review import extract_cards



def test_archived_review_retains_raw_cards_and_pdfs(tmp_path):
    original = next((ROOT / '복습노트/1001').glob('복습문제_*.html'), None)
    if original is None:
        archive = next((ROOT / '복습노트/1001/.pack/자료_복습팩').glob('복습문제_*.json'))
        original = tmp_path / archive.with_suffix('.html').name
        from review_source import archived_markup
        original.write_text(archived_markup(archive), encoding='utf-8')
    review = tmp_path / 'pack' / original.name
    review.parent.mkdir()
    shutil.copyfile(original, review)
    before = extract_cards(review.read_text(encoding='utf-8'))
    assert len(before) == 5
    stored = archive_review(review)
    review.unlink()
    assert stored.parent == review.parent / '.pack/자료_복습팩'
    assert review_paths(review.parent) == (review,)
    assert extract_cards(read_review(review)) == before


def test_legacy_empty_pack_can_be_archived(tmp_path):
    review = tmp_path / '복습문제_1001_Empty.html'
    review.write_text('<main><div class="hero"><h1>복습문제</h1><p>문항 없음</p></div></main>', encoding='utf-8')
    archive_review(review)
    review.unlink()
    assert extract_cards(read_review(review)) == []


def release_fixture(tmp_path, monkeypatch, *, mode="new", empty=False, nfd=False):
    repo, run = tmp_path / "repo", tmp_path / "run"
    shutil.copytree(MINI_RUN, run)
    manifest = run / "manifest.json"
    inputs = json.loads(manifest.read_text(encoding="utf-8"))
    if empty:
        links = run / "sections/s2.html"
        links.write_text("\n".join(line for line in links.read_text().splitlines()
                                   if "{{REVIEW_HREF}}" not in line), encoding="utf-8")
        inputs.update(problems=[], parts=[], links=[])
        manifest.write_text(json.dumps(inputs, ensure_ascii=False), encoding="utf-8")
    notes = repo / (unicodedata.normalize("NFD", "복습노트") if nfd else "복습노트")
    live = notes / inputs["range"]
    live.mkdir(parents=True)
    old = live / f"복습문제_{inputs['range']}_{inputs['slug']}.html"
    old.write_text("<main></main>", encoding="utf-8")
    shared = notes / "_assets/problem-explain/v1"
    for name in ("pretendard/pretendard.css", "katex/katex.min.css", "katex/katex.min.js",
                 "katex/contrib/auto-render.min.js", "pretendard/test.woff2"):
        path = shared / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name, encoding="utf-8")
    monkeypatch.setattr(assemble, "SHARED_ASSETS", shared)
    work = prepare(repo, inputs["range"], run, mode=mode)
    note, review = assemble.assemble(run, work)
    md = work / ".pack" / note.with_suffix(".md").name
    md.write_text("# 검증된 노트\n", encoding="utf-8")
    figure = work / ".pack" / f"figures_{inputs['range']}" / "test.svg"
    figure.parent.mkdir()
    figure.write_text("<svg/>", encoding="utf-8")
    markup = note.read_text(encoding="utf-8")
    image = f'<img src=".pack/{figure.parent.name}/test.svg?rev=1#view">'
    note.write_text(markup.replace("</main>", image + "</main>"), encoding="utf-8")

    names = []
    if not empty:
        pdf_run = tmp_path / "pdf"
        pdf_stage = pdf_run / "stage"
        pdf_stage.mkdir(parents=True)
        names = [review.stem + tail for tail in ("-문제.pdf", "-답안.pdf")]
        for name in names:
            (pdf_stage / name).write_bytes(b"test PDF fixture")
        hashes = stage_hashes(pdf_run)
        report = pdf_run / "report.json"
        dump(report, {
            "source": str(review), "source_sha256": hashlib.sha256(review.read_bytes()).hexdigest(),
            "dest": str(work), "checks": {"status": "pass", "errors": []},
            "artifact_hashes": hashes, "pdfs": names, "probes": {"problems": {"page_ids": ["p1"]}},
        })
        dump(pdf_run / "review.json", {
            "status": "pass", "reviewer": "fixture", "evidence": "controlled test input",
            "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(), "artifact_hashes": hashes,
        })
        publish_stage(pdf_run, repo)

    return SimpleNamespace(repo=repo, run=run, live=live, stage=work, old=old, note=note,
                           review=review, pdfs=names, figure=figure, font=shared / "pretendard/test.woff2")


def approve_browser(fixture):
    from release_review import start_browser_review

    request = start_browser_review(fixture.repo, fixture.run)
    payload = json.loads(request.read_bytes())
    result = fixture.run / "browser" / payload["attempt"] / "browser-review.json"
    dump(result, {
        "version": 1, "request_sha256": hashlib.sha256(request.read_bytes()).hexdigest(),
        "status": "pass", "reviewer": "fixture", "issues": [],
        "cases": {case: {"status": "pass", "evidence": "controlled test observation"} for case in payload["cases"]},
    })
    return result


def live_files_and_bytes(live: Path) -> dict[str, bytes]:
    return {p.relative_to(live).as_posix(): p.read_bytes() for p in live.rglob("*") if p.is_file()}


@pytest.mark.parametrize("nfd", [False, True], ids=["nfc", "nfd"])
def test_release_keeps_pdfs_and_archives_legacy_without_public_html(tmp_path, monkeypatch, nfd):
    fixture = release_fixture(tmp_path, monkeypatch, nfd=nfd)
    before = extract_cards(fixture.review.read_text(encoding="utf-8"))
    approve_browser(fixture)
    actual = publish(fixture.repo, fixture.run)
    assert actual.samefile(fixture.live)
    assert not fixture.stage.exists()
    assert not fixture.old.exists()
    assert extract_cards(read_review(fixture.old)) == before
    assert "답안지 PDF" in (actual / fixture.note.name).read_text(encoding="utf-8")
    assert all((actual / name).read_bytes() == b"test PDF fixture" for name in fixture.pdfs)


@pytest.mark.parametrize("mode,mutation", [
    ("new", "missing"), ("new", "missing-case"), ("update-existing", "missing-case"),
    ("revise-existing", "missing-case"), ("new", "old-attempt"), ("new", "note-changed"),
    ("new", "figure-changed"), ("new", "font-changed"),
], ids=["missing", "missing-case", "update-missing-case", "revise-missing-case",
        "old-attempt", "note-changed", "figure-changed", "font-changed"])
def test_publish_rejects_invalid_browser_review(tmp_path, monkeypatch, mode, mutation):
    from release_review import start_browser_review

    fixture = release_fixture(tmp_path, monkeypatch, mode=mode)
    before = live_files_and_bytes(fixture.live)
    if mutation == "missing":
        start_browser_review(fixture.repo, fixture.run)
    else:
        result = approve_browser(fixture)
        if mutation == "missing-case":
            approval = json.loads(result.read_bytes())
            del approval["cases"]["review/375x812/dark"]
            dump(result, approval)
        elif mutation == "old-attempt":
            request = start_browser_review(fixture.repo, fixture.run)
            attempt = json.loads(request.read_bytes())["attempt"]
            shutil.copyfile(result, result.parent.parent / attempt / result.name)
        else:
            changed = {"note-changed": fixture.note, "figure-changed": fixture.figure,
                       "font-changed": fixture.font}[mutation]
            changed.write_bytes(changed.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="브라우저 검토"):
        publish(fixture.repo, fixture.run)
    assert live_files_and_bytes(fixture.live) == before
    assert fixture.stage.is_dir()


@pytest.mark.parametrize("dependent", ["font.woff2", "inline image.png", "large.png", "other.png", "svg-image.png"])
def test_publish_rejects_changed_assets_outside_pack(tmp_path, monkeypatch, dependent):
    fixture = release_fixture(tmp_path, monkeypatch)
    assets = fixture.repo / "resources"
    assets.mkdir()
    (assets / "outer.css").write_text('@import "inner.css";', encoding="utf-8")
    (assets / "inner.css").write_text('@font-face { font-family: test; src: url(font.woff2); }',
                                      encoding="utf-8")
    (assets / "figure.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><image href="svg-image.png"/></svg>', encoding="utf-8",
    )
    for name in ("font.woff2", "inline image.png", "small.png", "large.png", "other.png", "svg-image.png"):
        (assets / name).write_bytes(b"test asset")
    note = fixture.note.read_text(encoding="utf-8")
    resources = (
        '<link rel="stylesheet" href="../../resources/outer.css">'
        '<style>main {background-image: url("../../resources/inline%20image.png?v=1");}</style>'
        '<img src="../../resources/figure.svg">'
        '<img src="../../resources/small.png" srcset="data:image/svg+xml,%3Csvg%3E 1x, '
        '../../resources/large.png 2x">'
        '<img srcset="../../resources/small.png, ../../resources/other.png 2x">'
    )
    fixture.note.write_text(note.replace("</main>", resources + "</main>"), encoding="utf-8")
    approve_browser(fixture)
    before = live_files_and_bytes(fixture.live)
    (assets / dependent).write_bytes(b"changed asset")
    with pytest.raises(ValueError, match="브라우저 검토"):
        publish(fixture.repo, fixture.run)
    assert live_files_and_bytes(fixture.live) == before


@pytest.mark.parametrize("mode,pages", [
    ("new", ("note", "review")), ("update-existing", ("review",)), ("revise-existing", ("review",)),
])
def test_review_cases_by_mode(mode, pages):
    from browser_review import required_cases

    assert set(required_cases(mode)) == {
        f"{page}/{size}/{theme}" for page in pages for size in ("1280x900", "375x812") for theme in ("light", "dark")
    }


def test_zero_card_release_requires_browser_review_and_no_pdfs(tmp_path, monkeypatch):
    fixture = release_fixture(tmp_path, monkeypatch, empty=True)
    before = live_files_and_bytes(fixture.live)
    with pytest.raises(ValueError, match="브라우저 검토"):
        publish(fixture.repo, fixture.run)
    assert live_files_and_bytes(fixture.live) == before
    approve_browser(fixture)
    live = publish(fixture.repo, fixture.run)
    assert not list(live.glob("*.pdf"))
    assert (live / fixture.note.name).read_bytes()
    assert (live / ".pack" / fixture.note.with_suffix(".md").name).read_text(encoding="utf-8") == "# 검증된 노트\n"


def test_problem_link_follows_verified_page_map(tmp_path):
    from review_links import refresh_pages

    source = tmp_path / "복습문제_1001_List.html"
    html = '<a href="복습문제_1001_List-문제.pdf#page=2">문제</a>'
    prior = {"p2": 2}
    assert refresh_pages(html, source, prior, {"p2": 3}) == html.replace("page=2", "page=3")
    assert refresh_pages(html, source, {}, {"p2": 3}) == html.replace("#page=2", "")
