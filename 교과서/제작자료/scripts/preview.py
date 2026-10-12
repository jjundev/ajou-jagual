"""Escaped static reading preview. Figures remain original newly authored SVG files."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import argparse,json
from bank import load_bank

def render_preview(bank,models):
    assets={a['id']:a for a in bank['assets']};modelmap={m['id']:m for m in models['models']};sources={s['id']:s for s in bank['sources']}
    def content(items):
        out=[]
        for b in items:
            if b['type']=='text':out.append('<p>'+escape(b['text'])+'</p>')
            elif b['type']=='code':out.append('<pre><code>'+escape(b['text'])+'</code></pre>')
            elif b['type'] in ('figure','table'):
                a=assets[b['asset_id']];m=modelmap[a['model_id']];width=m['layout'].get('width',800)
                out.append(f'<figure><div class="figure-scroll"><img src="{quote("../"+a["path"])}" alt="{escape(a["alt"],quote=True)}" style="width:{width}px" loading="eager"></div><figcaption>{escape(a["id"])}</figcaption></figure>')
                if m['kind']=='table':
                    cells=m['data']['cells'];rows=[]
                    for r in range(m['data']['rows']):
                        row=[]
                        for c in sorted([c for c in cells if c['row']==r],key=lambda c:c['col']):
                            tag='th' if c['header'] else 'td';row.append(f'<{tag} rowspan="{c["rowspan"]}" colspan="{c["colspan"]}">{escape(c["text"])}</{tag}>')
                        rows.append('<tr>'+''.join(row)+'</tr>')
                    out.append('<details><summary>표 데이터 보기</summary><div class="table-scroll"><table>'+''.join(rows)+'</table></div></details>')
            else:
                out.append('<div class="subquestions">'+''.join('<div><span class="label">('+escape(i['label'])+')</span>'+content(i['content'])+'</div>' for i in b['items'])+'</div>')
        return ''.join(out)
    nav=''.join(f'<a href="#{c["id"]}">{c["number"]:02} {escape(c["title"])}</a>' for c in bank['chapters'])
    sections=[]
    for ch in bank['chapters']:
        qs=[]
        for q in bank['questions']:
            if q['chapter_id']!=ch['id']:continue
            options=''.join('<div class="option"><span class="label">('+escape(o['label'])+')</span>'+content(o['content'])+'</div>' for o in q['options'])
            refs=' · '.join(f'<a href="{quote("../"+sources[r["source_id"]]["path"])}#page={r["pdf_page"]}">PDF {r["pdf_page"]}쪽'+(f' / 책 {r["book_page"]}쪽' if r['book_page'] is not None else ' / 책 쪽번호 미확인')+'</a>' for r in q['source_refs'])
            notes=q['observations']+q['issues'];extra=''
            if notes:extra='<details class="notes"><summary>원본 관찰·참조 메모</summary>'+''.join('<p>'+escape(i['description'])+'</p>' for i in notes)+'</details>'
            if q['printed_answer']:extra+='<details><summary>인쇄된 답</summary>'+content(q['printed_answer']['content'])+'</details>'
            qs.append(f'<article id="{q["id"]}"><h3>{ch["number"]:02}장 · {escape(q["number"])}번</h3>'+content(q['content'])+options+extra+f'<footer>{refs}</footer></article>')
        sections.append(f'<section id="{ch["id"]}"><h2>{ch["number"]:02} · {escape(ch["title"])}</h2>'+''.join(qs)+'</section>')
    return '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>교과서 연습문제</title><style>
:root{color-scheme:light dark;--bg:#fafaf8;--fg:#202a31;--line:#cfd5d8;--muted:#53636f;--code:#eef1f3}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.75 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif}main{max-width:1020px;padding:40px 24px;margin:auto;min-width:0}h1{font-size:32px;margin:0}h2{padding-top:24px;border-top:3px solid var(--fg);font-size:26px}h3{font-size:18px;color:var(--muted)}p{white-space:pre-wrap;overflow-wrap:anywhere;margin:12px 0}nav{display:flex;flex-wrap:wrap;gap:8px 20px;margin:30px 0}a{color:#296b96;overflow-wrap:anywhere}article{padding:16px 0 36px;border-bottom:1px solid var(--line);min-width:0}pre{max-width:100%;overflow:auto;background:var(--code);padding:20px;font:15px/1.6 ui-monospace,Menlo,monospace;tab-size:4}figure{margin:20px 0}.figure-scroll,.table-scroll{max-width:100%;overflow:auto}.figure-scroll{background:white;border:1px solid var(--line)}img{display:block;max-width:none;height:auto}figcaption,footer{font-size:13px;color:var(--muted)}footer{margin-top:22px}.option,.subquestions>div{display:flex;gap:14px;align-items:baseline;margin:6px 0}.label{flex:0 0 34px}.option p,.subquestions p{margin:0;flex:1}.subquestions>div{display:block;position:relative;padding-left:40px}.subquestions .label{position:absolute;left:0}.subquestions p{margin:8px 0}details{margin-top:12px;font-size:15px}summary{cursor:pointer;color:var(--muted)}table{border-collapse:collapse;white-space:pre-wrap;min-width:500px}th,td{border:1px solid var(--line);padding:10px 16px}html{scroll-behavior:smooth}@media(prefers-color-scheme:dark){:root{--bg:#171d21;--fg:#e6ebee;--line:#43505a;--muted:#b7c2ca;--code:#232d35}a{color:#8dc4e6}}@media(max-width:500px){main{padding:24px 18px}h1{font-size:27px}h2{font-size:23px}pre{padding:14px}nav{font-size:15px}img{min-width:600px}.option{gap:8px} }
</style><main><h1>교과서 연습문제</h1><p>14장 · '''+str(len(bank['questions']))+'문항 · '+str(len(bank['assets']))+'''개 새 SVG<br>인쇄 원문 추출본입니다. 직접 작성한 정답·해설은 포함하지 않았습니다.<br>넓은 그림·코드·표는 내부에서 가로로 스크롤할 수 있습니다.</p><nav>'''+nav+'</nav>'+''.join(sections)+'</main></html>\n'

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('bank',type=Path);args=parser.parse_args(argv);p=args.bank;models=json.loads((p/'제작자료/asset-models.json').read_text());(p/'제작자료/preview.html').write_text(render_preview(load_bank(p),models))
if __name__=='__main__':main()
