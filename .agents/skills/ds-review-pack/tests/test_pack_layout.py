"""복습노트/<range>/ 배치 검사·이전과, 이전 전 경로·해시 해석."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from _util import REPO
import pack_layout as pl


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class PackLayoutTests(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        self.notes = self.repo / "복습노트"
        (self.repo / "자료구조_강의록_2026").mkdir(parents=True)
        (self.repo / "자료구조_강의록_2026" / "S1.pdf").write_bytes(b"pdf")
        prev = self.notes / "0101"
        prev.mkdir(parents=True)
        (prev / "정리노트_0101_A.html").write_text("<p id='x'>x</p>", encoding="utf-8")
        self.pack = self.notes / "0102"
        self.pack.mkdir()
        p = self.pack
        (p / "정리노트_0102_B.html").write_text("note", encoding="utf-8")
        (p / "복습문제_0102_B.html").write_text("review", encoding="utf-8")
        (p / "복습문제_0102_B-문제.pdf").write_bytes(b"%PDF")
        (p / "문제설명_0102_B.html").write_text(
            '<link href="자료_문제설명_0102_B/vendor/katex/katex.min.css">'
            '<script src="자료_문제설명_0102_B/vendor/katex/katex.min.js"></script>'
            '<a href="복습문제_0102_B.html#p1">원 문제</a>', encoding="utf-8")
        (p / "정리노트_0102_B.md").write_text(
            "![f](figures_0102/a.svg) [r](복습문제_0102_B.md#p1) [prev](../0101/정리노트_0101_A.html#x) "
            "[s](../../자료구조_강의록_2026/S1.pdf) [w](https://example.com) [t](#top) "
            '<a href="복습문제_0102_B.html">h</a>', encoding="utf-8")
        (p / "복습문제_0102_B.md").write_text("[back](정리노트_0102_B.md)", encoding="utf-8")
        (p / "문제설명_0102_B.md").write_text(
            "[원 문제](%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_0102_B.html#p1) ![g](figures_문제설명_0102_B/e.svg)",
            encoding="utf-8")
        for d, f in [("figures_0102", "a.svg"), ("figures_문제설명_0102_B", "e.svg"),
                     ("자료_PDF", "pdf-validation.json"), ("자료_복습팩", "manifest.json"),
                     ("자료_문제설명_0102_B/vendor/katex", "katex.min.js")]:
            (p / d).mkdir(parents=True)
            (p / d / f).write_text("x", encoding="utf-8")
        (p / ".DS_Store").write_bytes(b"")

    def test_check_reports_old_layout(self):
        problems = pl.check_layout(self.pack)
        self.assertEqual(len(problems), 8)
        self.assertTrue(all(".pack" in x for x in problems))
        self.assertEqual(pl.check_layout(self.notes / "0101"), [])

    def test_dry_run_changes_nothing(self):
        before = sorted(p.name for p in self.pack.iterdir())
        r = pl.migrate_pack(self.pack, apply=False)
        self.assertEqual(len(r["move"]), 8)
        self.assertEqual(r["errors"], [])
        self.assertEqual(sorted(p.name for p in self.pack.iterdir()), before)

    def test_apply_moves_relinks_and_records(self):
        explain_before = sha(self.pack / "문제설명_0102_B.html")
        note_before = sha(self.pack / "정리노트_0102_B.md")
        r = pl.migrate_pack(self.pack, apply=True)
        self.assertEqual(r["errors"], [])
        self.assertEqual(pl.check_layout(self.pack), [])
        self.assertEqual(sorted(p.name for p in self.pack.iterdir()),
                         [".DS_Store", ".pack", "문제설명_0102_B.html", "복습문제_0102_B-문제.pdf",
                          "복습문제_0102_B.html", "정리노트_0102_B.html"])
        data = self.pack / ".pack"
        html = (self.pack / "문제설명_0102_B.html").read_text(encoding="utf-8")
        self.assertIn('href=".pack/자료_문제설명_0102_B/vendor/katex/katex.min.css"', html)
        self.assertIn('src=".pack/자료_문제설명_0102_B/vendor/katex/katex.min.js"', html)
        self.assertIn('href="복습문제_0102_B.html#p1"', html)
        note = (data / "정리노트_0102_B.md").read_text(encoding="utf-8")
        for want in ["(figures_0102/a.svg)", "(복습문제_0102_B.md#p1)", "(../../0101/정리노트_0101_A.html#x)",
                     "(../../../자료구조_강의록_2026/S1.pdf)", "(https://example.com)", "(#top)",
                     'href="../복습문제_0102_B.html"']:
            self.assertIn(want, note)
        explain_md = (data / "문제설명_0102_B.md").read_text(encoding="utf-8")
        self.assertIn("(../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_0102_B.html#p1)", explain_md)
        self.assertIn("(figures_문제설명_0102_B/e.svg)", explain_md)
        self.assertEqual((data / "복습문제_0102_B.md").read_text(encoding="utf-8"), "[back](정리노트_0102_B.md)")
        # 이전 기록이 옛 경로·옛 해시를 지금 파일로 이어 준다.
        old_note = self.pack / "정리노트_0102_B.md"
        self.assertEqual(pl.current_path(old_note), data / "정리노트_0102_B.md")
        self.assertEqual(pl.current_digest(old_note, note_before), sha(data / "정리노트_0102_B.md"))
        old_html = self.pack / "문제설명_0102_B.html"
        self.assertEqual(pl.current_digest(old_html, explain_before), sha(old_html))
        self.assertEqual(pl.current_digest(old_html, "other"), "other")
        old_js = self.pack / "자료_문제설명_0102_B/vendor/katex/katex.min.js"
        self.assertEqual(pl.current_path(old_js), data / "자료_문제설명_0102_B/vendor/katex/katex.min.js")
        (record,) = data.glob("migration-*.json")
        self.assertEqual(len(json.loads(record.read_text(encoding="utf-8"))["moved"]), 8)
        # 두 번째 실행은 할 일이 없다.
        again = pl.migrate_pack(self.pack, apply=True)
        self.assertEqual(again["move"], [])

    def test_conflict_aborts_whole_pack(self):
        (self.pack / ".pack" / "figures_0102").mkdir(parents=True)
        before = sorted(p.name for p in self.pack.iterdir())
        r = pl.migrate_pack(self.pack, apply=True)
        self.assertEqual(r["errors"], [".pack/figures_0102 이미 있음"])
        self.assertEqual(sorted(p.name for p in self.pack.iterdir()), before)

    def test_cli_check_exit_codes(self):
        self.assertEqual(pl.main(["check", "--repo", str(self.repo)]), 1)
        self.assertEqual(pl.main(["migrate", "--repo", str(self.repo), "--apply"]), 0)
        self.assertEqual(pl.main(["check", "--repo", str(self.repo)]), 0)

    def test_real_repo_uses_pack_layout(self):
        problems = [p for d in pl.pack_folders(REPO) for p in pl.check_layout(d)]
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
