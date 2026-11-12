import _util  # noqa: F401  (scripts/ 를 sys.path 에 넣는다)
import tree

T = ["A", "B", "C", "D", "E", None, "F"]          # A(B(D,E), C(-,F))
EXPR = ["+", "*", "/", "a", "b", "c", "d"]
NUM = ["-", "*", "/", "3", "4", "7", "2"]


def test_traversals():
    assert tree.preorder(T) == list("ABDECF")
    assert tree.inorder(T) == list("DBEACF")
    assert tree.postorder(T) == list("DEBFCA")
    assert tree.levelorder(T) == list("ABCDEF")
    assert tree.inorder(EXPR) == list("a*b+c/d")


def test_height_count():
    assert tree.height([]) == 0 and tree.height(["A"]) == 1 and tree.height(T) == 3
    assert tree.node_count(T) == 6


def test_evaluate_c_division():
    assert tree.evaluate(NUM) == 3 * 4 - 7 // 2          # 9
    assert tree.evaluate(["/", "-7", "2"]) == -3          # C 버림


def test_lecture_numbers():
    assert tree.lecture_number(T, "F") == 7
    assert (tree.parent_index(5), tree.left_index(3), tree.right_index(3)) == (2, 6, 7)


def test_lecture_number_missing():
    try:
        tree.lecture_number(T, "Z")
    except ValueError:
        return
    raise AssertionError("ValueError expected")


def test_compute_joins_sequences():
    assert tree.compute({"op": "postorder"}, T) == "D, E, B, F, C, A"
    assert tree.compute({"op": "parent_index", "arg": 5}, None) == "2"
    assert tree.compute({"op": "lecture_number", "arg": "F"}, T) == "7"


def test_ops_cover_compute():
    assert "evaluate" in tree.OPS and len(tree.OPS) == 11
    for op in ("height", "node_count", "evaluate"):
        assert tree.compute({"op": op}, NUM).isdigit() or op == "evaluate"


def test_svg_has_no_style_and_labels():
    svg = tree.tree_svg(T, "fig-q1", "트리 A")
    assert 'style=' not in svg and svg.count("<circle") == 6 and 'aria-label="트리 A"' in svg
    assert svg.count("<line") == 5 and 'id="fig-q1"' in svg and 'role="img"' in svg


def test_find_nfc(tmp_path):
    import unicodedata
    import _paths
    (tmp_path / unicodedata.normalize("NFD", "자료_복습팩")).mkdir()
    got = _paths.find_nfc(tmp_path, "자료_복습팩")
    assert got is not None and got.is_dir()
    assert _paths.find_nfc(tmp_path, "없음") is None
