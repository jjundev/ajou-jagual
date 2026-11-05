"""Blind verifier: self-contained solution derived only from supplied question text/figures.

This file intentionally never opens author answers, manifests, cards, or the repository.
Run: python independent_verify.py > independent-output.txt
"""
from dataclasses import dataclass
from copy import deepcopy
from collections import deque
import json
import math
from pathlib import Path


@dataclass
class Node:
    key: int
    left: object = None
    right: object = None


def tree_from_relations(root, relations):
    nodes = {}
    def get(k):
        if k is None:
            return None
        if k not in nodes:
            nodes[k] = Node(k)
        return nodes[k]
    for k, (left, right) in relations.items():
        get(k).left, get(k).right = get(left), get(right)
    return get(root)


def insert(root, key):
    if root is None:
        return Node(key)
    if key < root.key:
        root.left = insert(root.left, key)
    elif key > root.key:
        root.right = insert(root.right, key)
    return root


def build(keys):
    root = None
    for key in keys:
        root = insert(root, key)
    return root


def delete(root, key, replacement="successor"):
    assert root is not None
    if key < root.key:
        root.left = delete(root.left, key, replacement)
    elif key > root.key:
        root.right = delete(root.right, key, replacement)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        if replacement == "successor":
            candidate = root.right
            while candidate.left:
                candidate = candidate.left
            root.key = candidate.key
            root.right = delete(root.right, candidate.key, replacement)
        else:
            candidate = root.left
            while candidate.right:
                candidate = candidate.right
            root.key = candidate.key
            root.left = delete(root.left, candidate.key, replacement)
    return root


def walk(root, order):
    if root is None:
        return []
    v = [root.key]
    l, r = walk(root.left, order), walk(root.right, order)
    return {"pre": v+l+r, "in": l+v+r, "post": l+r+v}[order]


def sparse_array(root):
    result = {}
    def visit(t, i):
        if t is not None:
            result[i] = t.key
            visit(t.left, 2*i)
            visit(t.right, 2*i+1)
    visit(root, 1)
    return dict(sorted(result.items()))


def height(root):
    return 0 if root is None else 1+max(height(root.left), height(root.right))


def relations(root):
    result = {}
    def visit(t):
        if t:
            result[t.key] = {"left": t.left.key if t.left else None,
                             "right": t.right.key if t.right else None}
            visit(t.left)
            visit(t.right)
    visit(root)
    return result


def bst_violations(root, lower=-math.inf, upper=math.inf):
    if root is None:
        return []
    own = [] if lower < root.key < upper else [{"key": root.key, "lower_exclusive": lower, "upper_exclusive": upper}]
    return own + bst_violations(root.left, lower, root.key) + bst_violations(root.right, root.key, upper)


def snapshot(root):
    arr = sparse_array(root)
    return {"root": root.key if root else None, "relations": relations(root),
            "sparse_1based_array": arr, "preorder": walk(root, "pre"),
            "inorder": walk(root, "in"), "postorder": walk(root, "post"),
            "levelorder": list(arr.values()), "height_levels": height(root),
            "BST_violations": bst_violations(root)}


def complete_bst(sorted_keys):
    # Assign increasing keys during inorder of fixed occupied heap slots 1..n.
    n = len(sorted_keys)
    keys = iter(sorted_keys)
    def populate(i):
        if i > n:
            return None
        left = populate(2*i)
        t = Node(next(keys), left)
        t.right = populate(2*i+1)
        return t
    return populate(1)


def mirrored_shape(a, b):
    if a is None or b is None:
        return a is b
    return mirrored_shape(a.left, b.right) and mirrored_shape(a.right, b.left)


def search(root, key):
    path = []
    while root is not None:
        path.append(root.key)
        if key == root.key:
            return path, root
        root = root.left if key < root.key else root.right
    return path, None


def trace_insert(root, key):
    p, t, trace = None, root, []
    while t is not None:
        trace.append([p.key if p else None, t.key])
        if key == t.key:
            return root, {"loop_entry_pairs": trace, "body_iterations": len(trace),
                          "duplicate": True, "exit_p": p.key if p else None,
                          "exit_t": t.key, "changed_link": None}
        p = t
        t = p.left if key < p.key else p.right
    z = Node(key)
    if p is None:
        root, link = z, "root"
    elif key < p.key:
        p.left, link = z, f"{p.key}.left"
    else:
        p.right, link = z, f"{p.key}.right"
    return root, {"loop_entry_pairs": trace, "body_iterations": len(trace),
                  "final_false_condition_pair": [p.key if p else None, None],
                  "duplicate": False, "exit_p": p.key if p else None, "exit_t": None,
                  "changed_link": link, "new_key": z.key,
                  "new_links": [z.left, z.right]}


answers = {}

p1_initial = tree_from_relations(15, {15:(5,16), 5:(3,12), 12:(10,13), 10:(6,None),
    6:(None,7), 16:(None,20), 20:(18,23)})
assert not bst_violations(p1_initial)
answers["p1"] = {"initial": snapshot(p1_initial), "conventions": {}}
for convention in ("successor", "predecessor"):
    t, states = deepcopy(p1_initial), []
    for key in (13,16,5):
        t = delete(t, key, convention)
        assert not bst_violations(t)
        states.append({"deleted": key, "tree": snapshot(t)})
    assert walk(t,"in") == [3,6,7,10,12,15,18,20,23]
    answers["p1"]["conventions"][convention] = states

p2_keys = [520,490,650,380,570,250,450,610,280,430,460,580]
t = build(p2_keys)
answers["p2"] = {"initial": snapshot(t), "steps": []}
for key in (250,610):
    t = delete(t,key)
    answers["p2"]["steps"].append({"deleted":key, "tree":snapshot(t)})
arr = sparse_array(t)
answers["p2"]["array_slots_1_through_30"] = [arr.get(i) for i in range(1,31)]
assert sorted(arr.values()) == sorted(set(p2_keys)-{250,610})
assert not bst_violations(t)

for pid, keys in (("p3", list(range(110,301,10))), ("p5", list(range(1,17)))):
    t = complete_bst(keys)
    arr = sparse_array(t)
    n = len(keys)
    hmin = math.ceil(math.log2(n+1))
    assert sorted(arr) == list(range(1,n+1))
    assert not bst_violations(t)
    assert height(t) == hmin
    example_order = walk(t,"pre")
    assert sparse_array(build(example_order)) == arr
    answers[pid] = {"tree": snapshot(t), "example_input_order": example_order,
                   "also_valid_levelorder_input": list(arr.values()),
                   "array_slots_1_through_30": [arr.get(i) for i in range(1,31)],
                   "minimum_height_proof": f"n={n}; a height-{hmin-1} binary tree has at most {2**(hmin-1)-1} nodes, below {n}; constructed tree height={hmin}.",
                   "complete_proof": f"occupied 1-based heap slots are exactly 1..{n}; all earlier levels full, final level filled from left."}

t = tree_from_relations(5, {5:(3,7),3:(2,4),2:(1,None),7:(6,8),8:(None,9)})
assert not bst_violations(t)
assert mirrored_shape(t.left, t.right)
assert height(t) == 4
assert sparse_array(build(walk(t,"pre"))) == sparse_array(t)
answers["p4"] = {"tree":snapshot(t),"example_input_order":walk(t,"pre"),
    "also_valid_levelorder_input":list(sparse_array(t).values()),
    "symmetry_proof":"Shape mirror pairs: 3<->7; 2<->8; 4<->6; 1<->9. Empty child positions also mirror.",
    "minimum_height_proof":"9>2^3-1=7, so height at least 4 levels; construction attains 4.",
    "uniqueness_note":"Input order and symmetric minimum-height shape are not unique. Complete shape is not required."}

p6 = tree_from_relations(55,{55:(16,92),16:(4,29),29:(None,30),92:(60,None),60:(None,75)})
assert not bst_violations(p6)
path, found = search(p6,75)
assert found.key == 75
answers["p6"] = {"original":snapshot(p6),"search75_path":path,
                 "delete55":{}}
for convention in ("successor", "predecessor"):
    t=delete(deepcopy(p6),55,convention)
    assert not bst_violations(t)
    assert walk(t,"in") == [4,16,29,30,60,75,92]
    answers["p6"]["delete55"][convention]=snapshot(t)

balanced, skewed = build([2,1,3]), build([1,2,3])
for pid in ("p7","p8"):
    answers[pid] = {"answer":"X", "counterexample_same_n":3,
                   "balanced":snapshot(balanced),"skewed":snapshot(skewed),
                   "general_height_range_levels":"ceil(log2(n+1)) <= h <= n for n>=1"}
assert height(balanced)==2 and height(skewed)==3

answers["p9"]={
    "directly_viewed_figure": "work/ch08-q09-complexity.png",
    "table_header_literal":"삭제연산알고리즘 / 평균의 시간복잡도 / 최악의 시간복잡도",
    "figure_rows": ["탐색연산: O(log n), O(n) (printed)","삽입연산: blank, blank"],
    "fill_insertion_average":"O(log n)","fill_insertion_worst":"O(n)",
    "all_search_insert_delete":"O(h) worst upper bound per operation, using height h and ordinary linked BST operations",
    "average_assumptions":"Random BST model, e.g. n distinct keys inserted in uniformly random permutation, with suitable random target/new-key rank; expected path length O(log n). Equivalently a maintained logarithmic-height tree guarantees O(log n) worst path. Arbitrary ordinary BSTs need not have logarithmic height.",
    "worst_witness":"Sorted distinct insertions produce h=n chain; absent key beyond maximum requires n comparisons to insert; O(n).",
    "individual_best_case_note":"A root search or immediate insertion into a root's empty child can be O(1); table's average O(log n) is not a universal per-instance lower bound.",
    "header_note":"The first header literally mentions deletion, but rows visibly ask search and insertion. No deletion row is present in supplied figure."}

# Relations transcribed directly from supplied image, including 10.left=8.
p10=tree_from_relations(6,{6:(4,9),4:(2,5),2:(1,3),9:(7,10),10:(8,11)})
arr=sparse_array(p10)
assert arr == {1:6,2:4,3:9,4:2,5:5,6:7,7:10,8:1,9:3,14:8,15:11}
assert bst_violations(p10)==[{"key":8,"lower_exclusive":9,"upper_exclusive":10}]
answers["p10"]={"tree":snapshot(p10),"array_slots_1_through_15":[arr.get(i) for i in range(1,16)],
    "BST_answer":"No", "reason":"8 is in 9's right subtree, but 8<9. Local edge 8<10 passes; global ancestor condition fails. Inorder contains 9,8,10, hence is not increasing.",
    "directly_viewed_figure":"work/ch08-q10-tree.png"}

p11=tree_from_relations(18,{18:(7,26),7:(3,12),26:(None,31),31:(27,None)})
assert not bst_violations(p11)
path12,found12=search(p11,12)
path20,found20=search(p11,20)
assert found12.key==12 and found20 is None
bad=tree_from_relations(18,{18:(7,None),7:(None,20)})
assert bst_violations(bad)==[{"key":20,"lower_exclusive":7,"upper_exclusive":18}]
answers["p11"]={"a":{"student_one":"record","attribute_one":"field", "primary_key":"학번", "why":"학번은 서로 다르므로 레코드를 고유 식별한다. 이름은 중복 가능하므로 고유 키로 부적합."},
    "b":{"BST":"No","reason":"20 is in root18's left subtree, violating 20<18; 20>7 alone is insufficient.","duplicate7":"Not permitted by the stipulated unique-key strict-order BST."},
    "c":{"search12":{"compared_keys":path12,"return":"address of node key12"},"search20":{"compared_keys":path20,"next_link":"26.left=NULL","return":"NULL"},"return_is_array_index":False,"reason":"search returns TreeNode*, the found node address; no integer array index is returned by the given linked-tree procedure."}}

t,trace_a=trace_insert(deepcopy(p11),9)
before_duplicate=snapshot(t)
t,trace_b=trace_insert(t,9)
assert snapshot(t)==before_duplicate
empty,trace_c=trace_insert(None,9)
assert len(sparse_array(t))==8 and len(sparse_array(empty))==1
answers["p12"]={"a":{"trace":trace_a,"result":before_duplicate},
    "b":{"trace":trace_b,"node_count_before":8,"node_count_after":8,"links_unchanged":True,
           "reason":"Equal-key test returns before p=t or link update at the second 9; no new node is attached."},
    "c":{"trace":trace_c,"result":snapshot(empty),"root":"address of newly inserted node9"},
    "loop_wording_note":"loop_entry_pairs lists starts of executed while bodies. Final failing guard for (a) is (12,NULL), and (c)'s initial guard is (NULL,NULL), with zero body iterations."}

assert set(answers)=={f"p{i}" for i in range(1,13)}
result = {"status":"12 questions independently solved; all embedded assertions passed", "read_scope":"Supplied blind problem text, slides.txt theory, and directly viewed p9/p10 figure PNGs only", "height_convention":"root level1; empty height0; height counts levels as lecture slides", "empty_array_slot":"JSON null denotes empty; slot0 unused", "answers":answers, "unresolved":[]}
out=Path(__file__).with_name("independent-results.json")
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(result,ensure_ascii=False,indent=2))
print("\nPASS: independent simulation, complete/symmetric proofs, traversals, strict BST invariants and traces checked.")
