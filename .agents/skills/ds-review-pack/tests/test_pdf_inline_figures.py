from pathlib import Path
import tempfile
from _util import REPO
from pdf_cards import freeze_inline_html


def test_scrollable_review_figure_is_fully_visible_on_printed_solution():
    from playwright.sync_api import sync_playwright
    raw = '<figure><div class="figure-scroll" style="max-width:100%;overflow-x:auto"><svg viewBox="0 0 800 400" style="width:800px;max-width:none;height:auto"><text x="760" y="40">rightmost node</text></svg></div></figure>'
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
        frozen = freeze_inline_html(raw, Path(tmp)/'source.html', Path(tmp)/'assets')
        browser = pw.chromium.launch(channel='chrome',headless=True)
        page = browser.new_page()
        page.set_content('<div style="width:240px">'+frozen+'</div>')
        scroll = page.locator('.figure-scroll')
        assert scroll.evaluate('(e)=>e.scrollWidth <= e.clientWidth + 1')
        assert page.locator('svg').get_attribute('viewBox') == '0 0 800 400'
        assert page.locator('svg text').text_content() == 'rightmost node'
        browser.close()
