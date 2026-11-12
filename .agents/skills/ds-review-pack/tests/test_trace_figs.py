import copy
import json
from pathlib import Path
import tempfile
import unittest

from _util import FIXTURES

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


if __name__ == "__main__":
    unittest.main()
