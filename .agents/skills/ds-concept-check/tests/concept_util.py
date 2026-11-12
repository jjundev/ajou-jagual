import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
SCRIPTS = SKILL / "scripts"
FIXTURES = TESTS / "fixtures"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def review_template_with(parts: str) -> str:
    """ds-review-pack 복습문제 템플릿을 assemble.fill 로 채운다(build_review 는 개정 도장을 찍어 쓰지 않는다)."""
    import _paths
    ds_scripts = str(_paths.DS_REVIEW_PACK / "scripts")
    if ds_scripts not in sys.path:
        sys.path.insert(0, ds_scripts)
    import assemble
    template = (_paths.DS_REVIEW_PACK / "assets" / "review-template.html").read_text(encoding="utf-8")
    return assemble.fill(template, dict(
        PAGE_TITLE="확인문제 t", DESCRIPTION="테스트", RANGE="concept-check-t", NOTE_HREF="#",
        TOC="", TITLE="확인문제 t", INTRO="", PARTS=parts, FOOTER="", SCRIPTS=""))
