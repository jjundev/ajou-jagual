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


import tempfile
from pathlib import Path
from notion_targeted_edit import apply_edits


class FakeAPI:
    def __init__(self, blocks, member_ids=None, fail_patch=False):
        self.blocks = copy.deepcopy(blocks)
        self.member_ids = set(member_ids or blocks)
        self.fail_patch = fail_patch
        self.patches = []

    def tree(self, page_id):
        return [copy.deepcopy(self.blocks[key]) for key in self.member_ids]

    def request(self, method, path, body=None):
        if method == "GET" and path.endswith("/markdown"):
            return {"markdown": "# snapshot\n", "truncated": False, "unknown_block_ids": []}
        key = path.removeprefix("blocks/")
        if method == "GET":
            return copy.deepcopy(self.blocks[key])
        self.patches.append((key, copy.deepcopy(body)))
        if self.fail_patch:
            raise TimeoutError("response lost")
        kind = self.blocks[key]["type"]
        self.blocks[key][kind].update(copy.deepcopy(body[kind]))
        self.blocks[key]["last_edited_time"] = "after"
        return copy.deepcopy(self.blocks[key])


def block(key, value="old"):
    return {"id": key, "type": "paragraph", "last_edited_time": "before",
            "paragraph": {"rich_text": [rich(value)]}}


class ApplyTests(unittest.TestCase):
    def test_foreign_block(self):
        api = FakeAPI({"a": block("a"), "foreign": block("foreign")}, {"a"})
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "outside"):
                apply_edits(api, [{"block_id": "foreign", "type": "paragraph",
                                   "old_text": "old", "new_text": "new"}], Path(directory))
        self.assertEqual(api.patches, [])

    def test_stale_batch(self):
        api = FakeAPI({"a": block("a"), "b": block("b", "changed")})
        edits = [{"block_id": key, "type": "paragraph", "old_text": "old", "new_text": "new"}
                 for key in ("a", "b")]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "exactly once"):
                apply_edits(api, edits, Path(directory))
        self.assertEqual(api.patches, [])

    def test_uncertain_patch(self):
        api = FakeAPI({"a": block("a")}, fail_patch=True)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "uncertain"):
                apply_edits(api, [{"block_id": "a", "type": "paragraph",
                                   "old_text": "old", "new_text": "new"}], Path(directory))
            self.assertTrue(list(Path(directory).glob("before-targeted-*.json")))
        self.assertEqual(len(api.patches), 1)

    def test_concurrent_change(self):
        class ChangingAPI(FakeAPI):
            def request(self, method, path, body=None):
                if method == "GET" and path == "blocks/a":
                    self.gets = getattr(self, "gets", 0) + 1
                    if self.gets == 2:
                        self.blocks["a"]["last_edited_time"] = "someone-else"
                return super().request(method, path, body)
        api = ChangingAPI({"a": block("a")})
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "changed"):
                apply_edits(api, [{"block_id": "a", "type": "paragraph",
                                   "old_text": "old", "new_text": "new"}], Path(directory))
        self.assertEqual(api.patches, [])

    def test_success_reads_back(self):
        api = FakeAPI({"a": block("a")})
        with tempfile.TemporaryDirectory() as directory:
            done = apply_edits(api, [{"block_id": "a", "type": "paragraph",
                                      "old_text": "old", "new_text": "new"}], Path(directory))
            self.assertEqual(done, ["a"])
            self.assertTrue(list(Path(directory).glob("before-targeted-*.md")))
        self.assertEqual(api.blocks["a"]["paragraph"]["rich_text"][0]["text"]["content"], "new")
