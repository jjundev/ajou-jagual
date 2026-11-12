import json

import pytest

from concept_util import fixture_src, mutated_fixture, write

import blind

TABLE = "| 문항 | 고른 답 | 근거 | 이의 |\n|---|---|---|---|\n"


def _ok_ledger(tmp_path, src):
    write(tmp_path / "a.md", TABLE + "| q1 | 2 | s0-a | |\n| q2 | A | s0-b | |\n| q3 | b c a | s0-a | |")
    blind.record(src, tmp_path / "a.md", tmp_path / "l.json", 1)
    return tmp_path / "l.json"


def test_make_hides_answers(tmp_path):
    src = fixture_src(tmp_path); out = tmp_path / "b.md"
    blind.make(src, out)
    text = out.read_text(encoding="utf-8")
    assert "## q2." in text and "A. " in text
    assert "[그림: 트리 — 루트 A; A의 왼쪽 자식 B; A의 오른쪽 자식 C; B의 오른쪽 자식 D]" in text
    assert "(값을 쓰시오)" in text
    for leak in ("why", "정답", "misconception", "B, C, A", "solution", "compute"):
        assert leak not in text


def test_make_tree_has_no_slot_list(tmp_path):
    """그림에 없는 칸 번호를 사본이 흘리지 않는다: 레벨 순서 목록·빈 자리 표시가 없다."""
    src = fixture_src(tmp_path); out = tmp_path / "b.md"
    blind.make(src, out)
    text = out.read_text(encoding="utf-8")
    assert "레벨 순서" not in text and ", -" not in text


def test_tree_line_skips_unreachable_and_deep_gaps():
    line = blind._tree_line(["A", "B", None, "C", None, None, None, "D", None, None, None, None, None, None, "X"])
    assert line == "[그림: 트리 — 루트 A; A의 왼쪽 자식 B; B의 왼쪽 자식 C; C의 왼쪽 자식 D]"


def test_make_only(tmp_path):
    src = fixture_src(tmp_path); out = tmp_path / "b.md"
    blind.make(src, out, {"q2"})
    text = out.read_text(encoding="utf-8")
    assert "## q2." in text and "## q1." not in text


def test_record_and_status_ok(tmp_path):
    src = fixture_src(tmp_path)
    assert blind.status(src, _ok_ledger(tmp_path, src)) == []


def test_status_flags_mismatch_and_objection(tmp_path):
    src = fixture_src(tmp_path)
    write(tmp_path / "a.md", TABLE + "| q1 | 2 | s0-a | 부모 정의 모호 |\n| q2 | B | s0-b | |\n| q3 | B, C, A | s0-a | |")
    blind.record(src, tmp_path / "a.md", tmp_path / "l.json", 1)
    lines = blind.status(src, tmp_path / "l.json")
    assert lines == ["q1: 이의 — 부모 정의 모호", "q2: 답 불일치 (B ≠ A)"]


def test_status_invalidates_changed_item(tmp_path):
    src = fixture_src(tmp_path)
    ledger = _ok_ledger(tmp_path, src)
    path = src / "items.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["items"][1]["title"] = "바뀐 제목"
    path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    lines = blind.status(src, ledger)
    assert lines == ["q2: 수정됨"]


def test_status_missing_and_later_round_overwrites(tmp_path):
    src = fixture_src(tmp_path)
    write(tmp_path / "a.md", TABLE + "| q1 | 2 | x | |")
    blind.record(src, tmp_path / "a.md", tmp_path / "l.json", 1)
    assert "q2: 장부에 없음" in blind.status(src, tmp_path / "l.json")
    write(tmp_path / "b.md", TABLE + "| q1 | 3 | x | |")
    data = blind.record(src, tmp_path / "b.md", tmp_path / "l.json", 2)
    assert data["q1"]["round"] == 2 and data["q1"]["answer"] == "3"


def test_parse_answers_duplicate_and_prose():
    with pytest.raises(ValueError):
        blind.parse_answers(TABLE + "| q1 | 2 | | |\n| q1 | 3 | | |")
    got = blind.parse_answers("결과입니다.\n\n" + TABLE + "|  q1 |  2  | s0 |  |\n끝.")
    assert list(got) == ["q1"] and got["q1"]["answer"] == "2" and got["q1"]["objection"] == ""
