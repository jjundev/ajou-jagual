"""Verify theme behavior for a lesson loaded from disk or a local HTTP origin."""
import hashlib
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
from browser_preset import check_preset_pages


def check_theme(page, url):
    key = 'od-theme'
    page.emulate_media(color_scheme='dark')
    page.goto(url)
    page.evaluate('(key) => localStorage.removeItem(key)', key)
    page.reload()
    root = page.locator('html')
    button = page.locator('[data-action=theme]')

    def check_color(color):
        expect(root).to_have_css('color-scheme', color)
        other = '라이트' if color == 'dark' else '다크'
        expect(button).to_have_accessible_name(f'{other} 모드로 전환')
        expect(button).to_have_attribute('title', f'{other} 모드로 전환')
        expect(button.locator('circle')).to_have_count(1 if color == 'dark' else 0)

    def setting():
        return page.evaluate('(key) => localStorage.getItem(key)', key)

    check_color('dark')
    page.emulate_media(color_scheme='light')
    check_color('light')
    assert setting() is None
    button.click()
    check_color('dark')
    assert setting() == 'dark'
    page.reload()
    check_color('dark')
    page.emulate_media(color_scheme='dark')
    check_color('dark')
    page.emulate_media(color_scheme='light')
    check_color('dark')
    button.click()
    check_color('light')
    assert setting() is None
    page.emulate_media(color_scheme='dark')
    check_color('dark')
    button.click()
    check_color('light')
    assert setting() == 'light'
    page.reload()
    check_color('light')
    button.click()
    check_color('dark')
    assert setting() is None


def check_storage_unavailable(page, url):
    page.add_init_script("""Object.defineProperty(window, 'localStorage', {
      get() { throw new DOMException('Storage unavailable', 'SecurityError'); }
    });""")
    page.emulate_media(color_scheme='dark')
    page.goto(url)
    root = page.locator('html')
    expect(root).to_have_css('color-scheme', 'dark')
    page.locator('[data-action=theme]').click()
    expect(root).to_have_css('color-scheme', 'light')
    page.reload()
    expect(root).to_have_css('color-scheme', 'dark')


def check_cross_tab(browser, preview):
    with browser.new_context(color_scheme='light') as context:
        # Serve both pages from one intercepted origin to exercise real storage events.
        url = 'http://127.0.0.1/theme-test.html'
        context.route(url, lambda route: route.fulfill(path=preview, content_type='text/html'))
        context.route('**/pretendard.css', lambda route: route.fulfill(body='', content_type='text/css'))
        first, second = context.new_page(), context.new_page()
        first.goto(url)
        second.goto(url)
        first.locator('[data-action=theme]').click()
        expect(second.locator('html')).to_have_css('color-scheme', 'dark')
        second.locator('[data-action=theme]').click()
        expect(first.locator('html')).to_have_css('color-scheme', 'light')


def check_preview(browser, preview, *, check_preset=False):
    with browser.new_context(offline=True) as context:
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        if check_preset:
            check_preset_pages(page, preview.as_uri())
        check_theme(page, preview.as_uri())
        check_storage_unavailable(page, preview.as_uri())
        assert not errors, errors
    check_cross_tab(browser, preview)
    normalized = re.sub(rb'(data-ds-interactive-font href=")[^"]*', rb'\g<1>',
                        preview.read_bytes(), count=1)
    report = {'status': 'pass', 'build_sha256': hashlib.sha256(normalized).hexdigest(),
            'system': True, 'storage': True, 'storage_unavailable': True, 'cross_tab': True}
    if check_preset:
        report['preset_label_checked'] = True
    return report


def main(source, output, option=None):
    source = Path(source).resolve()
    preview = source / 'preview.html' if source.is_dir() else source
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        report = check_preview(browser, preview, check_preset=option == '--preset-label')
        browser.close()
    Path(output).write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main(*sys.argv[1:])
