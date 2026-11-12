import sys,threading,http.server,functools
from pathlib import Path
from playwright.sync_api import sync_playwright
stage=Path(sys.argv[1]).resolve(); name=next(stage.glob('*.html')).name
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=str(stage)))
threading.Thread(target=srv.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{srv.server_port}/{name}'
P=[f'p{i}' for i in range(1,9)]
with sync_playwright() as pw:
    b=pw.chromium.launch(channel='chrome')
    for w,h in [(1280,900),(375,812)]:
        p=b.new_page(viewport={'width':w,'height':h})
        p.goto(url+'#p8',wait_until='networkidle'); p.wait_for_timeout(200)
        seq=[]
        for _ in range(9):
            vis=[x for x in P if p.locator('#'+x).is_visible()]
            ids=p.evaluate("[...document.querySelectorAll('section,article')].filter(e=>e.offsetParent&&e.id).map(e=>e.id).slice(0,3)")
            seq.append((vis[:1],ids, p.locator('#pager-prev').is_disabled()))
            if p.locator('#pager-prev').is_disabled(): break
            p.locator('#pager-prev').click(); p.wait_for_timeout(120)
        print(w,seq)
        p.close()
    b.close()
srv.shutdown()
