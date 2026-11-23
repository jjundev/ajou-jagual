"""Check the preset selector's visible text, accessibility name and options."""
import sys
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def check_preset_label(page):
    preset = page.locator('[data-action=preset]')
    expect(preset).to_have_count(1)
    expect(preset).to_have_attribute('aria-label', '사례')
    assert preset.evaluate('''select => {
      const label = select.closest('label');
      return label && [...label.childNodes].every(node => node === select || !node.textContent.trim());
    }'''), 'Unexpected text beside the case selector'
    if preset.is_visible() and not preset.evaluate("select => !!select.closest('[inert],[aria-hidden=true]')"):
        expect(preset).to_have_accessible_name('사례')


def check_preset_pages(page, url):
    for width in (1440, 375):
        page.set_viewport_size({'width': width, 'height': 900 if width == 1440 else 812})
        page.goto(url)
        expect(page.locator('#app')).to_have_attribute('data-snapshot', 'initial')
        check_preset_label(page)
        preset = page.locator('[data-action=preset]')
        label = preset.locator('xpath=..')
        if label.get_attribute('hidden') is None and not page.get_by_role('combobox', name='사례', exact=True).count():
            page.locator('[data-action=toggle-left]').click()
        if label.get_attribute('hidden') is None:
            expect(preset).to_be_visible()
            expect(preset).to_have_accessible_name('사례')
            options = preset.locator('option')
            assert options.count() > 0
            assert preset.locator('option:checked').inner_text().strip()
            if options.count() > 1:
                selected = preset.select_option(index=1)
                expect(preset).to_have_value(selected[0])


if __name__ == '__main__':
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        with browser.new_context(offline=True) as context:
            check_preset_pages(context.new_page(), Path(sys.argv[1]).resolve().as_uri())
        browser.close()
