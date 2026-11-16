"""p3: 길이 1~8의 모든 숫자열(0~5)을 정의(단순 경로 + 시작=끝, 간선 3개 이상)로 판정하고
check_cycle 실행 결과와 비교한다."""
import itertools, subprocess, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
M = [[0,0,1,0,1,0],[0,0,1,0,0,0],[1,1,0,1,1,0],[0,0,1,0,1,1],[1,0,1,1,0,0],[0,0,0,1,0,0]]
def defn(p):
    if len(p) < 4 or p[0] != p[-1]: return 'n'
    if any(M[a][b] != 1 for a, b in zip(p, p[1:])): return 'n'
    return 'y' if len(set(p[:-1])) == len(p) - 1 else 'n'
paths = []
for L in range(1, 9):
    for t in itertools.product(range(6), repeat=L):
        # 걷기(walk)가 아닌 문자열은 처음 두 칸에서 바로 걸러지므로 걷기만 대량 비교한다
        if all(M[a][b] for a, b in zip(t, t[1:])):
            paths.append(t)
inp = "\n".join("".join(map(str, p)) for p in paths) + "\n"
out = subprocess.run([str(HERE / "check_cycle")], input=inp, capture_output=True, text=True, check=True).stdout.splitlines()
head, rows = out[:3], out[3:]
print("\n".join(head))
mism_mine = mism_model = 0; ys = []; model_diff = []
for p, row in zip(paths, rows):
    s, mine, model = row.split()
    d = defn(p)
    if mine != d: mism_mine += 1
    if model != d: model_diff.append(s)
    if d == 'y': ys.append(s)
print("walks compared:", len(paths))
print("mine vs definition mismatches:", mism_mine)
print("cycles by definition:", len(ys), ys)
print("model vs definition differences:", model_diff)
for s in ["0240", "02340", "0230", "0242", "024", "020", "235432"]:
    r = subprocess.run([str(HERE / "check_cycle")], input=s+"\n", capture_output=True, text=True).stdout.splitlines()[-1]
    print("sample", r)
