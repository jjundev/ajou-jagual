import unittest
import tempfile
from pathlib import Path

from notion_sync import (build_blocks, markdown_from_response, save_pulled_markdown,
                         assert_push_allowed, table_from_columns, locate_function_layout)


class NotionSyncTests(unittest.TestCase):
    def test_function_code_is_exact_text_in_left_column(self):
        source = (
            "# HW1\n\n"
            "## 2. 소스코드 분석\n\n"
            "### 2.1. read_state\n\n"
            "```c\n"
            "#include <stdio.h>\n"
            "int x = 1; // keep this space\n"
            "```\n\n"
            "**기능 명세**\n\n"
            "- 잘못된 입력에서 0을 반환한다.\n\n"
            "**분석**\n\n"
            "- 입력 검사 후 반환한다.\n"
        )
        blocks = build_blocks(source)
        groups = [block for block in blocks if block["type"] == "column_list"]
        self.assertEqual(len(groups), 1)
        columns = groups[0]["column_list"]["children"]
        self.assertEqual(len(columns), 2)
        left = columns[0]["column"]["children"]
        right = columns[1]["column"]["children"]
        self.assertEqual(left[0]["type"], "code")
        text = "".join(item["text"]["content"] for item in left[0]["code"]["rich_text"])
        self.assertEqual(text, "#include <stdio.h>\nint x = 1; // keep this space")
        self.assertEqual(right[0]["paragraph"]["rich_text"][0]["text"]["content"], "기능 명세")
        self.assertEqual(right[1]["type"], "bulleted_list_item")

    def test_table_cells_keep_expected_values(self):
        source = "## 결과\n\n| 과정 | 개수 |\n|---|---:|\n| 예제 1 | 1 |\n"
        table = next(block for block in build_blocks(source) if block["type"] == "table")
        self.assertEqual(table["table"]["table_width"], 2)
        rows = table["table"]["children"]
        self.assertEqual(len(rows), 2)
        values = ["".join(t["text"]["content"] for t in cell)
                  for cell in rows[1]["table_row"]["cells"]]
        self.assertEqual(values, ["예제 1", "1"])

    def test_pull_refuses_truncated_markdown(self):
        with self.assertRaisesRegex(ValueError, "truncated"):
            markdown_from_response({"markdown": "# Partial", "truncated": True,
                                    "unknown_block_ids": []})
        self.assertEqual(markdown_from_response({"markdown": "# Complete\n", "truncated": False,
                                                 "unknown_block_ids": []}), "# Complete\n")

    def test_real_report_produces_six_exact_c_blocks(self):
        root = Path(__file__).resolve().parents[1]
        blocks = build_blocks((root / "보고서.md").read_text())
        groups = [block for block in blocks if block["type"] == "column_list"]
        self.assertEqual(len(groups), 6)
        c_blocks = []
        for group in groups:
            left = group["column_list"]["children"][0]["column"]["children"]
            c_blocks.append("".join(item["text"]["content"]
                                    for item in left[0]["code"]["rich_text"]))
        nonblank = lambda text: [line.rstrip() for line in text.splitlines() if line.strip()]
        self.assertEqual(nonblank("\n".join(c_blocks)), nonblank((root / "HW1.c").read_text()))

    def test_new_pull_backs_up_previous_download_without_overwriting_it(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "notion.md"
            output.write_text("old Notion edit\n")
            backup = save_pulled_markdown("new Notion edit\n", output)
            self.assertEqual(output.read_text(), "new Notion edit\n")
            self.assertEqual(backup.read_text(), "old Notion edit\n")
            self.assertIsNone(save_pulled_markdown("new Notion edit\n", output))
            self.assertEqual(backup.read_text(), "old Notion edit\n")

    def test_push_refuses_to_overwrite_existing_api_synced_page(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text('{"status":"complete"}')
            with self.assertRaisesRegex(RuntimeError, "pull"):
                assert_push_allowed(manifest)

    def test_function_table_preserves_multiline_code_and_analysis(self):
        left = [{"type": "code", "code": {"rich_text": [
            {"type": "text", "plain_text": "int x = 1;\nreturn x;",
             "text": {"content": "int x = 1;\nreturn x;"}}]}}]
        right = [
            {"type": "paragraph", "paragraph": {"rich_text": [
                {"type": "text", "plain_text": "기능 명세", "text": {"content": "기능 명세"}}]}},
            {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [
                {"type": "text", "plain_text": "1을 반환", "text": {"content": "1을 반환"}}]}},
        ]
        table = table_from_columns(left, right)
        self.assertEqual(table["type"], "table")
        self.assertEqual(table["table"]["table_width"], 2)
        rows = table["table"]["children"]
        self.assertEqual(len(rows), 2)
        code_cell, analysis_cell = rows[1]["table_row"]["cells"]
        self.assertEqual("".join(item["text"]["content"] for item in code_cell),
                         "int x = 1;\nreturn x;")
        self.assertEqual("".join(item["text"]["content"] for item in analysis_cell),
                         "기능 명세\n• 1을 반환")

    def test_resumed_layout_finds_inserted_table_before_old_columns(self):
        root = [
            {"id": "heading", "type": "heading_3"},
            {"id": "new-table", "type": "table"},
            {"id": "old-columns", "type": "column_list"},
            {"id": "next", "type": "divider"},
        ]
        table, old = locate_function_layout(root, "heading", "old-columns")
        self.assertEqual(table["id"], "new-table")
        self.assertEqual(old["id"], "old-columns")


if __name__ == "__main__":
    unittest.main()
