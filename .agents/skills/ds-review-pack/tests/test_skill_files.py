"""SKILL.md 형식과, 본문이 가리키는 파일이 모두 있는지 확인한다."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest

from _util import SKILL

SKILL_MD = SKILL / "SKILL.md"
ML_WORDS = ("MML", "머신러닝", "정방철", "머러기", "Lecture", "강의노트/")


class TestSkillFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL_MD.read_text(encoding="utf-8")

    def test_frontmatter(self):
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", self.text)
        self.assertIsNotNone(m, "frontmatter는 name, description 두 줄")
        self.assertEqual(m.group(1), "ds-review-pack")
        for word in ("정리노트", "복습문제", "문제은행"):
            self.assertIn(word, m.group(2))
        self.assertLessEqual(len(m.group(2)), 1024)

    def test_referenced_files_exist(self):
        refs = set(re.findall(r"(?:references|scripts|assets)/[\w.-]+\.(?:md|py|html)", self.text))
        self.assertGreaterEqual(len(refs), 14)
        for rel in sorted(refs):
            with self.subTest(rel=rel):
                self.assertTrue((SKILL / rel).exists(), rel)

    def test_every_reference_is_used(self):
        for path in sorted((SKILL / "references").glob("*.md")):
            with self.subTest(ref=path.name):
                self.assertIn(f"references/{path.name}", self.text)

    def test_steps_present(self):
        for n in range(10):
            with self.subTest(step=n):
                self.assertRegex(self.text, rf"\n### {n}\. ")

    def test_bank_steps_present(self):
        for n in range(1, 5):
            with self.subTest(step=n):
                self.assertRegex(self.text, rf"\n### B{n}\. ")
        self.assertIn("`reviewed: true`인 `scan`·`photo` 원본은 B2·B3을 건너뛰고", self.text)

    def _step8(self):
        return self.text.split("\n### 8. ", 1)[1].split("\n### 9. ", 1)[0]

    def test_concept_check_after_pdf_before_layout(self):
        s8 = self._step8()
        self.assertLess(s8.index("references/pdf-build.md"), s8.index("ds-concept-check/SKILL.md"))
        self.assertLess(s8.index("ds-concept-check/SKILL.md"), s8.index("pack_layout.py"))

    def test_concept_check_scope_and_failure(self):
        self.assertTrue((SKILL.parent / "ds-concept-check" / "SKILL.md").exists())
        self.assertIn("**확인문제 연결**", self.text)
        self.assertIn("`update-existing`·`revise-existing`은 확인문제를 만들지 않고", self.text)
        self.assertIn("복습팩 생성됨 / 확인문제 보류", self.text)
        self.assertIn("| 확인문제 스킬 누락 |", self.text)
        self.assertIn("| 확인문제 검사 실패 |", self.text)
        self.assertIn("- 확인문제:", self.text.split("\n### 9. ", 1)[1])
        self.assertIn("stt-summary.md", self.text.split("\n### 9. ", 1)[1])

    def test_concept_check_withhold_triggers(self):
        # 근거 없음도 보류로 처리하고, 배치 검사는 이 팩 줄만 판정한다(다른 팩 문제로 보류하지 않는다).
        s8 = self._step8()
        self.assertIn("근거 파일이 없어 그 스킬 1단계가 멈춘 경우", s8)
        self.assertIn("이 팩(`복습노트/<range>/`) 줄만", s8)
        self.assertIn("| 확인문제 근거 없음 |", self.text)

    def test_no_ml_leftovers(self):
        for path in [SKILL_MD, *sorted((SKILL / "references").glob("*.md"))]:
            text = path.read_text(encoding="utf-8")
            for word in ML_WORDS:
                with self.subTest(file=path.name, word=word):
                    self.assertNotIn(word, text)


class TestBackupScript(unittest.TestCase):
    """4단계 백업 스크립트(scripts/backup.py)를 임시 폴더에서 실제로 실행한다."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.notes = self.tmp / "repo" / "복습노트"
        self.notes.mkdir(parents=True)
        self.run_dir = self.tmp / "run"
        self.run_dir.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def backup(self, range_):
        cmd = [sys.executable, str(SKILL / "scripts" / "backup.py"),
               "--range", range_, "--repo", str(self.tmp / "repo"), "--run", str(self.run_dir)]
        return subprocess.run(cmd, capture_output=True, text=True)

    def backups(self):
        return sorted(p for p in self.run_dir.iterdir() if p.name.startswith("previous-"))

    def test_nothing_to_back_up(self):
        r = self.backup("0921")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("백업할 기존 팩 없음", r.stdout)
        self.assertEqual(self.backups(), [])

    def test_backs_up_nfc_and_nfd_names_into_fresh_dirs(self):
        (self.notes / "정리노트_0921_A.html").write_text("n", encoding="utf-8")
        (self.notes / unicodedata.normalize("NFD", "복습문제_0921_A.md")).write_text("r", encoding="utf-8")
        (self.notes / "정리노트_0921-0923_B.html").write_text("other range", encoding="utf-8")
        (self.notes / "figures_0921").mkdir()
        (self.notes / "figures_0921" / "a.svg").write_text("<svg/>", encoding="utf-8")
        for _ in range(2):  # 같은 세션에서 다시 실행해도 이전 백업을 덮지 않는다
            r = self.backup("0921")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("백업 3항목(파일 3개)", r.stdout)
        dirs = self.backups()
        self.assertEqual(len(dirs), 2)
        for d in dirs:
            names = sorted(unicodedata.normalize("NFC", n) for n in os.listdir(d))
            self.assertEqual(names, ["figures_0921", "복습문제_0921_A.md", "정리노트_0921_A.html"])
            self.assertTrue((d / "figures_0921" / "a.svg").exists())

    def test_backs_up_pack_sources(self):
        # 4단계 조립이 덮어쓰는 manifest.json·stt-summary.md 도 백업한다. 다른 자료_복습팩 파일은 대상이 아니다.
        data = self.notes / "0921" / ".pack" / "자료_복습팩"
        data.mkdir(parents=True)
        (data / "manifest.json").write_text("{}", encoding="utf-8")
        (data / "stt-summary.md").write_text("요약", encoding="utf-8")
        (data / "answers.py").write_text("", encoding="utf-8")
        r = self.backup("0921")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("백업 2항목(파일 2개)", r.stdout)
        [d] = self.backups()
        self.assertEqual(sorted(os.listdir(d / ".pack" / "자료_복습팩")), ["manifest.json", "stt-summary.md"])

    def test_backs_up_dated_folder_layout(self):
        # 새 형식: 복습노트/<range>/ 루트의 HTML·PDF 와 .pack/ 안의 md·그림. 다른 range 폴더는 건드리지 않는다.
        pack = self.notes / "0921"
        (pack / ".pack" / "figures_0921").mkdir(parents=True)
        (pack / ".pack" / "figures_0921" / "a.svg").write_text("<svg/>", encoding="utf-8")
        (pack / "정리노트_0921_A.html").write_text("n", encoding="utf-8")
        (pack / ".pack" / unicodedata.normalize("NFD", "복습문제_0921_A.md")).write_text("r", encoding="utf-8")
        (pack / ".pack" / "자료_PDF").mkdir()
        (pack / ".pack" / "자료_PDF" / "pdf-validation.json").write_text("{}", encoding="utf-8")
        (self.notes / "0923").mkdir()
        (self.notes / "0923" / "정리노트_0923_B.html").write_text("other", encoding="utf-8")
        r = self.backup("0921")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("백업 3항목(파일 3개)", r.stdout)
        (d,) = self.backups()
        names = sorted(unicodedata.normalize("NFC", n) for n in os.listdir(d))
        self.assertEqual(names, [".pack", "정리노트_0921_A.html"])
        names = sorted(unicodedata.normalize("NFC", n) for n in os.listdir(d / ".pack"))
        self.assertEqual(names, ["figures_0921", "복습문제_0921_A.md"])

    def test_bad_range_fails_loudly(self):
        (self.notes / "정리노트_0921_A.html").write_text("n", encoding="utf-8")
        for bad in ("", "<range>", "921"):
            with self.subTest(bad=bad):
                r = self.backup(bad)
                self.assertEqual(r.returncode, 1)
                self.assertIn("백업 중단", r.stderr)
        self.assertEqual(self.backups(), [])


class TestScrollbar(unittest.TestCase):
    """생명과학 bio-interactive 66939ad 와 같은 테마 스크롤바."""

    def check(self, name):
        t = (SKILL / "assets" / name).read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"--scroll: #[0-9a-f]{6}; --scroll-hover: #[0-9a-f]{6};", t)), 3)
        self.assertEqual(t.count("--scroll: #c9d0db; --scroll-hover: #9aa3b2;"), 1)
        self.assertEqual(t.count("--scroll: #3f414b; --scroll-hover: #5b5e6a;"), 2)
        self.assertIn("::-webkit-scrollbar-thumb:hover { background: var(--scroll-hover); }", t)
        self.assertIn("pre::-webkit-scrollbar-thumb { background: var(--scroll); border-radius: 8px; border: 2px solid var(--surface); }", t)
        self.assertIn("scrollbar-color: var(--scroll) transparent;", t)
        self.assertIn("--scrollbar: 16px;", t)
        self.assertNotIn("katex-display, table)", t)

    def test_note_template_scrollbar(self):
        self.check("note-template.html")

    def test_review_template_scrollbar(self):
        self.check("review-template.html")


class TestTraceFigureDocs(unittest.TestCase):
    def test_trace_figures_doc_exists_and_links_resolve(self):
        self.assertTrue((SKILL / "references/trace-figures.md").exists())
        for rel in ("SKILL.md", "references/content-rules.md", "references/widget-rules.md"):
            with self.subTest(doc=rel):
                path = SKILL / rel
                text = path.read_text(encoding="utf-8")
                targets = re.findall(r"\]\(((?:references/)?trace-figures\.md)\)", text)
                self.assertTrue(targets, f"{rel}: trace-figures.md 링크 없음")
                for t in targets:
                    self.assertTrue((path.parent / t).exists(), t)

    def test_content_rules_cap_hand_written_steps(self):
        text = (SKILL / "references/content-rules.md").read_text(encoding="utf-8")
        self.assertIn("4단계까지만", text)

    def test_manifest_and_save_list_mention_trace(self):
        skill = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn('"rules": ["trace-v1", "layout-v2"]', skill)
        self.assertIn("traces/", skill)
        self.assertIn("rules", (SKILL / "references/manifest-guide.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
def test_revision_workflow_requires_full_audit_and_lecture_evidence():
    from _util import SKILL
    guide=(SKILL/'references/review-overhaul.md').read_text(encoding='utf-8')
    assert 'review_audit.py' in guide
    assert 'lecture_ref' in guide
    assert '핵심 범위 충족 우선' in guide
    assert 'revise-existing' in (SKILL/'SKILL.md').read_text(encoding='utf-8')
