import shutil

import pytest

import concept_util
from concept_util import copy_fixture, nfd_path
import build
import interaction


def test_build_writes_root_html(tmp_path):
    root = copy_fixture(tmp_path)
    out = build.build(root / ".pack/자료_확인문제_9999_Mini")
    assert out == root / "확인문제_9999_Mini.html"
    page = out.read_text(encoding="utf-8")
    assert "확인문제 9999" in page and page.count('class="card"') == 3
    assert interaction.build_model(page, "x")["errors"] == []
    assert "<p><p>" not in page
    assert '<strong class="brand">확인문제</strong>' in page
    assert '<strong class="brand">복습문제</strong>' not in page


def test_build_finds_nfd_pack_dir(tmp_path):
    root = copy_fixture(tmp_path, nfd=True)
    assert build.build(nfd_path(root, ".pack/자료_확인문제_9999_Mini")).exists()


def test_build_missing_pack_message(tmp_path):
    root = copy_fixture(tmp_path)
    shutil.rmtree(root / ".pack/자료_복습팩")
    with pytest.raises(build.BuildError, match="팩이 없어 근거가 없습니다"):
        build.build(root / ".pack/자료_확인문제_9999_Mini")


def test_build_unknown_objective(tmp_path):
    root = copy_fixture(tmp_path)
    p = root / ".pack/자료_확인문제_9999_Mini/items.json"
    p.write_text(p.read_text(encoding="utf-8").replace('"o2"', '"o9"', 1), encoding="utf-8")
    with pytest.raises(build.BuildError, match="o9"):
        build.build(root / ".pack/자료_확인문제_9999_Mini")


def test_cli_missing_pack_exits_1(tmp_path, capsys):
    root = copy_fixture(tmp_path)
    shutil.rmtree(root / ".pack/자료_복습팩")
    assert build.main(["build.py", str(root / ".pack/자료_확인문제_9999_Mini")]) == 1
    assert "팩이 없어 근거가 없습니다" in capsys.readouterr().err


def test_page_values_are_escaped(tmp_path):
    import json
    root = copy_fixture(tmp_path)
    m = root / ".pack/자료_복습팩/manifest.json"
    d = json.loads(m.read_text(encoding="utf-8"))
    d["course"] = 'A&B "C"'
    m.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    page = build.render_page(root / ".pack/자료_확인문제_9999_Mini")
    assert "A&amp;B &quot;C&quot; 확인문제 9999" in page
    assert 'A&B "C" 확인문제' not in page


@pytest.mark.parametrize("text", ["<header>없음</header>",
                                  '<strong class="brand">복습문제</strong>' * 2])
def test_swap_brand_needs_exactly_one_anchor(text):
    with pytest.raises(build.BuildError, match="brand"):
        build.swap_brand(text)


@pytest.mark.parametrize("key", ["range", "slug"])
def test_build_rejects_range_slug_mismatch(tmp_path, key):
    import json
    root = copy_fixture(tmp_path)
    p = root / ".pack/자료_확인문제_9999_Mini/objectives.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d[key] = "8888" if key == "range" else "Other"
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(build.BuildError, match=key):
        build.build(root / ".pack/자료_확인문제_9999_Mini")


def test_build_missing_stt_names_file(tmp_path):
    root = copy_fixture(tmp_path)
    (root / ".pack/자료_복습팩/stt-summary.md").unlink()
    with pytest.raises(build.BuildError, match=r"팩이 없어 근거가 없습니다: .* \(stt-summary\.md 없음\)"):
        build.build(root / ".pack/자료_확인문제_9999_Mini")


def test_build_links_each_card_to_note_topic(tmp_path):
    root = copy_fixture(tmp_path)
    page = build.render_page(root / ".pack/자료_확인문제_9999_Mini")
    assert 'href="정리노트_9999_Mini.html#s0-a"' in page and 'href="정리노트_9999_Mini.html#s0-b"' in page


def test_build_missing_note_html(tmp_path):
    root = copy_fixture(tmp_path)
    (root / "정리노트_9999_Mini.html").unlink()
    with pytest.raises(build.BuildError, match="정리노트 HTML이 없어"):
        build.build(root / ".pack/자료_확인문제_9999_Mini")


def test_build_missing_note_anchor(tmp_path):
    root = copy_fixture(tmp_path)
    note = root / "정리노트_9999_Mini.html"
    note.write_text(note.read_text(encoding="utf-8").replace('id="s0-b"', 'id="s0-x"'), encoding="utf-8")
    with pytest.raises(build.BuildError, match="#s0-b"):
        build.build(root / ".pack/자료_확인문제_9999_Mini")
