"""bank.py: 문제은행 스키마 검사, 후보 선별, manifest 출처 대조."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unicodedata
import unittest

from _util import SCRIPTS

import bank


def P(pid, chapters, type_, duplicate_of=None):
    source, number = pid.rsplit("-q", 1)
    return {"id": pid, "source": source, "number": number, "chapters": chapters, "type": type_,
            "points": 4, "text": f"{pid} 문제", "figure": None, "answer": "1", "answer_origin": "key",
            "duplicate_of": duplicate_of}


def S(sid, year, professor, transcribed_from, reviewed=True):
    return {"id": sid, "file": f"{sid}.pdf", "year": year, "exam": "기말", "professor": professor,
            "has_key": True, "transcribed_from": transcribed_from, "reviewed": reviewed}


def make_notes(root):
    """0921 팩(2016-final-ljw-q1)과 0923 팩(2019-mid-q8)이 든 복습노트 폴더."""
    notes = root / "복습노트"
    (notes / "0921").mkdir(parents=True)
    (notes / "0923").mkdir()
    (notes / "0921" / "복습문제_0921_Recursion.html").write_text(
        '<article class="card" data-source="2016-final-ljw-q1">', encoding="utf-8")
    (notes / "0923" / "복습문제_0923_Stack.html").write_text(
        '<article class="card" data-source="2019-mid-q8">', encoding="utf-8")
    return notes


def mini_bank():
    return {"version": 1,
            "sources": [S("2016-final-ljw", 2016, "이정원", "photo"),
                        S("2019-mid", 2019, "미상", "txt"),
                        S("2017-final-kdh", 2017, "김도희", "text"),
                        S("2015-ljw", 2015, "이정원", "scan", reviewed=False),
                        S("2021-mock1", 2021, "미상", "text"),
                        S("unk-final-ltk", None, "이태권", "text")],
            "problems": [P("2016-final-ljw-q1", [2], "trace"),
                         P("2016-final-ljw-q2", [2, 5], "trace"),  # 5장을 아직 안 배움
                         P("2019-mid-q8", [2], "code-read"),
                         P("2019-mid-q1", [2], "ox"),
                         P("2019-mid-q2", [2], "ox"),
                         P("2019-mid-q3", [2], "ox"),  # OX 셋째라 잘림
                         P("2017-final-kdh-q4", [1, 2], "short"),
                         P("2019-mid-q9", [1], "short"),  # 이번 범위(2장)와 안 겹침
                         P("2015-ljw-q1", [2], "trace"),  # 검수 전 원본
                         P("2021-mock1-q1", [2], "trace", duplicate_of="2016-final-ljw-q1"),
                         P("unk-final-ltk-q2", [2], "trace")]}


EXPECTED = ["2016-final-ljw-q1", "2019-mid-q8", "2019-mid-q1", "2019-mid-q2", "unk-final-ltk-q2",
            "2017-final-kdh-q4"]


class TestValidate(unittest.TestCase):
    def test_mini_bank_is_valid(self):
        self.assertEqual(bank.validate(mini_bank()), [])

    def test_bad_chapter(self):
        b = mini_bank()
        b["problems"][0]["chapters"] = [13]
        self.assertTrue(any(e.startswith("problems[0].chapters") for e in bank.validate(b)))

    def test_bool_is_not_a_chapter(self):
        b = mini_bank()
        b["problems"][0]["chapters"] = [True]
        self.assertTrue(any(e.startswith("problems[0].chapters") for e in bank.validate(b)))

    def test_id_must_match_source_and_number(self):
        b = mini_bank()
        b["problems"][0]["id"] = "2016-final-ljw-q9"
        self.assertTrue(any(e.startswith("problems[0].id") for e in bank.validate(b)))

    def test_duplicate_problem_id(self):
        b = mini_bank()
        b["problems"].append(dict(b["problems"][0]))
        self.assertIn("problems[11].id: 중복: 2016-final-ljw-q1", bank.validate(b))

    def test_unknown_type_and_origin(self):
        b = mini_bank()
        b["problems"][0]["type"] = "tree"
        b["sources"][0]["transcribed_from"] = "fax"
        errors = bank.validate(b)
        self.assertTrue(any(e.startswith("problems[0].type") for e in errors))
        self.assertTrue(any(e.startswith("sources[0].transcribed_from") for e in errors))

    def test_missing_field(self):
        b = mini_bank()
        del b["sources"][0]["reviewed"]
        self.assertIn("sources[0].reviewed: 없음", bank.validate(b))

    def test_duplicate_of_must_point_to_an_original(self):
        b = mini_bank()
        b["problems"][0]["duplicate_of"] = "2021-mock1-q1"  # 2021-mock1-q1도 중복 문항
        self.assertTrue(any(e.startswith("problems[0].duplicate_of") for e in bank.validate(b)))

    def test_unknown_duplicate_target(self):
        b = mini_bank()
        b["problems"][1]["duplicate_of"] = "nope-q1"
        self.assertIn("problems[1].duplicate_of: 없는 문항: nope-q1", bank.validate(b))

    def test_load_reports_json_error(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bank.json"
            p.write_text("{", encoding="utf-8")
            with self.assertRaises(bank.BankError) as cm:
                bank.load(p)
            self.assertIn("JSON 형식 오류", str(cm.exception))


class TestSelect(unittest.TestCase):
    def ids(self, b=None, used=frozenset()):
        return [q["id"] for q in bank.select(b or mini_bank(), {2}, {1, 2}, used)]

    def test_order_and_filters(self):
        self.assertEqual(self.ids(), EXPECTED)

    def test_used_are_skipped(self):
        self.assertEqual(self.ids(used={"2016-final-ljw-q1"}), EXPECTED[1:])

    def test_reviewed_source_becomes_eligible(self):
        b = mini_bank()
        b["sources"][3]["reviewed"] = True
        self.assertEqual(self.ids(b)[:2], ["2016-final-ljw-q1", "2015-ljw-q1"])

    def test_parse_chapters(self):
        self.assertEqual(bank.parse_chapters("1-3,5"), {1, 2, 3, 5})
        for bad in ("0", "3-1", "a", "", "13"):
            with self.subTest(bad=bad), self.assertRaises(bank.BankError):
                bank.parse_chapters(bad)

    def test_used_sources_reads_review_pages_only(self):
        with tempfile.TemporaryDirectory() as d:
            notes = Path(d) / "복습노트"
            (notes / "0921").mkdir(parents=True)
            (notes / "0923").mkdir()
            (notes / "0921" / "복습문제_0921_Recursion.html").write_text(
                '<article class="card" data-source="2016-final-ljw-q1">', encoding="utf-8")
            (notes / "0923" / unicodedata.normalize("NFD", "복습문제_0923_Stack.html")).write_text(
                '<article class="card" data-source="2019-mid-q8">', encoding="utf-8")
            (notes / "0921" / "정리노트_0921_Recursion.html").write_text(
                '<div data-source="2019-mid-q1">', encoding="utf-8")
            self.assertEqual(bank.used_sources(notes), {"2016-final-ljw-q1", "2019-mid-q8"})
            self.assertEqual(bank.used_sources(Path(d) / "없음"), set())

    def test_used_sources_skips_this_range(self):
        with tempfile.TemporaryDirectory() as d:
            notes = make_notes(Path(d))
            self.assertEqual(bank.used_sources(notes, skip_range="0921"), {"2019-mid-q8"})


class TestCheckManifest(unittest.TestCase):
    def errors(self, *items):
        m = {"problems": [{"id": f"p{i + 1}", "source": s, "variant": v} for i, (s, v) in enumerate(items)]}
        return bank.check_manifest(mini_bank(), m)

    def test_ok_with_variant_of_same_problem(self):
        self.assertEqual(self.errors(("2016-final-ljw-q1", False), ("2016-final-ljw-q1", True),
                                     ("2019-mid-q8", False)), [])

    def test_unknown_source(self):
        self.assertEqual(self.errors(("nope-q1", False)), ["problems[0].source: 은행에 없는 문항: 'nope-q1'"])

    def test_duplicate_problem_must_use_original(self):
        self.assertIn("원 문항 2016-final-ljw-q1", self.errors(("2021-mock1-q1", False))[0])

    def test_unreviewed_source(self):
        self.assertIn("검수 전 원본", self.errors(("2015-ljw-q1", False))[0])

    def test_same_problem_twice(self):
        self.assertIn("같은 문항이 두 번", self.errors(("2019-mid-q8", False), ("2019-mid-q8", False))[0])


class TestCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.bank = self.tmp / "bank.json"
        self.bank.write_text(json.dumps(mini_bank(), ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "bank.py"), *map(str, args)],
                              capture_output=True, text=True)

    def test_validate(self):
        r = self.run_cli("validate", self.bank)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "OK: 원본 6개, 문항 11개")

    def test_validate_broken_bank(self):
        self.bank.write_text(json.dumps({"version": 2, "sources": [], "problems": []}), encoding="utf-8")
        r = self.run_cli("validate", self.bank)
        self.assertEqual(r.returncode, 1)
        self.assertIn("version", r.stderr)

    def test_select(self):
        r = self.run_cli("select", self.bank, "--range-ch", "2", "--taught", "1-2")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertEqual(lines[0], "id\t출제자\t유형\t챕터\t정답출처")
        self.assertEqual(lines[1], "2016-final-ljw-q1\t이정원\ttrace\t2\tkey")
        self.assertEqual(len(lines), 1 + len(EXPECTED))

    def test_select_this_range_keeps_own_problems(self):
        notes = make_notes(self.tmp)
        r = self.run_cli("select", self.bank, "--range-ch", "2", "--taught", "1-2",
                         "--used-dir", notes, "--this-range", "0921")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertEqual(lines[1].split("\t")[0], "2016-final-ljw-q1")
        self.assertNotIn("2019-mid-q8", r.stdout)

    def test_check_manifest(self):
        m = self.tmp / "manifest.json"
        m.write_text(json.dumps({"problems": [{"id": "p1", "source": "nope-q1", "variant": False}]}), encoding="utf-8")
        r = self.run_cli("check-manifest", self.bank, m)
        self.assertEqual(r.returncode, 1)
        self.assertIn("은행에 없는 문항", r.stdout)


if __name__ == "__main__":
    unittest.main()
