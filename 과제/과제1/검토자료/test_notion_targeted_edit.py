# test_notion_targeted_edit.py
import copy
import unittest
from notion_targeted_edit import build_update


def rich(content, **annotations):
    return {"type": "text", "text": {"content": content},
            "annotations": annotations}


class ReplacementTests(unittest.TestCase):
    def test_paragraph_preserves_annotations_and_link(self):
        item = rich("앞: 뒤", bold=True)
        item["text"]["link"] = {"url": "https://example.org"}
        block = {"id": "a", "type": "paragraph", "paragraph": {"rich_text": [item]}}
        original = copy.deepcopy(block)
        body = build_update(block, {"block_id": "a", "type": "paragraph",
                                    "old_text": "앞: 뒤", "new_text": "앞:  뒤"})
        self.assertEqual(body["paragraph"]["rich_text"][0]["text"]["content"], "앞:  뒤")
        self.assertEqual(body["paragraph"]["rich_text"][0]["annotations"], {"bold": True})
        self.assertEqual(body["paragraph"]["rich_text"][0]["text"]["link"],
                         {"url": "https://example.org"})
        self.assertEqual(block, original)

    def test_table_cell_updates_only_selected_cell(self):
        block = {"id": "b", "type": "table_row", "table_row": {"cells": [[rich("other")], [rich("old")]]}}
        body = build_update(block, {"block_id": "b", "type": "table_row",
                                    "cell_index": 1, "old_text": "old", "new_text": "new"})
        self.assertEqual(body["table_row"]["cells"][0][0]["text"]["content"], "other")
        self.assertEqual(body["table_row"]["cells"][1][0]["text"]["content"], "new")

    def test_cross_item_rejected(self):
        block = {"id": "a", "type": "paragraph", "paragraph": {"rich_text": [rich("ab"), rich("cd")]}}
        with self.assertRaisesRegex(ValueError, "one text item"):
            build_update(block, {"block_id": "a", "type": "paragraph",
                                 "old_text": "bc", "new_text": "BC"})

    def test_repeated_phrase_rejected(self):
        block = {"id": "a", "type": "code", "code": {"rich_text": [rich("x x")]}}
        with self.assertRaisesRegex(ValueError, "exactly once"):
            build_update(block, {"block_id": "a", "type": "code",
                                 "old_text": "x", "new_text": "y"})

    def test_bad_cell_index_rejected(self):
        block = {"id": "b", "type": "table_row", "table_row": {"cells": [[rich("x")]]}}
        with self.assertRaisesRegex(ValueError, "cell_index"):
            build_update(block, {"block_id": "b", "type": "table_row",
                                 "cell_index": 2, "old_text": "x", "new_text": "y"})

    def test_code_language_survives(self):
        block = {"id": "c", "type": "code", "code": {"rich_text": [rich("a: ")],
                                                       "language": "c"}}
        body = build_update(block, {"block_id": "c", "type": "code",
                                    "old_text": "a: ", "new_text": "a:  "})
        self.assertEqual(body["code"]["language"], "c")
