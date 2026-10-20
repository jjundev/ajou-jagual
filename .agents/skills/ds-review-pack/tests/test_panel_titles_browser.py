"""Real generated note/review panel behavior, served over an ephemeral HTTP port."""
import functools
import http.server
import threading
import shutil
import re
import pytest
from playwright.sync_api import sync_playwright
from _util import MINI_RUN
import assemble


@pytest.mark.parametrize('width,height', [(1280,900),(375,812)])
@pytest.mark.parametrize('theme', ['light','dark'])
def test_note_and_review_panel_copy(tmp_path,width,height,theme):
    run=tmp_path/'run'
    shutil.copytree(MINI_RUN,run)
    section=run/'sections/s1.html'
    counter=iter(['첫 토픽 요약','둘째 토픽 요약'])
    section.write_text(re.sub(r'<div class="sum" hidden>.*?</article>',lambda m:'<div class="sum" hidden><p>'+next(counter)+'</p></div></article>',section.read_text(),flags=re.S))
    note,review=assemble.assemble(run,tmp_path)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args): pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(tmp_path)))
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            try:
                context=browser.new_context(viewport={'width':width,'height':height},color_scheme=theme)
                page=context.new_page(); errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                for path in [note,review]:
                    page.goto(f'http://127.0.0.1:{server.server_port}/{path.name}',wait_until='networkidle')
                    if not page.locator('#panel-right').is_visible(): page.locator('#toggle-right').click()
                    page.wait_for_timeout(180)
                    assert page.locator('#panel-right .panel-empty:visible').count()==1
                    expected_summaries=['첫 토픽 요약','둘째 토픽 요약']
                    ids=page.locator('main article.topic' if path==note else 'main article.card').evaluate_all('(els)=>els.map(e=>e.id)')
                    for index,topic in enumerate(ids[:2]):
                        page.evaluate('(id)=>{location.hash=id}',topic)
                        page.wait_for_timeout(80)
                        title=page.locator(f'main #{topic} h3').inner_text()
                        assert page.locator('main h3',has_text=title).is_visible()
                        assert page.locator('#panel-right').get_by_text(title,exact=True).count()==0
                        if path==note:
                            assert page.locator('#sum-for.sums').count()==1
                            assert page.locator('#panel-right .sum:not([hidden])').count()==1
                            assert page.locator('#panel-right .sum:not([hidden])').inner_text()==expected_summaries[index]
                        else:
                            assert page.locator('#panel-right .aid:not([hidden]) details').count()>=2
                            page.locator('#panel-right .aid:not([hidden]) details.hint summary').click()
                            assert '더해서 개수로 나눈다.' in page.locator('#panel-right .aid:not([hidden]) details.hint').inner_text()
                            page.locator('#panel-right .aid:not([hidden]) details.solution summary').click()
                            assert page.locator('#panel-right .aid:not([hidden]) .answer').is_visible()
                            page.locator('#solved-btn').click()
                            assert page.locator('#solved-btn').get_attribute('aria-pressed')=='true'
                    assert page.evaluate("Object.keys(localStorage).some(k=>k.startsWith('od-note-read:'))")
                    page.reload(wait_until='networkidle')
                    assert page.evaluate("Object.keys(localStorage).some(k=>k.startsWith('od-note-read:'))")
                    if path==review: assert page.locator('#solved-btn').get_attribute('aria-pressed')=='true'
                    assert errors==[]
                context.close()
            finally: browser.close()
    finally:
        server.shutdown();thread.join();server.server_close()
