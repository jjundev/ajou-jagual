"""Check one rerendered problem explanation in a real browser before publish.

Usage: problem-panel-browser.py RUN_BUCKET OUT_JSON
RUN_BUCKET is the rerender run's pack folder (holds source.json and stage.json).
Applies the ds-problem-explain browser acceptance checks for the problem panel to every
problem, compares each panel copy with the source card, and leaves screenshots next to OUT_JSON.
Exits non-zero on the first failed check.
"""
import functools, hashlib, http.server, json, re, sys, threading
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / '.agents/skills/ds-problem-explain'
sys.path[:0] = [str(SKILL / 'scripts')]
from mpe_shared import compact, parse  # noqa: E402
from mpe_source import load_source  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

COMBOS = [(1280, 900, 'light'), (1280, 900, 'dark'), (1024, 768, 'light'), (375, 812, 'light'), (375, 812, 'dark')]


def tags(markup, name): return len(re.findall(rf'<{name}\b', markup))


def source_fidelity(pack, html_text):
    """Each panel copy carries the card's statement and original text with the same code blocks and figures."""
    doc = parse(html_text)
    one = lambda key, pid: [n for n in doc.find_all(lambda n: n.attrs.get(key) == pid)]
    for p in pack.problems:
        statement = one('data-source-problem', p.id)
        assert len(statement) == 1, (p.id, 'statement copies', len(statement))
        assert compact(p.conditions_html) in re.sub(r'\s+', '', statement[0].text()), (p.id, 'statement text differs')
        pane = html_text[html_text.index(f'data-problem-for="{p.id}"'):]
        pane = pane[:pane.index('<div class="layer formal" data-explanation=')]
        for name in ('pre', 'svg', 'img', 'table'):
            assert tags(pane, name) == tags(p.conditions_html, name) + tags(p.original_html, name), (p.id, name)
        original = one('data-original-problem', p.id)
        assert len(original) == (1 if p.original_html else 0), (p.id, 'original copies')
        if p.original_html:
            assert compact(p.original_html) in re.sub(r'\s+', '', original[0].text()), (p.id, 'original text differs')
    return len(pack.problems)


def main():
    bucket, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    value = json.loads((bucket / 'source.json').read_text(encoding='utf-8'))
    source = Path(value['path']); repo = Path(json.loads((bucket.parent / 'run.json').read_text())['repo'])
    pack = load_source(source, repo)
    stage = json.loads((bucket / 'stage.json').read_text())
    html_path = bucket / stage['stage'] / stage['html']
    checked = source_fidelity(pack, html_path.read_text(encoding='utf-8'))

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(html_path.parent)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/'
    url = base + stage['html']
    ids = [p.id for p in pack.problems]
    has_original = {p.id: bool(p.original_html) for p in pack.problems}
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for width, height, theme in COMBOS:
            page = browser.new_page(viewport={'width': width, 'height': height}, color_scheme=theme)
            logs, failed, external = [], [], []
            page.on('pageerror', lambda e: logs.append(str(e)))
            page.on('console', lambda e: logs.append(e.text) if e.type == 'error' else None)
            page.on('requestfailed', lambda r: failed.append(r.url))
            page.on('response', lambda r: failed.append(f'{r.status} {r.url}') if r.status >= 400 else None)
            page.on('request', lambda r: external.append(r.url) if not r.url.startswith(base) else None)
            page.goto(url, wait_until='networkidle')
            page.evaluate('localStorage.clear()'); page.reload(wait_until='networkidle')
            for pid in ids:
                page.goto(f'{url}#{pid}'); page.wait_for_timeout(120)
                if width >= 1024:
                    pane = page.locator(f'#panel-prob .probs [data-problem-for="{pid}"]')
                    assert pane.is_visible(), (width, theme, pid, 'panel problem hidden')
                    assert page.locator(f'#{pid} > [data-problem-for]').count() == 0
                    assert page.locator('#tab-original').is_visible() == has_original[pid], (pid, 'original tab')
                    if (width, theme) == (1280, 'light'):
                        page.locator('#panel-prob').screenshot(path=str(out.parent / f'panel-{pid}-problem.png'))
                    if has_original[pid]:
                        page.locator('#tab-original').click(); page.wait_for_timeout(80)
                        orig = page.locator(f'#tabpanel-original details.original[data-original-problem="{pid}"][open]')
                        assert orig.is_visible(), (pid, 'original panel')
                        if (width, theme) == (1280, 'light'):
                            page.locator('#panel-prob').screenshot(path=str(out.parent / f'panel-{pid}-original.png'))
                        page.locator('#tab-problem').click(); page.wait_for_timeout(80)
                    box = page.locator('#panel-prob').bounding_box(); content = page.locator('.content').bounding_box()
                    assert box['x'] + box['width'] <= content['x'] + 1, (pid, 'panel not left of content')
                else:
                    toggle = page.locator(f'#{pid} .problem-toggle')
                    assert toggle.get_attribute('aria-expanded') == 'false'
                    toggle.click(); page.wait_for_timeout(80)
                    pane = page.locator(f'#{pid} [data-problem-for="{pid}"]')
                    assert pane.is_visible(), (pid, 'inline problem hidden')
                    assert pane.locator('details.original').count() == (1 if has_original[pid] else 0)
                for pre in pane.locator('pre').all():
                    if pre.is_visible():
                        assert pre.evaluate("e=>e.scrollWidth<=e.clientWidth||['auto','scroll'].includes(getComputedStyle(e).overflowX)"), (pid, 'pre overflow')
                for img in pane.locator('img').all():
                    assert img.evaluate('e=>e.complete&&e.naturalWidth>0'), (pid, 'image')
                assert page.evaluate('document.scrollingElement.scrollWidth<=innerWidth'), (width, theme, pid, 'page overflow')
                if width < 1024:
                    page.locator(f'#{pid} .problem-toggle').click()
            if (width, theme) == (1280, 'light'):
                for dock in ('right', 'float', 'left'):
                    page.locator(f'#panel-prob [data-dock="{dock}"]').click(); page.wait_for_timeout(150)
                    assert page.locator('.layout').get_attribute('data-prob-dock') == dock
                    assert page.evaluate('document.scrollingElement.scrollWidth<=innerWidth')
                    page.screenshot(path=str(out.parent / f'dock-{dock}.png'))
            assert page.locator('.katex-error').count() == 0
            page.goto(f'{url}#{ids[0]}'); page.wait_for_timeout(150)
            page.screenshot(path=str(out.parent / f'{width}-{theme}.png'))
            assert not logs and not failed and not external, (width, theme, logs, failed, external)
            results.append({'viewport': [width, height], 'theme': theme, 'problems': ids, 'console_errors': logs,
                            'failed_resources': failed, 'external_requests': external, 'overflow': False})
            page.close()
        browser.close()
    server.shutdown()
    report = {'html': stage['html'], 'html_sha256': hashlib.sha256(html_path.read_bytes()).hexdigest(), 'source': source.name, 'source_fidelity': f'{checked} problems: statement/original text, pre/svg/img/table counts match the source cards',
              'checks': 'panel left of content, original tab iff original, inline toggle at 375, pre scrolls inside, images load, no page overflow, dock left/right/float, no console/KaTeX/resource/external errors',
              'results': results}
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
