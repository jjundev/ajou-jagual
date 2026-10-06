import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents/skills/ds-stt"
CLAUDE_DIR = ROOT / ".claude/skills/ds-stt"


class DsSttTests(unittest.TestCase):
    def setUp(self):
        import sys
        scripts_dir = str(SKILL_DIR / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)

    def test_01_skill_entrypoints_and_metadata(self):
        skill_md = SKILL_DIR / "SKILL.md"
        self.assertTrue(skill_md.is_file(), "SKILL.md must exist in .agents/skills/ds-stt/")
        # Ensure it is NOT linked into .claude/skills (disallow Claude)
        self.assertFalse(CLAUDE_DIR.exists(), ".claude/skills/ds-stt must NOT exist (disallow Claude)")

        content = skill_md.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---"), "SKILL.md must have frontmatter")
        self.assertIn("name: ds-stt", content)
        self.assertIn("description:", content)
        self.assertIn("Gemini Only", content, "SKILL.md must specify Gemini Only guard")
        self.assertIn("Model Compatibility Gate", content, "SKILL.md must contain Model Compatibility Gate")
        self.assertIn("STT/<MMDD> 자구알.md", content, "SKILL.md must document standard output path")

    def test_02_parse_date(self):
        from infer_context import parse_date

        self.assertEqual(parse_date("20261005_자구알.m4a"), "1005")
        self.assertEqual(parse_date("1005 자구알.mp3"), "1005")
        self.assertEqual(parse_date("1005.m4a"), "1005")
        self.assertEqual(parse_date("녹음_1001.wav"), "1001")
        self.assertEqual(parse_date("/path/to/2026-0928-class.m4a"), "0928")
        self.assertEqual(parse_date("audio.m4a", date_override="1005"), "1005")

        with self.assertRaises(ValueError):
            parse_date("audio_without_date.m4a")

    def test_03_infer_chapter(self):
        from infer_context import infer_chapter

        # 1005 has 복습노트/1005 covering 4장 List
        ch_1005 = infer_chapter(ROOT, "1005")
        self.assertEqual(ch_1005, 4)

        # 0928 has 복습노트/0928 covering 3장 ArrayStructureList
        ch_0928 = infer_chapter(ROOT, "0928")
        self.assertEqual(ch_0928, 3)

        # 0914 has 복습노트/0914 covering 2장 Recursion
        ch_0914 = infer_chapter(ROOT, "0914")
        self.assertEqual(ch_0914, 2)

    def test_04_extract_terms(self):
        from infer_context import extract_chapter_terms

        terms = extract_chapter_terms(ROOT, chapter=4)
        self.assertIsInstance(terms, list)
        self.assertGreater(len(terms), 10)
        # Should include core terms of chapter 4 (List)
        term_text = " ".join(terms)
        self.assertTrue(any(k in term_text for k in ["node", "link", "head", "포인터", "리스트", "malloc", "free"]))

    def test_05_build_stt_prompt(self):
        from infer_context import build_stt_prompt

        prompt = build_stt_prompt(chapter=4, chapter_title="Software_4_List", terms=["node", "link", "head", "malloc"])
        self.assertIn("자료구조", prompt)
        self.assertIn("4장", prompt)
        self.assertIn("List", prompt)
        self.assertIn("node", prompt)
        self.assertIn("malloc", prompt)  # Common error correction rule

    def test_06_merge_transcripts(self):
        import tempfile
        from merge_transcripts import merge_transcripts

        with tempfile.TemporaryDirectory() as tmpdir:
            part1 = Path(tmpdir) / "1005_자구알_part01.md"
            part2 = Path(tmpdir) / "1005_자구알_part02.md"
            part1.write_text("첫 번째 파트 발화 내용입니다.\n\n단순 연결 리스트에 대해 설명합니다.\n", encoding="utf-8")
            part2.write_text("두 번째 파트 발화 내용입니다.\n\nmalloc 함수로 메모리를 할당합니다.\n", encoding="utf-8")

            out_file = Path(tmpdir) / "1005 자구알.md"
            res = merge_transcripts(
                target_dir=tmpdir,
                prefix="1005_자구알",
                out_file=str(out_file),
                keep_parts=True,
            )
            self.assertTrue(out_file.is_file())
            content = out_file.read_text(encoding="utf-8")
            self.assertIn("# 1005_자구알 전체 오디오 전사본", content)
            self.assertIn("## Part 01", content)
            self.assertIn("## Part 02", content)
            self.assertIn("단순 연결 리스트에 대해 설명합니다.", content)
            self.assertIn("malloc 함수로 메모리를 할당합니다.", content)

            # Test timestamp stripping when timestamps=False
            part3 = Path(tmpdir) / "1005_자구알_part03.md"
            part3.write_text("01:23\n이 문장은 타임스탬프가 붙어있습니다.\n", encoding="utf-8")
            res_stripped = merge_transcripts(
                target_dir=tmpdir,
                prefix="1005_자구알",
                out_file=str(out_file),
                keep_parts=True,
                timestamps=False,
            )
            content_stripped = out_file.read_text(encoding="utf-8")
            self.assertNotIn("01:23", content_stripped)
            self.assertIn("이 문장은 타임스탬프가 붙어있습니다.", content_stripped)


if __name__ == "__main__":
    unittest.main()
