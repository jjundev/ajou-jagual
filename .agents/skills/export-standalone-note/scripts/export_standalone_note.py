"""자구알 복습팩의 HTML 의존성을 인라인하고 기존 PDF와 함께 내보낸다."""
from __future__ import annotations

import argparse
import base64
import hashlib
from dataclasses import dataclass
from datetime import date
from html import escape
from html.parser import HTMLParser
import json
import mimetypes
import os
from pathlib import Path
import posixpath
import re
import sys
import tempfile
import unicodedata
from urllib.parse import quote, unquote, urlsplit
from urllib.request import url2pathname
import zipfile

PACK_KINDS = ('정리노트', '복습문제', '문제설명', '확인문제')
INTERACTIVE_KINDS = ('인터렉티브', '인터랙티브')
KINDS = (*PACK_KINDS, *INTERACTIVE_KINDS)
SKILL = Path(__file__).resolve().parents[1]
VENDOR = SKILL / 'assets/vendor'
CDNS = {
    'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/': VENDOR / 'katex',
    'https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/': VENDOR / 'pretendard',
}
RANGE = re.compile(r'\d{4}(?:-\d{4})?\Z')
URL = re.compile(r'''url\(\s*(['"]?)(.*?)\1\s*\)''', re.I)


class ExportError(ValueError):
    pass


@dataclass
class Result:
    path: Path
    files: list[str]
    skipped: list[str]
    excluded: list[str]
    warnings: list[str]


def nfc(value):
    return unicodedata.normalize('NFC', str(value))


def normalized_path(path: Path) -> Path:
    """NFC入力でもNFDの実ファイルを見つける。"""
    if path.exists():
        return path
    parent = path.parent
    if parent == path:
        return path
    parent = normalized_path(parent)
    if parent.is_dir():
        matches = [p for p in parent.iterdir() if nfc(p.name) == nfc(path.name)]
        if len(matches) > 1:
            raise ExportError(f'正規化後に名前が重複: {path}')
        if matches:
            return matches[0]
    return parent / path.name


def key(path):
    return os.path.normcase(nfc(Path(path).resolve()))


def bounds(value):
    if not RANGE.fullmatch(value):
        raise ExportError(f'잘못된 날짜: {value}')
    parts = value.split('-')
    for part in parts:
        try:
            date(2026, int(part[:2]), int(part[2:]))
        except ValueError as exc:
            raise ExportError(f'잘못된 날짜: {value}') from exc
    if parts[0] > parts[-1]:
        raise ExportError(f'거꾸로 된 범위: {value}')
    return parts[0], parts[-1]


def select(repo, names, kind, include_pdf):
    notes = repo / '복습노트'
    if not all((repo / p).is_dir() for p in ('STT', '자료구조_강의록_2026', '복습노트')):
        raise ExportError('자구알 저장소에서만 동작합니다 (--repo 경로 확인)')
    packs = {nfc(p.name): p for p in notes.iterdir() if p.is_dir() and RANGE.fullmatch(nfc(p.name))}
    if not names:
        raise ExportError('날짜 또는 all을 지정하세요. 사용 가능: ' + ', '.join(sorted(packs)))
    if 'all' in names and names != ['all']:
        raise ExportError('all은 다른 대상과 함께 지정할 수 없습니다')
    chosen, direct = {}, {}
    for name in names:
        name = nfc(name)
        candidate = normalized_path(Path(name) if Path(name).is_absolute() else repo / name)
        if name.lower().endswith('.html'):
            if not candidate.is_file() or not candidate.resolve().is_relative_to(notes.resolve()):
                raise ExportError(f'복습노트 안의 HTML이 아닙니다: {name}')
            if not any(nfc(candidate.name).startswith(k + '_') for k in KINDS):
                raise ExportError(f'지원하지 않는 HTML: {name}')
            direct[key(candidate)] = candidate
        elif name == 'all':
            chosen.update(packs)
        elif name in packs:
            bounds(name)
            chosen[name] = packs[name]
        else:
            lo, hi = bounds(name)
            found = {n: p for n, p in packs.items() if lo <= bounds(n)[0] and bounds(n)[1] <= hi}
            if not found:
                raise ExportError(f'해당 날짜의 팩이 없습니다: {name}')
            chosen.update(found)
    selected, skipped = dict(direct), []
    for name, folder in sorted(chosen.items()):
        prefixes = PACK_KINDS if kind == 'all' else (() if kind in INTERACTIVE_KINDS else (kind,))
        patterns = [f'{k}_{name}_*.html' for k in prefixes]
        if include_pdf and kind == 'all':
            patterns += [f'복습문제_{name}_*-{k}.pdf' for k in ('문제', '답안')]
        for pattern in patterns:
            import fnmatch
            hits = sorted(p for p in folder.iterdir() if p.is_file() and fnmatch.fnmatchcase(nfc(p.name), pattern))
            if len(hits) > 1:
                raise ExportError(f'후보가 여러 개입니다: {folder / pattern}')
            if not hits:
                if kind != 'all':
                    raise ExportError(f'없는 파일: {folder / pattern}')
                skipped.append(f'{name}/{pattern}')
            else:
                selected[key(hits[0])] = hits[0]
        if kind == 'all' or kind in INTERACTIVE_KINDS:
            pages = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix == '.html'
                           and nfc(p.name).startswith(tuple(k + '_' for k in INTERACTIVE_KINDS)))
            if not pages and kind in INTERACTIVE_KINDS:
                raise ExportError(f'인터랙티브가 없습니다: {folder}')
            for page in pages:
                selected[key(page)] = page
    if not selected:
        raise ExportError('내보낼 파일이 없습니다')
    if kind != 'all':
        prefixes = INTERACTIVE_KINDS if kind in INTERACTIVE_KINDS else (kind,)
        if any(not nfc(p.name).startswith(tuple(k + '_' for k in prefixes)) for p in direct.values()):
            raise ExportError('직접 지정한 HTML과 --kind가 다릅니다')
    return sorted(selected.values(), key=lambda p: nfc(p.as_posix())), skipped


class Assets:
    def __init__(self, repo):
        self.repo = repo.resolve()
        self.active = set()
        self.verified = set()
        manifest = VENDOR / 'provenance.json'
        self.vendor_hashes = set(json.loads(manifest.read_text(encoding='utf-8'))['files'].values()) if manifest.is_file() else set()

    def resolve(self, ref, base):
        parsed = urlsplit(ref)
        if parsed.scheme or parsed.netloc:
            for prefix, root in CDNS.items():
                if ref.startswith(prefix):
                    path = (root / unquote(urlsplit(ref[len(prefix):]).path)).resolve()
                    if not path.is_relative_to(root.resolve()):
                        break
                    return self.require(path)
            raise ExportError(f'지원하지 않는 외부 자원: {ref}')
        path = normalized_path(base / unquote(parsed.path)).resolve()
        if not (path.is_relative_to(self.repo) or path.is_relative_to(VENDOR.resolve())):
            raise ExportError(f'저장소 밖 자원: {ref}')
        return self.require(path)

    def require(self, path):
        if not path.is_file():
            raise ExportError(f'자원 누락: {path}')
        if path.is_relative_to(VENDOR.resolve()) and path not in self.verified:
            manifest = json.loads((VENDOR / 'provenance.json').read_text(encoding='utf-8'))
            relative = path.relative_to(VENDOR.resolve()).as_posix()
            expected = manifest['files'].get(relative)
            if expected != hashlib.sha256(path.read_bytes()).hexdigest():
                raise ExportError(f'vendor 해시 불일치: {relative}')
            self.verified.add(path)
        return path

    def uri(self, ref, base):
        if ref.startswith(('data:', '#')):
            return ref
        path = self.resolve(ref, base)
        data = path.read_bytes()
        if path.suffix.lower() == '.svg':
            # SVG 내부의 별도 파일 의존성도 단일 파일 조건에 포함된다.
            probe = Audit()
            probe.feed(data.decode('utf-8'))
            if probe.resources:
                raise ExportError(f'SVG 내부 외부 참조: {path}: {probe.resources}')
        mime = {'.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff'}.get(path.suffix.lower())
        mime = mime or mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        fragment = urlsplit(ref).fragment
        return f'data:{mime};base64,' + base64.b64encode(data).decode('ascii') + ('#' + fragment if fragment else '')

    def css_file(self, path):
        if path in self.active:
            raise ExportError(f'CSS 순환 참조: {path}')
        self.active.add(path)
        try:
            return self.css(path.read_text(encoding='utf-8'), path.parent)
        finally:
            self.active.remove(path)

    def css(self, text, base):
        def imported(m):
            path = self.resolve(m.group(2), base)
            css = self.css_file(path)
            media = m.group(3).strip()
            return f'@media {media}{{{css}}}' if media else css
        text = re.sub(r'''@import\s+(?:url\(\s*)?(['"])(.*?)\1\s*\)?\s*([^;]*);''', imported, text, flags=re.I)
        if re.search(r'@import\b', text, re.I):
            raise ExportError('지원하지 않는 CSS @import 구문')
        # woff2가 있는 font-face는 대체 woff와 시스템 글꼴에 의존하지 않는다.
        def font(m):
            block = m.group(0)
            woff = [u.group(2) for u in URL.finditer(block) if urlsplit(u.group(2)).path.endswith('.woff2')]
            if woff:
                block = re.sub(r'src\s*:[^;}]+', lambda _: f'src:url("{woff[0]}") format("woff2")', block, flags=re.I)
            return block
        text = re.sub(r'@font-face\s*\{[^}]*\}', font, text, flags=re.I)
        return URL.sub(lambda m: 'url("' + self.uri(m.group(2), base) + '")', text)


def tag_text(tag, attrs, closing=False):
    return '<' + tag + ''.join(' ' + k if v is None else f' {k}="{escape(v, quote=True)}"' for k, v in attrs) + ('/>' if closing else '>')


class Inliner(HTMLParser):
    def __init__(self, source, mapping, assets, excluded):
        super().__init__(convert_charrefs=False)
        self.source, self.mapping, self.assets, self.excluded = source, mapping, assets, excluded
        self.out, self.late, self.anchors = [], [], []
        self.capture = None

    def validate_script(self, code):
        trusted = hashlib.sha256(code.encode('utf-8')).hexdigest() in self.assets.vendor_hashes
        if not trusted and re.search(r'\b(?:fetch\s*\(|XMLHttpRequest\b|import\s*\()', code):
            raise ExportError(f'동적 자원 로딩 스크립트: {self.source}')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs, True)

    def handle_starttag(self, tag, attrs, selfclose=False):
        a = dict(attrs)
        for attr, value in attrs:
            if attr.startswith('on') and value:
                self.validate_script(value)
        if tag == 'base':
            raise ExportError(f'base 태그는 지원하지 않습니다: {self.source}')
        if tag in ('iframe', 'object', 'embed') or any(k in a for k in ('srcset', 'srcdoc')):
            raise ExportError(f'지원하지 않는 의존성: <{tag}>: {self.source}')
        if tag in ('script', 'style'):
            if tag == 'script' and ('async' in a or a.get('type', '').lower() == 'module'):
                raise ExportError(f'async/module 스크립트는 지원하지 않습니다: {self.source}')
            self.capture = (tag, attrs, [])
            return
        if tag == 'link':
            rel = a.get('rel', '').lower().split()
            if 'stylesheet' in rel:
                path = self.assets.resolve(a.get('href', ''), self.source.parent)
                css = self.assets.css_file(path)
                if path.name == 'pretendard.css':
                    license_path = self.assets.require(path.with_name('LICENSE'))
                    css = '/*\n' + license_path.read_text(encoding='utf-8') + '\n*/\n' + css
                if a.get('media'):
                    css = f'@media {a["media"]}{{{css}}}'
                self.out.append('<style>' + re.sub(r'</style', r'<\/style', css, flags=re.I) + '</style>')
                return
            if set(rel) & {'preconnect', 'dns-prefetch', 'preload', 'modulepreload'}:
                return
        if tag == 'a':
            target = a.get('href', '')
            parsed = urlsplit(target)
            newtag = 'a'
            if target and not target.startswith('#') and (parsed.scheme == 'file' or not (parsed.scheme or parsed.netloc)):
                dest = normalized_path(Path(url2pathname(parsed.path)) if parsed.scheme == 'file' else self.source.parent / unquote(parsed.path))
                if key(dest) in self.mapping:
                    name = posixpath.relpath(self.mapping[key(dest)], posixpath.dirname(self.mapping[key(self.source)]) or '.')
                    a['href'] = quote(name, safe='/') + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')
                else:
                    newtag = 'span'
                    a.pop('href', None)
                    a.pop('target', None)
                    a.pop('download', None)
                    self.excluded.append(f'{self.source.name}: {target}')
            self.anchors.append(newtag)
            tag = newtag
        for attr in ('src', 'poster'):
            if a.get(attr):
                a[attr] = self.assets.uri(a[attr], self.source.parent)
        if tag in ('image', 'use', 'link'):
            for attr in ('href', 'xlink:href'):
                if a.get(attr):
                    a[attr] = self.assets.uri(a[attr], self.source.parent)
        if 'style' in a:
            a['style'] = self.assets.css(a['style'], self.source.parent)
        self.out.append(tag_text(tag, list(a.items()), selfclose))

    def handle_endtag(self, tag):
        if self.capture and tag == self.capture[0]:
            kind, attrs, chunks = self.capture
            a = dict(attrs)
            self.capture = None
            code = ''.join(chunks)
            if kind == 'style':
                code = self.assets.css(code, self.source.parent)
                self.out.append('<style>' + re.sub(r'</style', r'<\/style', code, flags=re.I) + '</style>')
            else:
                if a.get('src'):
                    code = self.assets.resolve(a['src'], self.source.parent).read_text(encoding='utf-8')
                self.validate_script(code)
                code = re.sub(r'</script', r'<\/script', code, flags=re.I)
                kept = [(k, v) for k, v in attrs if k not in ('src', 'defer', 'onload', 'integrity', 'crossorigin')]
                fragment = tag_text('script', kept) + code + '</script>'
                if a.get('onload'):
                    fragment += '<script>' + re.sub(r'</script', r'<\/script', a['onload'], flags=re.I) + '</script>'
                (self.late if 'defer' in a else self.out).append(fragment)
            return
        if tag == 'body':
            self.out.extend(self.late)
            self.late.clear()
        if tag == 'a':
            tag = self.anchors.pop() if self.anchors else tag
        self.out.append(f'</{tag}>')

    def emit(self, text):
        (self.capture[2] if self.capture else self.out).append(text)

    def handle_data(self, data):
        self.emit(data)

    def handle_entityref(self, name):
        self.emit('&' + name + ';')

    def handle_charref(self, name):
        self.emit('&#' + name + ';')

    def handle_comment(self, data):
        self.emit('<!--' + data + '-->')

    def handle_decl(self, decl):
        self.emit('<!' + decl + '>')

    def build(self):
        self.feed(self.source.read_text(encoding='utf-8'))
        self.close()
        if self.capture or self.late:
            raise ExportError(f'닫히지 않은 script/style 또는 body 누락: {self.source}')
        return ''.join(self.out)


class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.resources, self.links, self.ids = [], [], set()
        self.in_style = False
        self.charset = False

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'a' and a.get('name'):
            self.ids.add(a['name'])
        if tag == 'meta' and a.get('charset', '').lower() == 'utf-8':
            self.charset = True
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        refs = [a.get(k, '') for k in ('src', 'poster')]
        if tag in ('link', 'image', 'use'):
            refs += [a.get('href', ''), a.get('xlink:href', '')]
        self.resources += [r for r in refs if r and not r.startswith(('data:', '#'))]
        self.css(a.get('style', ''))
        self.in_style = tag == 'style' or self.in_style

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.css(data)

    def css(self, css):
        self.resources += [m.group(2) for m in URL.finditer(css) if not m.group(2).startswith(('data:', '#'))]


def check_bundle(data):
    errors, pages = [], {}
    for name, content in data.items():
        if name.endswith('.html'):
            page = Audit()
            page.feed(content.decode('utf-8'))
            pages[name] = page
            if not page.charset:
                errors.append(f'UTF-8 charset 누락: {name}')
            errors += [f'남은 참조: {name}: {r}' for r in page.resources]
    for name, page in pages.items():
        for ref in page.links:
            u = urlsplit(ref)
            if u.scheme or u.netloc:
                continue
            target = nfc(posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(u.path)))) if u.path else name
            if target not in data:
                errors.append(f'끊긴 링크: {name}: {ref}')
            elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
                errors.append(f'없는 fragment: {name}: {ref}')
    return errors


def export(repo, names, out, kind='all', include_pdf=True):
    repo, out = Path(repo).resolve(), Path(out).resolve()
    if kind not in (*KINDS, 'all'):
        raise ExportError(f'지원하지 않는 종류: {kind}')
    if out.is_relative_to(repo / '복습노트'):
        raise ExportError('원본 복습노트 안으로 내보낼 수 없습니다')
    sources, skipped = select(repo, names, kind, include_pdf)
    multi = len(sources) > 1
    mapping = {key(p): nfc(f'{p.parent.name}/{p.name}' if multi else p.name) for p in sources}
    if len(set(mapping.values())) != len(sources):
        raise ExportError('정규화 후 출력 이름이 중복됩니다')
    excluded, data = [], {}
    assets = Assets(repo)
    for source in sources:
        name = mapping[key(source)]
        if re.search(r'[<>:"|?*\\]', name) or len(name) > 200:
            raise ExportError(f'Windows에서 사용할 수 없는 경로: {name}')
        data[name] = Inliner(source, mapping, assets, excluded).build().encode('utf-8') if source.suffix == '.html' else source.read_bytes()
    errors = check_bundle(data)
    if errors:
        raise ExportError('\n'.join(errors))
    packs = sorted({nfc(p.parent.name) for p in sources})
    label = packs[0] if len(packs) == 1 else packs[0] + '~' + packs[-1]
    filename = f'자구알_복습노트_{label}.zip' if multi else nfc(sources[0].name)
    out.mkdir(parents=True, exist_ok=True)
    target = out / filename
    warnings = []
    if target.exists():
        warnings.append(f'같은 이름의 출력 교체: {target}')
    if multi:
        warnings += [f'기존 낱개 HTML 유지: {p}' for p in out.glob('*.html') if any(p.name == s.name for s in sources)]
    fd, temporary = tempfile.mkstemp(prefix='.standalone-', suffix=target.suffix, dir=out)
    os.close(fd)
    temp = Path(temporary)
    try:
        if multi:
            with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as z:
                for name, content in data.items():
                    z.writestr(name, content)
            with zipfile.ZipFile(temp) as z:
                if z.testzip() or any(not i.flag_bits & 0x800 for i in z.infolist()):
                    raise ExportError('ZIP 무결성 또는 UTF-8 파일명 검사 실패')
                errors = check_bundle({n: z.read(n) for n in z.namelist()})
                if errors:
                    raise ExportError('\n'.join(errors))
        else:
            temp.write_bytes(next(iter(data.values())))
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)
    return Result(target, list(data), skipped, sorted(set(excluded)), warnings)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('targets', nargs='*', help='1015, 1008 1015, 0907-1015, all, 또는 HTML 경로')
    ap.add_argument('--kind', choices=(*KINDS, 'all'), default='all')
    ap.add_argument('--no-pdf', action='store_true', help='기본 묶음에서 기존 문제·답안 PDF 제외')
    ap.add_argument('--repo', type=Path, default=SKILL.parents[2])
    ap.add_argument('--out', type=Path, default=Path.home() / 'Downloads')
    a = ap.parse_args(argv)
    try:
        result = export(a.repo, a.targets, a.out, a.kind, not a.no_pdf)
    except (ExportError, OSError, UnicodeError) as exc:
        print(f'내보내기 실패: {exc}', file=sys.stderr)
        return 1
    print(f'출력: {result.path} ({result.path.stat().st_size:,} bytes)')
    print(f'검사 통과: 파일 {len(result.files)}개, 남은 자원 참조 0, 묶음 링크·fragment 유효')
    for label, values in [('건너뜀', result.skipped), ('제외한 로컬 링크', result.excluded), ('알림', result.warnings)]:
        for value in values:
            print(f'{label}: {value}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
