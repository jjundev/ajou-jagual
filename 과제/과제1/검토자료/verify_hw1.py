import hashlib
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

source = Path(sys.argv[1]).resolve()
binary = Path(sys.argv[2]).resolve()
record = Path(sys.argv[3]).resolve()
binary.parent.mkdir(parents=True, exist_ok=True)
record.parent.mkdir(parents=True, exist_ok=True)
command = ['clang', '-std=c11', '-Wall', '-Wextra', '-Wpedantic',
           str(source), '-o', str(binary)]
build = subprocess.run(command, capture_output=True, text=True)
if build.returncode:
    sys.exit(build.stderr)
cases = [
    ('example-1', '2\n2\n1 0\n0 1\n1 0\n1 1\n1 1\n', 1, [[1, 0], [0, 1]]),
    ('example-2', '3\n1\n2\n1\n1\n0\n1\n2\n2\n', 6, [[0], [1], [2]]),
    ('example-3', '3\n2\n1 0\n1 0\n0 1\n0 0\n1 1\n2 1\n0 1\n', 0, [[0, 1], [2, 0], [0, 1]]),
    ('eight-processes-zero-resources', '8\n0\n', 40320, [[] for _ in range(8)]),
    ('one-process-five-resources', '1\n5\n' + '0 0 0 0 0\n' * 3, 1, [[0] * 5]),
    ('process-negative', '-1\n', None, None),
    ('process-zero', '0\n', None, None),
    ('process-nine', '9\n', None, None),
    ('resource-negative', '1\n-1\n', None, None),
    ('resource-six', '1\n6\n', None, None),
    ('available-negative', '1\n1\n-1\n', None, None),
    ('allocation-negative', '1\n1\n0\n-1\n', None, None),
    ('maximum-negative', '1\n1\n0\n0\n-1\n', None, None),
    ('maximum-below-allocation', '1\n1\n0\n2\n1\n', None, None),
    ('nonnumeric-process', 'x\n', None, None),
    ('nonnumeric-available', '1\n1\nx\n', None, None),
    ('empty-input', '', None, None),
    ('missing-maximum', '1\n1\n0\n0\n', None, None),
]
results = []
for name, stdin, count, need in cases:
    run = subprocess.run([str(binary)], input=stdin, capture_output=True,
                         text=True, timeout=5)
    if count is None:
        ok = ('잘못된 값을 입력하셨습니다.' in run.stdout
              and 'Need matrix:' not in run.stdout
              and '가능한 시퀀스의 개수:' not in run.stdout)
    else:
        match = re.search(r'가능한 시퀀스의 개수:\s*(\d+)', run.stdout)
        rows = re.findall(r'^P(\d+):([^\n]*)$', run.stdout, re.MULTILINE)
        actual_need = [list(map(int, values.split())) for _, values in rows]
        ok = (match is not None and int(match.group(1)) == count
              and [int(i) for i, _ in rows] == list(range(len(need)))
              and actual_need == need
              and '잘못된 값을 입력하셨습니다.' not in run.stdout)
    ok = bool(ok and run.returncode == 0 and not run.stderr)
    results.append(dict(name=name, stdin=stdin, stdout=run.stdout,
                        stderr=run.stderr, returncode=run.returncode,
                        expected_count=count, expected_need=need, passed=ok))
payload = dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
               platform=platform.platform(),
               compiler=subprocess.check_output(['clang', '--version'], text=True),
               build_command=command, build_stderr=build.stderr, cases=results)
record.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(f'{sum(r["passed"] for r in results)}/{len(results)} passed')
if build.stderr:
    print(build.stderr, file=sys.stderr)
sys.exit(0 if all(r['passed'] for r in results) else 1)
