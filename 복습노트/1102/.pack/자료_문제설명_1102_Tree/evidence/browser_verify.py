"""Playwright 6-viewport browser verification for 1102 (Tree)."""
import json
import subprocess
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_DIR = Path(__file__).resolve().parent
RUN_REL = 'tmp/ds-problem-explain-1102'
PORT = 41102

VIEWPORTS = [
    (1280, 900, 'light'),
    (1280, 900, 'dark'),
    (1024, 900, 'light'),
    (1024, 900, 'dark'),
    (375, 812, 'light'),
    (375, 812, 'dark'),
]

def main():
    cmd = [
        sys.executable,
        str(ROOT / '.agents' / 'skills' / 'ds-problem-explain' / 'scripts' / 'mpe_cli.py'),
        'preview', '--run', RUN_REL, '--port', str(PORT),
    ]
    proc = subprocess.Popen(
        cmd, cwd=str(ROOT),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding='utf-8'
    )
    report = {'port': PORT, 'combinations': [], 'all_passed': True}
    try:
        url = None
        deadline = time.time() + 15
        while time.time() < deadline:
            line = proc.stdout.readline().strip()
            if line.startswith('http://'):
                url = line
                break
        if not url:
            err = proc.stderr.read()
            raise RuntimeError(f'Preview server failed to output URL: {err}')
        report['url'] = url

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                for width, height, theme in VIEWPORTS:
                    context = browser.new_context(
                        viewport={'width': width, 'height': height},
                        color_scheme=theme,
                    )
                    page = context.new_page()
                    console_errors = []
                    page_errors = []
                    bad_responses = []
                    external_requests = []

                    page.on('console', lambda m: console_errors.append(m.text) if m.type == 'error' else None)
                    page.on('pageerror', lambda e: page_errors.append(str(e)))
                    page.on('response', lambda r: bad_responses.append((r.status, r.url)) if r.status >= 400 and not r.url.endswith('/favicon.ico') else None)
                    page.on('request', lambda req: external_requests.append(req.url) if not req.url.startswith(('http://127.0.0.1:', 'data:', 'blob:')) else None)

                    page.goto(url, wait_until='networkidle')
                    # Force explicit theme attribute check via #theme-toggle if needed
                    cur_theme = page.evaluate('document.documentElement.getAttribute("data-theme")')
                    if cur_theme != theme:
                        page.click('#theme-toggle')
                        page.wait_for_timeout(50)

                    # Navigate through all 12 problems and inspect structure + KaTeX + overflow + SVGs + imgs
                    problems_checked = []
                    for i in range(1, 13):
                        pid = f'p{i}'
                        page.goto(f'{url}#{pid}', wait_until='domcontentloaded')
                        page.wait_for_timeout(80)
                        info = page.evaluate('''(pid) => {
                            const art = document.getElementById(pid);
                            const layers = art ? art.querySelectorAll(':scope > [data-explanation]').length : 0;
                            const katexCount = art ? art.querySelectorAll('.katex').length : 0;
                            const katexErr = document.querySelectorAll('.katex-error').length;
                            const imgs = Array.from(document.querySelectorAll('img')).map(im => ({src: im.src, w: im.naturalWidth}));
                            const svgs = art ? Array.from(art.querySelectorAll('svg')).map(s => s.getBoundingClientRect().width) : [];
                            const docOverflow = document.documentElement.scrollWidth > window.innerWidth;
                            const inlineMathScroll = Array.from(document.querySelectorAll('.katex:not(.katex-display .katex)')).filter(el => {
                                const cs = getComputedStyle(el);
                                return cs.overflowX === 'auto' || cs.overflowX === 'scroll';
                            }).length;
                            return {
                                visible: art ? getComputedStyle(art).display !== 'none' : false,
                                layers, katexCount, katexErr, imgs, svgs, docOverflow, inlineMathScroll,
                                scrollWidth: document.documentElement.scrollWidth,
                                innerWidth: window.innerWidth
                            };
                        }''', pid)
                        assert info['visible'], f'{pid} not visible at {width}x{height} {theme}'
                        assert info['layers'] == 7, f'{pid} layers={info["layers"]}'
                        assert info['katexErr'] == 0, f'{pid} katexErr={info["katexErr"]}'
                        assert not info['docOverflow'], f'{pid} horizontal overflow {info["scrollWidth"]} > {info["innerWidth"]}'
                        assert info['inlineMathScroll'] == 0, f'{pid} inlineMathScroll={info["inlineMathScroll"]}'
                        assert all(im['w'] > 0 for im in info['imgs']), f'{pid} broken img: {info["imgs"]}'
                        problems_checked.append({'id': pid, 'katex': info['katexCount'], 'svgs': len(info['svgs'])})

                    # Check UI controls: summary panel, original tab, dock modes / collapse toggle
                    page.goto(f'{url}#p3', wait_until='domcontentloaded')
                    page.wait_for_timeout(80)

                    ui_state = {}
                    # Summary toggle
                    page.click('#toggle-right')
                    page.wait_for_timeout(50)
                    ui_state['right_open'] = page.evaluate('document.querySelector(".layout").getAttribute("data-right")')
                    ui_state['sum_count'] = page.evaluate('document.querySelectorAll("#sum-for .summary-group").length')
                    assert ui_state['sum_count'] >= 1, 'summary-group missing when right panel opened'

                    if width >= 1024:
                        # Desktop: check left/prob open by default, original tab, prob-dock switching
                        ui_state['default_left'] = page.evaluate('document.querySelector(".layout").getAttribute("data-left")')
                        ui_state['default_prob'] = page.evaluate('document.querySelector(".layout").getAttribute("data-prob")')
                        # Original tab
                        orig_hidden = page.evaluate('document.getElementById("tab-original").hidden')
                        assert not orig_hidden, 'tab-original should be visible on p3'
                        page.click('#tab-original')
                        page.wait_for_timeout(50)
                        ui_state['orig_tab_selected'] = page.evaluate('document.getElementById("tab-original").getAttribute("aria-selected")')
                        assert ui_state['orig_tab_selected'] == 'true'
                        page.click('#tab-problem')
                        page.wait_for_timeout(50)

                        # Dock modes: right, float, left
                        for dock in ('right', 'float', 'left'):
                            page.click(f'.prob-dock [data-dock="{dock}"]')
                            page.wait_for_timeout(50)
                            cur_dock = page.evaluate('document.querySelector(".layout").getAttribute("data-prob-dock")')
                            assert cur_dock == dock, f'dock mismatch {cur_dock} != {dock}'
                        ui_state['dock_tested'] = ['right', 'float', 'left']

                        # Close right panel first so fit() has room, then test collapse toggle on left panel
                        if page.evaluate('document.querySelector(".layout").getAttribute("data-right")') == 'open':
                            page.click('#toggle-right')
                            page.wait_for_timeout(50)
                        before_left = page.evaluate('document.querySelector(".layout").getAttribute("data-left")')
                        page.click('#toggle-left')
                        page.wait_for_timeout(50)
                        after_left = page.evaluate('document.querySelector(".layout").getAttribute("data-left")')
                        assert after_left != before_left, f'toggle-left did not flip {before_left}'
                        page.click('#toggle-left')
                        page.wait_for_timeout(50)
                        assert page.evaluate('document.querySelector(".layout").getAttribute("data-left")') == before_left
                        ui_state['left_toggle'] = f'{before_left}->{after_left}->{before_left}'
                    else:
                        # Mobile 375x812: close summary drawer first, then test problem-toggle collapse/expand
                        page.click('#panel-right [data-panel-close]')
                        page.wait_for_timeout(50)
                        prob_btn = page.locator('#p3 .problem-toggle')
                        assert prob_btn.count() == 1, 'mobile .problem-toggle missing'
                        prob_btn.click()
                        page.wait_for_timeout(50)
                        expanded = prob_btn.get_attribute('aria-expanded')
                        assert expanded == 'true', f'mobile problem-toggle aria-expanded={expanded}'
                        ui_state['mobile_prob_toggle'] = expanded
                        prob_btn.click()

                    assert not console_errors, f'console errors: {console_errors}'
                    assert not page_errors, f'page errors: {page_errors}'
                    assert not bad_responses, f'bad responses: {bad_responses}'
                    assert not external_requests, f'external requests: {external_requests}'

                    report['combinations'].append({
                        'viewport': f'{width}x{height}',
                        'theme': theme,
                        'problems_checked': len(problems_checked),
                        'console_errors': 0,
                        'page_errors': 0,
                        'http_errors': 0,
                        'external_requests': 0,
                        'ui_state': ui_state,
                        'passed': True,
                    })
                    context.close()
            finally:
                browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    (EVIDENCE_DIR / 'browser-checks.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print('browser_verify: ALL 6 COMBINATIONS PASSED')

if __name__ == '__main__':
    main()
