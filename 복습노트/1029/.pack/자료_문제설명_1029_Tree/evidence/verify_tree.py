"""Independent verification for 1029 Tree (p1~p10) from source.json."""
import json
import math
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "source.json"
probs = {p["id"]: p for p in json.loads(SRC.read_text(encoding="utf-8"))["problems"]}


def tree_from_svg(svg):
    nodes = []
    for m in re.finditer(
        r'<circle[^>]*cx="([\d.]+)"[^>]*cy="([\d.]+)"[^>]*/>\s*<text[^>]*>([^<]+)</text>',
        svg,
    ):
        nodes.append((m.group(3).strip(), float(m.group(1)), float(m.group(2))))
    edges = []
    for m in re.finditer(
        r'<line[^>]*x1="([\d.]+)"[^>]*y1="([\d.]+)"[^>]*x2="([\d.]+)"[^>]*y2="([\d.]+)"',
        svg,
    ):
        x1, y1, x2, y2 = map(float, m.groups())

        def near(x, y):
            return min(nodes, key=lambda n: math.hypot(n[1] - x, n[2] - y))

        a, b = near(x1, y1), near(x2, y2)
        par, ch = (a, b) if a[2] < b[2] else (b, a)
        side = "L" if ch[1] < par[1] else ("R" if ch[1] > par[1] else "M")
        edges.append((par[0], ch[0], side, ch[1]))
    children = {n[0]: [] for n in nodes}
    for par, ch, side, _ in sorted(edges, key=lambda e: e[3]):
        children[par].append((ch, side))
    return nodes, children


def svg_of(pid):
    return re.search(r"<svg.*?</svg>", probs[pid]["conditions_html"], re.S).group(0)


def levels(children):
    allc = {c for v in children.values() for c, _ in v}
    root = [n for n in children if n not in allc]
    assert len(root) == 1, root
    lv = {root[0]: 1}
    q = [root[0]]
    while q:
        u = q.pop(0)
        for c, _ in children[u]:
            lv[c] = lv[u] + 1
            q.append(c)
    return root[0], lv


def descendants(children, u):
    out = []
    for c, _ in children[u]:
        out.append(c)
        out += descendants(children, c)
    return out


def shapes(h):
    if h == 0:
        yield frozenset()
        return

    def build(maxd):
        if maxd == 0:
            yield None
            return
        yield None
        for l in build(maxd - 1):
            for r in build(maxd - 1):
                yield (l, r)

    def pos(t, lvl, idx, acc):
        if t is None:
            return
        acc.add((lvl, idx))
        pos(t[0], lvl + 1, 2 * idx, acc)
        pos(t[1], lvl + 1, 2 * idx + 1, acc)

    for t in build(h):
        if t is None:
            continue
        acc = set()
        pos(t, 1, 0, acc)
        if max(l for l, _ in acc) == h:
            yield frozenset(acc)


def is_complete(S):
    h = max(l for l, _ in S)
    for L in range(1, h):
        if sum(1 for l, _ in S if l == L) != 2 ** (L - 1):
            return False
    last = sorted(i for l, i in S if l == h)
    return last == list(range(len(last)))


def is_full(S):
    h = max(l for l, _ in S)
    return all(sum(1 for l, _ in S if l == L) == 2 ** (L - 1) for L in range(1, h + 1))


def main():
    results = {}
    lines = []

    # p1
    _, ch1 = tree_from_svg(svg_of("p1"))
    root1, lv1 = levels(ch1)
    parent1 = {c: u for u, v in ch1.items() for c, _ in v}
    lv3 = sorted([n for n in ch1 if lv1[n] == 3], key=lambda s: int(s[1:]))
    sibs = [c for c, _ in ch1[parent1["v8"]] if c != "v8"]
    same_lv_other_par = [n for n in ch1 if lv1[n] == lv1["v8"] and parent1.get(n) != parent1["v8"]]
    desc_v8 = sorted(descendants(ch1, "v8"), key=lambda s: int(s[1:]))
    h1 = max(lv1.values())
    deg_v8 = len(ch1["v8"])
    results["p1"] = {
        "nodes": len(ch1),
        "edges": sum(len(v) for v in ch1.values()),
        "root": root1,
        "levels": {str(L): [n for n in ch1 if lv1[n] == L] for L in range(1, h1 + 1)},
        "a": lv3,
        "b": sibs,
        "b_other_parent_same_level": same_lv_other_par,
        "c": desc_v8,
        "d": h1,
        "e": deg_v8,
    }
    lines.append(f"[p1] nodes={len(ch1)} edges={results['p1']['edges']} a={lv3} b={sibs} c={desc_v8} d={h1} e={deg_v8}")

    # p6
    _, ch6 = tree_from_svg(svg_of("p6"))
    leaves6 = [n for n, v in ch6.items() if not v]
    nonleaves6 = [n for n, v in ch6.items() if v]
    _, lv6 = levels(ch6)
    max_lv_nodes6 = [n for n in ch6 if lv6[n] == max(lv6.values())]
    results["p6"] = {
        "nodes": len(ch6),
        "leaves": leaves6,
        "non_leaves": nonleaves6,
        "leaf_count": len(leaves6),
        "max_level_nodes_only": max_lv_nodes6,
    }
    lines.append(f"[p6] leaves={leaves6} count={len(leaves6)} non_leaves={nonleaves6}")

    # p7
    _, ch7 = tree_from_svg(svg_of("p7"))
    deg7 = {n: len(v) for n, v in ch7.items()}
    results["p7"] = {
        "nodes": len(ch7),
        "degrees": deg7,
        "tree_degree": max(deg7.values()),
        "degree_sum": sum(deg7.values()),
        "edges": len(ch7) - 1,
        "leaf_count": sum(1 for d in deg7.values() if d == 0),
    }
    lines.append(f"[p7] degrees={deg7} max={max(deg7.values())} sum={sum(deg7.values())}")

    # DP for binary tree heights (p8, p9)
    N = 35
    H = {0: {0}}
    for n in range(1, N + 1):
        s = set()
        for nl in range(n):
            for hl in H[nl]:
                for hr in H[n - 1 - nl]:
                    s.add(1 + max(hl, hr))
        H[n] = s
    by_h = {}
    for n in range(1, N + 1):
        for h in H[n]:
            by_h.setdefault(h, []).append(n)

    results["p8"] = {
        "level_max": [2 ** (i - 1) for i in range(1, 6)],
        "max_nodes_h5": max(by_h[5]),
        "min_nodes_h5": min(by_h[5]),
        "choices_possible_at_h5": {str(v): (v in by_h[5]) for v in (26, 8, 32, 31)},
    }
    lines.append(f"[p8] h5 nodes={min(by_h[5])}..{max(by_h[5])} choices={results['p8']['choices_possible_at_h5']}")

    results["p9"] = {
        "a_edges_n12": 12 - 1,
        "b_heights_n12": sorted(H[12]),
        "b_min_max": [min(H[12]), max(H[12])],
        "b_ceil_log2_13": math.ceil(math.log2(13)),
        "b_counterexample_n8_ceil_log2_8": math.ceil(math.log2(8)),
        "b_counterexample_n8_min_height": min(H[8]),
        "c_nodes_h4": by_h[4],
        "c_min_max": [min(by_h[4]), max(by_h[4])],
    }
    lines.append(f"[p9] a=11 b={results['p9']['b_min_max']} c={results['p9']['c_min_max']}")

    # p5
    p5_res = {}
    for K in range(1, 5):
        target = [S for S in shapes(K) if len(S) == 2 ** K - 1]
        p5_res[f"K={K}"] = {
            "count": len(target),
            "all_full": all(map(is_full, target)),
            "all_complete": all(map(is_complete, target)),
        }
    results["p5"] = p5_res
    lines.append(f"[p5] K=1..4 verified: {p5_res}")

    # p10
    _, ch10 = tree_from_svg(svg_of("p10"))

    def slots(ch):
        root, _ = levels(ch)
        acc = {}

        def go(u, lvl, idx):
            acc[u] = (lvl, idx)
            for c, s in ch[u]:
                go(c, lvl + 1, 2 * idx + (0 if s == "L" else 1))

        go(root, 1, 0)
        return acc

    S10 = slots(ch10)
    SS10 = frozenset(S10.values())
    h10 = max(l for l, _ in SS10)
    free10 = [i for i in range(2 ** (h10 - 1)) if (h10, i) not in SS10]
    par_of = {v: k for k, v in S10.items()}
    first_free = free10[0]
    k_parent = par_of[(h10 - 1, first_free // 2)]
    k_side = "L" if first_free % 2 == 0 else "R"
    ch_c = {u: [(c, ("R" if c == "J" else s)) for c, s in v] for u, v in ch10.items()}
    Sc = frozenset(slots(ch_c).values())
    results["p10"] = {
        "a_nodes": len(S10),
        "a_height": h10,
        "a_is_full": is_full(SS10),
        "a_is_complete": is_complete(SS10),
        "b_first_free_slot": first_free,
        "b_parent": k_parent,
        "b_side": k_side,
        "b_after_K_complete": is_complete(SS10 | {(h10, first_free)}),
        "c_all_deg_le_2": all(len(v) <= 2 for v in ch_c.values()),
        "c_is_complete": is_complete(Sc),
        "c_level4_slots": sorted(i for l, i in Sc if l == 4),
    }
    lines.append(f"[p10] a=(full:{is_full(SS10)},comp:{is_complete(SS10)}) b={k_parent}({k_side}) c=(deg<=2:{results['p10']['c_all_deg_le_2']},comp:{is_complete(Sc)},slots:{results['p10']['c_level4_slots']})")

    out_dir = Path(__file__).resolve().parent
    (out_dir / "verify_tree.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "verify_tree.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
