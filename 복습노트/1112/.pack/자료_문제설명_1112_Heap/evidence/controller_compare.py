"""컨트롤러 대조: 독립 검산(independent-results.json)과 source.json 참고 답을 소문항별로 비교한다.
수치 핵심값을 정규식으로 뽑아 두 쪽에 모두 들어 있는지 확인한다(코드 비트 문자열은 좌우 배치가 달라 길이·총 비트로 비교)."""
import json, re, sys, pathlib
here = pathlib.Path(__file__).resolve().parent
ind = json.load(open(here / 'independent-results.json'))['items']
src = json.load(open(here.parent / 'source.json'))
ref = {p['id']: p['reference_answer'] for p in src['problems']}
checks = {
 'p1:main': ['300', '247'], 'p2:main': ['250', '011', '0100', '0101'],
 'p3:main': ['①'], 'p4:1': ['60, ?40, ?30, ?12, ?10, ?6, ?15, ?5, ?9|60 40 30 12 10 6 15 5 9'],
 'p4:2': ['60, ?40, ?30, ?12, ?10, ?6, ?15, ?5, ?9|60 40 30 12 10 6 15 5 9'],
 'p4:3': ['40, ?12, ?30, ?9, ?10, ?6, ?15, ?5|40 12 30 9 10 6 15 5'],
 'p5:main': ['132', '162'], 'p6:a': ['23, ?20, ?7, ?1, ?8|23 20 7 1 8'],
 'p6:b': ['1, ?7, ?8, ?20, ?23|1 7 8 20 23'], 'p6:c': ['log'],
 'p7:a': ['135'], 'p7:b': ['8, ?10, ?15, ?12|8 10 15 12', '12, ?15, ?18|12 15 18', '18, ?27|18 27'],
 'p7:c': ['100', '35', '25.9'], 'p8:a': ['우선순위'], 'p8:b': ['10'], 'p8:c': ['7', '5'],
}
ok_all = True
for key, pats in checks.items():
    pid = key.split(':')[0]
    a = ind[key]['answer']; r = ref[pid]
    res = []
    for pat in pats:
        ia = re.search(pat, a) is not None; ra = re.search(pat, r) is not None
        res.append((pat, ia, ra)); ok_all &= ia and ra
    print(key, 'OK' if all(i and j for _, i, j in res) else 'MISMATCH', res)
# p8:b 단계 순서·의자 수
print('p8:b 독립:', ind['p8:b']['answer'])
print('p8:b 참고:', re.search(r'\(b\)(.*?)\(c\)', ref['p8']).group(1).strip())
print('ALL', 'OK' if ok_all else 'MISMATCH')
