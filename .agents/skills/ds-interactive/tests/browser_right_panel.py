"""Check the example copy and loaded type in the right panel."""
import hashlib
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


VIEWPORTS = ((1440, 900), (1280, 800), (1279, 800), (375, 812), (320, 812))


def check_change_hierarchy(panel):
    styles = panel.evaluate("""panel => {
      const textStyle = element => {
        const style = getComputedStyle(element);
        return [style.fontSize, style.fontWeight];
      };
      const detail = [...panel.querySelectorAll('h2')].find(heading => heading.textContent === '실행 상태 상세');
      const headings = [...panel.querySelectorAll('.graph-state h3, .panel-changes-title')].map(textStyle);
      const scrub = document.querySelector('[data-action=scrub]');
      const setStep = step => {
        scrub.value = step;
        scrub.dispatchEvent(new Event('input', {bubbles: true}));
      };
      const start = scrub.value;
      const rowsByCount = {};
      for (let step = 0; step <= Math.min(Number(scrub.max), 30); step++) {
        setStep(step);
        const rows = [...panel.querySelectorAll('.changes > .change')];
        if (!rows.length) continue;
        const key = rows.length === 1 ? 'single' : 'multiple';
        if (!rowsByCount[key]) {
          rowsByCount[key] = rows.map(row => ({
            label: textStyle(row.querySelector('strong')),
            value: textStyle(row.querySelector('div')),
            border: getComputedStyle(row).borderBottomWidth,
          }));
        }
        if (rowsByCount.single && rowsByCount.multiple) break;
      }
      setStep(start);
      const example = panel.querySelector('.provenance, .tree-example');
      const changeSection = getComputedStyle(panel.querySelector('.changes').parentElement);
      return {
        detail: detail && textStyle(detail),
        headings,
        rowsByCount,
        sectionPadding: [changeSection.paddingBlockStart, changeSection.paddingBlockEnd],
        exampleBorder: getComputedStyle(example).borderTopWidth,
      };
    }""")
    assert styles['detail'] in (None, ['21px', '700']), styles
    assert styles['headings'] and all(style == ['16px', '700'] for style in styles['headings']), styles
    assert styles['sectionPadding'] == ['8px', '8px'], styles
    assert styles['exampleBorder'] == '1px', styles
    for rows in styles['rowsByCount'].values():
        assert all(row['label'] == ['14px', '600'] and row['value'] == ['14px', '400'] for row in rows), rows
        assert [row['border'] for row in rows] == ['1px'] * (len(rows) - 1) + ['0px'], rows


def check_right_panel(page, expected):
    panel = page.locator('#panel-right')
    toggle = page.locator('[data-action=toggle-right]')
    was_open = toggle.get_attribute('aria-expanded') == 'true'
    if not was_open:
        toggle.click()
    changes = panel.locator('.changes')
    if page.locator('#app').get_attribute('data-kind') == 'c-tree' and not page.locator('#app').get_attribute('data-ui-version'):
        assert changes.count() == 0
    else:
        heading = panel.get_by_role('heading', level=3, name='변경 전 → 후')
        assert heading.count() == 1 and heading.is_visible()
        assert changes.is_visible() and changes.inner_text().strip()
        assert changes.evaluate("el => !el.closest('details')")
        assert panel.locator('summary', has_text='변경 전 → 후').count() == 0
        stack = panel.locator('.graph-state h3', has_text='호출 스택').first
        if stack.count():
            def style(locator):
                return locator.evaluate("""el => {
                  const s = getComputedStyle(el);
                  return [s.fontFamily, s.fontSize, s.fontWeight, s.lineHeight, s.marginBottom];
                }""")
            assert style(heading) == style(stack)
        check_change_hierarchy(panel)

    parameters = page.evaluate(r"""() => {
      if (DSInteractive.scenario.kind !== 'c-graph') return [];
      const scenario = DSInteractive.scenario;
      const input = Object.fromEntries(scenario.inputs.map(field => [field.key, field.default]));
      const {snapshots} = DSInteractive.compileScenario(scenario, input);
      const bindings = [
        [snapshots.findIndex(step => step.writes.some(write =>
          /^GraphType\s*\*$/.test(step.state.cells[write.cellId]?.type) &&
          write.before === null && write.after?.kind === 'pointer' && write.after.target !== null)),
          '(그래프 포인터)', '그래프 주소'],
      ];
      const vertex = snapshots.findIndex(step => step.title === '정점 번호 전달');
      if (vertex >= 0) {
        const write = snapshots[vertex].writes.find(write => write.before === null && write.after?.kind === 'int');
        bindings.push([vertex, '(정점 번호)', String(write.after.value)]);
      }
      const declaration = snapshots.findIndex(step => step.title === '행 검사 시작' &&
        step.writes.some(write => write.before === null && write.after?.kind === 'int'));
      if (declaration >= 0) {
        const write = snapshots[declaration].writes[0];
        bindings.push([declaration, snapshots[declaration].state.cells[write.cellId].name,
          String(write.after.value), '선언 전']);
      }
      return bindings.filter(([step]) => step >= 0);
    }""")
    if parameters:
        scrub = page.locator('[data-action=scrub]')
        def move_to(step):
            scrub.evaluate("""(el, step) => {
              el.value = step;
              el.dispatchEvent(new Event('input', {bubbles: true}));
            }""", step)

        for step, label, value, *origin in parameters:
            move_to(step)
            row = panel.locator('.change', has_text=label)
            assert row.count() == 1 and f"{origin[0] if origin else '전달 전'} → {value}" in row.inner_text()
        move_to(0)
    example = panel.locator('details').filter(has=page.locator('summary', has_text=re.compile('^예제 정보$')))
    assert example.count() == 1 and not example.evaluate('el => el.open'), 'Example info starts collapsed'
    example.locator('summary').click()
    summary = example.locator('.example-summary')
    assert summary.count() == 1 and summary.inner_text() == expected, 'Expected a single learning cue'
    assert re.fullmatch(r'[^\n]+[.!?]', expected) and len(re.findall(r'[.!?](?=\s|$)', expected)) == 1, expected
    assert [line for line in example.inner_text().splitlines() if line.strip()] == ['예제 정보', expected], 'Unexpected copy in example info'
    assert panel.locator('.provenance-text, .takeaway').count() == 0
    assert summary.evaluate('el => el.scrollWidth <= el.clientWidth'), 'Example text overflows'

    fonts = panel.evaluate(r"""async panel => {
      await document.fonts.ready;
      const checks = [...panel.querySelectorAll('*')].filter(el =>
        el instanceof HTMLElement && el.checkVisibility()).map(async el => {
        const sample = [...el.childNodes].filter(node => node.nodeType === Node.TEXT_NODE)
          .map(node => node.textContent.trim()).join(' ');
        if (!/[\p{L}\p{N}]/u.test(sample)) return null;
        const style = getComputedStyle(el);
        const faces = await document.fonts.load(`${style.fontWeight} ${style.fontSize} Pretendard`, sample);
        return {
          sample,
          pass: style.fontFamily.split(',')[0].replaceAll('"', '').trim() === 'Pretendard' &&
            faces.some(face => face.status === 'loaded') &&
            (!/^\[?\d+\]?$/.test(sample) || style.fontVariantNumeric.includes('tabular-nums')),
        };
      });
      return (await Promise.all(checks)).filter(Boolean);
    }""")
    assert fonts and all(font['pass'] for font in fonts), fonts

    example.locator('summary').click()
    if not was_open:
        page.keyboard.press('Escape')
    return {'right_panel_checked': True}


def check_preview(browser, preview, expected):
    normalized = re.sub(rb'(data-ds-interactive-font href=")[^"]*', rb'\g<1>', preview.read_bytes(), count=1)
    digest = hashlib.sha256(normalized).hexdigest()
    results = []
    errors = []
    for mobile in (False, True):
        context = browser.new_context(offline=True, is_mobile=mobile, has_touch=mobile, reduced_motion='reduce')
        try:
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            for width, height in VIEWPORTS:
                if (width <= 375) != mobile:
                    continue
                page.set_viewport_size({'width': width, 'height': height})
                for theme in ('light', 'dark'):
                    page.emulate_media(color_scheme=theme)
                    page.goto(preview.resolve().as_uri())
                    assert page.locator('html').get_attribute('data-theme') == theme
                    checks = check_right_panel(page, expected)
                    results.append(dict(checks, status='pass', viewport=[width, height], theme=theme, build_sha256=digest))
        finally:
            context.close()
    assert not errors, (preview, errors)
    return {'status': 'pass', 'results': results}


if __name__ == '__main__':
    entries = json.loads(Path(sys.argv[1]).read_text())
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for entry in entries:
            preview = Path(entry['preview'])
            report = check_preview(browser, preview, entry['summary'])
            if entry.get('evidence'):
                Path(entry['evidence']).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
            print(preview.parent.name, len(report['results']), flush=True)
