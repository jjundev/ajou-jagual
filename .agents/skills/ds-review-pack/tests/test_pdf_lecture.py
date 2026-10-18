import html, re
from _util import REPO
from pdf_cards import read_pack
from pdf_lecture import split_lecture_problem
from pdf_types import Block

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
