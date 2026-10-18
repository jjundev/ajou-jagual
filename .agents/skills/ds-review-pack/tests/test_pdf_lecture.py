import html, json, re, tempfile
from pathlib import Path
from _util import REPO
from pdf_cards import read_pack, to_payload
from pdf_lecture import split_lecture_problem
from pdf_types import Block, PageSlice

def strip(s): return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
def squash(s): return re.sub(r'\s+', '', strip(s))
def P(h): return Block('prose', h, strip(h))
def lecture(range_, pid):
    pack = read_pack(next((REPO / '복습노트' / range_).glob('복습문제_*.html')))
    card = next(c for c in pack.cards if c.id == pid and c.kind == '강의 코드')
    return tuple(b for b in card.problem if b.kind == 'prose')

def test_1015_p5_split():
    cond, ask = split_lecture_problem(lecture('1015', 'p5'))
    assert cond.count('<p>') == 4 and ask.count('<li>') == 2
    assert strip(ask).startswith('clock=1,2,3에서')
    assert '강의 예제 기반' not in cond + ask and 'S6 p22' not in cond + ask

def test_trailing_parenthetical_is_ask():
    cond, ask = split_lecture_problem(lecture('1001', 'p5'))
    assert cond.count('<p>') == 1 and ask.count('<li>') == 5

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

def test_all_lecture_cards_lossless_and_badge_free():
    n = 0
    for src in sorted((REPO / '복습노트').glob('*/복습문제_*.html')):
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
    pack = read_pack(next((REPO / '복습노트' / range_).glob('복습문제_*.html')))
    pages = tuple(PageSlice(c.id, c.id, 1, c.problem, c.solution, True, True) for c in pack.cards)
    return pack, to_payload(pack, mode, pages, Path(tempfile.mkdtemp()) / 'assets')

def test_lecture_payload_uses_conditions():
    pack, data = payload('1015')
    p5 = next(p for p in data['problems'] if p['id'] == 'p5')
    assert p5['html']['conditions'].count('<p>') == 4 and '<ol class="ds-asks">' in p5['html']['ask']
    assert 'service_time--' in p5['html']['code']

def test_lecture_answers_mode_split():
    _, data = payload('1015', 'answers')
    assert all('강의 예제 기반' not in json.dumps(p['html'], ensure_ascii=False) for p in data['problems'])
    p5 = next(p for p in data['problems'] if p['id'] == 'p5')
    assert '<ol class="ds-asks">' in p5['html']['ask'] and p5['solution']['steps']

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

def test_lecture_long_card_renders(tmp_path):
    import pdf_render
    from pdf_layout import plan_pages, check_coverage
    pack = read_pack(next((REPO / '복습노트/1001').glob('복습문제_*.html')))
    pack = pack.__class__(pack.source, pack.source_sha256, pack.range, pack.slug, tuple(c for c in pack.cards if c.id == 'p5'))
    with pdf_render.render_session():
        pages = plan_pages(pack, tmp_path / 'layout')
        assert check_coverage(pack, pages) == []
        for mode in ('problems', 'answers'):
            r = pdf_render.render(to_payload(pack, mode, pages, tmp_path / 'assets'), mode, tmp_path / mode, tmp_path / (mode + '.pdf'))
            assert r.errors == () and r.overflow == ()
