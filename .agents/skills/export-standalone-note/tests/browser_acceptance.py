"""Actual-pack offline acceptance. Requires Playwright, not an export dependency.

python browser_acceptance.py REPO EMPTY_SCRATCH
"""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import export_standalone_note as sn


def digest_notes(repo):
    return {str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (repo / '복습노트').rglob('*') if p.is_file()}


def main(repo, scratch, reuse=False):
    repo, scratch = Path(repo).resolve(), Path(scratch).resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    if any(scratch.iterdir()) and not reuse:
        raise RuntimeError('scratch must be empty')
    before = digest_notes(repo)
    if reuse:
        # Browser-only iteration against the previously verified export.
        archive = next(scratch.glob('자구알_복습노트_*.zip'))
        with zipfile.ZipFile(archive) as z:
            result = sn.Result(archive, z.namelist(), [], [], [])
    else:
        result = sn.export(repo, ['all'], scratch)
    unpacked = scratch / 'unpacked'
    with zipfile.ZipFile(result.path) as z:
        for name in z.namelist():
            if name.endswith('.pdf'):
                assert z.read(name) == (repo / '복습노트' / name).read_bytes(), name
        if not reuse:
            z.extractall(unpacked)
    assert digest_notes(repo) == before, 'source notes changed'
    report = {'archive': str(result.path), 'files': len(result.files),
              'bytes': result.path.stat().st_size, 'skipped': result.skipped,
              'excluded': result.excluded, 'source_unchanged': True, 'pages': []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(offline=True, viewport={'width': 1280, 'height': 900})
        samples = [(kind, '1015') for kind in sn.PACK_KINDS[:3]]
        samples += [('확인문제', '1102'), ('인터렉티브', '0928')]
        for kind, day in samples:
            page = context.new_page()
            if kind == '복습문제':
                page.set_viewport_size({'width': 390, 'height': 844})
            errors, external = [], []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('request', lambda r: external.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
            path = sorted((unpacked / day).glob(kind + '_*.html'))[0]
            page.goto(path.as_uri() + ('#p1' if kind in ('복습문제', '문제설명') else ''), wait_until='load')
            page.evaluate('document.fonts.ready')
            measures = page.evaluate('''async () => ({
                math:document.querySelectorAll('.katex').length,
                mathErrors:document.querySelectorAll('.katex-error').length,
                brokenImages:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).length,
                font:(await document.fonts.load('400 16px Pretendard', '한글')).some(f => f.status === 'loaded')
            })''')
            assert measures['mathErrors'] == measures['brokenImages'] == 0, measures
            assert measures['font'], measures
            # Some review pages contain no TeX. Check the renderer independently.
            if kind != '인터렉티브':
                assert page.evaluate('''() => {
                    const probe=document.createElement('span');
                    katex.render('x^2',probe,{throwOnError:true});
                    return !!probe.querySelector('.katex');
                }''')
            theme = page.locator('[data-action=theme]' if kind == '인터렉티브' else '#theme-toggle')
            initial = page.locator('html').get_attribute('data-theme')
            theme.click()
            assert page.locator('html').get_attribute('data-theme') != initial
            if kind == '인터렉티브':
                page.locator('[data-action=next]').click()
                assert page.locator('#app').get_attribute('data-index') == '1'
            if kind == '확인문제':
                page.evaluate("location.hash = document.querySelector('article.card:has(.review-choice)').id")
                page.locator('article.card:visible .review-choice').first.click()
                assert page.locator('article.card:visible .review-status').inner_text()
            if kind == '복습문제':
                if page.locator('#toggle-right').get_attribute('aria-expanded') != 'true':
                    page.locator('#toggle-right').click()
                detail = page.locator('details.solution:visible').first
                detail.locator('summary').click()
                assert detail.get_attribute('open') is not None
            if kind == '문제설명':
                page.goto(path.as_uri() + '#p3', wait_until='load')
                fig = page.locator('svg.zoomable:visible').first
                fig.wait_for(state='visible')
                fig.click()
                assert page.locator('dialog.figure-sheet').is_visible()
                page.locator('dialog.figure-sheet .sheet-close').click()
                page.goto(path.as_uri() + '#p8', wait_until='load')
                assert not page.locator('dialog.figure-sheet').is_visible()
                link = page.locator('a[href*=".html#p8"]').first
                href = link.get_attribute('href')
                assert href
                page.goto(page.evaluate('(href) => new URL(href, location.href).href', href), wait_until='load')
                assert page.locator('#p8').count() == 1
            assert not errors and not external, (errors, external)
            page.screenshot(path=str(scratch / f'{kind}.png'))
            report['pages'].append({'kind': kind, 'method': 'offline file:// Chromium', **measures,
                                    'errors': errors, 'external_requests': external})
            page.close()
        # The 0907 note contains a real enqueue/dequeue widget.
        page = context.new_page()
        path = next((unpacked / '0907').glob('정리노트_*.html'))
        page.goto(path.as_uri(), wait_until='load')
        topic = page.locator('#qs-put').evaluate('(e) => e.closest(".topic").id')
        page.goto(path.as_uri() + '#' + topic, wait_until='load')
        button = page.locator('#qs-put')
        before_widget = page.locator('#qs-put').evaluate('(e) => e.closest(".widget").textContent')
        button.click()
        after_widget = page.locator('#qs-put').evaluate('(e) => e.closest(".widget").textContent')
        assert before_widget != after_widget
        report['widget'] = '0907 enqueue changes state'
        browser.close()
    (scratch / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ('excluded', 'skipped')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main(*sys.argv[1:3], reuse='--reuse' in sys.argv[3:])
