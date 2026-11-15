import html, json, re, tempfile
from pathlib import Path
from _util import REPO
from review_source import review_paths
from review_pdf import discover_reviews
from pdf_cards import read_pack, to_payload
from pdf_lecture import split_lecture_problem
from pdf_types import Block, PageSlice

def strip(s): return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
def squash(s): return re.sub(r'\s+', '', strip(s))
def P(h): return Block('prose', h, strip(h))
def lecture(range_, pid):
    pack = read_pack(review_paths(REPO / '복습노트' / range_)[0])
    card = next(c for c in pack.cards if c.id == pid and c.kind == '강의 코드')
    return tuple(b for b in card.problem if b.kind == 'prose')

def test_1015_p5_split():
    cond, ask = split_lecture_problem(lecture('1015', 'p5'))
    assert cond.count('<p>') == 1 and ask.count('<li>') == 2
    assert strip(ask).startswith('(a) clock = 1, 2, 3')
    assert '강의 예제 기반' not in cond + ask and 'S6 p22' not in cond + ask

def test_trailing_parenthetical_is_ask():
    cond, ask = split_lecture_problem(lecture('1001', 'p5'))
    assert cond.count('<p>') == 1 and ask.count('<li>') == 2
    c2, a2 = split_lecture_problem((P('<p>상황이에요. 결과를 설명하세요(링크 변경만 묻습니다).</p>'),))
    assert c2 == '<p>상황이에요.</p>' and a2 == '<ol class="ds-asks"><li>결과를 설명하세요(링크 변경만 묻습니다).</li></ol>'

def test_supplement_kept_as_caption():
    cond, ask = split_lecture_problem(lecture('0907', 'p4'))
    assert cond.startswith('<p class="ds-source">') and '후속 수업 보충' in cond
    assert '강의 예제 기반' not in cond + ask

def test_no_split_inside_open_element():
    cond, ask = split_lecture_problem((P('<p>A는 <code>x. y</code>예요. <strong>a. b</strong>를 쓰세요.</p>'),))
    assert cond == '<p>A는 <code>x. y</code>예요.</p>'
    assert ask == '<ol class="ds-asks"><li><strong>a. b</strong>를 쓰세요.</li></ol>'

def test_fallback_existing_list_and_no_question():
    badge = P('<p><span class="badge">강의 예제 기반 자체 출제</span> S1 p2</p>')
    lst = P('<ol><li>(a) 쓰세요.</li></ol>')
    assert split_lecture_problem((badge, lst)) == ('', lst.html)
    plain = P('<p>상황만 있어요. 끝이에요.</p>')
    assert split_lecture_problem((badge, plain)) == ('', plain.html)

def test_structured_lecture_ol_split():
    badge = P('<p><span class="badge">강의 예제 기반 자체 출제</span> S4 p18</p>')
    cond_p = P('<p>단순 연결 리스트에서 <code>head = 300</code>이에요.</p>')
    asks_ol = P('<ol><li>(a) 방문 순서를 쓰세요.</li><li>(b) 삽입 후 링크를 쓰세요.</li></ol>')
    cond, ask = split_lecture_problem((badge, cond_p, asks_ol))
    assert cond == '<p>단순 연결 리스트에서 <code>head = 300</code>이에요.</p>'
    assert ask == '<ol class="ds-asks ds-labeled"><li>(a) 방문 순서를 쓰세요.</li><li>(b) 삽입 후 링크를 쓰세요.</li></ol>'

def test_split_list_blocks_merge_into_one_ol():
    cond_p = P('<p>상황이에요.</p>')
    a, b = P('<ol start="1"><li>(a) 첫째를 쓰세요.</li></ol>'), P('<ol start="2"><li>(b) 둘째를 쓰세요.</li></ol>')
    assert split_lecture_problem((cond_p, a, b))[1] == '<ol class="ds-asks ds-labeled"><li>(a) 첫째를 쓰세요.</li><li>(b) 둘째를 쓰세요.</li></ol>'
    plain = P('<ol><li>첫째를 쓰세요.</li></ol>')
    assert split_lecture_problem((cond_p, plain))[1] == '<ol class="ds-asks"><li>첫째를 쓰세요.</li></ol>'

def test_list_before_prose_keeps_original_order():
    blocks = (P('<p>다음 연산을 실행해요.</p>'), P('<ol><li>push(1)</li></ol>'), P('<p>최종 상태를 쓰세요.</p>'))
    assert split_lecture_problem(blocks) == ('', ''.join(b.html for b in blocks))

def test_all_lecture_cards_lossless_and_badge_free():
    n = 0
    for src in discover_reviews(REPO, 'all'):
        for c in read_pack(src).cards:
            if c.kind != '강의 코드': continue
            prose = tuple(b for b in c.problem if b.kind == 'prose')
            cond, ask = split_lecture_problem(prose)
            assert '<li>' in ask, c.id
            # 조건이 질문 뒤에 있으면 조건 쪽으로 올라가므로 순서 무관 비교
            assert sorted(squash(cond + ask)) == sorted(squash(''.join(b.html for b in prose if 'class="badge"' not in b.html))), c.id
            assert '강의 예제 기반' not in cond + ask
            n += 1
    assert n == 47

def payload(range_, mode='problems'):
    pack = read_pack(review_paths(REPO / '복습노트' / range_)[0])
    pages = tuple(PageSlice(c.id, c.id, 1, c.problem, c.solution, True, True) for c in pack.cards)
    return pack, to_payload(pack, mode, pages, Path(tempfile.mkdtemp()) / 'assets')

def test_lecture_payload_uses_conditions():
    pack, data = payload('1015')
    p5 = next(p for p in data['problems'] if p['id'] == 'p5')
    assert p5['html']['conditions'].count('<p>') == 1 and p5['html']['ask'].count('<ol class="ds-asks ds-labeled">') == 1
    assert 'service_time--' in p5['html']['code']

def test_lecture_answers_mode_split():
    _, data = payload('1015', 'answers')
    assert all('강의 예제 기반' not in json.dumps(p['html'], ensure_ascii=False) for p in data['problems'])
    p5 = next(p for p in data['problems'] if p['id'] == 'p5')
    assert '<ol class="ds-asks ds-labeled">' in p5['html']['ask'] and p5['solution']['steps']

def test_non_lecture_payload_unchanged():
    _, data = payload('1015')
    p1 = next(p for p in data['problems'] if p['id'] == 'p1')
    assert p1['html']['conditions'] == '' and 'ds-asks' not in p1['html']['ask']

def test_lecture_figure_still_extracted(tmp_path):
    src = tmp_path / '복습문제_0907_Test.html'
    src.write_text('<article class="card" id="p1" data-source="lecture-s01-p1-x" data-source-kind="lecture-code"><h3>P1. Fig</h3>'
                   '<div class="problem"><p><span class="badge">강의 예제 기반 자체 출제</span> S1 p1</p><p>상황이에요. 값을 쓰세요.</p>'
                   '<svg viewBox="0 0 80 40"><path d="M0 0 L80 40"/></svg></div>'
                   '<details class="solution"><summary>S</summary><p class="answer">A</p></details></article>', encoding='utf-8')
    pack = read_pack(src); c = pack.cards[0]
    p = to_payload(pack, 'problems', (PageSlice(c.id, c.id, 1, c.problem, c.solution, True, True),), tmp_path / 'assets')['problems'][0]
    assert len(p['figures']) == 1 and '<svg' not in p['html']['ask'] and '<li>' in p['html']['ask']
    assert p['html']['conditions'] == '<p>상황이에요.</p>' and '강의 예제 기반' not in json.dumps(p, ensure_ascii=False)

def test_lecture_wrapped_figure_in_conditions_extracted(tmp_path):
    src = tmp_path / '복습문제_0907_Test.html'
    src.write_text('<article class="card" id="p1" data-source="lecture-s01-p1-x" data-source-kind="lecture-code"><h3>P1. Fig</h3>'
                   '<div class="problem"><p><span class="badge">강의 예제 기반 자체 출제</span> S1 p1</p><p>상황이에요.</p>'
                   '<figure class="figure"><svg viewBox="0 0 80 40"><circle class="fig-ink" cx="9" cy="9" r="5"/></svg>'
                   '<figcaption>그림 설명이에요.</figcaption></figure><ol><li>(a) 값을 쓰세요.</li></ol></div>'
                   '<details class="solution"><summary>S</summary><p class="answer">A</p></details></article>', encoding='utf-8')
    pack = read_pack(src); c = pack.cards[0]
    p = to_payload(pack, 'problems', (PageSlice(c.id, c.id, 1, c.problem, c.solution, True, True),), tmp_path / 'assets')['problems'][0]
    assert len(p['figures']) == 1 and '<svg' not in p['html']['conditions'] + p['html']['ask']
    assert '그림 설명이에요.' in p['html']['conditions'] and '<li>' in p['html']['ask']
    assert '.fig-ink' in Path(p['figures'][0]['src'].removeprefix('file://')).read_text(encoding='utf-8')

def test_lecture_long_card_renders(tmp_path):
    import pdf_render
    from pdf_layout import plan_pages, check_coverage
    pack = read_pack(review_paths(REPO / '복습노트/1001')[0])
    pack = pack.__class__(pack.source, pack.source_sha256, pack.range, pack.slug, tuple(c for c in pack.cards if c.id == 'p5'))
    with pdf_render.render_session():
        pages = plan_pages(pack, tmp_path / 'layout')
        assert check_coverage(pack, pages) == []
        for mode in ('problems', 'answers'):
            r = pdf_render.render(to_payload(pack, mode, pages, tmp_path / 'assets'), mode, tmp_path / mode, tmp_path / (mode + '.pdf'))
            assert r.errors == () and r.overflow == ()

def test_lecture_labeled_asks_hide_numbers(tmp_path):
    from pdf_render import probe, render_session
    _, data = payload('1015')
    data = {'meta': data['meta'], 'problems': [p for p in data['problems'] if p['id'] == 'p5']}
    assert not probe(data, 'problems', 'video-16x9', tmp_path).errors
    with render_session() as browser:
        page = browser.new_page()
        page.goto((tmp_path / 'problems-video-16x9.html').resolve().as_uri())
        page.wait_for_function('document.documentElement.dataset.ready', timeout=120000)
        marks = page.evaluate("[...document.querySelectorAll('.ds-asks li')].map(li => [getComputedStyle(li, '::before').display, getComputedStyle(li).listStyleType])")
    assert marks == [['none', 'none']] * 2

def test_badge_with_extra_text_raises():
    import pytest
    from pdf_types import PdfError
    bad = P('<p><span class="badge">강의 예제 기반 자체 출제</span> S4 p5. 위 코드에서 x의 최종값을 쓰세요.</p>')
    with pytest.raises(PdfError, match='badge'):
        split_lecture_problem((bad, P('<p>상황이에요. 값을 쓰세요.</p>')))
    ok = P('<p><span class="badge">강의 예제 기반 자체 출제</span> S4 p37 · 추가 근거 p33,34</p>')
    assert split_lecture_problem((ok, P('<p>값을 쓰세요.</p>')))[1] == '<ol class="ds-asks"><li>값을 쓰세요.</li></ol>'

def test_assert_lossless_rejects_missing_and_duplicate():
    import pytest
    from pdf_lecture import assert_lossless
    from pdf_types import PdfError
    assert_lossless('<p>A다. B를 쓰세요.</p>', '<p>B를 쓰세요.</p><ol><li>A다.</li></ol>')
    for out in ('<p>A다.</p>', '<p>A다. A다. B를 쓰세요.</p>'):
        with pytest.raises(PdfError, match='lost text'):
            assert_lossless('<p>A다. B를 쓰세요.</p>', out)
