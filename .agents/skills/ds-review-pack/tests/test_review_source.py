import shutil

from _util import REPO as ROOT
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


def test_release_keeps_pdfs_and_archives_legacy_without_public_html(tmp_path):
    import hashlib
    import json
    from _util import MINI_RUN
    from assemble import assemble
    from pdf_publish import dump, publish_stage, stage_hashes
    from release_review import prepare, publish

    repo = tmp_path / "repo"
    run = tmp_path / "run"
    shutil.copytree(MINI_RUN, run)
    inputs = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    folder = repo / "복습노트" / inputs["range"]
    folder.mkdir(parents=True)
    old = folder / f"복습문제_{inputs['range']}_{inputs['slug']}.html"
    old.write_text("<main></main>", encoding="utf-8")
    work = prepare(repo, inputs["range"], run)
    note, review = assemble(run, work)
    md = work / ".pack" / note.with_suffix(".md").name
    md.write_text("# 검증된 노트\n", encoding="utf-8")

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

    before = extract_cards(review.read_text(encoding="utf-8"))
    actual = publish(repo, run)
    assert actual == folder
    assert not work.exists()
    assert not old.exists()
    assert extract_cards(read_review(old)) == before
    assert "답안지 PDF" in (actual / note.name).read_text(encoding="utf-8")
    assert all((actual / name).read_bytes() == b"test PDF fixture" for name in names)



def test_problem_link_follows_verified_page_map(tmp_path):
    from review_links import refresh_pages

    source = tmp_path / "복습문제_1001_List.html"
    html = '<a href="복습문제_1001_List-문제.pdf#page=2">문제</a>'
    prior = {"p2": 2}
    assert refresh_pages(html, source, prior, {"p2": 3}) == html.replace("page=2", "page=3")
    assert refresh_pages(html, source, {}, {"p2": 3}) == html.replace("#page=2", "")
