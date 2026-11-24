"""Exercise the single header selector and all merged controls in Chromium."""
import hashlib
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def check_header_selector(page):
    return page.evaluate("""() => {
      const app = document.querySelector('#app');
      const header = app.querySelector('.topbar');
      const visible = [...app.querySelectorAll('select')].filter(el => el.checkVisibility());
      const select = visible[0];
      if (visible.length !== 1 || !header.contains(select) || !select.getAttribute('aria-label')) {
        throw Error('Expected one visible, named selector in the header');
      }
      const box = select.getBoundingClientRect();
      if (box.width < 44 || box.height < 40 || box.left < 0 || box.right > innerWidth + 1 ||
          box.bottom > header.getBoundingClientRect().bottom + 1 ||
          !select.contains(document.elementFromPoint(box.x + box.width / 2, box.y + box.height / 2))) {
        throw Error('Header selector is clipped, covered or too small');
      }
      const set = (field, value, type = 'change') => {
        field.value = value;
        field.dispatchEvent(new Event(type, {bubbles: true}));
      };
      const assert = (ok, message) => { if (!ok) throw Error(message); };
      const {inputs, presets} = DSInteractive.scenario;
      const defaults = Object.fromEntries(inputs.map(field => [field.key, field.default]));
      const controls = [...app.querySelectorAll('[data-input]')];
      const read = field => field.value;
      const expected = input => controls.every(field => read(field) === String(input[field.dataset.input]));
      if (select.dataset.input) {
        for (const option of select.options) {
          set(select, option.value);
          assert(select.value === option.value, 'Setup selection did not apply');
        }
      } else {
        const cases = [{id: 'default', input: defaults}, ...presets];
        for (const {id, input} of cases) {
          set(select, id);
          assert(expected(input), 'Preset did not apply: ' + id);
        }
        set(select, 'default');
        const direct = [...select.querySelectorAll('option[data-header-choice]')];
        if (direct.length) {
          const savedLabels = new Set([...select.options].filter(option => !option.hasAttribute('data-header-choice'))
            .map(option => option.label));
          assert(direct.every(option => !savedLabels.has(option.label)), 'A direct option shares a saved case label');
          const enums = controls.filter(field => field.tagName === 'SELECT' && field.closest('label').hidden &&
            field.dataset.input !== 'mode');
          const size = enums.reduce((count, field) => count * field.options.length, 1);
          const combinations = new Set();
          const number = controls.find(field => field.type === 'number');
          if (number) set(number, Number(number.value) === Number(number.max) ? number.min : number.max, 'input');
          const numericValue = number?.value;
          for (const option of direct) {
            set(select, option.value);
            assert(select.value === option.value, 'Direct option is not displayed');
            assert(number?.value === numericValue, 'Direct option changed the number');
            combinations.add(JSON.stringify(enums.map(read)));
          }
          assert(combinations.size === size && direct.length === size, 'An input combination is missing');
          if (number) {
            set(number, '', 'input');
            assert(select.selectedOptions[0].disabled &&
              enums.every(field => select.selectedOptions[0].label.includes(field.selectedOptions[0].label)) &&
              app.querySelector('[data-action=play]').disabled, 'The custom option lost execution context');
          }
        }
        set(select, 'default');
        assert(expected(defaults), 'Default inputs were not restored');
      }
      return {header_selector_checked: true, input_behavior_checked: true};
    }""")


def check_preview(page, preview):
    normalized = re.sub(rb'(data-ds-interactive-font href=")[^"]*', rb'\g<1>', preview.read_bytes(), count=1)
    digest = hashlib.sha256(normalized).hexdigest()
    results = []
    for width, height in ((1440, 900), (1280, 800), (1279, 800), (375, 812), (320, 812)):
        for theme in ('light', 'dark'):
            page.emulate_media(color_scheme=theme)
            page.set_viewport_size({'width': width, 'height': height})
            page.goto(preview.resolve().as_uri())
            page.evaluate('document.fonts.ready')
            checks = check_header_selector(page)
            results.append(dict(checks, status='pass', viewport=[width, height], theme=theme, build_sha256=digest))
    return {'status': 'pass', 'results': results}


if __name__ == '__main__':
    manifest = json.loads(Path(sys.argv[1]).read_text())
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(offline=True)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        for entry in manifest:
            preview = Path(entry['preview'])
            report = check_preview(page, preview)
            assert not errors, (preview, errors)
            if entry.get('evidence'):
                Path(entry['evidence']).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
            print(entry.get('name', preview.name), len(report['results']), flush=True)
