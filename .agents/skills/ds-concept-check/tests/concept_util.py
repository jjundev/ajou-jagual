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


def copy_fixture(tmp_path, nfd: bool = False):
    """tests/fixtures/mini/9999 를 tmp_path/9999 로 복사. nfd 면 .pack 안 한글 폴더명을 NFD 로 바꾼다."""
    import shutil
    import unicodedata
    root = Path(tmp_path) / "9999"
    shutil.copytree(FIXTURES / "mini" / "9999", root)
    if nfd:
        for child in list((root / ".pack").iterdir()):
            child.rename(child.with_name(unicodedata.normalize("NFD", child.name)))
    return root


def nfd_path(root, rel: str):
    """root 아래 rel 을 디스크에 실제 있는 철자(NFC·NFD 무관)로 풀어 돌려준다."""
    import unicodedata
    path = Path(root)
    for part in Path(rel).parts:
        want = unicodedata.normalize("NFC", part)
        hit = next((c for c in path.iterdir() if unicodedata.normalize("NFC", c.name) == want), None)
        path = hit if hit is not None else path / part
    return path
