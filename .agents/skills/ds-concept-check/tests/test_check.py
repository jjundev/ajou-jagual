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


@pytest.mark.parametrize("mutate", [
    lambda item: item.pop("hint", None),
    lambda item: item.update(hint="   "),
    lambda item: item.update(hint=["첫 단계"]),
    lambda item: item.update(hint="첫 줄\n둘째 줄"),
])
def test_rejects_missing_or_malformed_hint(tmp_path, mutate):
    assert _fires(tmp_path, lambda d: mutate(d["items"][0]), "[hint] q1:")


def test_forbidden_preview_term_in_hint(tmp_path):
    assert _fires(tmp_path, lambda d: d["items"][0].update(hint="이진 탐색 트리를 떠올려 보세요."), "[forbidden] q1:")


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


def test_short_stem_is_never_duplicate(tmp_path):
    assert not _fires(tmp_path, lambda d: d["items"][1].update(stem_html="<p>A</p>"), "[duplicate]")



# ── 걸음 상한 [steps] · 구별 거리 [distance] ──────────────────────────────
import tree as treemod

Q8 = ["A", "B", "C", "D", "E", None, "F", None, None, "G"]       # 1102 q8, 7노드
BST9 = ["45", "20", "70", "8", "33", "52", "90", None, None, "27", None, None, "61"]  # 1105 q5


def _seq_mcq(src, t, op, wrong_ops, answer="B"):
    """o1 을 절차 결과로 바꾸고 q3 을 순서열 객관식으로 만든다. wrong_ops 는 op 이름 또는 순서열 문자열."""
    obj = src / "objectives.json"
    d = json.loads(obj.read_text(encoding="utf-8"))
    d["objectives"][0]["kind"] = "절차 결과"
    obj.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    p = src / "items.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    right = treemod.compute({"op": op}, t)
    wrongs = iter(w if ", " in w else treemod.compute({"op": w}, t) for w in wrong_ops)
    opts = []
    for oid in "ABCD":
        if oid == answer:
            opts.append({"id": oid, "text": right, "value": right, "why": "맞아요."})
        else:
            v = next(wrongs)
            opts.append({"id": oid, "text": v, "value": v, "why": "달라요.",
                         "misconception": "다른 순서로 착각", "source": "stt:1절"})
    d["items"][2] = dict(d["items"][2], format="mcq", tree=t, compute={"op": op},
                         options=opts, answer=answer)
    d["items"][2].pop("solution", None)
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return src


def _codes(src, code):
    return [x for x in check.check(src) if x.startswith(code)]


def test_short_sequence_over_cap(tmp_path):
    def mut(d):
        d["items"][2].update(tree=BST9, compute={"op": "inorder"})
        d["items"][2]["answer"]["canonical"] = treemod.compute({"op": "inorder"}, BST9)
    lines = _fires(tmp_path, mut, "[steps]")
    assert lines and "9걸음" in lines[0]


def test_short_sequence_at_cap_passes(tmp_path):
    def mut(d):
        d["items"][2].update(tree=Q8, compute={"op": "preorder"})
        d["items"][2]["answer"]["canonical"] = treemod.compute({"op": "preorder"}, Q8)
    assert check.check(mutated_fixture(tmp_path, mut)) == []


def test_evaluate_over_cap(tmp_path):
    t = ["+", "*", "-", "1", "2", "3", "/", None, None, None, None, None, None, "8", "2"]
    def mut(d):
        d["items"][2].update(tree=t, compute={"op": "evaluate"})
        d["items"][2]["answer"]["canonical"] = treemod.compute({"op": "evaluate"}, t)
    assert _fires(tmp_path, mut, "[steps]")


def test_seq_mcq_big_tree_passes(tmp_path):
    # 노드 9개라도 오답이 1·2·1칸에서 갈리면 통과
    src = _seq_mcq(fixture_src(tmp_path), BST9, "inorder", ["preorder", "postorder", "levelorder"])
    assert check.check(src) == []


def test_seq_mcq_ok_q8(tmp_path):
    src = _seq_mcq(fixture_src(tmp_path), Q8, "preorder", ["inorder", "postorder", "levelorder"])
    assert check.check(src) == []


def test_seq_mcq_missing_value(tmp_path):
    src = _seq_mcq(fixture_src(tmp_path), Q8, "preorder", ["inorder", "postorder", "levelorder"])
    p = src / "items.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["items"][2]["options"][0].pop("value")
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    assert _codes(src, "[distance]")


def test_seq_mcq_made_up_nodes(tmp_path):
    src = _seq_mcq(fixture_src(tmp_path), Q8, "preorder", ["inorder", "postorder", "A, B, D, E, G, C, Z"])
    assert any("같은 노드" in x for x in _codes(src, "[distance]"))


def test_seq_mcq_late_split(tmp_path):
    # 정답 A,B,D,E,G,C,F 와 5칸째에서야 갈림
    src = _seq_mcq(fixture_src(tmp_path), Q8, "preorder", ["inorder", "levelorder", "A, B, D, E, C, G, F"])
    assert any("5번째" in x for x in _codes(src, "[distance]"))


def test_seq_mcq_all_first_cell(tmp_path):
    src = _seq_mcq(fixture_src(tmp_path), Q8, "preorder", ["inorder", "postorder", "G, B, D, E, A, C, F"])
    assert any("첫 칸" in x for x in _codes(src, "[distance]"))


def test_rule_kind_mcq_still_rejected(tmp_path):
    # 규칙 적용은 여전히 단답만
    assert _fires(tmp_path, lambda d: d["items"][0].update(format="mcq"), "[format]")


def test_procedure_numeric_mcq_rejected(tmp_path):
    src = _seq_mcq(fixture_src(tmp_path), Q8, "preorder", ["inorder", "postorder", "levelorder"])
    p = src / "items.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["items"][2]["compute"] = {"op": "height"}
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    assert _codes(src, "[format]")
