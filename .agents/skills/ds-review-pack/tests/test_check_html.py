import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from _util import MINI_RUN

import assemble
import check_html


class TestPrimitives(unittest.TestCase):
    def test_note_rejects_recording_locators(self):
        for locator in (
            '(1105 Part 05 · 시각 미제공)', '(0907 01:11)',
            '(0921 00:14–01:47)', '(1012 Part 02–03)',
            '(1001 수업 Part 02–03)', '(1015 Part 01, 시간 정보 없음)',
            '(1029 Part 01 앞)', 'Part 05', '시각 미제공',
            '시간 미제공', '시간 정보 없음', '(01:11)',
            '(1105 <span>Part 05</span>)',
        ):
            with self.subTest(locator=locator):
                src = f'<html lang="ko"><body><article class="topic" id="t"><p>{locator}</p></article></body></html>'
                codes = [p.code for p in check_html.check_common(check_html.parse_html(src), src, Path('note.html'))]
                self.assertIn('recording-locator', codes)

    def test_named_note_without_topics_rejects_recording_locator(self):
        src = '<html lang="ko"><body>(1105 Part 05)</body></html>'
        codes = [p.code for p in check_html.check_common(check_html.parse_html(src), src, Path('정리노트_1105_Tree.html'))]
        self.assertIn('recording-locator', codes)

    def test_note_allows_dates_sources_and_algorithm_content(self):
        src = ('<html lang="ko"><body><article class="topic" id="t">'
               '<p>1105 수업 · S7 p19–28 · 수업 녹음 전사(1105)</p>'
               '<p>시간복잡도 O(h), 도착 시각, 시간 정보가 필요해요.</p>'
               '<pre><code>case 1:11; int Part = 5;</code></pre>'
               '</article></body></html>')
        self.assertEqual(check_html.check_common(check_html.parse_html(src), src, Path('note.html')), [])

    def test_note_rejects_date_tag_at_quote_end(self):
        for quote in ('"메모리가 여왕벌이구나." (1112)', '“말씀” （1112）', '말씀 ( 1112 ) ', '말씀. (1109 수업)'):
            with self.subTest(quote=quote):
                src = f'<html lang="ko"><body><article class="topic" id="t"><blockquote>{quote}</blockquote></article></body></html>'
                codes = [p.code for p in check_html.check_common(check_html.parse_html(src), src, Path('note.html'))]
                self.assertIn('quote-date', codes)

    def test_note_allows_date_outside_quote_end(self):
        src = ('<html lang="ko"><body><article class="topic" id="t">'
               '<span class="tag date">1112 수업</span>'
               '<blockquote>"1112년에는 (1112) 이런 일이 있었다"</blockquote></article>'
               '<footer>출처: 수업 녹음 전사(1112).</footer></body></html>')
        self.assertEqual(check_html.check_common(check_html.parse_html(src), src, Path('note.html')), [])

    def test_review_is_not_subject_to_note_recording_policy(self):
        src = '<html lang="ko"><body><article class="card" id="p1">(1105 Part 05)</article></body></html>'
        self.assertEqual(check_html.check_common(check_html.parse_html(src), src, Path('review.html')), [])

    def test_adjacent_inline_math_in_list_items_is_not_display_math(self):
        doc = check_html.parse_html('<html lang="ko"><body><ol><li>$a$</li><li>$b$</li></ol></body></html>')
        self.assertEqual(check_html.math_delimiter_errors(doc.body_text), [])

    def test_unbalanced_inline_math(self):
        self.assertEqual(check_html.math_delimiter_errors("a $x b"), ["unbalanced $ (inline math)"])

    def test_widget_without_static(self):
        src = '<html lang="ko"><body><div class="widget" id="w1"><h4>x</h4></div></body></html>'
        problems = check_html.check_common(check_html.parse_html(src), src, Path("x.html"))
        self.assertEqual([p.code for p in problems], ["widget-static-missing"])

    def test_leftover_slot_and_external(self):
        src = '<html lang="ko"><head><script src="https://cdn.tailwindcss.com"></script></head><body>{{TOC}}</body></html>'
        codes = sorted(p.code for p in check_html.check_common(check_html.parse_html(src), src, Path("x.html")))
        self.assertEqual(codes, ["external", "leftover-slot"])

    def external_codes(self, head: str, body: str = "") -> list[str]:
        src = f'<html lang="ko"><head>{head}</head><body>{body}</body></html>'
        return [p.code for p in check_html.check_common(check_html.parse_html(src), src, Path("x.html"))]

    def test_remote_resources_on_any_tag_are_external(self):
        cases = [
            ("", '<img src="https://evil.com/x.png" alt="">'),
            ("", '<iframe src="https://evil.com/frame"></iframe>'),
            ('<link rel="preload" href="https://evil.com/f.woff2" as="font">', ""),
            ('<style>@import url("https://x/y.css");</style>', ""),
            ('<script src="//cdn.example.com/a.js"></script>', ""),
        ]
        for head, body in cases:
            with self.subTest(head=head, body=body):
                self.assertEqual(self.external_codes(head, body), ["external"])

    def test_relative_and_allowed_resources_are_not_external(self):
        head = ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">'
                '<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>')
        self.assertEqual(self.external_codes(head, '<img src="figures_0101-0102/a.svg" alt="">'), [])


class TestPack(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.run = self.tmp / "run"
        shutil.copytree(MINI_RUN, self.run)
        self.m = json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def codes(self):
        note, review = assemble.assemble(self.run, self.tmp / "out")
        return sorted(p.code for p in check_html.check_pack(self.m, note, review))

    def edit(self, rel: str, old: str, new: str):
        path = self.run / rel
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def test_mini_pack_passes(self):
        self.assertEqual(self.codes(), [])

    def test_missing_required_term(self):
        self.edit("sections/s1.html", "무게중심", "가운데")
        self.assertEqual(self.codes(), ["missing-term"])

    def test_forbidden_term_outside_preview(self):
        self.edit("sections/s1.html", "분산은 흩어진 정도예요.", "분산은 d-separation과 무관해요.")
        self.assertEqual(self.codes(), ["forbidden-term"])

    def test_missing_layer(self):
        self.edit("sections/s1.html", '<div class="layer prof"><span class="layer-title">교수님 말씀</span><p>"평균부터 봐요."</p></div>', "")
        self.assertEqual(self.codes(), ["missing-layer"])

    def test_missing_supp_badge(self):
        self.edit("sections/s1.html", '<span class="badge supp">보충 · 수업에서 유도하진 않았어요</span>', "")
        self.assertEqual(self.codes(), ["missing-supp"])

    def test_missing_sum(self):
        self.edit("sections/s1.html", '<div class="sum" hidden>\n          <p class="sum-lead">평균은', '<div class="summary" hidden>\n          <p class="sum-lead">평균은')
        self.assertEqual(self.codes(), ["missing-sum"])

    def test_sum_not_required_without_summary_panel(self):
        # 요약 패널이 없는 예전 템플릿으로 만든 팩은 .sum을 요구하지 않는다.
        self.edit("sections/s1.html", '<div class="sum" hidden>\n          <p class="sum-lead">평균은', '<div class="summary" hidden>\n          <p class="sum-lead">평균은')
        note, review = assemble.assemble(self.run, self.tmp / "out")
        note.write_text(note.read_text(encoding="utf-8").replace('id="sum-for"', 'id="old-panel"'), encoding="utf-8")
        self.assertEqual([p.code for p in check_html.check_pack(self.m, note, review)], [])

    def test_card_source(self):
        self.edit("cards/p1.html", 'data-source="2016-final-ljw-q1"', 'data-source="2016-final-ljw-q2"')
        self.assertEqual(self.codes(), ["card-source"])

    def test_card_missing_hint(self):
        self.edit("cards/p1.html", '<details class="hint"><summary>힌트 보기</summary>더해서 개수로 나눈다.</details>', "")
        self.assertEqual(self.codes(), ["card-parts"])

    def test_widget_static_required(self):
        self.edit("sections/s1.html", 'class="widget-static"', 'class="widget-snap"')
        self.assertEqual(self.codes(), ["widget-static-missing"])

    def test_cli_exit_codes(self):
        note, review = assemble.assemble(self.run, self.tmp / "out")
        args = ["--manifest", str(self.run / "manifest.json"), "--note", str(note), "--review", str(review)]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(check_html.main(args), 0)
            self.assertEqual(check_html.main([str(note), str(review)]), 0)
            note.write_text(note.read_text(encoding="utf-8").replace('lang="ko"', 'lang="en"'), encoding="utf-8")
            self.assertEqual(check_html.main(args), 1)
        self.assertIn("[lang]", out.getvalue())


if __name__ == "__main__":
    unittest.main()
