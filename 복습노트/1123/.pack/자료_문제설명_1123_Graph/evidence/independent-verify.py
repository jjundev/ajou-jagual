"""Run with Python 3. The sole source is the adjacent blind-input.json."""
from itertools import combinations, permutations
import json
from math import dist
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def table_edges(html):
    return [(a, b, int(w)) for a, b, w in re.findall(r'<code>([A-Z])([A-Z]) \((\d+)\)</code>', html)]


def directed_edges(html):
    return [(int(a), int(b)) for a, b in re.findall(r'<code>(\d+)→(\d+)</code>', html)]


def svg_edges(html, directed=False):
    svg = re.search(r'<svg\b.*?</svg>', html, re.S).group()
    groups = ET.fromstring(svg).findall('{*}g')
    nodes = {}
    for group in groups:
        circle = group.find('{*}circle')
        if circle is not None:
            center = tuple(float(circle.attrib[key]) for key in ('cx', 'cy'))
            nodes[center] = group.find('{*}text').text.strip()
    edges = []
    for group in groups:
        line = group.find('{*}line')
        path = group.find('{*}path')
        if line is not None:
            coordinates = [float(line.attrib[key]) for key in ('x1', 'y1', 'x2', 'y2')]
        elif path is not None:
            coordinates = [float(value) for value in re.findall(r'-?\d+(?:\.\d+)?', path.attrib['d'])]
        else:
            continue
        start, finish = tuple(coordinates[:2]), tuple(coordinates[-2:])
        if directed:
            # The first polygon point is the tip. Check that it is on the finish side.
            polygon = group.find('{*}polygon')
            tip = tuple(map(float, polygon.attrib['points'].split()[0].split(',')))
            assert dist(tip, finish) < dist(tip, start)
            edges.append((nodes[start], nodes[finish]))
        else:
            edges.append((nodes[start], nodes[finish], int(group.find('{*}text').text)))
    return sorted(nodes.values()), edges


def group_name(group):
    return '{' + ', '.join(map(str, sorted(group))) + '}'


def groups_name(groups):
    return ' '.join(sorted(map(group_name, groups)))


def edge_name(edge):
    a, b, weight = edge
    return f'{a}{b}({weight})'


def edge_names(edges):
    return ', '.join(map(edge_name, edges))


def kruskal(nodes, edges):
    groups = [{node} for node in nodes]
    selected = []
    history = []
    for edge in sorted(edges, key=lambda edge: (edge[2], edge[0], edge[1])):
        a, b, _ = edge
        left = next(group for group in groups if a in group)
        right = next(group for group in groups if b in group)
        accept = left != right
        if accept:
            selected.append(edge)
            groups.remove(left)
            groups.remove(right)
            groups.append(left | right)
        history.append((edge, group_name(left), group_name(right), accept, groups_name(groups)))
        if len(selected) == len(nodes) - 1:
            break
    return selected, history


def prim(nodes, edges, start):
    order = [start]
    selected = []
    history = []
    while len(order) < len(nodes):
        candidates = sorted(
            (edge for edge in edges if (edge[0] in order) != (edge[1] in order)),
            key=lambda edge: (edge[2], edge[0], edge[1]),
        )
        chosen = candidates[0]
        a, b, _ = chosen
        added = b if a in order else a
        history.append((tuple(order), candidates, chosen, added))
        selected.append(chosen)
        order.append(added)
    return order, selected, history


def topology(nodes, edges, prefix=()):
    remaining = set(nodes)
    order = []
    sets = []
    while remaining:
        candidates = sorted(remaining - {b for a, b in edges if a in remaining})
        sets.append(candidates)
        if not candidates:
            break
        choice = prefix[len(order)] if len(order) < len(prefix) else candidates[0]
        assert choice in candidates
        order.append(choice)
        remaining.remove(choice)
    return order, sets, remaining, [(a, b) for a, b in edges if a in remaining and b in remaining]


def violations(order, edges):
    position = {node: index for index, node in enumerate(order)}
    return [(a, b) for a, b in edges if position[a] >= position[b]]


def arrows(edges):
    return ', '.join(f'{a}→{b}' for a, b in edges)


def connected(nodes, edges):
    reached = {nodes[0]}
    for _ in nodes:
        for a, b, _ in edges:
            if a in reached or b in reached:
                reached.update((a, b))
    return len(reached) == len(nodes)


def tree_weight(edges):
    return sum(weight for _, _, weight in edges)


def minimum_trees(nodes, edges):
    trees = [tree for tree in combinations(edges, len(nodes) - 1) if connected(nodes, tree)]
    weight = min(map(tree_weight, trees))
    return weight, [tree for tree in trees if tree_weight(tree) == weight]


def show_kruskal(selected, history, edges):
    for edge, left, right, accept, groups in history:
        status = '선택' if accept else '제외(사이클)'
        print(f'  {edge_name(edge)} {left} / {right} → {status}; 처리 후 {groups}')
    unexamined = [edge for edge in edges if edge not in [row[0] for row in history]]
    print(f'  선택 {edge_names(selected)}; 합 {tree_weight(selected)}; 미검사 {edge_names(unexamined) or "없음"}')


def show_prim(order, selected, history):
    for tree, candidates, chosen, added in history:
        print(f'  {group_name(tree)}의 경계 후보 {edge_names(candidates)} → {edge_name(chosen)}, {added} 추가')
    print(f'  정점 {" → ".join(order)}; 선택 {edge_names(selected)}; 합 {tree_weight(selected)}')


def main():
    problems = {row['id']: row for row in json.loads(Path(__file__).with_name('blind-input.json').read_text())}
    conditions = {key: row['conditions_html'] for key, row in problems.items()}
    print('독립 입력: blind-input.json의 문제 조건과 질문. 정답이나 해설 미사용.')
    print('P1(a) 연결 그래프의 신장 트리는 정점 7개를 이으므로 간선 7−1=6개. MST는 선택한 도로 길이의 합을 최소화.')
    print('P1(b) 더 높은 이웃이 없어 지역 최적해. 더 높은 봉우리가 따로 있으므로 전역 최적해가 아님.')

    nodes = list('ABCDEFG')
    edges = table_edges(conditions['p2'])
    assert edges == table_edges(conditions['p3'])
    selected, history = kruskal(nodes, edges)
    print('P2(a) 다음 순서로 검사하고 여섯 번째 선택 EF 직후 종료.')
    show_kruskal(selected, history, edges)
    print('P2(b) DG 검사 시 D,G 모두 {B,C,D,G}에 속하고 D–C–B–G가 이미 연결됨.')
    print('      EG 검사 시 E,G 모두 {B,C,D,E,G}에 속하고 E–D–C–B–G가 이미 연결됨.')
    print('      이미 이어진 두 끝을 새 간선으로 다시 이으면 그 경로와 함께 사이클이 생김.')

    order, prim_tree, history = prim(nodes, edges, 'A')
    print('P3(a) A에서 시작한 Prim.')
    show_prim(order, prim_tree, history)
    print(f'P3(b) A,F 직후 경계 후보 {edge_names(history[1][1])}. 그중 가중치가 더 작은 EF 선택.')
    print('P3(c) Prim은 현재 트리 안과 밖을 잇는 간선만 비교. Kruskal은 그래프 전체 간선을 가중치순으로 검사하며 서로 다른 집합을 잇는 간선을 선택.')
    weight, trees = minimum_trees(nodes, edges)
    assert tree_weight(selected) == tree_weight(prim_tree) == weight
    print(f'      두 방법 모두 최소 비용 {weight}. 독립적인 전체 신장 트리 열거에서도 MST {len(trees)}개.')

    nodes = list(range(6))
    edges = directed_edges(conditions['p4'])
    order, sets, remaining, _ = topology(nodes, edges)
    assert not remaining and not violations(order, edges)
    print(f'P4(a) 순서 {order}, 처음 세 번의 후보 집합 {", ".join(map(group_name, sets[:3]))}.')
    order, sets, remaining, _ = topology(nodes, edges, (1, 4))
    assert not remaining and not violations(order, edges)
    print(f'P4(b) 순서 {order}. 첫 두 후보 집합은 {group_name(sets[0])}, {group_name(sets[1])}.')
    print(f'P4(c) 위반한 간선은 {arrows(violations([2, 0, 1, 3, 4, 5], edges))}. 2가 선수 과목 0보다 앞섬.')

    extra_edges = directed_edges(conditions['p5'])
    assert extra_edges[:-1] == edges
    order, sets, remaining, remaining_edges = topology(nodes, extra_edges)
    print(f'P5(a) 삭제 순서 {order}, 후보 집합 {", ".join(map(group_name, sets))}.')
    print(f'      남은 정점 {group_name(remaining)}, 남은 간선 {arrows(remaining_edges)}.')
    cycle = [(0, 2), (2, 5), (5, 0)]
    assert set(cycle) <= set(remaining_edges)
    print('P5(b) 위상 정렬 불가. 사이클 0→2→5→0이 있으며 남은 모든 정점의 진입 차수가 양수.')

    nodes, edges = svg_edges(conditions['p6'])
    assert (nodes, edges) == svg_edges(conditions['p7'])
    print(f'P6/P7 SVG의 정점 {", ".join(nodes)}, 간선 {edge_names(edges)}.')
    print('P6 전체 가중치 오름차순으로 검사. 동률은 끝점 이름순. 여섯 번째 간선 선택 직후 종료.')
    tree, history = kruskal(nodes, edges)
    show_kruskal(tree, history, edges)
    print('P7 A에서 시작. 각 단계에서 현재 트리 경계의 가중치 최솟값 선택.')
    order, prim_tree, history = prim(nodes, edges, 'A')
    show_prim(order, prim_tree, history)
    weight, trees = minimum_trees(nodes, edges)
    assert tree_weight(tree) == tree_weight(prim_tree) == weight
    print(f'P6/P7 모든 신장 트리 열거로 최소 비용 {weight}, 가능한 MST {len(trees)}개 확인.')
    for minimum in trees:
        print(' ', edge_names(minimum))
    print('  가중치 8 동률인 BC와 EF는 어느 것을 먼저 검사해도 둘 다 제외. 가중치 9 동률에서 EG를 BD보다 먼저 검사하면 여섯 번째 선택 직후 종료하므로 BD는 미검사. 최종 MST는 같음.')

    nodes, edges = svg_edges(conditions['p8'], directed=True)
    print(f'P8 SVG의 방향 간선 {arrows(edges)}.')
    order, sets, remaining, _ = topology(nodes, edges)
    assert not remaining and not violations(order, edges)
    print(f'   진입 차수 0 후보 집합 {", ".join(map(group_name, sets))}.')
    print(f'   위상 순서 한 가지 {" → ".join(order)}.')
    alternatives = [possible for possible in permutations(nodes) if not violations(possible, edges)]
    print(f'   전체 정점 순열 검사에서 가능한 위상 순서 {len(alternatives)}개.')
    for possible in alternatives:
        print('  ', ' → '.join(possible))


if __name__ == '__main__':
    main()
