"""Independent verification & evidence generator for 1102 (Tree, 12 problems)."""
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # worktree root
RUN_DIR = Path(__file__).resolve().parents[1]
FRAG_DIR = RUN_DIR / 'explanations'
EVIDENCE_DIR = Path(__file__).resolve().parent
INDEP_DIR = EVIDENCE_DIR / 'independent'

def run_solve_py():
    proc = subprocess.run(
        [sys.executable, str(INDEP_DIR / 'solve.py')],
        capture_output=True, text=True, encoding='utf-8', check=True
    )
    (INDEP_DIR / 'solve-output.txt').write_text(proc.stdout, encoding='utf-8')
    return proc.stdout

def run_c_checks():
    results = {}
    out_lines = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for name in ('p10.c', 'p12.c'):
            src = INDEP_DIR / name
            exe = tmp_path / (src.stem + '.exe')
            comp = subprocess.run(
                ['gcc', '-std=c11', '-Wall', '-Wextra', str(src), '-o', str(exe)],
                capture_output=True, text=True, encoding='utf-8'
            )
            if comp.returncode != 0:
                raise RuntimeError(f'{name} compile failed: {comp.stderr}')
            run = subprocess.run([str(exe)], capture_output=True, text=True, encoding='utf-8', check=True)
            results[name] = {
                'compile_warnings': comp.stderr.strip(),
                'stdout': run.stdout.strip(),
                'exit_code': run.returncode,
            }
            out_lines.append(f'=== {name}: gcc -std=c11 -Wall -Wextra ===')
            if comp.stderr.strip():
                out_lines.append(comp.stderr.strip())
            else:
                out_lines.append('(warnings: 0)')
            out_lines.append(run.stdout.strip())

        # Variant check for p10: root data = 9
        p10_var_src = (INDEP_DIR / 'p10.c').read_text(encoding='utf-8').replace(
            'TreeNode n3 = {3, &n5, &n1};', 'TreeNode n3 = {9, &n5, &n1};'
        )
        var_c = tmp_path / 'p10_root9.c'
        var_exe = tmp_path / 'p10_root9.exe'
        var_c.write_text(p10_var_src, encoding='utf-8')
        subprocess.run(['gcc', '-std=c11', '-Wall', '-Wextra', str(var_c), '-o', str(var_exe)], check=True)
        var_run = subprocess.run([str(var_exe)], capture_output=True, text=True, encoding='utf-8', check=True)
        results['p10_root9'] = var_run.stdout.strip()
        out_lines.append('=== p10_root9 variant ===')
        out_lines.append(var_run.stdout.strip())

    (INDEP_DIR / 'c-output.txt').write_text('\n'.join(out_lines) + '\n', encoding='utf-8')
    return results

def reconstruct_svg_edges(svg_xml: str):
    root = ET.fromstring(svg_xml)
    circles = []
    texts = []
    lines = []
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]
        if tag == 'circle':
            circles.append((float(elem.attrib['cx']), float(elem.attrib['cy'])))
        elif tag == 'text':
            texts.append((float(elem.attrib['x']), float(elem.attrib['y']), ''.join(elem.itertext()).strip()))
        elif tag == 'line':
            lines.append((float(elem.attrib['x1']), float(elem.attrib['y1']), float(elem.attrib['x2']), float(elem.attrib['y2'])))
    nodes = {}
    for cx, cy in circles:
        nearest = min(texts, key=lambda t: math.hypot(t[0] - cx, t[1] - cy))
        nodes[(cx, cy)] = nearest[2]
    edges = []
    for x1, y1, x2, y2 in lines:
        p1 = min(nodes, key=lambda c: math.hypot(c[0] - x1, c[1] - y1))
        p2 = min(nodes, key=lambda c: math.hypot(c[0] - x2, c[1] - y2))
        parent, child = (p1, p2) if p1[1] < p2[1] else (p2, p1)
        side = 'L' if child[0] < parent[0] else 'R'
        edges.append((nodes[parent], nodes[child], side))
    return sorted(edges)

def verify_svgs():
    expected = {
        'p2': sorted([('H','G','L'),('H','K','R'),('G','D','L'),('G','E','R'),('D','F','R'),('K','M','L'),('M','N','L'),('M','P','R'),('N','T','L'),('N','S','R'),('T','R','L')]),
        'p3': sorted([('B','C','L'),('B','D','R'),('C','E','L'),('D','M','R'),('E','F','L'),('E','K','R'),('M','O','L'),('M','P','R'),('F','G','L'),('F','H','R'),('P','R','L'),('P','T','R')]),
        'p4': sorted([('A','B','L'),('A','C','R'),('B','D','L'),('C','E','L'),('C','F','R'),('E','G','R'),('F','H','R')]),
    }
    out = {}
    for pid, exp in expected.items():
        html = (FRAG_DIR / f'{pid}.html').read_text(encoding='utf-8')
        m = re.search(r'<svg\b.*?</svg>', html, re.S)
        assert m, f'{pid}: missing svg'
        got = reconstruct_svg_edges(m.group(0))
        assert got == exp, f'{pid}: svg mismatch {got} != {exp}'
        out[pid] = {'edge_count': len(got), 'match': True, 'edges': [f'{p}->{c}({s})' for p, c, s in got]}
    return out

def verify_fragments_and_links():
    note_path = ROOT / '복습노트' / '1102' / '정리노트_1102_Tree.html'
    note_anchors = set(re.findall(r'id="([^"]+)"', note_path.read_text(encoding='utf-8')))
    link_checks = []
    content_checks = {}

    for i in range(1, 13):
        pid = f'p{i}'
        text = (FRAG_DIR / f'{pid}.html').read_text(encoding='utf-8')
        issues = []

        # Check td/th boundary math spacing
        if re.search(r'<t[dh][^>]*>\$|\$</t[dh]>', text):
            issues.append('td/th adjacent $ without space')
        # Check backticks outside pre/code
        cleaned = re.sub(r'<pre>.*?</pre>|<code>.*?</code>', '', text, flags=re.S)
        if '`' in cleaned:
            issues.append('stray markdown backtick outside code tag')
        # Check QA log phrases
        for forbidden in ('evidence/', '.py', '별도 프로그램', 'cc -std=c11', 'ASAN', 'UBSan'):
            if forbidden in text:
                issues.append(f'forbidden QA phrase: {forbidden}')
        # Check start meta declarations
        m_start = re.search(r'data-explanation="start">(.*?)</div>', text, re.S)
        if m_start:
            start_body = m_start.group(1)
            for meta in ('먼저 ', '살펴보', '해 봅시다', '알아보', '읽어 볼게요', '첫 줄을 이렇게 써요'):
                if meta in start_body:
                    issues.append(f'start meta phrase: {meta}')
        # Check MCQ choices elimination
        if pid in ('p7', 'p8', 'p9'):
            for opt in ('①', '②', '③', '④'):
                if opt not in text:
                    issues.append(f'missing MCQ option {opt}')
        # Check links
        for href in re.findall(r'href="([^"]+)"', text):
            if '#' in href:
                target, frag = href.split('#', 1)
                if target == '정리노트_1102_Tree.html':
                    ok = frag in note_anchors
                    link_checks.append({'problem': pid, 'href': href, 'ok': ok})
                    if not ok:
                        issues.append(f'broken anchor: {href}')
                else:
                    link_checks.append({'problem': pid, 'href': href, 'ok': False})
                    issues.append(f'unexpected link target: {href}')
        content_checks[pid] = {'issues': issues, 'passed': len(issues) == 0}
        assert not issues, f'{pid} content issues: {issues}'
    return link_checks, content_checks

def main():
    solve_out = run_solve_py()
    c_out = run_c_checks()
    svg_out = verify_svgs()
    links_out, content_out = verify_fragments_and_links()

    summary = {
        'pack': '1102-Tree',
        'solve_py_lines': len(solve_out.splitlines()),
        'c_checks': c_out,
        'svg_checks': svg_out,
        'content_checks': content_out,
        'all_passed': True,
    }
    (EVIDENCE_DIR / 'independent-checks.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    (EVIDENCE_DIR / 'source-links-check.json').write_text(
        json.dumps({'links': links_out, 'all_ok': all(x['ok'] for x in links_out)}, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8'
    )
    print('verify_1102: ALL PASSED')

if __name__ == '__main__':
    main()
