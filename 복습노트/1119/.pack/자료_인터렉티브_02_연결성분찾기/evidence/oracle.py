"""Compile the lesson functions with observation hooks and compare execution to trace.json."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

SUPPORT = r'''
#include <assert.h>
#include <stdlib.h>

static GraphType *shared_graph;
static int observed(const char *tag, int a, int b, int c) {
    fprintf(stderr, "%s %d %d %d", tag, a, b, c);
    for (int i = 0; i < N; i++) fprintf(stderr, " %d", visited[i]);
    for (int i = 0; i < N; i++) fprintf(stderr, " %d", parent[i]);
    fprintf(stderr, "\n");
    return c;
}
static int adjacency(GraphType *g, int v, int w) {
    assert(g == shared_graph);
    return observed("matrix", v, w, g->adj_mat[v][w]);
}
static int unvisited(int w) {
    return !observed("visited", w, 0, visited[w]);
}
'''

MAIN = r'''
int main(int argc, char **argv) {
    assert(argc >= 3);
    GraphType g = {0};
    shared_graph = &g;
    for (int i = 0; i < N; i++) parent[i] = -1;
    for (int i = 3; i < argc; i++) {
        int a = argv[i][0] - '0', b = argv[i][1] - '0';
        assert(a >= 0 && a < N && b >= 0 && b < N && a != b);
        g.adj_mat[a][b] = g.adj_mat[b][a] = 1;
    }
    int start = atoi(argv[2]);
    DISPATCH
    return 0;
}
'''

LECTURE = ("01", "02", "04", "12", "23", "24", "34")
SPLIT = ("01", "02", "34")
CASES = {
    "default": ("dfs", 0, LECTURE),
    "dfs-lecture-3": ("dfs", 3, LECTURE),
    "dfs-split-0": ("dfs", 0, SPLIT),
    "bfs-lecture-0": ("bfs", 0, LECTURE),
    "bfs-lecture-3": ("bfs", 3, LECTURE),
    "bfs-split-0": ("bfs", 0, SPLIT),
}
GROUPS = {
    "default": ("components", 0, SPLIT),
    "bridge": ("components", 0, (*SPLIT, "23")),
    "isolated": ("components", 0, SPLIT[:-1]),
}


def instrument(source, components):
    header, functions = source.split("\nvoid dfs_mat", 1)
    functions = "void dfs_mat" + functions
    changes = [
        ("if (g->adj_mat[v][w] && !visited[w])", "if (adjacency(g, v, w) && unvisited(w))"),
        ("parent[w] = v;", 'parent[w] = v; observed("parent", w, 0, parent[w]);'),
        ('printf("%d ", v);', 'printf("%d ", v); observed("print", v, 0, 0);'),
    ]
    if components:
        changes += [
            ("visited[v] = count;", 'visited[v] = count; observed("mark", v, 0, visited[v]);'),
            ("if (!visited[i])", 'if (!observed("outer", i, 0, visited[i]))'),
            ("count = 0;", 'count = 0; observed("count", 0, 0, count);'),
            ("count++;", 'count++; observed("count", 0, 0, count);'),
        ]
        dispatch = "(void)start; find_connected_component(&g);"
    else:
        changes += [
            ("visited[v] = 1;", 'visited[v] = 1; observed("mark", v, 0, visited[v]);'),
            ("visited[w] = 1;", 'visited[w] = 1; observed("mark", w, 0, visited[w]);'),
            ('printf("%d ", w);', 'printf("%d ", w); observed("print", w, 0, 0);'),
            ("q[tail] = v; tail++;", 'q[tail] = v; observed("store", v, 0, tail); tail++; observed("push", v, head, tail);'),
            ("q[tail] = w; tail++;", 'q[tail] = w; observed("store", w, 0, tail); tail++; observed("push", w, head, tail);'),
            ("v = q[head]; head++;", 'v = q[head]; observed("current", v, head, tail); head++; observed("pop", v, head, tail);'),
        ]
        dispatch = "if (argv[1][0] == 'b') bfs_mat(&g, start); else dfs_mat(&g, start);"
    for match, replacement in changes:
        assert match in functions, match
        functions = functions.replace(match, replacement)

    # Execute the same recursion and loops and observe each call on entry and return.
    parts = functions.split("\nvoid ")
    for i, function in enumerate(parts):
        prefix = "" if i == 0 else "void "
        name = (prefix + function).split("(")[0].split()[-1]
        mode = {"dfs_mat": "dfs", "bfs_mat": "bfs", "find_connected_component": "components"}[name]
        argument = "0" if mode == "components" else "v"
        start, body = function.split("{", 1)
        before_return, close = body.rsplit("}", 1)
        parts[i] = (
            start + "{\n"
            f'    assert(g == shared_graph); observed("enter-{mode}", {argument}, 0, 0);'
            + before_return
            + f'    observed("return-{mode}", {argument}, 0, 0);\n' + "}" + close
        )
    return header + SUPPORT + "\n" + "\nvoid ".join(parts) + MAIN.replace("DISPATCH", dispatch)


def projected(snapshots):
    result = []
    previous_frame = None
    for snapshot in snapshots:
        state = snapshot["state"]
        cells = state["cells"]
        active = state["activeFrame"]
        name = lambda frame: state["frames"][frame]["functionId"]
        value = lambda field: cells[field]["value"]["value"]
        row = lambda prefix: [value(f"graph.{prefix}.{i}") for i in range(5)]
        location = snapshot["at"]["sourceId"]
        kind = snapshot["title"]
        if active != previous_frame:
            frame = active if kind == "함수 진입" else previous_frame
            suffix = {"dfs_mat": "dfs", "bfs_mat": "bfs", "find_connected_component": "components"}[name(frame)]
            argument = 0 if suffix == "components" else value(f"{frame}.v")
            event = (("enter-" if kind == "함수 진입" else "return-") + suffix, argument, 0, 0)
            assert cells[f"{frame}.g"]["value"] == {"kind": "pointer", "target": "graph.a.0.0"}
            assert cells[f"{frame}.g"]["lifetime"] == ("live" if kind == "함수 진입" else "ended")
        elif snapshot["reads"] and any(id.startswith("graph.a.") for id in snapshot["reads"]):
            cell_id = next(id for id in snapshot["reads"] if id.startswith("graph.a."))
            v, w = map(int, cell_id.split(".")[2:])
            assert value(f"{active}.v") == v and value(f"{active}.w") == w
            assert f"{active}.g" in snapshot["reads"]
            event = ("matrix", v, w, value(cell_id))
        elif snapshot["reads"] and snapshot["reads"][0].startswith("graph.visited."):
            cell_id = snapshot["reads"][0]
            v = int(cell_id.rsplit(".", 1)[1])
            assert value(f"{active}.{'i' if location == 'components' else 'w'}") == v
            event = ("outer" if location == "components" else "visited", v, 0, value(cell_id))
        elif kind == "큐 앞 정점 읽기":
            # Independently compare the next C assignment and current queue boundaries.
            assert snapshot["reads"] == [f"{active}.q.{value(f'{active}.head')}"]
            continue
        elif kind in {"큐 뒤에 추가", "큐 앞 정점 꺼내기", "현재 정점 갱신"}:
            head, tail = value(f"{active}.head"), value(f"{active}.tail")
            if kind == "큐 뒤에 추가":
                event = ("push", value(f"{active}.q.{tail-1}"), head, tail)
            else:
                event = ("pop" if kind == "큐 앞 정점 꺼내기" else "current", value(f"{active}.v"), head, tail)
        elif kind == "큐에 정점 저장":
            tail = value(f"{active}.tail")
            assert snapshot["writes"][0]["cellId"] == f"{active}.q.{tail}"
            event = ("store", value(f"{active}.q.{tail}"), 0, tail)
        elif kind in {"방문 표시", "발견 간선 기록"}:
            cell_id = snapshot["writes"][0]["cellId"]
            action = "mark" if kind == "방문 표시" else "parent"
            v = int(cell_id.rsplit(".", 1)[1])
            event = (action, v, 0, value(cell_id))
        elif kind == "정점 출력":
            event = ("print", int(state["stdout"][-1]), 0, 0)
        elif kind in {"성분 수 초기화", "성분 번호 증가"}:
            event = ("count", 0, 0, value("graph.count"))
        else:
            continue
        previous_frame = active
        result.append((*event, *row("visited"), *row("parent")))
    return result


def run(folder):
    traces = json.loads((folder / "trace.json").read_text())
    source = (folder / "source.c").read_text()
    components = "find_connected_component" in source
    cases = GROUPS if components else CASES
    assert traces.keys() == cases.keys()
    for trace in traces.values():
        assert all(item["text"] in source for item in trace["sources"])
    flags = ["-std=c17", "-Wall", "-Wextra", "-Werror", "-fsanitize=undefined", "-fno-sanitize-recover=all"]
    checks = []
    compiler = subprocess.check_output(["clang", "--version"], text=True).splitlines()[0]

    with tempfile.TemporaryDirectory() as temp:
        code, executable = Path(temp) / "oracle.c", Path(temp) / "oracle"
        code.write_text(instrument(source, components))
        subprocess.run(["clang", *flags, str(code), "-o", str(executable)], check=True)
        for case, (mode, start, edges) in cases.items():
            snapshots = traces[case]["snapshots"]
            initial = snapshots[0]["state"]["cells"]
            for v in range(5):
                for w in range(5):
                    assert initial[f"graph.a.{v}.{w}"]["value"]["value"] == int(f"{min(v,w)}{max(v,w)}" in edges)
            assert not any(snap["diagnostic"] for snap in snapshots)
            result = subprocess.run([str(executable), mode, str(start), *edges], check=True, capture_output=True, text=True)
            actual = [(words[0], *map(int, words[1:])) for line in result.stderr.splitlines() if (words := line.split())]
            expected = projected(snapshots)
            assert len(actual) == len(expected), (case, len(actual), len(expected))
            for index, (lhs, rhs) in enumerate(zip(actual, expected, strict=True)):
                assert lhs == rhs, (case, index, lhs, rhs)
            state = snapshots[-1]["state"]
            assert result.stdout == "".join(state["stdout"])
            assert state["activeFrame"] is None
            checks.append({"case": case, "eventsCompared": len(actual), "stdout": result.stdout.strip(),
                           "visited": actual[-1][4:9], "parent": actual[-1][9:14]})
    return {"status": "pass", "compiler": compiler, "flags": flags, "cases": checks}


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1])), indent=2))
