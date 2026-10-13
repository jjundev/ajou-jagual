"""Offline, fixed-size block-code typography contract."""
import hashlib
import json
from pathlib import Path
from pdf_types import PdfError

FONT_DIR=Path(__file__).resolve().parent.parent/'assets/pdf/vendor/jetbrains-mono'
FONT_URL='https://ds-pdf.local/JetBrainsMono-Regular.ttf'

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

def code_css(layout):
    # Frozen conversion is applied before this extension, so override inherited scales.
    scale=(900/(210*72/25.4))/(1920/1440)
    size=12 if layout=='video-16x9' else 12/scale
    return f'''@font-face {{ font-family: 'DS JetBrains Mono'; src: url('{FONT_URL}') format('truetype'); font-weight: 400; font-style: normal; }}
.panel pre, .work pre, .panel pre code, .work pre code {{
 font-family: 'DS JetBrains Mono', Pretendard, monospace !important;
 font-size: {size:.8f}pt !important; font-weight: 400 !important;
 font-style: normal; font-variant-ligatures: none; font-feature-settings: 'liga' 0, 'calt' 0;
 line-height: 1.45 !important; color: #000; background: #fff;
 white-space: pre; tab-size: 4;
}}
.panel pre, .work pre {{ padding: 2mm; border-radius: 1mm; }}'''
