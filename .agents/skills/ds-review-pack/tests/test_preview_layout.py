"""Author and reviewer commands using temporary render inputs."""
from contextlib import contextmanager
import json
from pathlib import Path
import shutil

import pytest

from _util import MINI_RUN
import preview_layout
from pdf_types import PdfError


@pytest.fixture
def run(tmp_path):
    return Path(shutil.copytree(MINI_RUN, tmp_path / "run"))


def insert(path, markup):
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("</h3>", "</h3>" + markup, 1), encoding="utf-8")


def author(run, capsys, *selection):
    code = preview_layout.main(["author", "--run", str(run), *selection])
    report = Path(capsys.readouterr().out.strip().splitlines()[-1])
    assert report.is_relative_to(run / "work/preview")
    return code, json.loads(report.read_bytes())


def test_preview_uses_only_selected_fragments(run, tmp_path):
    (run / "sections/s2.html").unlink()
    original_manifest = run / "manifest.json"
    m = json.loads(original_manifest.read_bytes())
    m["problems"].append({**m["problems"][0], "id": "p9"})
    original_manifest.write_text(json.dumps(m))
    before = original_manifest.read_bytes()
    note, partial_note = preview_layout.build_author_page(run, tmp_path / "note", section="s1", cards=())
    review, partial_review = preview_layout.build_author_page(run, tmp_path / "review", section=None, cards=("p1",))
    assert note.is_file() and review.is_file()
    assert [section["id"] for section in partial_note["sections"]] == ["s1"]
    assert [card["id"] for card in partial_review["problems"]] == ["p1"]
    assert original_manifest.read_bytes() == before


@pytest.mark.parametrize("source", ["missing.svg", "../outside.svg", "https://example.com/remote.svg"])
def test_preview_reports_missing_local_asset(run, capsys, source):
    insert(run / "sections/s1.html", f'<img src="{source}">')
    rc, report = author(run, capsys, "--section", "s1")
    assert rc == 1 and report["status"] == "fail"
    assert any(source in error for error in report["issues"])


def test_preview_can_report_unavailable(run, capsys, monkeypatch):
    @contextmanager
    def unavailable():
        raise PdfError("Chrome is unavailable")
        yield

    monkeypatch.setattr(preview_layout, "render_session", unavailable)
    unavailable_rc, unavailable_report = author(run, capsys, "--card", "p1")
    assert unavailable_report["status"] == "unavailable" and unavailable_rc == 2
    assert unavailable_report["cases"] == {}


def test_author_cli_returns_both_light_cases(run, capsys):
    asset = run / ".pack/figures_1119/grid.svg"
    asset.parent.mkdir(parents=True)
    asset.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"/>')
    insert(run / "cards/p1.html", f'<img src="{asset.relative_to(run).as_posix()}">')
    rc, card_report = author(run, capsys, "--card", "p1")
    assert rc == 0 and card_report["status"] == "pass"
    assert set(card_report["cases"]) == {"review/375x812/light", "review/1280x900/light"}
    assert any(p.read_bytes() == asset.read_bytes() for p in (run / "work/preview").rglob("grid.svg"))


def test_author_rejects_unknown_id(run, capsys):
    rc, report = author(run, capsys, "--card", "p99")
    assert rc == 1 and report["status"] == "fail"
    assert any("p99" in error for error in report["issues"])


def lecture_review(tmp_path, *, code_lines, solution_steps=1):
    path = tmp_path / "복습문제_1119_Graph.html"
    code = "int main(void) {\n" + "    /* same result */\n" * code_lines + "    return 0;\n}"
    steps = "<li><pre><code>" + "    visit(vertex);\n" * solution_steps + "</code></pre></li>"
    path.write_text(
        '<article class="card" id="p10" data-source="lecture-s10-p17-graph" data-source-kind="lecture-code">'
        '<h3>P10. 연결 성분</h3><div class="problem"><p>정점은 0부터 7까지예요.</p>'
        f"<pre><code>{code}</code></pre>"
        "<ol><li>(a) 출력 순서를 쓰세요.</li><li>(b) 방문 배열 값을 쓰세요.</li>"
        "<li>(c) 연결 성분의 개수를 쓰세요.</li></ol></div>"
        f'<details class="solution"><summary>풀이</summary><ol class="steps">{steps}</ol>'
        '<p class="answer">정답은 1개예요.</p></details></article>',
        encoding="utf-8",
    )
    return path


def test_lecture_preview_detects_question_split(tmp_path):
    review = lecture_review(tmp_path, code_lines=15)
    work = tmp_path / "short"
    short, = preview_layout.probe_lecture_pages(review, work)
    assert short["question_pages"] == short["conditions_pages"] == short["ask_pages"] == ["p10"]
    assert short["split_ok"] is True

    review = lecture_review(tmp_path, code_lines=37)
    long, = preview_layout.probe_lecture_pages(review, tmp_path / "long")
    assert len(long["question_pages"]) >= 2 and "p10-c2" in long["question_pages"]
    assert long["split_ok"] is False
    assert not list(tmp_path.rglob("*.pdf")) and not list(tmp_path.rglob("*.png"))


def test_solution_continuation_does_not_count_as_question_page(tmp_path):
    from pdf_cards import read_pack
    from pdf_layout import plan_pages

    review = lecture_review(tmp_path, code_lines=10, solution_steps=70)
    with preview_layout.render_session():
        pages = plan_pages(read_pack(review), tmp_path / "reference")
        assert "p10-c2" in {page.physical_id for page in pages}
        long_answer_only, = preview_layout.probe_lecture_pages(review, tmp_path / "probe")
    assert long_answer_only["question_pages"] == ["p10"]
    assert long_answer_only["split_ok"] is True


def test_nonlecture_preview_skips_pdf_probe(run, tmp_path):
    review, _ = preview_layout.build_author_page(run, tmp_path / "author", section=None, cards=("p1",))
    work = tmp_path / "skip"
    assert preview_layout.probe_lecture_pages(review, work) == []
    assert not work.exists()


@pytest.mark.parametrize("empty", [False, True], ids=["with-cards", "zero-cards"])
def test_stage_cli_writes_current_attempt_only(run, tmp_path, capsys, monkeypatch, empty):
    import hashlib
    import assemble
    from release_review import prepare, start_browser_review

    repo = tmp_path / "repo"
    shared = repo / "복습노트/_assets/problem-explain/v1"
    shutil.copytree(assemble.SHARED_ASSETS, shared)
    monkeypatch.setattr(assemble, "SHARED_ASSETS", shared)
    if empty:
        path = run / "manifest.json"
        inputs = json.loads(path.read_bytes())
        inputs.update(problems=[], parts=[], links=[])
        path.write_text(json.dumps(inputs))
    stage = prepare(repo, "0101-0102", run)
    assemble.assemble(run, stage)

    request = start_browser_review(repo, run)
    previous = json.loads(request.read_bytes())["attempt"]
    request = start_browser_review(repo, run)
    raw = request.read_bytes()
    payload = json.loads(raw)
    command = ["stage", "--repo", str(repo), "--run", str(run)]
    assert preview_layout.main(command) == 0
    path = Path(capsys.readouterr().out.strip().splitlines()[-1])
    assert path == run / "browser" / payload["attempt"] / "layout-measurements.json"
    assert not (run / "browser" / previous / path.name).exists()
    assert not path.with_name("browser-review.json").exists()
    result = json.loads(path.read_bytes())
    assert result["request_sha256"] == hashlib.sha256(raw).hexdigest()
    assert set(result["cases"]) == set(payload["cases"]) and len(result["cases"]) == 8
    for case, measured in result["cases"].items():
        assert measured["errors"] == []
        assert sorted([row["id"], row["area"]] for row in measured["rows"]) == sorted(payload["expected_scopes"][case])
        if empty and case.startswith("review/"):
            assert [(row["id"], row["area"]) for row in measured["rows"]] == [("hero", "body")]


def test_author_rejects_unmarked_lecture_card(run, capsys):
    manifest = run / "manifest.json"
    data = json.loads(manifest.read_bytes())
    card = data["problems"][0]
    card.update(source_kind="lecture-code", source="lecture-s10-p17-graph",
                lecture_ref={"page": 17}, objectives=["graph-trace"], task_family="graph")
    manifest.write_text(json.dumps(data))
    fragment = run / "cards/p1.html"
    fragment.write_text(fragment.read_text().replace("2016-final-ljw-q1", card["source"]))
    code, report = author(run, capsys, "--card", "p1")
    assert code == 1
    assert any("p1" in issue and "lecture-code" in issue for issue in report["issues"])
