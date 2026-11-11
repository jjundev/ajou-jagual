import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import report_md  # noqa: E402

URL = "https://prod-files-secure.s3.us-west-2.amazonaws.com/a/b/case-01.png?X-Amz-Date=20261029T022949Z&X-Amz-Expires=3600&X-Amz-Security-Token=TOKEN"

BASE = f"""<table_of_contents color="gray"/>
# 소스코드 분석
## 헤더
<table header-row="true">
<colgroup>
<col width="600">
<col width="400">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>#include \\<stdio.h\\><br>int x = a \\< b;</td>
<td>stdio.h는 printf 때문에 포함했다. 0으로 초기화한 값이 같은 셈이다.</td>
</tr>
</table>
## 공식 예시
**실제 출력**
```plain text
T  1 P 1 R 2 Q 1
```
![T2에 끝난다.]({URL})
# 전체 소스코드
```c
#include <stdio.h>
int main(void)
{{
    return 0;
}}
```
"""


class ProseTests(unittest.TestCase):
    def test_code_cells_and_blocks_are_excluded(self):
        lines = report_md.prose_lines(BASE)
        text = "\n".join(t for _, t in lines)
        self.assertIn("stdio.h는 printf 때문에 포함했다.", text)
        self.assertNotIn("#include", text)
        self.assertNotIn("T  1 P 1", text)
        self.assertNotIn("return 0", text)

    def test_image_url_is_masked_but_alt_kept(self):
        text = "\n".join(t for _, t in report_md.prose_lines(BASE))
        self.assertIn("![T2에 끝난다.](URL)", text)
        self.assertNotIn("amazonaws", text)

    def test_paragraph_breaks_in_cells_stay_visible(self):
        text = "<table>\n<tr>\n<td>앞 문단.<br><br>프로세스가 다 돈 경우.<br><br>뒤 문단.</td>\n</tr>\n</table>\n"
        self.assertEqual(
            report_md.prose_lines(text),
            [(3, "앞 문단. ¶ 프로세스가 다 돈 경우. ¶ 뒤 문단.")],
        )

    def test_line_numbers_point_to_source_lines(self):
        src = BASE.splitlines()
        for number, text in report_md.prose_lines(BASE):
            if "셈이다" in text:
                self.assertIn("셈이다", src[number - 1])
                break
        else:
            self.fail("prose line missing")


class ProtectedSpanTests(unittest.TestCase):
    def test_alt_text_and_prose_edits_pass(self):
        after = BASE.replace("![T2에 끝난다.]", "![T3에 끝난다.]").replace("같은 셈이다", "같다")
        self.assertEqual(report_md.compare_protected(BASE, after), [])

    def test_escaped_angle_bracket_in_code_cell_is_preserved(self):
        spans = report_md.protected_spans(BASE)
        self.assertTrue(any("\\<stdio.h\\>" in cell for cell in spans["code cells"]))
        after = BASE.replace("\\<stdio.h\\>", "stdio.h")
        self.assertIn("code cells", [area for area, _ in report_md.compare_protected(BASE, after)])

    def test_url_change_fails(self):
        after = BASE.replace("TOKEN", "TOKEX")
        self.assertEqual([a for a, _ in report_md.compare_protected(BASE, after)], ["image URLs"])

    def test_code_block_change_fails(self):
        after = BASE.replace("return 0;", "return 1;")
        self.assertIn("code blocks", [a for a, _ in report_md.compare_protected(BASE, after)])

    def test_missing_td_fails(self):
        after = BASE.replace("<td>기능 명세와 분석</td>\n", "", 1)
        self.assertIn("table structure", [a for a, _ in report_md.compare_protected(BASE, after)])

    def test_heading_change_fails(self):
        after = BASE.replace("## 공식 예시", "## 공식 예제")
        self.assertIn("headings", [a for a, _ in report_md.compare_protected(BASE, after)])


class GitRevisionTests(unittest.TestCase):
    def test_check_reads_revision_relative_to_repo_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / "과제" / "과제3" / "보고서_노션.md"
            report.parent.mkdir(parents=True)
            report.write_text(BASE, encoding="utf-8")
            git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(git + ["commit", "-qm", "base"], cwd=root, check=True)
            report.write_text(BASE.replace("같은 셈이다", "같다"), encoding="utf-8")
            # Run from a different directory than the repo root on purpose.
            self.assertEqual(report_md.read_before("HEAD", report), BASE)
            report.write_text(BASE.replace("TOKEN", "TOKEX"), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(Path(report_md.__file__)), "check", str(report), "--before", "HEAD"],
                cwd=report.parent, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("image URLs", result.stdout)


class CodeCompareTests(unittest.TestCase):
    def test_format_only_difference(self):
        source = "#include <stdio.h>\n\nint main(void) {\n  return 0;\n}\n"
        result = report_md.code_compare(BASE, source)
        self.assertTrue(result["tokens_equal"])
        self.assertTrue(result["format_differs"])

    def test_token_difference(self):
        source = "#include <stdio.h>\nint main(void)\n{\n    return 1;\n}\n"
        result = report_md.code_compare(BASE, source)
        self.assertFalse(result["tokens_equal"])

    def test_blank_lines_alone_are_not_a_difference(self):
        source = "#include <stdio.h>\n\nint main(void)\n{\n\n    return 0;\n}\n"
        result = report_md.code_compare(BASE, source)
        self.assertTrue(result["tokens_equal"])
        self.assertFalse(result["format_differs"])


class WarningTests(unittest.TestCase):
    def test_signed_url_warning(self):
        warnings = report_md.url_warnings(BASE)
        self.assertEqual(len(warnings), 1)
        self.assertIn("20261029", warnings[0])


class SignalTests(unittest.TestCase):
    def test_signals_on_empty_file_exits_zero(self):
        self.assertEqual(
            [r for r in report_md.style_signals("") if r[1] != "skipped"],
            [],
        )

    def test_run_script_trace_fires_on_exit_status_and_run_command(self):
        text = "실행:\n```plain text\n$ ./run 01\nALLOC P1 20: SUCCESS\nEXIT_STATUS: 0\n```\n"
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertIn("run-script-trace", names)

    def test_run_script_trace_quiet_on_plain_run(self):
        text = "실행:\n```plain text\n$ ./HW2\nALLOC P1 20: SUCCESS\n```\n"
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertNotIn("run-script-trace", names)


class ReviewFocusTests(unittest.TestCase):
    def test_signals_cli_on_empty_file_exits_zero(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write("")
            path = fh.name
        result = subprocess.run(
            [sys.executable, str(Path(report_md.__file__)), "signals", path],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
