"""Run with Python 3 to reproduce the graph exercise answers."""
from itertools import combinations
from json import dumps

LECTURE = [(10, "AF"), (12, "CD"), (15, "BG"), (16, "BC"), (18, "DG"),
           (22, "DE"), (25, "EG"), (27, "EF"), (29, "AB")]
BOOK = [(7, "AB"), (5, "AD"), (9, "BD"), (8, "BC"), (7, "BE"), (5, "CE"),
        (15, "DE"), (6, "DF"), (8, "EF"), (9, "EG"), (11, "FG")]
COURSES = [(0, 2), (0, 3), (1, 3), (1, 4), (2, 3), (2, 5), (3, 5), (4, 5)]
BOOK_DAG = [(1, 2), (2, 3), (2, 4), (2, 5), (3, 8), (4, 7), (5, 6),
            (5, 7), (6, 8), (7, 8)]

def kruskal(vertices, edges):
    components = {vertex: {vertex} for vertex in vertices}
    included, rejected = [], []
    for weight, edge in sorted(edges):
        left, right = (components[v] for v in edge)
        if left == right:
            rejected.append(edge)
            continue
        included.append((weight, edge))
        group = left | right
        for vertex in group:
            components[vertex] = group
        if len(included) == len(vertices) - 1:
            break
    return included, rejected

def prim(vertices, edges, start):
    visited = {start}
    order = [start]
    included = []
    while len(visited) < len(vertices):
        weight, edge = min((weight, edge) for weight, edge in edges
                           if len(visited.intersection(edge)) == 1)
        vertex = (set(edge) - visited).pop()
        included.append((weight, edge))
        visited.add(vertex)
        order.append(vertex)
    return included, order

def topo(vertices, edges, prefix=()):
    remaining = set(vertices)
    order = []
    while remaining:
        zero = remaining - {v for u, v in edges if u in remaining}
        if not zero:
            return order, sorted(remaining)
        chosen = prefix[len(order)] if len(order) < len(prefix) else min(zero)
        assert chosen in zero, (chosen, zero)
        order.append(chosen)
        remaining.remove(chosen)
    return order, []

def exhaustive_mst(vertices, edges):
    eligible = []
    for subset in combinations(edges, len(vertices) - 1):
        accepted, _ = kruskal(vertices, subset)
        if len(accepted) == len(vertices) - 1:
            eligible.append(sum(weight for weight, _ in accepted))
    return min(eligible)

def cost(edges):
    return sum(weight for weight, _ in edges)

def labels(edges):
    return " ".join(edge for _, edge in edges)

def solve():
    vertices = "ABCDEFG"
    lecture_kruskal, rejected = kruskal(vertices, LECTURE)
    lecture_prim, visits = prim(vertices, LECTURE, "A")
    book_kruskal, _ = kruskal(vertices, BOOK)
    book_prim, book_visits = prim(vertices, BOOK, "A")
    assert cost(lecture_kruskal) == cost(lecture_prim) == exhaustive_mst(vertices, LECTURE) == 102
    assert cost(book_kruskal) == cost(book_prim) == exhaustive_mst(vertices, BOOK) == 39
    assert lecture_kruskal[:4] == [(10, "AF"), (12, "CD"), (15, "BG"), (16, "BC")]
    first, remainder = topo(range(6), COURSES)
    second, other_remainder = topo(range(6), COURSES, (1, 4))
    assert not remainder and not other_remainder
    assert first == [0, 1, 2, 3, 4, 5] and second == [1, 4, 0, 2, 3, 5]
    invalid_order = [2, 0, 1, 3, 4, 5]
    assert [(u, v) for u, v in COURSES if invalid_order.index(u) > invalid_order.index(v)] == [(0, 2)]
    partial, blocked = topo(range(6), COURSES + [(5, 0)])
    assert partial == [1, 4] and blocked == [0, 2, 3, 5]
    textbook_topo, remainder = topo(range(1, 9), BOOK_DAG)
    assert not remainder and all(textbook_topo.index(u) < textbook_topo.index(v) for u, v in BOOK_DAG)

    return {
        "p1": "6개, 전체 가중치 합 최소, 지역 최적해",
        "p2": f"{labels(lecture_kruskal)} / {' '.join(rejected)} 제외 / {cost(lecture_kruskal)}",
        "p3": f"{' '.join(visits)} / {labels(lecture_prim)} / {cost(lecture_prim)}",
        "p4": "0 1 2 3 4 5 / 1 4 0 2 3 5 / 0이 2보다 먼저",
        "p5": "1 4 제거 / 0 2 3 5 남음 / 위상 정렬 불가",
        "p6": f"{labels(book_kruskal)} / {cost(book_kruskal)}",
        "p7": f"{' '.join(book_visits)} / {labels(book_prim)} / {cost(book_prim)}",
        "p8": " ".join(f"cs{vertex}" for vertex in textbook_topo),
    }

if __name__ == "__main__":
    print(dumps(solve(), ensure_ascii=False, indent=2))
