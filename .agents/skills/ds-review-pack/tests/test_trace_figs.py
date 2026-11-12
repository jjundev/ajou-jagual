import copy
import json
import re
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

from _util import FIXTURES, SCRIPTS

import trace_figs


def write_tmp(trace: dict, directory: str) -> Path:
    """trace 를 directory 아래 JSON 파일로 쓰고 경로를 돌려준다."""
    path = Path(directory) / "trace.json"
    path.write_text(json.dumps(trace, ensure_ascii=False), encoding="utf-8")
    return path


class TestLint(unittest.TestCase):
    def setUp(self):
        self.t = trace_figs.load(FIXTURES / "trace" / "inorder-1105.json")

    def test_fixture_is_clean(self):
        self.assertEqual(trace_figs.lint(self.t), [])

    def test_lint_codes(self):
        cases = {
            "missing-node": lambda t: t["structures"][0]["nodes"]["7"].update(l="99"),
            "key-count": lambda t: [s.pop("key", None) for s in t["steps"]],
            "too-many-steps": lambda t: t["steps"].extend([t["steps"][0]] * 27),
            "unknown-structure": lambda t: t["steps"][0]["state"].update(zz=[]),
            "dollar": lambda t: t["steps"][0].update(text="$x$"),
            "version": lambda t: t.update(version=2),
            "id": lambda t: t.update(id="Bad Id"),
            "no-steps": lambda t: t.update(steps=[]),
            "unknown-kind": lambda t: t["structures"][1].update(kind="heap"),
            "too-many-nodes": lambda t: t["structures"][0]["nodes"].update(
                {f"n{i}": {} for i in range(25)}),
            "too-many-cells": lambda t: t["structures"][2].update(size=21),
        }
        for code, mutate in cases.items():
            with self.subTest(code=code):
                t = copy.deepcopy(self.t)
                mutate(t)
                self.assertIn(code, trace_figs.lint(t))

    def test_lint_rejects_dollar(self):
        t = copy.deepcopy(self.t)
        t["steps"][3]["text"] = "비용은 $O(n)$"
        self.assertEqual(trace_figs.lint(t), ["dollar"])
        with tempfile.TemporaryDirectory() as tmp:
            path = write_tmp(t, tmp)
            with self.assertRaises(trace_figs.TraceError) as ctx:
                trace_figs.load(path)
        self.assertEqual(ctx.exception.code, "dollar")

    def test_sha_is_stable_under_key_order(self):
        a = trace_figs.trace_sha(self.t)
        b = trace_figs.trace_sha(json.loads(json.dumps(self.t, sort_keys=False)))
        self.assertEqual(a, b)
        self.assertEqual(len(a), 12)


def full_tree(n: int) -> dict:
    """완전 이진 트리. 키 "1".."n"."""
    nodes = {}
    for i in range(1, n + 1):
        child = {}
        if 2 * i <= n:
            child["l"] = str(2 * i)
        if 2 * i + 1 <= n:
            child["r"] = str(2 * i + 1)
        nodes[str(i)] = child
    return {"id": "t", "kind": "bintree", "root": "1", "nodes": nodes}


def single_step_trace(struct: dict) -> dict:
    return {"version": 1, "id": "one", "structures": [struct],
            "steps": [{"text": "한 단계예요.", "state": {struct["id"]: {"cur": "1", "done": [], "null_at": None, "changed": []}}}]}


def viewbox_width(svg: str) -> float:
    return float(re.search(r'viewBox="0 0 ([\d.]+) ', svg).group(1))


class TestRender(unittest.TestCase):
    def setUp(self):
        self.t = trace_figs.load(FIXTURES / "trace" / "inorder-1105.json")

    def test_layout_x_follows_inorder(self):
        pos = trace_figs.tree_layout(self.t["structures"][0])
        self.assertEqual(sorted(pos, key=lambda k: pos[k][0]), ["3", "7", "12", "18", "26", "27", "31"])
        self.assertEqual(pos["27"][1], pos["18"][1] + 3 * 56)

    def test_layout_uses_structure_not_key_order(self):
        s = {"id": "t", "kind": "bintree", "root": "+", "nodes": {
            "+": {"l": "*", "r": "/"}, "*": {"l": "a", "r": "b"}, "/": {"l": "c", "r": "d"},
            "a": {}, "b": {}, "c": {}, "d": {}}}
        pos = trace_figs.tree_layout(s)
        self.assertEqual(sorted(pos, key=lambda k: pos[k][0]), ["a", "*", "b", "+", "c", "/", "d"])

    def test_wide_tree_fits_width(self):
        svg = trace_figs.step_svg(single_step_trace(full_tree(31)), 0, "x")
        self.assertLessEqual(viewbox_width(svg), 720)

    def test_step_svg_contract(self):
        svg = trace_figs.step_svg(self.t, 0, "trace-inorder-1105-s1")
        self.assertNotIn("style=", svg)
        self.assertEqual(set(re.findall(r'class="([^"]+)"', svg)) - {"fig-ink", "fig-accent", "fig-dot", "fig-text", "fig-muted"}, set())
        self.assertIn('aria-label="18에서는 왼쪽을 먼저 처리해요.', svg)
        self.assertIn(">미뤄 둔 노드<", svg)
        # 스택 칸은 글자 18 바로 앞에 rect 가 있고, 트리 노드는 circle 뒤에 18 이 온다
        self.assertRegex(svg, r'<rect class="fig-ink"[^>]*/><text class="fig-text"[^>]*>18</text>')

    def test_null_marker(self):
        i = next(n for n, s in enumerate(self.t["steps"]) if s["state"]["t"].get("null_at"))
        self.assertIn(">NULL<", trace_figs.step_svg(self.t, i, "x"))

    def test_shadow_order(self):
        svg = trace_figs.shadow_svg(self.t, "t", "fig-inorder-shadow")
        self.assertIn("3, 7, 12, 18, 26, 27, 31", svg)

    def test_deterministic_and_stable_viewbox(self):
        a = [trace_figs.step_svg(self.t, i, "x") for i in range(len(self.t["steps"]))]
        b = [trace_figs.step_svg(self.t, i, "x") for i in range(len(self.t["steps"]))]
        self.assertEqual(a, b)
        self.assertEqual(len({re.search(r'viewBox="[^"]+"', s).group(0) for s in a}), 1)

    def test_text_is_escaped(self):
        t = copy.deepcopy(self.t)
        t["steps"][0]["text"] = 'a < b & "c"'
        svg = trace_figs.step_svg(t, 0, "x", hidden=True)
        self.assertIn('aria-label="a &lt; b &amp; &quot;c&quot;"', svg)
        self.assertIn(" hidden>", svg)

    def test_list_structure(self):
        t = {"version": 1, "id": "l", "structures": [{"id": "ls", "kind": "list", "label": "연결"}],
             "steps": [{"text": "이어요.", "state": {"ls": {"order": ["a", "b", "c"], "ptr": {"p": "b"}, "edge_changed": [["a", "b"]]}}}]}
        svg = trace_figs.step_svg(t, 0, "x")
        self.assertIn(">p<", svg)
        self.assertIn('class="fig-accent" d="M', svg)
        self.assertNotIn("style=", svg)

    def test_stack_and_wide_content_fit_width(self):
        t = single_step_trace(full_tree(31))
        t["structures"].append({"id": "st", "kind": "stack", "label": "미뤄 둔 노드"})
        t["steps"][0]["state"]["st"] = ["1", "2", "4"]
        self.assertLessEqual(viewbox_width(trace_figs.step_svg(t, 0, "x")), 720)

    def test_20_cell_array_fits_width(self):
        vals = [str(i) for i in range(20)]
        t = {"version": 1, "id": "a", "structures": [{"id": "a", "kind": "array", "size": 20}],
             "steps": [{"text": "배열이에요.", "state": {"a": {"values": vals, "hi": [3], "ptr": {"i": 3}}}}]}
        self.assertLessEqual(viewbox_width(trace_figs.step_svg(t, 0, "x")), 720)

    def test_20_node_list_fits_width(self):
        order = [f"n{i}" for i in range(20)]
        t = {"version": 1, "id": "l", "structures": [{"id": "l", "kind": "list"}],
             "steps": [{"text": "목록이에요.", "state": {"l": {"order": order, "ptr": {}, "edge_changed": [["n0", "n1"]]}}}]}
        self.assertLessEqual(viewbox_width(trace_figs.step_svg(t, 0, "x")), 720)

    def test_shadow_structure(self):
        svg = trace_figs.shadow_svg(self.t, "t", "x")
        self.assertEqual(svg.count('stroke-dasharray="4 3"'), 7)
        self.assertEqual(len(re.findall(r'<text class="fig-text"', svg)), 14)  # 노드 안 7 + 아래 값 7
        self.assertIn('class="fig-accent" d="M', svg)

    def test_shadow_unknown_structure(self):
        with self.assertRaises(ValueError):
            trace_figs.shadow_svg(self.t, "nope", "x")


class TestFragments(unittest.TestCase):
    def setUp(self):
        self.t = trace_figs.load(FIXTURES / "trace" / "inorder-1105.json")

    def test_note_fragment_parts(self):
        h = trace_figs.render(self.t, "note")
        self.assertEqual(h.count("<svg id=\"trace-inorder-1105-s"), 14)
        self.assertEqual(h.count(" hidden"), 13 + 1)  # 숨긴 단계 13 + widget-static
        self.assertEqual(re.findall(r"<li>(.*?)</li>", h), [s["text"] for s in self.t["steps"]])
        self.assertIn('data-trace-sha="' + trace_figs.trace_sha(self.t) + '"', h)
        self.assertEqual(h.count('id="widget-trace-inorder-1105-static-'), 4)
        self.assertIn("<!-- /trace inorder-1105 -->", h)
        self.assertLess(h.index("<!-- /trace inorder-1105 -->"), h.index('<script id="widget-trace-inorder-1105-ui">'))

    def test_two_players_do_not_collide(self):
        t2 = copy.deepcopy(self.t)
        t2["id"] = "inorder-b"
        doc = trace_figs.render(self.t, "note") + trace_figs.render(t2, "note")
        ids = re.findall(r' id="([^"]+)"', doc)
        self.assertEqual(len(ids), len(set(ids)))

    def test_text_is_escaped(self):
        t = copy.deepcopy(self.t)
        t["steps"][0]["text"] = "a<b & c"
        self.assertIn("a&lt;b &amp; c", trace_figs.render(t, "note"))

    def test_cli_render_matches_function(self):
        path = str(FIXTURES / "trace" / "inorder-1105.json")
        for target in ("note", "explain"):
            out = subprocess.run([sys.executable, str(SCRIPTS / "trace_figs.py"), "render", path, "--target", target],
                                 capture_output=True, text=True, check=True).stdout
            self.assertEqual(out, trace_figs.render(self.t, target))

    def test_cli_lint_and_shadow(self):
        path = str(FIXTURES / "trace" / "inorder-1105.json")
        r = subprocess.run([sys.executable, str(SCRIPTS / "trace_figs.py"), "lint", path], capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        sid = self.t["structures"][0]["id"]
        r = subprocess.run([sys.executable, str(SCRIPTS / "trace_figs.py"), "shadow", path, "--structure", sid, "--id", "sh-1"],
                           capture_output=True, text=True, check=True)
        self.assertIn('<svg id="sh-1"', r.stdout)
        with tempfile.TemporaryDirectory() as d:
            bad = copy.deepcopy(self.t)
            bad["steps"][0]["text"] = "비용 $x$"
            r = subprocess.run([sys.executable, str(SCRIPTS / "trace_figs.py"), "lint", str(write_tmp(bad, d))],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertTrue(r.stdout.strip())

    def test_render_rejects_bad_target(self):
        with self.assertRaises(ValueError):
            trace_figs.render(self.t, "pdf")


if __name__ == "__main__":
    unittest.main()


class TestVerify(unittest.TestCase):
    def setUp(self):
        self.t = trace_figs.load(FIXTURES / "trace" / "inorder-1105.json")
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(__import__("shutil").rmtree, self.dir, True)

    def dump(self):
        (self.dir / "inorder-1105.json").write_text(json.dumps(self.t, ensure_ascii=False), encoding="utf-8")

    def test_stale_trace_fails(self):
        self.dump()
        h = trace_figs.render(self.t, "note")
        self.assertEqual(trace_figs.verify(h, self.dir), [])
        self.t["steps"][2]["text"] += "!"
        self.dump()
        self.assertEqual(trace_figs.verify(h, self.dir), [("trace-stale", "inorder-1105")])

    def test_missing_json(self):
        self.assertEqual(trace_figs.verify(trace_figs.render(self.t, "note"), self.dir),
                         [("trace-missing", "inorder-1105")])

    def test_broken_json_is_stale_not_crash(self):
        (self.dir / "inorder-1105.json").write_text("{", encoding="utf-8")
        self.assertEqual(trace_figs.verify(trace_figs.render(self.t, "note"), self.dir),
                         [("trace-stale", "inorder-1105")])

    def test_script_moved_before_body_end_is_fresh(self):
        self.dump()
        h = trace_figs.render(self.t, "note")
        i = h.index("<script")
        doc = f"<html><body>{h[:i]}<p>later</p>{h[i:]}</body></html>"
        self.assertEqual(trace_figs.verify(doc, self.dir), [])

    def test_missing_or_changed_script_is_stale(self):
        self.dump()
        h = trace_figs.render(self.t, "note")
        i = h.index("<script")
        self.assertEqual(trace_figs.verify(h[:i], self.dir), [("trace-stale", "inorder-1105")])
        self.assertEqual(trace_figs.verify(h.replace("function", "fun ction", 1), self.dir),
                         [("trace-stale", "inorder-1105")])

    def test_explain_fragment(self):
        self.dump()
        h = trace_figs.render(self.t, "explain")
        self.assertEqual(trace_figs.verify(h, self.dir), [])

    def test_cli_verify(self):
        self.dump()
        f = self.dir / "n.html"
        f.write_text(trace_figs.render(self.t, "note"), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPTS / "trace_figs.py"), "verify", str(f), "--traces", str(self.dir)],
                           capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        self.t["steps"][0]["text"] += "!"
        self.dump()
        r = subprocess.run([sys.executable, str(SCRIPTS / "trace_figs.py"), "verify", str(f), "--traces", str(self.dir)],
                           capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout.strip()), (1, "trace-stale inorder-1105"))
