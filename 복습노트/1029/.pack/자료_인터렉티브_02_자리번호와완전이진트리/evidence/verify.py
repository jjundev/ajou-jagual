"""Compare every authoring line and its state with an instrumented C run."""
import json
from pathlib import Path
import subprocess
import tempfile


def value(state, cell_id):
    return state["cells"][cell_id]["value"]["value"]


def visit_row(previous, step):
    state = step["state"]
    at = step["executed"]["at"]
    line = at["line"] + (100 if at["sourceId"] == "driver" else 0)
    key = depth = 0
    if line != 102:
        is_call = line in (101, 6, 7)
        frame_id = state["activeFrame"] if is_call else step["executed"]["frameId"]
        frame = state["frames"][frame_id]
        parameter = state["cells"][frame["parameterCellId"]]
        target = parameter["value"]["target"]
        key = value(state, target) if target else 0
        depth = value(state, frame_id + ".d")
        if is_call:
            assert parameter["value"] == previous["state"]["cells"][frame["argumentSourceCellId"]]["value"]
            assert frame["caller"] == previous["state"]["activeFrame"]
        if line == 8 or (line == 2 and key == 0):
            assert state["activeFrame"] == frame["caller"]
            assert parameter["lifetime"] == state["cells"][frame_id + ".d"]["lifetime"] == "ended"
            assert step["next"]["at"] == frame["resumeAt"]
    return (line, key, depth, value(state, "stats.n"), value(state, "stats.h"))


def slot_row(_, step):
    names = ("i", "gap", "n", "last", "complete", "perfect")
    return (step["executed"]["at"]["line"], *(value(step["state"], "main." + name) for name in names))


folder = Path(__file__).resolve().parent
traces = json.loads((folder.parent / "trace.json").read_text())
row = visit_row if traces["default"]["id"] == "height-1029" else slot_row
report = {}
with tempfile.TemporaryDirectory() as scratch:
    binary = Path(scratch) / "oracle"
    subprocess.run(["cc", "-std=c17", "-Wall", "-Wextra", "-Werror", str(folder / "oracle.c"),
                    "-o", str(binary)], check=True)
    for case, trace in traces.items():
        run = subprocess.run([str(binary), case], capture_output=True, text=True, check=True)
        steps = trace["lineSteps"]
        actual = [row(before, after) for before, after in zip(steps, steps[1:])]
        expected = [tuple(map(int, line.split())) for line in run.stderr.splitlines()]
        assert len(actual) == len(expected), (case, len(actual), len(expected))
        for index, (js, c) in enumerate(zip(actual, expected), 1):
            assert js == c, (case, index, js, c)
        assert "".join(steps[-1]["state"]["stdout"]) == run.stdout, case

        # Every output transition must add exactly its current C node or slot number.
        outputs = []
        for before, after, observation in zip(steps, steps[1:], expected):
            if observation[0] == (5 if row is visit_row else 6):
                outputs.append(str(observation[1]) + " ")
                assert after["prints"][-1]["cellId"] == f"node-{observation[1]}.key"
            else:
                assert before["prints"] == after["prints"]
            assert outputs == after["state"]["stdout"]
        report[case] = {"lines": len(expected), "stdout": run.stdout, "last": expected[-1]}

print(json.dumps({"compiler": subprocess.check_output(["cc", "--version"], text=True).splitlines()[0],
                  "status": "pass", "cases": report}, indent=2))
