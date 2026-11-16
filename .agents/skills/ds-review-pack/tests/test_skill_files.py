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

    def test_followups_start_after_base_publish(self):
        s8 = self._step8()
        publish = s8.index('release_review.py" publish')
        followups = s8.index("references/pack-followups.md")
        self.assertLess(s8.index("references/pdf-build.md"), publish)
        self.assertLess(publish, followups)
        self.assertLess(followups, s8.index("pack_layout.py"))
        self.assertNotIn("ds-concept-check/SKILL.md", s8)

    def test_followup_modes_and_publish_owner(self):
        refs = SKILL / "references"
        contract = (refs / "pack-followups.md").read_text()
        for phrase in ("신규", "병렬", "update-existing", "revise-existing", "bank", "0문항",
                       "메인만 발행", "ready", "withheld", "skipped", "각각", "복습노트"):
            self.assertIn(phrase, contract)
        for name in ("textbook-update.md", "review-overhaul.md"):
            self.assertIn("(pack-followups.md)", (refs / name).read_text())
        self.assertIn("| 확인문제 근거 없음 |", self.text)
        self.assertIn("| 확인문제 검사 실패 |", self.text)
        self.assertIn("- 확인문제:", self.text.split("\n### 9. ", 1)[1])

    def test_blind_relay_contract(self):
        contract = (SKILL / "references/pack-followups.md").read_text().split("## 블라인드 중계", 1)[1]
        for phrase in ("새 컨텍스트", "브리프", "현재 사본", "정리노트 MD", "답안 경로",
                       "이전 답안", "items.json", "r3", "정답"):
            self.assertIn(phrase, contract)
        concept = (SKILL.parent / "ds-concept-check/SKILL.md").read_text()
        self.assertIn("review-request", concept)
        self.assertIn("visual-review.json", concept)
        self.assertIn("두 번째로 높은 모델", concept)

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


def markdown_headings(text):
    """Return indexed ATX headings outside code fences."""
    fence = None
    for index, line in enumerate(text.splitlines()):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            marker, suffix = match.groups()
            if fence is None:
                fence = marker
            elif marker.startswith(fence) and not suffix.strip():
                fence = None
            continue
        if fence is None and (heading := re.fullmatch(r"(#{1,6}) (.+)", line)):
            yield index, len(heading[1]), heading[2]


def test_main_reference_sections_resolve():
    docs = (SKILL_MD, *(SKILL / "references" / name for name in ("textbook-update.md", "review-overhaul.md")))
    links = set()
    for doc in docs:
        for line in doc.read_text(encoding="utf-8").splitlines():
            if "메인 읽기" not in line:
                continue
            for title, relative in re.findall(r"\[([^\]]+)\]\(((?:references/)?[\w-]+\.md)\)", line):
                target = doc.parent / relative
                headings = list(markdown_headings(target.read_text(encoding="utf-8")))
                assert sum(name == title for _, _, name in headings) == 1, (target.name, title)
                links.add((target.name, title))
    assert {
        ("bank-build.md", "원본 표"),
        ("problem-selection.md", "후보 추출"),
        ("problem-selection.md", "문항 원문 모으기"),
        ("manifest-guide.md", "검증"),
        ("widget-rules.md", "언제"),
        ("browser-check.md", "검사 요청과 결과"),
        ("browser-check.md", "서버"),
        ("pdf-build.md", "생성과 기계 검사"),
        ("pdf-build.md", "쪽별 실화면 검토"),
        ("pdf-build.md", "발행"),
        ("pack-followups.md", "준비"),
        ("pack-followups.md", "병렬 시작"),
        ("pack-followups.md", "블라인드 중계"),
        ("pack-followups.md", "발행"),
        ("textbook-update.md", "준비·선별"),
        ("textbook-update.md", "작성·검증"),
        ("textbook-update.md", "발행·보고"),
        ("review-overhaul.md", "Stage와 전역 검사"),
        ("review-overhaul.md", "개편 기계 검사"),
        ("review-overhaul.md", "새 날짜의 감사 입력"),
    } <= links
    selection = (SKILL / "references/problem-selection.md").read_text(encoding="utf-8")
    headings = list(markdown_headings(selection))
    index = next(i for i, (_, _, title) in enumerate(headings) if title == "문항 원문 모으기")
    start, level, _ = headings[index]
    end, _, next_title = next(item for item in headings[index + 1:] if item[1] <= level)
    assert next_title == "정답"
    assert "## <은행 문항 id>" in "\n".join(selection.splitlines()[start:end])
    overhaul = (SKILL / "references/review-overhaul.md").read_text(encoding="utf-8")
    normal_audit = overhaul.split("## Stage와 전역 검사\n", 1)[1].split("\n## ", 1)[0]
    assert "check_html.py" not in normal_audit and "audit-repo" not in normal_audit


def test_run_report_commands_by_mode():
    skill = SKILL_MD.read_text(encoding="utf-8")
    bank = skill.split("### B4. ", 1)[1].split("## 복습팩 절차", 1)[0]
    prepare = skill.split("### 0. ", 1)[1].split("### 1. ", 1)[0]
    preview = skill.split("### 1. ", 1)[1].split("### 2. ", 1)[0]
    manifest = skill.split("### 2. ", 1)[1].split("### 3. ", 1)[0]
    assert 'validate "$RUN/bank.json" --out "$RUN/bank-validation.json"' in bank
    assert 'validate "$BANK" --out "$RUN/bank-validation.json"' in prepare
    assert prepare.index('mkdir -p "$RUN"') < prepare.index('validate "$BANK"')
    assert "candidates-preview.json" in preview and "candidates.json" in manifest
    refs = SKILL / "references"
    selection = (refs / "problem-selection.md").read_text(encoding="utf-8")
    assert 'select "$BANK"' in selection and '--out "$RUN/$CANDIDATE_REPORT"' in selection
    for filename in ("manifest-guide.md", "textbook-update.md", "review-overhaul.md"):
        guide = (refs / filename).read_text(encoding="utf-8")
        assert "check-manifest" in guide and "bank-manifest-check.json" in guide
    assert 'validate "$BANK" --out "$PACK_RUN/bank-validation.json"' in (
        refs / "textbook-update.md").read_text(encoding="utf-8")
    common = (refs / "review-overhaul.md").read_text(encoding="utf-8")
    assert '--out "$RUN/audit.json"' in common
    assert all(word in common for word in ("`blocking`", "`candidates`", "`status=pass`"))
    assert "보고서 저장 실패" in skill and "이전 보고서" in skill


def test_existing_modes_use_manifest_bound_html_checks():
    for filename in ("textbook-update.md", "review-overhaul.md"):
        guide = (SKILL / "references" / filename).read_text(encoding="utf-8")
        assert 'check_html.py" --manifest "$MANIFEST" --note "$NOTE" --review "$REVIEW"' in guide, filename
        assert 'manifest.py" "$MANIFEST"' in guide, filename
