"""Read and navigate a complete graph history in the execution-code panel."""

import re

from playwright.sync_api import expect


def check_graph_history(page):
    history = page.locator('.study-history')
    listing = history.locator('.step-list')
    rows = listing.locator('[data-action=step]')
    expect(rows.first).to_have_attribute('aria-label', re.compile(r'^0 .+'))
    page.evaluate(r"""() => {
      function checkRows() {
       const list = document.querySelector('.study-history .step-list');
       const header = document.querySelector('.graph-history-source');
       const inputs = Object.fromEntries([...document.querySelectorAll('[data-input]')]
         .map(el => [el.dataset.input, el.type === 'number' ? el.valueAsNumber : el.value]));
       const trace = DSInteractive.compileScenario(DSInteractive.scenario, inputs);
       const entries = trace.lineSteps || trace.snapshots;
       const locations = entries.map(entry => entry.executed?.at ?? entry.at);
       const sourceIds = new Set(locations.map(location => location?.sourceId).filter(Boolean));
       const names = new Map(trace.sources.map(source => [source.id, source.label || source.id]));
       const rows = [...list.querySelectorAll('[data-action=step]')];
       const verify = (ok, message) => { if (!ok) throw Error('Graph history: ' + message); };
       verify(header.hidden === (sourceIds.size !== 1), 'wrong source heading visibility');
       if (!header.hidden) {
         verify(header.textContent === names.get([...sourceIds][0]), 'wrong source heading');
       }
       verify(rows.length === entries.length, 'row count');
       verify(list.clientHeight === 182 && list.scrollWidth <= list.clientWidth + 1, 'list size');
       for (const [i, row] of rows.entries()) {
         const loc = locations[i];
         const source = names.get(loc?.sourceId);
         const line = loc ? loc.line + '행' : '';
         const action = row.querySelector('.graph-history-action');
         const sourceText = row.querySelector('.graph-history-row-source');
         const label = row.getAttribute('aria-label');
         const style = getComputedStyle(row);
         verify(action.textContent === entries[i].title && label.includes(entries[i].title), 'row ' + i + ' action');
         if (line) {
           verify(row.querySelector('.graph-history-line').textContent === line && label.includes(line), 'row ' + i + ' location');
         }
         if (source) verify(label.includes(source), 'row ' + i + ' accessible source');
         verify((sourceText?.textContent || '') === (sourceIds.size > 1 ? source || '' : ''), 'row ' + i + ' source');
         const text = row.querySelector('.step-txt');
         const number = row.querySelector('.step-num');
         const box = row.getBoundingClientRect();
         const content = text.getBoundingClientRect();
         verify(style.padding === '12px 16px' && row.offsetHeight >= 60, 'row ' + i + ' padding');
         verify(number.getBoundingClientRect().left - box.left >= 16 &&
           box.right - content.right >= 16 &&
           content.top - box.top >= 12 && box.bottom - content.bottom >= 12, 'row ' + i + ' text inset');
         verify(style.columnGap === '6px' && getComputedStyle(text).columnGap === '5px', 'row ' + i + ' text gaps');
         verify(row.scrollWidth <= row.clientWidth + 1 && row.scrollHeight <= row.clientHeight + 1, 'row ' + i + ' overflow');
         for (const part of [action, sourceText].filter(Boolean)) {
           verify(part.scrollWidth <= part.clientWidth + 1 && part.scrollHeight <= part.clientHeight + 1 &&
             getComputedStyle(part).textOverflow !== 'ellipsis', 'row ' + i + ' truncated text');
         }
       }
      }

      const preset = document.querySelector('[data-action=preset]');
      const options = [...preset.options].filter(option => !option.disabled).map(option => option.value);
      const select = value => {
        preset.value = value;
        preset.dispatchEvent(new Event('change', {bubbles: true}));
      };
      for (const option of options) {
        select(option);
        checkRows();
      }
      select('default');
      const modes = [...document.querySelectorAll('[data-mode-value]')];
      const initialMode = modes.find(button => button.getAttribute('aria-pressed') === 'true');
      for (const mode of modes) {
        mode.click();
        if (mode.getAttribute('aria-pressed') !== 'true') throw Error('Graph history: mode did not change');
        checkRows();
      }
      initialMode?.click();
      checkRows();
    }""")
    if rows.count() < 3:
        return
    rows.nth(1).press('Enter')
    expect(rows.nth(1)).to_have_attribute('aria-pressed', 'true')
    page.locator('[data-action=scrub]').evaluate("""el => {
      el.value = el.max;
      el.dispatchEvent(new Event('input', {bubbles: true}));
    }""")
    expect(rows.last).to_have_attribute('aria-pressed', 'true')
    assert listing.evaluate("""list => {
      const a = list.getBoundingClientRect();
      const row = list.querySelector('[aria-pressed=true]').getBoundingClientRect();
      const offset = Math.max(0, (a.height - row.height) / 2);
      return Math.abs(row.top - a.top - offset) <= 2;
    }"""), 'last row follows the execution position'
    listing.evaluate('list => list.scrollTop = 0')
    follow = history.locator('.study-follow')
    expect(follow).to_be_visible()
    follow.press('Enter')
    expect(follow).to_be_hidden()
    expect(listing).to_be_focused()
    rows.first.evaluate('row => row.click()')
    expect(rows.first).to_have_attribute('aria-pressed', 'true')
    assert listing.evaluate('list => list.scrollTop') <= 1
