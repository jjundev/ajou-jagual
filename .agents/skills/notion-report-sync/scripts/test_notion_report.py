import copy
import json
import unittest
from notion_report import build_update


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


NB = " "


def code_row(content):
    return {"id": "r", "type": "table_row",
            "table_row": {"cells": [[rich(content)], [rich("설명")]]}}


def code_edit(old, new):
    return {"block_id": "r", "type": "table_row", "cell_index": 0,
            "old_text": old, "new_text": new}


class NbspIndentTests(unittest.TestCase):
    def test_space_indented_plan_matches_nbsp_cell_and_keeps_nbsp(self):
        block = code_row(f"int f(void) {{\n{NB*2}return 0;\n}}")
        body = build_update(block, code_edit("\n  return 0;", "\n  return 1;\n  /* x */"))
        self.assertEqual(body["table_row"]["cells"][0][0]["text"]["content"],
                         f"int f(void) {{\n{NB*2}return 1;\n{NB*2}/* x */\n}}")

    def test_cell_without_nbsp_indent_keeps_ascii_spaces(self):
        block = code_row("a\n  b")
        body = build_update(block, code_edit("\n  b", "\n  c"))
        self.assertEqual(body["table_row"]["cells"][0][0]["text"]["content"], "a\n  c")

    def test_mid_line_spaces_are_not_converted(self):
        block = code_row(f"x\n{NB*2}a = 1;")
        body = build_update(block, code_edit("a = 1;", "a  =  2;"))
        self.assertEqual(body["table_row"]["cells"][0][0]["text"]["content"],
                         f"x\n{NB*2}a  =  2;")

    def test_raw_and_converted_matches_at_different_places_rejected(self):
        block = code_row(f"x\n{NB*2}y\n  y")
        with self.assertRaisesRegex(ValueError, "exactly once"):
            build_update(block, code_edit("\n  y", "\n  z"))


import tempfile
from pathlib import Path
from notion_report import apply_edits


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
                apply_edits(api, "page-a", [{"block_id": "foreign", "type": "paragraph",
                                   "old_text": "old", "new_text": "new"}], Path(directory))
        self.assertEqual(api.patches, [])

    def test_stale_batch(self):
        api = FakeAPI({"a": block("a"), "b": block("b", "changed")})
        edits = [{"block_id": key, "type": "paragraph", "old_text": "old", "new_text": "new"}
                 for key in ("a", "b")]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "exactly once"):
                apply_edits(api, "page-a", edits, Path(directory))
        self.assertEqual(api.patches, [])

    def test_uncertain_patch(self):
        api = FakeAPI({"a": block("a")}, fail_patch=True)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "uncertain"):
                apply_edits(api, "page-a", [{"block_id": "a", "type": "paragraph",
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
                apply_edits(api, "page-a", [{"block_id": "a", "type": "paragraph",
                                   "old_text": "old", "new_text": "new"}], Path(directory))
        self.assertEqual(api.patches, [])

    def test_success_reads_back(self):
        api = FakeAPI({"a": block("a")})
        with tempfile.TemporaryDirectory() as directory:
            done = apply_edits(api, "page-a", [{"block_id": "a", "type": "paragraph",
                                      "old_text": "old", "new_text": "new"}], Path(directory))
            self.assertEqual(done, ["a"])
            self.assertTrue(list(Path(directory).glob("before-targeted-*.md")))
        self.assertEqual(api.blocks["a"]["paragraph"]["rich_text"][0]["text"]["content"], "new")

class RecoveryTests(unittest.TestCase):
    def test_backup_records_exact_individual_preflight_block(self):
        class ChangedBetweenReads(FakeAPI):
            def tree(self, page_id):
                snapshot = super().tree(page_id)
                self.blocks["a"]["paragraph"]["rich_text"][0]["text"]["content"] = "prefix old"
                return snapshot

        api = ChangedBetweenReads({"a": block("a")})
        with tempfile.TemporaryDirectory() as directory:
            apply_edits(api, "page-a", [{"block_id": "a", "type": "paragraph",
                               "old_text": "old", "new_text": "new"}], Path(directory))
            backup = json.loads(next(Path(directory).glob("before-targeted-*.json")).read_text())
            self.assertEqual(backup["blocks"]["a"]["paragraph"]["rich_text"][0]["text"]["content"],
                             "prefix old")

    def test_recovery_get_failure_reports_partial_completion(self):
        class LostConnection(FakeAPI):
            def request(self, method, path, body=None):
                if method == "PATCH" and path == "blocks/b":
                    self.patches.append(("b", copy.deepcopy(body)))
                    raise TimeoutError("response lost")
                if method == "GET" and path == "blocks/b":
                    self.b_reads = getattr(self, "b_reads", 0) + 1
                    if self.b_reads == 3:
                        raise ConnectionError("network unavailable")
                return super().request(method, path, body)

        api = LostConnection({"a": block("a"), "b": block("b")})
        edits = [{"block_id": key, "type": "paragraph", "old_text": "old", "new_text": "new"}
                 for key in ("a", "b")]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, r"PATCH uncertain for b.*completed=\['a'\].*recovery GET failed"):
                apply_edits(api, "page-a", edits, Path(directory))
        self.assertEqual(len(api.patches), 2)

    def test_prepatch_get_failure_reports_partial_completion(self):
        class LostRead(FakeAPI):
            def request(self, method, path, body=None):
                if method == "GET" and path == "blocks/b" and self.patches:
                    raise ConnectionError("network unavailable")
                return super().request(method, path, body)

        api = LostRead({"a": block("a"), "b": block("b")})
        edits = [{"block_id": key, "type": "paragraph", "old_text": "old", "new_text": "new"}
                 for key in ("a", "b")]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, r"Pre-PATCH GET failed for b.*completed=\['a'\]"):
                apply_edits(api, "page-a", edits, Path(directory))
        self.assertEqual(len(api.patches), 1)

    def test_timeout_after_application_reports_observed_expected_state(self):
        class AppliedThenLost(FakeAPI):
            def request(self, method, path, body=None):
                if method == "PATCH":
                    super().request(method, path, body)
                    raise TimeoutError("response lost")
                return super().request(method, path, body)

        api = AppliedThenLost({"a": block("a")})
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "state=matches expected"):
                apply_edits(api, "page-a", [{"block_id": "a", "type": "paragraph",
                                   "old_text": "old", "new_text": "new"}], Path(directory))
            observed = list(Path(directory).glob("uncertain-a-*.json"))
            self.assertEqual(len(observed), 1)
            self.assertEqual(json.loads(observed[0].read_text())["paragraph"]["rich_text"][0]["text"]["content"],
                             "new")

    def test_timeout_after_divergent_type_reports_state(self):
        class DivergedThenLost(FakeAPI):
            def request(self, method, path, body=None):
                if method == "PATCH":
                    self.patches.append((path, copy.deepcopy(body)))
                    self.blocks["a"]["type"] = "heading_2"
                    self.blocks["a"]["heading_2"] = {"rich_text": [rich("someone else's heading")]}
                    raise TimeoutError("response lost")
                return super().request(method, path, body)

        api = DivergedThenLost({"a": block("a")})
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "state=diverged"):
                apply_edits(api, "page-a", [{"block_id": "a", "type": "paragraph",
                                   "old_text": "old", "new_text": "new"}], Path(directory))

class ReuseTests(unittest.TestCase):
    def test_edits_use_selected_page_instead_of_hw1_constant(self):
        class PageAwareAPI(FakeAPI):
            def tree(self, page_id):
                if page_id != "another-page":
                    raise AssertionError(f"wrong page: {page_id}")
                return super().tree(page_id)

            def request(self, method, path, body=None):
                if path.startswith("pages/") and path != "pages/another-page/markdown":
                    raise AssertionError(f"wrong page: {path}")
                return super().request(method, path, body)

        api = PageAwareAPI({"a": block("a")})
        with tempfile.TemporaryDirectory() as directory:
            done = apply_edits(api, "another-page", [{"block_id": "a", "type": "paragraph",
                                                      "old_text": "old", "new_text": "new"}], Path(directory))
        self.assertEqual(done, ["a"])

class PullReuseTests(unittest.TestCase):
    def test_pull_selected_page_backs_up_and_compares_without_overwriting_source(self):
        from notion_report import pull_markdown

        class PageAwareAPI(FakeAPI):
            def request(self, method, path, body=None):
                if path != "pages/second-page/markdown":
                    raise AssertionError(path)
                return {"markdown": "# edited\n", "truncated": False, "unknown_block_ids": []}

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.md"
            output = Path(directory) / "notion.md"
            report.write_text("# original\n")
            output.write_text("# previous\n")
            local_diff, previous_diff, backup = pull_markdown(
                PageAwareAPI({}), "second-page", output, report)
            self.assertEqual(output.read_text(), "# edited\n")
            self.assertEqual(report.read_text(), "# original\n")
            self.assertEqual(backup.read_text(), "# previous\n")
            self.assertEqual(backup.parent, Path(directory) / "검토자료" / "노션_백업")
            self.assertEqual(list(Path(directory).glob("notion-backup-*.md")), [])
            self.assertIn("-# original", local_diff)
            self.assertIn("+# edited", local_diff)
            self.assertIn("-# previous", previous_diff)
            self.assertIn("+# edited", previous_diff)
            self.assertIn(str(backup), previous_diff)

    def test_pull_unchanged_does_not_create_backup(self):
        from notion_report import pull_markdown

        class SamePageAPI(FakeAPI):
            def request(self, method, path, body=None):
                return {"markdown": "# same\n", "truncated": False,
                        "unknown_block_ids": []}

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.md"
            output = Path(directory) / "notion.md"
            report.write_text("# local\n")
            output.write_text("# same\n")
            local_diff, previous_diff, backup = pull_markdown(
                SamePageAPI({}), "page-a", output, report)
            self.assertIsNone(backup)
            self.assertEqual(previous_diff, "")
            self.assertIn("-# local", local_diff)
            self.assertEqual(list(Path(directory).glob("notion-backup-*.md")), [])

    def test_pull_accepts_separate_backup_directory(self):
        from notion_report import save_pulled_markdown
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            output = base / "notion.md"
            archive = base / "archive"
            output.write_text("# old\n")
            backup = save_pulled_markdown("# new\n", output, archive)
            self.assertEqual(backup.parent, archive)
            self.assertEqual(backup.read_text(), "# old\n")
            self.assertEqual(output.read_text(), "# new\n")

    def test_first_pull_has_no_previous_comparison(self):
        from notion_report import pull_markdown

        class FirstPageAPI(FakeAPI):
            def request(self, method, path, body=None):
                return {"markdown": "# first\n", "truncated": False,
                        "unknown_block_ids": []}

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.md"
            output = Path(directory) / "notion.md"
            report.write_text("# local\n")
            local_diff, previous_diff, backup = pull_markdown(
                FirstPageAPI({}), "page-a", output, report)
            self.assertIsNone(backup)
            self.assertIsNone(previous_diff)
            self.assertEqual(output.read_text(), "# first\n")
            self.assertIn("+# first", local_diff)

    def test_incomplete_pull_preserves_previous_download(self):
        from notion_report import pull_markdown

        class IncompletePageAPI(FakeAPI):
            def request(self, method, path, body=None):
                return {"markdown": "# partial\n", "truncated": True,
                        "unknown_block_ids": []}

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.md"
            output = Path(directory) / "notion.md"
            report.write_text("# local\n")
            output.write_text("# previous\n")
            with self.assertRaisesRegex(ValueError, "incomplete"):
                pull_markdown(IncompletePageAPI({}), "page-a", output, report)
            self.assertEqual(output.read_text(), "# previous\n")
            self.assertEqual(list(Path(directory).glob("notion-backup-*.md")), [])

    def test_pull_rejects_output_equal_to_local_report(self):
        from notion_report import pull_markdown
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.md"
            report.write_text("# original\n")
            with self.assertRaisesRegex(ValueError, "must differ"):
                pull_markdown(FakeAPI({}), "page-a", report, report)
            self.assertEqual(report.read_text(), "# original\n")
