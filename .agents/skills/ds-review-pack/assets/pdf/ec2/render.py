"""문제집 JSON → 템플릿 HTML → PDF.

템플릿 계약(workbook/templates/*.html): #workbook-data 안의 자리표시자 __WORKBOOK_DATA__ 를 JSON으로 바꾼다.
템플릿은 다 그리면 html[data-ready]를 'true'(실패면 'error')로, body[data-overflow]를 넘친 쪽 id(쉼표)로 둔다.
PDF는 Playwright가 설치된 Google Chrome(channel="chrome")으로 만든다. 템플릿이 CDN 글꼴·KaTeX를 받으므로 인터넷이 필요하다.
"""
import json
import re
from pathlib import Path

from paths import TEMPLATES

PLACEHOLDER = "__WORKBOOK_DATA__"
TEMPLATE_FILES = {"problems": "problem.html", "answers": "answer.html"}
INSTALL_HINT = "pip3 install --user --break-system-packages playwright"
VIEWPORT = {"width": 1400, "height": 1000}   # 화면 배율 1 (템플릿 screenZoom 기준 297mm ≈ 1123px)
# A4 overview is fitted to 900px high. The full widescreen PDF maps 1440pt to 1920px.
VIDEO_TEXT_SCALE = (900 / (210 * 72 / 25.4)) / (1920 / 1440)


class RenderError(Exception):
    pass


def load_template(mode, layout="a4"):
    if layout not in ("a4", "video-16x9"):
        raise RenderError(f"알 수 없는 페이지 규격: {layout}")
    template = (TEMPLATES / TEMPLATE_FILES[mode]).read_text(encoding="utf-8")
    if layout == "video-16x9":
        template = re.sub(r'((?:font-size|--fs-body)\s*:\s*)(\d+(?:\.\d+)?)pt',
            lambda m: m[1] + f'{float(m[2])*VIDEO_TEXT_SCALE:.6f}pt', template)
        css = (TEMPLATES / "video-16x9.css").read_text(encoding="utf-8")
        template = template.replace('</head>', '<style>'+css+'</style>'
            '<script>window.workbookVideoLayout=true;</script></head>')
    return template


def inject(template, data):
    """자리표시자를 JSON으로 바꾼다. '<'를 \\u003c로 적어 </script>, <!-- 가 스크립트를 끊지 못하게 한다."""
    count = template.count(PLACEHOLDER)
    if count != 1:
        raise RenderError(f"템플릿의 자리표시자 {PLACEHOLDER} 가 {count}번 있음 (1번이어야 함)")
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return template.replace(PLACEHOLDER, payload)


def _render_html(html_path, pdf_path=None, timeout_ms=120_000):
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise RenderError(f"playwright가 없음. 설치: {INSTALL_HINT}") from e
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome")
            try:
                page = browser.new_page(viewport=VIEWPORT)
                page.goto(Path(html_path).resolve().as_uri())
                page.wait_for_function("document.documentElement.dataset.ready", timeout=timeout_ms)
                ready, overflow = page.evaluate(
                    "[document.documentElement.dataset.ready, document.body.dataset.overflow || '']")
                if ready != "true":
                    raise RenderError(f"템플릿이 데이터를 그리지 못함 (data-ready={ready!r}): {html_path}")
                typography = page.evaluate("""Object.fromEntries([...document.querySelectorAll('.page--problem')].map(p => {
                    const panel=p.querySelector('.panel'), work=p.querySelector('.work');
                    const scale=n=>{const t=getComputedStyle(n).transform;return t==='none'?1:new DOMMatrix(t).a;};
                    return [p.id, {panel:parseFloat(getComputedStyle(panel).getPropertyValue('--fs'))||1,
                        solution:parseFloat(getComputedStyle(work).getPropertyValue('--sfs'))||1,
                        math:[...p.querySelectorAll('.katex-display > .katex')].map(scale),
                        hints:[...p.querySelectorAll('.hint-strip-formula')].map(scale)}];
                }))""")
                if pdf_path is not None:
                    page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True)
            finally:
                browser.close()
    except PlaywrightError as e:
        raise RenderError(f"Chrome 렌더링 실패 (Google Chrome 설치와 인터넷 연결 확인): {e}") from e
    return {"overflow": [x for x in overflow.split(",") if x], "typography": typography}


def measure_typography(html_path):
    """Freeze A4 fitting scales before adapting point sizes to the video page ratio."""
    return _render_html(html_path)["typography"]


def render_pdf(html_path, pdf_path, timeout_ms=120_000):
    """HTML을 Chrome으로 열어 다 그려지면 PDF로 저장하고, 넘친 쪽 id 목록을 돌려준다."""
    return _render_html(html_path, pdf_path, timeout_ms)["overflow"]
