import json

import pytest

from concept_util import copy_fixture, fixture_src, mutated_fixture, nfd_path

import check


def _lines(src):
    return check.check(src)


def _fires(tmp_path, mutate, code):
    return [p for p in _lines(mutated_fixture(tmp_path, mutate)) if p.startswith(code)]


def test_fixture_is_clean(tmp_path):
    assert check.check(fixture_src(tmp_path)) == []


@pytest.mark.parametrize("mutate, code", [
    (lambda d: d["items"][1]["options"].pop(), "[mcq-shape]"),
    (lambda d: d["items"][1]["options"][1].update(misconception=""), "[explain]"),
    (lambda d: d["items"][0]["answer"].update(canonical="3"), "[compute]"),
    (lambda d: d["items"][1].update(title=d["items"][1]["options"][0]["text"]), "[title-leak]"),
    (lambda d: d["items"][1].update(stem_html="<p>이진 탐색 트리에서</p>"), "[forbidden]"),
    (lambda d: d["items"][1].update(stem_html="<p>다음 트리를 후위 순회한 결과를 쓰시오. 루트는 A이다.</p>"), "[duplicate]"),
    (lambda d: d["items"][1].update(stem_html='<p style="color:red">x</p>'), "[style]"),
    (lambda d: d["items"].extend(dict(d["items"][0], id=f"x{i}") for i in range(14)), "[count]"),
    (lambda d: d["items"][1]["options"][1].update(source="foo:1"), "[explain]"),
    (lambda d: d["items"][0].update(format="mcq"), "[format]"),
    (lambda d: d["items"][0].pop("compute"), "[compute]"),
    (lambda d: d["items"].pop(1), "[count]"),
])
def test_rule_fires(tmp_path, mutate, code):
    assert _fires(tmp_path, mutate, code)


def test_negative_ratio(tmp_path):
    assert _fires(tmp_path, lambda d: d["items"][1].update(stem_html="<p>옳지 않은 것은?</p>"), "[negative]")


def test_line_format(tmp_path):
    lines = _fires(tmp_path, lambda d: d["items"][0]["answer"].update(canonical="3"), "[compute]")
    assert lines[0].startswith("[compute] q1: ")


def test_topic_and_source_rules(tmp_path):
    def mut(src):
        d = json.loads((src / "objectives.json").read_text(encoding="utf-8"))
        d["objectives"][0]["topic_id"] = "s0-c"
        d["objectives"][1]["topic_id"] = "nope"
        d["objectives"][1]["source"]["slide"] = "슬라이드 3"
        (src / "objectives.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    src = fixture_src(tmp_path)
    mut(src)
    lines = check.check(src)
    assert sum(p.startswith("[topic]") for p in lines) == 2
    assert any(p.startswith("[source] o2:") for p in lines)


def test_balance_only_with_four_mcq(tmp_path):
    def mut(d):
        base = d["items"][1]
        d["items"].extend(dict(base, id=f"m{i}") for i in range(3))
    assert _fires(tmp_path, mut, "[balance]")
    assert not _fires(tmp_path / "b", lambda d: None, "[balance]")


def test_compute_error_reported(tmp_path):
    assert _fires(tmp_path, lambda d: d["items"][0]["compute"].update(op="zzz"), "[compute]")


def test_duplicate_nfd_card_file(tmp_path):
    root = copy_fixture(tmp_path)
    import unicodedata
    card = root / "복습문제_9999_Mini.html"
    card.rename(card.with_name(unicodedata.normalize("NFD", card.name)))
    src = nfd_path(root, ".pack/자료_확인문제_9999_Mini")
    p = src / "items.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["items"][1]["stem_html"] = "<p>다음 트리를 후위 순회한 결과를 쓰시오. 루트는 A이다.</p>"
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    assert any(x.startswith("[duplicate]") for x in check.check(src))


def test_cli_ok_and_fail(tmp_path, capsys):
    assert check.main(["check.py", str(fixture_src(tmp_path))]) == 0
    assert capsys.readouterr().out.strip() == "OK"
    bad = mutated_fixture(tmp_path / "x", lambda d: d["items"][0]["answer"].update(canonical="3"))
    assert check.main(["check.py", str(bad)]) == 1
    assert "[compute]" in capsys.readouterr().out
