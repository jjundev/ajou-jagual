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

    def test_smushed_prompts_fires_on_run_from_captured_output(self):
        text = (
            "```plain text\n"
            "프로세스의 수를 입력하세요. (1~8): 자원의 종류의 개수를 입력하세요. (0~5):\n"
            "Need matrix:\n"
            "```\n"
        )
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertIn("output-block-smushed-prompts", names)

    def test_smushed_prompts_fires_regardless_of_fence_language(self):
        for lang in ("", "text", "c", "plain text"):
            text = f"```{lang}\nX를 입력하세요: Y를 입력하세요:\n```\n"
            names = [n for n, _, _ in report_md.style_signals(text)]
            self.assertIn("output-block-smushed-prompts", names, lang)

    def test_smushed_prompts_quiet_with_interleaved_input(self):
        text = "```plain text\n프로세스의 수를 입력하세요. (1~8): 2\n자원의 종류를 입력하세요. (0~5): 2\n```\n"
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertNotIn("output-block-smushed-prompts", names)

    def test_caption_duplication_fires_when_all_three_captions_equal(self):
        text = (
            "![동일한 캡션 문구입니다](https://example.com/a.png)\n"
            "![동일한 캡션 문구입니다](https://example.com/a.png)\n"
            "![동일한 캡션 문구입니다](https://example.com/a.png)\n"
        )
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertIn("caption-duplication", names)

    def test_caption_duplication_needs_three_images(self):
        text = "![동일한 캡션 문구입니다](https://example.com/a.png)\n![동일한 캡션 문구입니다](https://example.com/b.png)\n"
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertNotIn("caption-duplication", names)

    def test_caption_duplication_quiet_when_captions_differ(self):
        text = (
            "![사례 1 설명 push](https://example.com/a.png)\n"
            "![사례 2 설명 pop](https://example.com/b.png)\n"
            "![사례 3 설명 idle](https://example.com/c.png)\n"
        )
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertNotIn("caption-duplication", names)

    def test_cell_prefix_repetition_fires_on_uniform_intro(self):
        header = "<tr>\n<td>소스코드</td>\n<td>기능 명세와 분석</td>\n</tr>"
        body = "\n".join(
            f"<tr>\n<td>void f{i}(void);</td>\n<td>인자: 없음. 반환값: 없음. 변경 상태: 없음.</td>\n</tr>"
            for i in range(5)
        )
        text = f"<table>\n{header}\n{body}\n</table>\n"
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertIn("cell-prefix-repetition", names)

    def test_cell_prefix_matches_after_escape_strip(self):
        header = "<tr>\n<td>소스코드</td>\n<td>기능 명세와 분석</td>\n</tr>"
        body = "\n".join(
            f"<tr>\n<td>#define X{i} 1</td>\n<td>\\#기능 명세 X{i} 상한이다.</td>\n</tr>"
            for i in range(4)
        )
        text = f"<table>\n{header}\n{body}\n</table>\n"
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertIn("cell-prefix-repetition", names)

    def test_out_of_scope_vocabulary_fires_with_three_hits(self):
        text = "최악은 O(n)이다. 정의되지 않은 동작이다. Best-Fit과 다르다. MSVC 경고."
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertIn("out-of-scope-vocabulary", names)

    def test_out_of_scope_vocabulary_quiet_below_threshold(self):
        text = "최악은 O(n)이다. 다른 내용은 평범하다."
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertNotIn("out-of-scope-vocabulary", names)

    def test_no_personal_voice_fires_on_prose_without_markers(self):
        text = "함수는 1을 반환한다. 성공하면 상태가 바뀐다. 실패하면 유지한다." * 8
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertIn("no-personal-voice", names)

    def test_no_personal_voice_quiet_when_any_marker_present(self):
        text = "함수는 1을 반환한다. 처음에 헷갈렸다. 이후 수정했다." * 8
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertNotIn("no-personal-voice", names)

    def test_no_personal_voice_quiet_on_short_text(self):
        text = "짧다."
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertNotIn("no-personal-voice", names)

    def test_cell_prefix_quiet_when_intros_vary(self):
        bodies = [
            "인자: 없음. 반환값: 없음.",
            "인자: 큐. 반환값: 1.",
            "front == rear 이면 비었다고 본다.",
            "top == -1 이면 1을 반환한다.",
        ]
        header = "<tr>\n<td>소스코드</td>\n<td>기능 명세와 분석</td>\n</tr>"
        rows = "\n".join(f"<tr>\n<td>f{i}();</td>\n<td>{b}</td>\n</tr>" for i, b in enumerate(bodies))
        text = f"<table>\n{header}\n{rows}\n</table>\n"
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertNotIn("cell-prefix-repetition", names)


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
