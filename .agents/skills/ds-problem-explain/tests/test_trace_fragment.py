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


if __name__ == "__main__":
    unittest.main()
