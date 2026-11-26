"""Verify reviewed-byte delivery, file:// playback and contextual same-tab round trips."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import expect, sync_playwright

from browser_graph_layout import open_options


PACKS = {
    '0928': ('정리노트_0928_ArrayStructureList.html', 3, 4),
    '1105': ('정리노트_1105_Tree.html', 1, 1),
    '1116': ('정리노트_1116_Graph.html', 2, 3),
    '1119': ('정리노트_1119_Graph.html', 2, 4),
    '1123': ('정리노트_1123_Graph.html', 2, 5),
    '1126': ('정리노트_1126_Sorting.html', 2, 2),
}
LINK_SECTIONS = {
    '1105': ['s0-inorder'],
    '1116': ['s1-euler', 's2-terms', 's3-adj-matrix'],
    '1119': ['s0-dfs-not-done', 's1-bfs-trace', 's1-compare', 's2-components'],
    '1123': ['s1-kruskal', 's1-union', 's2-prim', 's3-removal', 's3-cycle'],
    '1126': ['s1-merge-join', 's1-partition'],
}
INORDER_FILE = '인터렉티브_01_중위순회_실행.html'
FONT_HREF = rb'(data-ds-interactive-font href=")[^"]+'


def check_public_files(browser, files):
    rows = []
    with browser.new_context(offline=True) as context:
        page = context.new_page()
        for file in files:
            public = file.read_bytes()
            preview = (file.parent / '.pack' / ('자료_' + file.stem) / 'preview.html').read_bytes()
            assert re.sub(FONT_HREF, rb'\g<1>', public) == re.sub(FONT_HREF, rb'\g<1>', preview), file
            page.goto(file.as_uri())
            expect(page.locator('#app')).to_have_attribute('data-snapshot', 'initial')
            assert page.evaluate("""async () => (
                await document.fonts.load('400 16px Pretendard', '한글')
            ).some(face => face.status === 'loaded')"""), file
            page.locator('[data-action=next]').click()
            expect(page.locator('#app')).to_have_attribute('data-index', '1')
            graph_view = page.locator('#app').get_attribute('data-graph-view')
            if graph_view or page.locator('#app').get_attribute('data-ui-version'):
                open_options(page)
            elif page.locator('[data-action=tree-options]').count():
                page.locator('[data-action=tree-options]').click()
            page.locator('[data-action=last]').click()
            expect(page.locator('[data-action=next]')).to_be_disabled()
            if graph_view:
                if graph_view == 'traversal':
                    page.locator('[data-input=setup]').select_option(index=1)
                else:
                    page.locator('[data-action=preset]').select_option(index=1)
                expect(page.locator('#app')).to_have_attribute('data-index', '0')
                if page.locator('[data-mode-value=bfs]').count():
                    page.locator('[data-mode-value=bfs]').click()
                    expect(page.locator('[data-graph-state=queue]')).to_be_visible()
                if graph_view == 'mst':
                    page.locator('[data-action=preset]').select_option('tie-kruskal')
                    page.locator('[data-mode-value=prim]').click()
                    expect(page.locator('[data-action=preset]')).to_have_value('tie-prim')
                    expect(page.locator('.code-line.current')).to_have_attribute('data-source-id', 'prim')
                if graph_view == 'topo':
                    page.locator('[data-action=preset]').select_option('cycle')
                    open_options(page).locator('[data-action=next-output]').click()
                    expect(page.locator('[data-decision-state=topo-result]')).to_have_text('1')
                open_options(page)
                page.locator('[data-action=last]').click()
                expect(page.locator('[data-action=next]')).to_be_disabled()
                if graph_view == 'mst':
                    expect(page.locator('[data-decision-state=mst-result]')).to_contain_text('총비용 102')
                if graph_view == 'topo':
                    expect(page.locator('[data-decision-state=cycle]')).to_have_text('0 → 2 → 5 → 0')
            if page.locator('.study-arrays').count():
                page.locator('[data-action=preset]').select_option(index=1)
                expect(page.locator('#app')).to_have_attribute('data-index', '0')
                page.locator('[data-action=play]').click()
                expect(page.locator('#app')).to_have_attribute('data-index', '1')
                page.locator('[data-action=preset]').select_option('default')
                expect(page.locator('#app')).to_have_attribute('data-playing', 'false')
                expect(page.locator('#app')).to_have_attribute('data-index', '0')
            rows.append({'file': file.name, 'sha256': hashlib.sha256(public).hexdigest(),
                         'content_matches_reviewed_preview': True, 'final_playback': 'pass'})
    return rows


def check_note_links(browser, note, files, expected_count, date, mobile=False):
    viewport = {'width': 375, 'height': 812} if mobile else {'width': 1440, 'height': 900}
    with browser.new_context(offline=True, viewport=viewport, is_mobile=mobile,
                             has_touch=mobile) as context:
        page = context.new_page()
        page.goto(note.as_uri())
        links = page.locator('[data-ds-interactive] a')
        expect(links).to_have_count(expected_count)
        sections = links.evaluate_all(
            'links => links.map(link => link.closest("article,section").id)')
        if date in LINK_SECTIONS:
            assert sections == LINK_SECTIONS[date], sections

        rows = []
        for section in sections:
            page.goto(note.as_uri() + '#' + section)
            original_url = page.url
            link = page.locator('#' + section + ' [data-ds-interactive] a')
            expect(link).to_have_attribute('target', '_self')
            href = link.get_attribute('href')
            assert href is not None
            target = (note.parent / unquote(href)).resolve()
            assert target in files, href
            if mobile:
                link.tap()
            else:
                link.click()
            expect(page.locator('#app')).to_have_attribute('data-snapshot', 'initial')
            destination = urlsplit(page.url)
            assert destination.scheme == 'file' and Path(unquote(destination.path)).samefile(target)
            assert context.pages == [page]
            page.go_back()
            expect(page).to_have_url(original_url)
            expect(link).to_be_visible()
            assert context.pages == [page]
            rows.append({'link': href, 'section': section, 'viewport': viewport,
                         'same_tab_roundtrip': 'pass'})
        return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', type=Path)
    parser.add_argument('report', type=Path)
    parser.add_argument('--date', choices=PACKS, default='0928')
    args = parser.parse_args()
    note_name, file_count, link_count = PACKS[args.date]
    folder = args.repo.resolve() / '복습노트' / args.date
    files = sorted(folder.glob('인터렉티브_*.html'))
    assert len(files) == file_count, files
    if args.date == '1105':
        assert files == [folder / INORDER_FILE], files

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        rows = check_public_files(browser, files)
        rows += check_note_links(browser, folder / note_name, files, link_count, args.date)
        if args.date in LINK_SECTIONS:
            rows += check_note_links(browser, folder / note_name, files, link_count, args.date, mobile=True)
        browser.close()

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({'status': 'pass', 'results': rows}, ensure_ascii=False,
                                      indent=2) + '\n', encoding='utf8')
    print(f'{args.date}: {file_count} reviewed materials, {len(rows) - file_count} same-tab round trips pass')


if __name__ == '__main__':
    main()
