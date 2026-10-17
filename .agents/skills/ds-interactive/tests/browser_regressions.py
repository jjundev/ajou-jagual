from pathlib import Path
from playwright.sync_api import sync_playwright
import sys
with sync_playwright() as pw:
 b=pw.chromium.launch();page=b.new_page(viewport={'width':1440,'height':900});page.goto(Path(sys.argv[1]).resolve().as_uri());page.wait_for_selector('[data-snapshot]')
 failures=[]
 page.locator('[data-action=play]').click();n=page.locator('input[type=number]').first;n.fill('7');page.wait_for_timeout(1100)
 if page.locator('#app').get_attribute('data-playing')!='false' or page.locator('#app').get_attribute('data-index')!='0':failures.append('editing input without blur must stop and reset')
 page.locator('[data-action=preset]').select_option('default')
 c=page.locator('[data-cell-id]').first;cid=c.get_attribute('data-cell-id');c.focus();page.keyboard.press('Enter')
 if page.evaluate('document.activeElement.dataset.cellId')!=cid:failures.append('keyboard cell activation must retain focus')
 page.locator('[data-action=next]').click()
 if not page.locator('output[data-step]').inner_text().startswith('1 /'):failures.append('visible step counter does not follow snapshot')
 page.locator('[data-action=last]').click();n=page.locator('input[type=number]').first;n.fill('');n.dispatch_event('change')
 if page.locator('#app').get_attribute('data-index')!='0':failures.append('invalid input does not reset displayed snapshot')
 page.locator('[data-action=preset]').select_option('default')
 for value in ['-99','99']:n.fill(value);n.dispatch_event('change')
 page.locator('[data-action=last]').click();n.fill('');n.dispatch_event('change')
 page.locator('[data-action=preset]').select_option('default');page.locator('[data-action=play]').click()
 if page.locator('#app').get_attribute('data-playing')!='true':failures.append('pending numeric blur must not swallow play click after preset reset')
 b.close();assert not failures,failures
print('browser regressions pass')
