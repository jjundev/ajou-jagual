import concept_util  # noqa: F401  (scripts/ 를 sys.path 에 넣는다)
import interaction
import render

OBJ = {"id": "o2", "topic_id": "s1-traversal", "concept": "레벨 순회와 표준 순회의 구분",
       "can_do": "순회 이름과 방문 순서를 짝짓는다", "kind": "개념 구분",
       "source": {"slide": "S7 p18", "stt": "7절"}}

MCQ = {"id": "q2", "objective": "o2", "format": "mcq", "title": "순회 이름",
       "stem_html": "<p>루트부터 층마다 왼쪽에서 오른쪽으로 방문하는 순회는 무엇일까요?</p>",
       "tree": ["A", "B", "C", None, "D"],
       "options": [
           {"id": "A", "text": "레벨 순회", "why": "층 단위로 방문해요."},
           {"id": "B", "text": "전위 순회", "why": "전위는 루트-왼쪽-오른쪽 깊이 우선이에요.",
            "misconception": "레벨 순회를 표준 순회로 봄", "source": "stt:7절"},
           {"id": "C", "text": "중위 순회", "why": "중위는 왼쪽-루트-오른쪽이에요.",
            "misconception": "왼쪽부터라서 중위로 봄", "source": "note:s1"},
           {"id": "D", "text": "후위 순회", "why": "후위는 루트를 마지막에 방문해요.",
            "misconception": "층 순서를 아래부터로 봄", "source": "bank:q3"}],
       "answer": "A", "compute": None}

SHORT = {"id": "q1", "objective": "o2", "format": "short", "title": "전위 순회 결과",
         "stem_html": "<p>이 트리를 전위 순회한 결과를 쓰세요.</p>",
         "tree": ["A", "B", "C", None, "D"],
         "compute": {"op": "preorder"},
         "answer": {"canonical": "A, B, D", "accepted": []},
         "solution": ["루트 A 를 먼저 방문해요.", "왼쪽 B, 그다음 D 예요."]}

NOTE = "정리노트_1102_Tree.html"

TEMPLATE_WITH_CARD = concept_util.review_template_with(render.card_html(MCQ, OBJ, 1, NOTE))


def test_accepted_variants():
    v = render.accepted_variants("A, B, D")
    assert {"A,B,D", "A B D", "ABD", "A→B→D", "A → B → D"} <= set(v) and "A, B, D" not in v
    assert render.accepted_variants("2") == []


def test_card_has_no_source_line():
    """목표 근거(쪽 번호·개념 이름)는 카드에 찍지 않는다."""
    for item in (MCQ, SHORT):
        html_ = render.card_html(item, OBJ, 1, NOTE)
        assert 'class="source"' not in html_ and "확인:" not in html_
        assert OBJ["source"]["slide"] not in html_ and OBJ["concept"] not in html_


def test_check_button_is_primary():
    """답 확인은 템플릿의 파란 주 버튼(btn-primary)으로 그린다."""
    assert '<button class="btn btn-primary check-answer" type="button">답 확인</button>' in render.card_html(SHORT, OBJ, 1, NOTE)


def test_mcq_card_builds_model():
    page = "<html><body><main>" + render.card_html(MCQ, OBJ, 1, NOTE) + "</main></body></html>"
    m = interaction.build_model(page, "t")
    assert m["errors"] == [] and m["cards"]["q2"]["answer"] == "A"
    assert len(m["cards"]["q2"]["options"]) == 4


def test_short_card_builds_model():
    m = interaction.build_model("<body>" + render.card_html(SHORT, OBJ, 2, NOTE) + "</body>", "t")
    assert m["cards"]["q1"]["format"] == "short" and "ABD" in m["cards"]["q1"]["answer"]["accepted"]


def test_option_text_is_escaped():
    item = {**MCQ, "options": [{**MCQ["options"][0], "text": "a<b && c"}] + MCQ["options"][1:]}
    html_ = render.card_html(item, OBJ, 1, NOTE)
    assert "a&lt;b &amp;&amp; c" in html_
    assert interaction.build_model("<body>" + html_ + "</body>", "t")["errors"] == []


def test_install_boots_without_storage():
    out = interaction.install(TEMPLATE_WITH_CARD, "확인문제_t")
    assert "storage = null" in out and "review-interaction-model" in out


def test_install_gaps_problem_from_choices():
    # 문제 문장과 첫 보기 사이가 카드 사이(--s3)보다 넓어야 한다.
    out = interaction.install(TEMPLATE_WITH_CARD, "확인문제_t")
    assert ".review-ready .problem > .choices { margin-top:var(--s6); }" in out


def test_install_labels_choices_a_to_d():
    out = interaction.install(TEMPLATE_WITH_CARD, "확인문제_t")
    assert 'content:"(" counter(opt, upper-alpha) ") "' in out


def _setup_review(page: str) -> str:
    begin = page.index("function setupReview()")
    return page[begin:page.index("function setupNote()", begin)]


def test_install_drops_solved_progress_persistence():
    section = _setup_review(interaction.install(TEMPLATE_WITH_CARD, "확인문제_t"))
    assert "store.get(KEY" not in section and "store.set(KEY" not in section
    assert "solved.add(curId)" in section  # 푼 문제 버튼은 메모리에서 그대로 동작


def test_install_rejects_unknown_solved_store_shape():
    import pytest
    broken = TEMPLATE_WITH_CARD.replace("store.set(KEY, Array.from(solved));", "save(solved);")
    with pytest.raises(ValueError):
        interaction.install(broken, "확인문제_t")


def test_interaction_has_no_cli():
    """복사해 온 CLI(--write)는 ds-review-pack 산출물을 덮어쓸 수 있어 지웠다."""
    assert not hasattr(interaction, "main")
    assert "__main__" not in (concept_util.SCRIPTS / "interaction.py").read_text(encoding="utf-8")


def test_solution_ends_with_note_topic_link():
    """풀이 끝에 그 목표의 정리노트 토픽 링크가 새 탭으로 붙는다. 문구엔 토픽·개념 이름이 없다."""
    import re
    for item in (MCQ, SHORT):
        html_ = render.card_html(item, OBJ, 1, NOTE)
        sol = re.search(r'<details class="solution">(.*?)</details>', html_, re.S).group(1)
        assert sol.endswith(
            '<p class="note-link"><a href="정리노트_1102_Tree.html#s1-traversal" target="_blank" rel="noopener">'
            f'{render.NOTE_LINK_TEXT}</a></p>')
        assert html_.count('class="note-link"') == 1
        assert OBJ["concept"] not in render.NOTE_LINK_TEXT


def test_note_link_survives_review_shell():
    """템플릿이 풀이(details)를 오른쪽 패널로 옮겨도 링크는 풀이 안에 그대로 있다."""
    page = interaction.install(TEMPLATE_WITH_CARD, "t")
    assert 'href="정리노트_1102_Tree.html#s1-traversal"' in page
