"""실제 stage 브라우저 검토: python browser_check.py STAGE_DIR OUT_DIR"""
import sys, json, threading, http.server, functools
from pathlib import Path
from playwright.sync_api import sync_playwright

stage = Path(sys.argv[1]).resolve(); out = Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
html = 'stage_page.html'
name = next(stage.glob('*.html')).name
PIDS = [f'p{i}' for i in range(1, 9)]
SUBS = {'p1': ['main'], 'p2': ['main'], 'p3': ['main'], 'p4': ['1', '2', '3'], 'p5': ['main'],
        'p6': ['a', 'b', 'c'], 'p7': ['a', 'b', 'c'], 'p8': ['a', 'b', 'c']}
SECTIONS = ['understand', 'recall', 'start', 'solve', 'verify', 'pitfall', 'retry']


SERVER404 = []
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *a):
        line = fmt % a
        if ' 404 ' in line or '"GET' in line and '404' in line: SERVER404.append(line)


srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(H, directory=str(stage)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_port
base = f'http://127.0.0.1:{port}/'
url = base + name
report = {'port': port, 'runs': []}
problems = []


def chk(cond, msg):
    if not cond:
        problems.append(msg)
    return cond


with sync_playwright() as pw:
    try:
        browser = pw.chromium.launch()
    except Exception:
        browser = pw.chromium.launch(channel='chrome')
    for (w, h) in [(1280, 900), (1024, 900), (375, 812)]:
        for theme in ['light', 'dark']:
            tag = f'{w}x{h}-{theme}'
            ctx = browser.new_context(viewport={'width': w, 'height': h}, color_scheme=theme)
            page = ctx.new_page()
            logs, failed, external = [], [], []
            page.on('pageerror', lambda e: logs.append('pageerror ' + str(e)))
            page.on('console', lambda m: logs.append(m.text) if m.type == 'error' else None)
            page.on('requestfailed', lambda r: failed.append(r.url))
            page.on('response', lambda r: failed.append(f'{r.status} {r.url}') if r.status >= 400 else None)
            page.on('request', lambda r: external.append(r.url) if not r.url.startswith(base) and not r.url.startswith('data:') else None)
            page.goto(url + '#p1', wait_until='networkidle'); page.wait_for_timeout(300)
            run = {'tag': tag}
            run['dark_bg'] = page.evaluate("getComputedStyle(document.body).backgroundColor")
            run['katex_total'] = page.locator('.katex').count()
            run['katex_errors'] = page.locator('.katex-error').count()
            chk(run['katex_errors'] == 0, f'{tag} katex errors')
            # sum containers unique
            chk(page.evaluate('(()=>{const a=[...document.querySelectorAll("[id]")].map(e=>e.id);return a.length===new Set(a).size})()'), f'{tag} dup ids')
            per = {}
            for pid in PIDS:
                page.goto(url + '#' + pid); page.wait_for_timeout(150)
                d = {}
                d['visible'] = page.locator('#' + pid).is_visible()
                d['sections'] = [s for s in SECTIONS if page.locator(f'#{pid} [data-explanation="{s}"]').count() == 1]
                d['subparts_ok'] = all(page.locator(f'#{pid} [data-explanation="{s}"] [data-subpart="{sp}"]').count() == 1 for s in ('solve', 'verify') for sp in SUBS[pid])
                d['overflow_doc'] = page.evaluate('document.documentElement.scrollWidth>innerWidth')
                d['pre'] = page.locator(f'#{pid} pre').count()
                d['pre_bad'] = page.evaluate(f"""[...document.querySelectorAll('#{pid} pre')].filter(e=>!['auto','scroll'].includes(getComputedStyle(e).overflowX)).length""")
                d['pre_scrolling'] = page.evaluate(f"""[...document.querySelectorAll('#{pid} pre')].filter(e=>e.scrollWidth>e.clientWidth).length""")
                d['tables'] = page.locator(f'#{pid} table').count()
                d['katex'] = page.locator(f'#{pid} .katex').count()
                d['katex_inline_scroll'] = page.evaluate(f"""[...document.querySelectorAll('#{pid} .katex')].filter(e=>!e.closest('.katex-display')&&['auto','scroll'].includes(getComputedStyle(e).overflowX)).length""")
                d['katex_display_scrollbar'] = page.evaluate(f"""[...document.querySelectorAll('#{pid} .katex-display')].filter(e=>e.scrollWidth>e.clientWidth+1).length""")
                d['links'] = page.evaluate(f"""[...document.querySelectorAll('#{pid} a[href]')].map(a=>a.getAttribute('href'))""")
                if w >= 1024:
                    d['prob_panel'] = page.locator(f'#panel-prob .probs [data-problem-for="{pid}"]').is_visible()
                    d['orig_tab'] = page.locator('#tab-original').is_visible()
                    if d['orig_tab']:
                        page.locator('#tab-original').click(); page.wait_for_timeout(100)
                        d['orig_shown'] = page.locator(f'#tabpanel-original details.original[data-original-problem="{pid}"]').is_visible()
                        page.locator('#tab-problem').click(); page.wait_for_timeout(100)
                    # problem panel inner overflow (code/svg/table)
                    d['prob_svg'] = page.locator(f'#panel-prob [data-problem-for="{pid}"] svg').count()
                else:
                    t = page.locator(f'#{pid} .problem-toggle')
                    d['toggle'] = t.count() == 1 and t.get_attribute('aria-expanded') == 'false'
                    tb = t.bounding_box(); ub = page.locator(f'#{pid} [data-explanation="understand"]').bounding_box()
                    d['toggle_above'] = tb is not None and ub is not None and tb['y'] < ub['y']
                    t.click(); page.wait_for_timeout(120)
                    d['prob_open'] = page.locator(f'#{pid} [data-problem-for="{pid}"]').is_visible()
                    d['overflow_doc_open'] = page.evaluate('document.documentElement.scrollWidth>innerWidth')
                    d['prob_pre_bad'] = page.evaluate(f"""[...document.querySelectorAll('#{pid} [data-problem-for] pre')].filter(e=>!['auto','scroll'].includes(getComputedStyle(e).overflowX)).length""")
                    t.click(); page.wait_for_timeout(80)
                # summary
                page.locator('#toggle-right').click(); page.wait_for_timeout(250)
                d['sum_visible'] = page.locator('#panel-right').is_visible()
                d['sum_groups_visible'] = page.locator('#panel-right .summary-group:visible').count()
                d['sum_text'] = page.locator('#panel-right .summary-group:visible').first.inner_text()[:40] if d['sum_groups_visible'] else ''
                if w < 800:
                    page.locator('#panel-right [data-panel-close]').click()
                else:
                    page.locator('#toggle-right').click()
                page.wait_for_timeout(200)
                chk(d['visible'] and len(d['sections']) == 7 and d['subparts_ok'], f'{tag} {pid} sections/subparts')
                chk(not d['overflow_doc'], f'{tag} {pid} doc overflow')
                chk(d['pre_bad'] == 0 and d['katex_inline_scroll'] == 0 and d['katex_display_scrollbar'] == 0, f'{tag} {pid} pre/katex scroll')
                chk(d['sum_visible'] and d['sum_groups_visible'] >= 1, f'{tag} {pid} summary')
                if w >= 1024:
                    chk(d['prob_panel'] and d['orig_tab'] and d.get('orig_shown'), f'{tag} {pid} problem panel/original')
                else:
                    chk(d['toggle'] and d['toggle_above'] and d['prob_open'] and not d['overflow_doc_open'] and d['prob_pre_bad'] == 0, f'{tag} {pid} mobile toggle')
                per[pid] = d
            run['per'] = per
            # pager walk
            page.goto(url, wait_until='networkidle'); page.wait_for_timeout(150)
            seen = []
            for _ in range(10):
                vis = [p for p in PIDS if page.locator('#' + p).is_visible()]
                seen.append(vis[0] if vis else None)
                nb = page.locator('#pager-next')
                if nb.is_disabled() if nb.count() else True:
                    break
                nb.click(); page.wait_for_timeout(100)
            run['pager_next_seq'] = seen
            back = []
            for _ in range(10):
                pb = page.locator('#pager-prev')
                if pb.is_disabled():
                    break
                pb.click(); page.wait_for_timeout(100)
                vis = [p for p in PIDS if page.locator('#' + p).is_visible()]
                back.append(vis[0] if vis else None)
            run['pager_prev_seq'] = back
            chk([s for s in seen if s] == PIDS, f'{tag} pager next {seen}')
            # TOC
            if page.locator('#toggle-left').get_attribute('aria-expanded') == 'false':
                page.locator('#toggle-left').click(); page.wait_for_timeout(250)
            toc = []
            for pid in PIDS:
                a = page.locator(f'#panel-left a[href="#{pid}"]')
                if a.count() and a.first.is_visible():
                    a.first.click(); page.wait_for_timeout(150)
                    toc.append(page.locator('#' + pid).is_visible())
                    if w < 1024 and page.locator('#toggle-left').get_attribute('aria-expanded') == 'false':
                        page.locator('#toggle-left').click(); page.wait_for_timeout(200)
                else:
                    toc.append(False)
            run['toc'] = toc
            if w < 1024 and page.locator('#toggle-left').get_attribute('aria-expanded') == 'true':
                cl = page.locator('#panel-left [data-panel-close]')
                (cl.first.click() if cl.count() else page.keyboard.press('Escape')); page.wait_for_timeout(250)
                if page.locator('#toggle-left').get_attribute('aria-expanded') == 'true':
                    page.locator('#toggle-left').click(force=True); page.wait_for_timeout(250)
            chk(all(toc), f'{tag} toc {toc}')
            # figure zoom on p2 problem svg (desktop panel / mobile inline)
            page.goto(url + '#p2'); page.wait_for_timeout(150)
            if w < 1024:
                page.locator('#p2 .problem-toggle').click(); page.wait_for_timeout(100)
                svg = page.locator('#p2 [data-problem-for="p2"] svg').first
            else:
                svg = page.locator('#panel-prob [data-problem-for="p2"] svg').first
            svg.click(); page.wait_for_timeout(200)
            run['figure_zoom'] = page.locator('dialog.figure-sheet[open]').count() == 1
            page.keyboard.press('Escape'); page.wait_for_timeout(150)
            run['figure_closed'] = page.locator('dialog.figure-sheet[open]').count() == 0
            chk(run['figure_zoom'] and run['figure_closed'], f'{tag} figure zoom')
            # theme toggle roundtrip
            page.locator('#theme-toggle').click(); page.wait_for_timeout(100)
            run['theme_after_toggle'] = page.evaluate("document.documentElement.getAttribute('data-theme')")
            page.locator('#theme-toggle').click(); page.wait_for_timeout(100)
            if w == 1280 and theme == 'light':
                box = lambda s: page.locator(s).bounding_box()
                page.goto(url + '#p1'); page.wait_for_timeout(150)
                dock = {}
                dock['default'] = page.locator('.layout').get_attribute('data-prob-dock')
                dock['left_and_toc'] = page.locator('#panel-left').is_visible() and page.locator('#panel-prob').is_visible()
                page.locator('#panel-prob [data-dock="right"]').click(); page.wait_for_timeout(200)
                dock['right'] = page.locator('.layout').get_attribute('data-prob-dock')
                page.locator('#toggle-right').click(); page.wait_for_timeout(250)
                dock['right_with_summary'] = page.locator('#panel-prob').is_visible() and page.locator('#panel-right').is_visible()
                page.locator('#toggle-right').click(); page.wait_for_timeout(250)
                page.locator('#panel-prob [data-dock="float"]').click(); page.wait_for_timeout(200)
                dock['float'] = page.locator('.layout').get_attribute('data-prob-dock')
                F = box('#panel-prob'); M = box('#panel-prob .float-move')
                page.mouse.move(M['x'] + M['width'] / 2, M['y'] + M['height'] / 2); page.mouse.down()
                page.mouse.move(M['x'] + M['width'] / 2 - 150, M['y'] + M['height'] / 2 + 80, steps=8); page.mouse.up(); page.wait_for_timeout(150)
                F2 = box('#panel-prob'); dock['moved'] = abs(F2['x'] - (F['x'] - 150)) <= 2 and abs(F2['y'] - (F['y'] + 80)) <= 2
                R = box('#panel-prob .float-resize')
                page.mouse.move(R['x'] + R['width'] / 2, R['y'] + R['height'] / 2); page.mouse.down()
                page.mouse.move(R['x'] + 80, R['y'] + 60, steps=6); page.mouse.up(); page.wait_for_timeout(150)
                F3 = box('#panel-prob'); dock['resized'] = F3['width'] > F2['width'] + 40
                M = box('#panel-prob .float-move')
                page.mouse.move(M['x'] + 5, M['y'] + 5); page.mouse.down(); page.mouse.move(M['x'] + 5, M['y'] + 3000, steps=6); page.mouse.up(); page.wait_for_timeout(150)
                F4 = box('#panel-prob'); dock['clamped'] = F4['y'] + F4['height'] <= box('.pager')['y'] + 1 and F4['x'] >= 0 and F4['x'] + F4['width'] <= 1280
                dock['saved'] = page.evaluate("localStorage.getItem('od-panels:explain:v2:prob')")
                page.reload(); page.wait_for_timeout(200)
                dock['float_after_reload'] = page.locator('.layout').get_attribute('data-prob-dock')
                page.locator('#panel-prob [data-dock="left"]').click(); page.wait_for_timeout(200)
                dock['back_left'] = page.locator('.layout').get_attribute('data-prob-dock')
                # 1023 boundary
                page.set_viewport_size({'width': 1023, 'height': 900}); page.wait_for_timeout(200)
                dock['at1023_panel_hidden'] = page.locator('#panel-prob').is_hidden() and page.locator('#p1 .problem-toggle').count() == 1
                page.set_viewport_size({'width': 1024, 'height': 900}); page.wait_for_timeout(200)
                dock['at1024_panel_visible'] = page.locator('#panel-prob').is_visible()
                page.set_viewport_size({'width': 1280, 'height': 900}); page.wait_for_timeout(200)
                # closed choice persists
                page.locator('#toggle-prob').click(); page.wait_for_timeout(150)
                page.reload(); page.wait_for_timeout(200)
                dock['closed_persists'] = page.locator('#panel-prob').is_hidden()
                page.locator('#toggle-prob').click(); page.wait_for_timeout(150)
                run['dock'] = dock
                chk(dock['default'] == 'left' and dock['left_and_toc'] and dock['right'] == 'right' and dock['right_with_summary'] and dock['float'] == 'float'
                    and dock['moved'] and dock['resized'] and dock['clamped'] and dock['float_after_reload'] == 'float' and dock['back_left'] == 'left'
                    and dock['at1023_panel_hidden'] and dock['at1024_panel_visible'] and dock['closed_persists'], f'dock {dock}')
                # print media keeps problem + original
                page.goto(url + '#p1'); page.wait_for_timeout(150)
                page.emulate_media(media='print'); page.wait_for_timeout(150)
                run['print'] = page.locator('#p1 > [data-problem-for="p1"]').is_visible() and page.locator('#p1 > [data-problem-for="p1"] details.original[open]').is_visible()
                page.emulate_media(media='screen'); page.wait_for_timeout(150)
                chk(run['print'], 'print')
            page.goto(url + '#p7'); page.wait_for_timeout(200)
            page.screenshot(path=str(out / f'{tag}-p7.png'), full_page=False)
            page.goto(url + '#p1'); page.wait_for_timeout(200)
            page.screenshot(path=str(out / f'{tag}-p1.png'), full_page=False)
            run['console_errors'] = logs; run['failed'] = failed; run['external'] = external
            chk(not logs and not failed and not external, f'{tag} logs/failed/external {logs} {failed} {external}')
            report['runs'].append(run)
            ctx.close()
    browser.close()
srv.shutdown()
report['problems'] = problems
report['server_404'] = SERVER404
print('SERVER404', SERVER404)
(out / 'browser-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1))
print('PROBLEMS:', len(problems))
for p in problems: print(' -', p)
