import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
RP = HERE.parents[1] / "ds-review-pack"
sys.path.insert(0, str(RP / "scripts"))
sys.path.insert(0, str(HERE.parent / "scripts"))

import trace_figs  # noqa: E402
from mpe_contract import markup_errors  # noqa: E402
from mpe_shared import parse  # noqa: E402


class TestExplainFragment(unittest.TestCase):
    def setUp(self):
        self.t = trace_figs.load(RP / "tests" / "fixtures" / "trace" / "inorder-1105.json")

    def test_explain_fragment_passes_contract(self):
        h = trace_figs.render(self.t, "explain")
        self.assertEqual(markup_errors(parse(h)), [])
        self.assertNotIn("<script", h)
        self.assertNotIn("hidden", h)
        self.assertEqual(h.count("<figure"), 4)
        self.assertIn('id="trace-inorder-1105-k4"', h)
        self.assertIn("<!-- /trace inorder-1105 -->", h)
        self.assertNotIn("<ol", h)

    def _item(self):
        import shutil
        import tempfile
        from helpers import fragment, pack
        tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, tmp, True)
        pk = pack(tmp / "복습문제_0917_Recursion.html")
        folder = tmp / "run" / "t"
        (folder / "traces").mkdir(parents=True)
        shutil.copy2(RP / "tests" / "fixtures" / "trace" / "inorder-1105.json", folder / "traces")
        frag = fragment(pk.problems[0]) + trace_figs.render(self.t, "explain")
        (tmp / "repo").mkdir()
        item = {"pack": pk, "folder": folder, "repo": tmp / "repo", "run": tmp / "run"}
        return item, {"p1": frag}, folder

    def test_build_keeps_traces(self):
        import json
        import mpe_cli
        item, frags, folder = self._item()
        mpe_cli.build(item, frags)
        found = list(folder.glob("stage/*/**/traces/inorder-1105.json"))
        self.assertEqual(len(found), 1)
        manifest = json.loads(next(folder.glob("stage/*/**/manifest.json")).read_text(encoding="utf-8"))
        self.assertTrue(any(k.endswith("traces/inorder-1105.json") for k in manifest["files"]))

    def test_build_rejects_stale_trace(self):
        import mpe_cli
        from mpe_types import ExplainError
        item, frags, folder = self._item()
        path = folder / "traces" / "inorder-1105.json"
        path.write_text(path.read_text(encoding="utf-8").replace('"text": "', '"text": "바뀐 ', 1), encoding="utf-8")
        with self.assertRaisesRegex(ExplainError, "p1: trace-stale inorder-1105"):
            mpe_cli.build(item, frags)

    def test_build_rejects_missing_trace_json(self):
        import mpe_cli
        from mpe_types import ExplainError
        item, frags, folder = self._item()
        (folder / "traces" / "inorder-1105.json").unlink()
        with self.assertRaisesRegex(ExplainError, "trace-missing inorder-1105"):
            mpe_cli.build(item, frags)


    def test_build_rejects_trace_block_without_traces_dir(self):
        import shutil
        import mpe_cli
        from mpe_types import ExplainError
        item, frags, folder = self._item()
        shutil.rmtree(folder / "traces")
        with self.assertRaisesRegex(ExplainError, "p1: trace-missing inorder-1105"):
            mpe_cli.build(item, frags)

    def test_build_copies_only_json_traces(self):
        import mpe_cli
        item, frags, folder = self._item()
        (folder / "traces" / "stray.txt").write_text("x", encoding="utf-8")
        mpe_cli.build(item, frags)
        self.assertEqual(list(folder.glob("stage/*/**/traces/stray.txt")), [])
        self.assertEqual(len(list(folder.glob("stage/*/**/traces/inorder-1105.json"))), 1)


if __name__ == "__main__":
    unittest.main()
