from _util import SCRIPTS
from review_source import review_paths, read_review
from check_html import check_review,parse_html

def test_lecture_original_label_and_extra_cards():
    m={'forbidden_outside_preview':[],'problems':[{'id':'p1','source':'lecture-s02-p10-power','source_kind':'lecture-code','terms':[]}]}
    card='<article id="p1" class="card" data-source="lecture-s02-p10-power" data-source-kind="lecture-code"><div class="problem">Q</div><details class="original"><summary>기출 원문 보기</summary>C</details><details class="hint">H</details><details class="solution"><p class="answer">S</p></details></article>'
    assert any(e.code=='lecture-label' for e in check_review(parse_html(card),m))
    fixed=card.replace('기출 원문 보기','강의 예제 보기').replace('Q</div>','강의 예제 기반 자체 출제 Q</div>')
    assert check_review(parse_html(fixed),m)==[]
    assert any(e.code=='extra-card' for e in check_review(parse_html(fixed+fixed.replace('id="p1"','id="p2"')),m))

M={'forbidden_outside_preview':[],'problems':[{'id':'p1','source':'lecture-x','source_kind':'lecture-code','terms':[]}]}
def card(problem, hint='H', sol='S', kind='lecture-code'):
    return (f'<article id="p1" class="card" data-source="lecture-x" data-source-kind="{kind}">'
            f'<div class="problem"><p><span class="badge">강의 예제 기반 자체 출제</span> S4 p48 · 추가 근거 p28,47</p>{problem}</div>'
            '<details class="original"><summary>강의 예제 보기</summary><p>S4 p48 · Software_4_List.pdf</p></details>'
            f'<details class="hint">{hint}</details><details class="solution"><p class="answer">{sol}</p></details></article>')
def codes(html, m=M): return [(e.code, e.detail) for e in check_review(parse_html(html), m)]

def test_lecture_standalone_ignores_badge_and_original():
    assert codes(card('<p>길이 1인 리스트에서 값을 쓰세요.</p>')) == []

def test_lecture_standalone_flags_lecture_reference():
    out = codes(card('<p>강의 p47에서 get_node_at은 NULL을 반환해요.</p>'))
    assert [c for c,_ in out] == ['lecture-standalone'] and '강의' in out[0][1]

def test_lecture_standalone_flags_slide_citation_and_other_problem():
    assert [c for c,_ in codes(card('<p>S3 p8에서 높은 차수만 읽어요.</p>'))] == ['lecture-standalone']
    assert [c for c,_ in codes(card('<p>값을 쓰세요.</p>', hint='P3의 결과를 써요.'))] == ['lecture-standalone']
    assert [c for c,_ in codes(card('<p>앞 문제의 리스트를 써요.</p>'))] == ['lecture-standalone']

def test_lecture_standalone_flags_solution_answer():
    assert [c for c,_ in codes(card('<p>값을 쓰세요.</p>', sol='이 예제는 강의 원문의 결함이에요.'))] == ['lecture-standalone']

def test_lecture_standalone_allows_code_identifiers():
    assert codes(card('<pre><code>ListNode *p1, *p2; p1=p2-&gt;link;</code></pre><p>위 코드의 p1을 쓰세요.</p>')) == []

def test_past_exam_cards_not_linted():
    m={**M,'problems':[{**M['problems'][0],'source_kind':'past-exam'}]}
    assert codes(card('<p>강의 p3 참고</p>', kind='past-exam').replace('강의 예제 보기','기출 원문 보기'), m) == []

def test_lecture_standalone_ignores_badge_after_supplement_note():
    html = card('<p>값을 쓰세요.</p>').replace('<div class="problem">','<div class="problem"><p><strong>후속 수업 보충:</strong> 0914 수업에서 다뤘어요.</p>')
    assert codes(html) == []

def test_repo_lecture_cards_are_standalone():
    from _util import REPO
    import json
    bad = []
    for m in sorted((REPO/'복습노트').glob('*/.pack/자료_복습팩/manifest.json')):
        rng = m.parents[2]
        html = read_review(review_paths(rng)[0])
        bad += [(rng.name, e.where, e.detail) for e in check_review(parse_html(html), json.loads(m.read_text(encoding='utf-8'))) if e.code == 'lecture-standalone']
    assert bad == []

def test_lecture_standalone_allows_pointer_variable_prose():
    assert codes(card('<p>p1의 link를 p2에 복사하고 변수 p2에서 읽어요. 노드 P1을 배열 P3에 넣어요.</p>')) == []
    assert [c for c,_ in codes(card('<p>p28의 remove_node를 쓰세요.</p>'))] == ['lecture-standalone']
