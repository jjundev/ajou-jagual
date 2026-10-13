"""Offline, fixed-size block-code typography contract."""
import hashlib
import json
from pathlib import Path
from pdf_types import PdfError

FONT_DIR=Path(__file__).resolve().parent.parent/'assets/pdf/vendor/jetbrains-mono'
FONT_URL='https://ds-pdf.local/JetBrainsMono-Regular.ttf'
KOREAN_FONT_URL='https://ds-pdf.local/Pretendard-Regular.woff2'

def font_manifest():
    try:return json.loads((FONT_DIR/'manifest.json').read_text())
    except (OSError,ValueError) as exc:raise PdfError('Code font manifest missing/invalid') from exc

def check_font_assets(expected=None):
    manifest=font_manifest()
    if expected is not None and manifest!=expected:raise PdfError('Code font manifest changed since build')
    if set(manifest.get('files',{}))!={'JetBrainsMono-Regular.ttf','OFL.txt'}:
        raise PdfError('Code font manifest files invalid')
    for name,sha in manifest['files'].items():
        p=FONT_DIR/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
            raise PdfError('Code font missing/changed: '+name)

def check_vendor_assets(root, expected=None):
    """Enforce frozen vendor provenance before rendering; bind stage vendor bytes."""
    root=Path(root)
    try:pinned=json.loads((root/'provenance.json').read_text())['files']
    except (OSError,ValueError,KeyError) as exc:raise PdfError('Frozen vendor provenance missing/invalid') from exc
    for files in (pinned, expected or {}):
        for name,sha in files.items():
            p=root/name
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
                raise PdfError('PDF vendor missing/changed: '+name)


def code_css(layout):
    # Frozen conversion is applied before this extension, so override inherited scales.
    scale=(900/(210*72/25.4))/(1920/1440)
    size=12 if layout=='video-16x9' else 12/scale
    return f'''@font-face {{ font-family: 'DS Pretendard'; src: url('{KOREAN_FONT_URL}') format('woff2'); font-weight: 400; font-style: normal; }}
@font-face {{ font-family: 'DS JetBrains Mono'; src: url('{FONT_URL}') format('truetype'); font-weight: 400; font-style: normal; }}
.panel pre, .work pre, .panel pre code, .work pre code {{
 font-family: 'DS JetBrains Mono', 'DS Pretendard', monospace !important;
 font-size: {size:.8f}pt !important; font-weight: 400 !important;
 font-style: normal; font-variant-ligatures: none; font-feature-settings: 'liga' 0, 'calt' 0;
 line-height: 1.45 !important; color: #000; background: #fff;
 white-space: normal; tab-size: 4;
}}
.ds-code-line {{ display: block; box-sizing: border-box; width: 100%; min-height: 1.45em;
 white-space: pre-wrap; overflow-wrap: anywhere; padding-left: 2ch; text-indent: -2ch; }}
.panel pre, .work pre {{ padding: 2mm; border-radius: 1mm; }}'''

def check_pdf_code(pdf: Path, geometry: dict) -> list[str]:
    """Check actual glyphs in measured block-code rectangles (CSS px → PDF pt)."""
    import fitz
    import re
    errors=[]
    compact=lambda t:re.sub(r'\s+','',t)
    with fitz.open(pdf) as doc:
        if len(doc)!=len(geometry):return ['Code geometry/PDF page count mismatch']
        for page,(pid,g) in zip(doc,geometry.items()):
            spans=[s for b in page.get_text('rawdict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
            for index,code in enumerate(g.get('code',[])):
                r=code['rect'];box=fitz.Rect(r['x']*.75,r['y']*.75,(r['x']+r['w'])*.75,(r['y']+r['h'])*.75)
                text=[]
                for span in spans:
                    chars=[c['c'] for c in span['chars'] if box.contains(fitz.Point((c['bbox'][0]+c['bbox'][2])/2,(c['bbox'][1]+c['bbox'][3])/2))]
                    if not chars:continue
                    text.extend(chars)
                    visible=''.join(chars).strip()
                    if not visible:continue
                    prefix=f'{pid} code {index+1}: '
                    if abs(span['size']-12)>.05:errors.append(prefix+'actual size '+str(span['size']))
                    if any(ord(c)<128 and not c.isspace() for c in chars) and re.sub(r'^[A-Z]{6}\+', '', span['font'])!='JetBrainsMono-Regular':
                        errors.append(prefix+'actual English font '+span['font'])
                    if any('\uac00'<=c<='\ud7a3' for c in chars) and re.sub(r'^[A-Z]{6}\+', '', span['font'])!='Pretendard-Regular':
                        errors.append(prefix+'actual Korean font '+span['font'])
                wanted=compact(code['text']);actual=compact(''.join(text))
                if wanted!=actual:errors.append(f'{pid} code {index+1}: code text missing/changed')
                if '\ufffd' in actual or '\u25a1' in actual and '\u25a1' not in wanted:
                    errors.append(f'{pid} code {index+1}: missing glyph')
    return list(dict.fromkeys(errors))
