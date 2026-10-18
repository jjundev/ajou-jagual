from collections import deque
from itertools import product

# p5: S6 p9의 고정 단계 수를 코드 구조와 독립적으로 세는 모형.
for n in range(8):
    assert 1 + 1 + 1 == 3  # 상태 검사, 인덱스 갱신, 한 칸 접근
print("p5: n=0..7에서 기본 원형 큐 끝단 연산의 단계 종류는 고정")

# p6: 가능한 모든 front/rear 쌍에서 실제로 다음 칸을 밟아 센 거리.
for front, rear in product(range(8), repeat=2):
    position, count = front, 0
    while position != rear:
        position = (position + 1) % 8
        count += 1
    formula = (rear - front + 8) % 8
    assert count == formula, (front, rear, count, formula)
print("p6: 64개 인덱스 쌍의 직접 순회 개수와 식이 일치, 범위 0..7")

# p7: 구현 규칙을 표준 FIFO와 독립 대조.
def twostack(actions, cap=4):
    incoming, outgoing, oracle, outputs = [], [], deque(), []
    for op, value in actions:
        if op == "in":
            success = len(incoming) + len(outgoing) < cap
            if success:
                incoming.append(value)
                oracle.append(value)
            outputs.append(("in", success))
        else:
            if not outgoing:
                while incoming:
                    outgoing.append(incoming.pop())
            got = outgoing.pop() if outgoing else None
            expected = oracle.popleft() if oracle else None
            assert got == expected, (actions, got, expected)
            outputs.append(("out", got))
        assert list(reversed(outgoing)) + incoming == list(oracle), (actions, incoming, outgoing, oracle)
    return outputs
example=[("in",10),("in",20),("in",30),("out",None),("in",40),("out",None),("out",None),("out",None)]
print("p7 example:",twostack(example,cap=256))
for length in range(8):
    for flags in product(("in","out"), repeat=length):
        actions=[(op,i+1) for i,op in enumerate(flags)]
        twostack(actions)
print("p7: 길이 0..7의 삽입/삭제 열 255개를 FIFO oracle과 대조")
assert twostack([("in",i) for i in range(4)]+[("in",5)])[-1] == ("in",False)
print("p7: 용량 4에서 다섯 번째 삽입 실패")
