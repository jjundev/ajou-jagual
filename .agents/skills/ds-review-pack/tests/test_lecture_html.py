from _util import SCRIPTS
from check_html import check_review,parse_html

def test_lecture_original_label_and_extra_cards():
    m={'forbidden_outside_preview':[],'problems':[{'id':'p1','source':'lecture-s02-p10-power','source_kind':'lecture-code','terms':[]}]}
    card='<article id="p1" class="card" data-source="lecture-s02-p10-power" data-source-kind="lecture-code"><div class="problem">Q</div><details class="original"><summary>기출 원문 보기</summary>C</details><details class="hint">H</details><details class="solution"><p class="answer">S</p></details></article>'
    assert any(e.code=='lecture-label' for e in check_review(parse_html(card),m))
    fixed=card.replace('기출 원문 보기','강의 예제 보기').replace('Q</div>','강의 예제 기반 자체 출제 Q</div>')
    assert check_review(parse_html(fixed),m)==[]
    assert any(e.code=='extra-card' for e in check_review(parse_html(fixed+fixed.replace('id="p1"','id="p2"')),m))
