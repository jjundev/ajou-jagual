import json

import pytest

from concept_util import copy_fixture, playwright_available
import build
import browser_check

pytestmark = pytest.mark.skipif(not playwright_available(), reason="playwright·chromium 없음")


def test_browser_passes_on_fixture(tmp_path):
    root = copy_fixture(tmp_path)
    src = root / ".pack/자료_확인문제_9999_Mini"
    html = build.build(src)
    out = tmp_path / "b.json"
    result = browser_check.check(html, out, None, src=src, serve_root=tmp_path)
    assert result["failures"] == [] and len(result["runs"]) == 4
    assert all(run["detail"]["hints_checked"] == 3 for run in result["runs"])
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["sha256"] == result["sha256"]
    # 기기 경로(홈 폴더)를 남기지 않는다: serve_root 기준 상대 POSIX 경로
    assert saved["html"] == html.relative_to(tmp_path).as_posix()
    assert not saved["html"].startswith("/") and str(tmp_path) not in saved["html"]


def test_browser_rejects_html_outside_serve_root(tmp_path):
    root = copy_fixture(tmp_path / "a")
    src = root / ".pack/자료_확인문제_9999_Mini"
    html = build.build(src)
    (tmp_path / "b").mkdir()
    with pytest.raises(ValueError):
        browser_check.check(html, tmp_path / "b.json", None, src=src, serve_root=tmp_path / "b")
