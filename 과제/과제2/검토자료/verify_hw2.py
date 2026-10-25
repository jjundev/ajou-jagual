"""Check HW2 behavior against fixed examples and a byte-array memory model.

Detects wrong fit selection, lost blocks, failed coalescing, and mutation on failure.
Only the temporary test harness substitutes malloc to exercise allocation failure.
"""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import re
import subprocess
import tempfile


def model(total, commands):
    memory = [None] * total
    results = []
    maps = []
    for command in commands:
        parts = command.split()
        pid = int(parts[1])
        success = False
        if parts[0] == "ALLOC":
            size = int(parts[2])
            if pid not in memory:
                for start in range(total - size + 1):
                    if all(value is None for value in memory[start:start + size]):
                        memory[start:start + size] = [pid] * size
                        success = True
                        break
            results.append(f"ALLOC P{pid} {size}: {'SUCCESS' if success else 'FAIL'}")
        else:
            success = pid in memory
            memory = [None if value == pid else value for value in memory]
            results.append(f"FREE P{pid}: {'SUCCESS' if success else 'FAIL'}")
        blocks = []
        start = 0
        while start < total:
            end = start
            while end + 1 < total and memory[end + 1] == memory[start]:
                end += 1
            owner = "FREE" if memory[start] is None else f"P{memory[start]}"
            blocks.append(f"[{start}-{end}, {owner}]")
            start = end + 1
        maps.append(" <-> ".join(blocks))
    return results, maps


def cases():
    # Named traces catch distinct branches rather than a fixed required test count.
    records = [
        ("official-16", 100, ["ALLOC 1 20", "ALLOC 2 30"]),
        ("official-17", 100, ["ALLOC 1 20", "ALLOC 2 30", "ALLOC 3 10", "FREE 2", "FREE 1", "FREE 3"]),
        ("official-18", 50, ["ALLOC 1 30", "ALLOC 2 30", "FREE 7", "ALLOC 1 10"]),
        ("exact-fit-and-single-node", 1, ["ALLOC 1 1", "ALLOC 2 1", "FREE 1", "ALLOC 2 1"]),
        ("choose-first-not-best-fit", 40, ["ALLOC 1 15", "ALLOC 2 5", "ALLOC 3 10", "ALLOC 4 10", "FREE 1", "FREE 3", "ALLOC 5 8"]),
        ("merge-left", 30, ["ALLOC 1 10", "ALLOC 2 10", "ALLOC 3 10", "FREE 1", "FREE 2"]),
        ("merge-right", 30, ["ALLOC 1 10", "ALLOC 2 10", "ALLOC 3 10", "FREE 2", "FREE 1"]),
        ("merge-both", 30, ["ALLOC 1 10", "ALLOC 2 10", "ALLOC 3 10", "FREE 1", "FREE 3", "FREE 2"]),
        ("fragmentation-and-recovery", 30, ["ALLOC 1 10", "ALLOC 2 10", "ALLOC 3 10", "FREE 1", "FREE 3", "ALLOC 4 15", "FREE 2", "ALLOC 4 30"]),
        ("duplicate-absent-and-reuse", 20, ["ALLOC 1 8", "ALLOC 1 5", "FREE 7", "FREE 1", "FREE 1", "ALLOC 1 20"]),
        ("no-commands", 10, []),
    ]
    # Anchor the independent model to hand-checked values from the PDF.
    assert model(100, records[0][2])[1][-1] == "[0-19, P1] <-> [20-49, P2] <-> [50-99, FREE]"
    assert model(100, records[1][2])[1][-1] == "[0-99, FREE]"
    assert model(50, records[2][2])[0] == ["ALLOC P1 30: SUCCESS", "ALLOC P2 30: FAIL", "FREE P7: FAIL", "ALLOC P1 10: FAIL"]
    for seed in range(20):
        rng = random.Random(seed)
        commands = []
        for _ in range(80):
            pid = rng.randint(1, 12)
            commands.append(f"ALLOC {pid} {rng.randint(1, 25)}" if rng.random() < 0.65 else f"FREE {pid}")
        records.append((f"seeded-sequence-{seed}", 64, commands))
    return records


HARNESS = r'''
#include <assert.h>
#include <stdlib.h>
static int fail_next_allocation;
static void *checked_malloc(size_t size)
{
    if (fail_next_allocation) { fail_next_allocation = 0; return NULL; }
    return malloc(size);
}
#define malloc checked_malloc
#define main hw2_program_main
#include "SOURCE_PATH"
#undef main
#undef malloc

int main(void)
{
    MemoryList list;
    MemoryBlock *block;
    MemoryBlock *remainder;
    assert(init_list(&list, 20) == 1);
    block = list.head.next;
    assert(find_first_fit(&list, 10) == block);
    assert(find_process_block(&list, 1) == NULL);

    /* A split allocation failure must preserve the entire existing block. */
    fail_next_allocation = 1;
    assert(allocate_memory(&list, 1, 8) == 0);
    assert(list.head.next == block && list.head.prev == block);
    assert(block->prev == &list.head && block->next == &list.head);
    assert(block->start == 0 && block->size == 20 && block->pid == FREE_PID);

    assert(allocate_memory(&list, 1, 8) == 1);
    assert(find_process_block(&list, 1) == block);
    remainder = block->next;
    assert(remainder->start == 8 && remainder->size == 12);
    assert(remainder->prev == block && remainder->next == &list.head);
    assert(list.head.prev == remainder);
    assert(find_first_fit(&list, 13) == NULL);

    /* Exact fit must succeed without allocating a new node. */
    fail_next_allocation = 1;
    assert(allocate_memory(&list, 2, 12) == 1);
    assert(fail_next_allocation == 1);
    fail_next_allocation = 0;
    assert(allocate_memory(&list, 1, 1) == 0);
    assert(release_memory(&list, 7) == 0);
    assert(block->pid == 1 && remainder->pid == 2);

    assert(release_memory(&list, 1) == 1);
    assert(release_memory(&list, 2) == 1);
    assert(list.head.next == block && list.head.prev == block);
    assert(block->prev == &list.head && block->next == &list.head);
    assert(block->start == 0 && block->size == 20 && block->pid == FREE_PID);
    destroy_list(&list);
    assert(list.head.next == &list.head && list.head.prev == &list.head);
    return 0;
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    flags = ["-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-fsanitize=address,undefined", "-g"]
    report = {
        "source": str(source),
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "environment": platform.platform(),
        "compiler": subprocess.run(["clang", "--version"], capture_output=True, text=True, check=True).stdout,
        "flags": flags,
        "cases": [],
    }
    with tempfile.TemporaryDirectory(prefix="hw2-verify-") as work:
        work = Path(work)
        binary = work / "hw2"
        build = subprocess.run(["clang", *flags, str(source), "-o", str(binary)], capture_output=True, text=True)
        report["build"] = {"returncode": build.returncode, "stderr": build.stderr}
        if build.returncode == 0:
            for name, total, commands in cases():
                stdin = f"{total}\n{len(commands)}\n" + "\n".join(commands) + "\n"
                expected_results, expected_maps = model(total, commands)
                run = subprocess.run([str(binary)], input=stdin, capture_output=True, text=True, timeout=10)
                results = re.findall(r"(?:ALLOC P\d+ \d+|FREE P\d+): (?:SUCCESS|FAIL)", run.stdout)
                maps = re.findall(r"Memory map: (.*)", run.stdout)
                passed = run.returncode == 0 and not run.stderr and results == expected_results and maps == expected_maps
                report["cases"].append(dict(name=name, stdin=stdin, stdout=run.stdout, stderr=run.stderr, returncode=run.returncode, expected_results=expected_results, expected_maps=expected_maps, passed=passed))
            harness = work / "harness.c"
            harness.write_text(HARNESS.replace("SOURCE_PATH", str(source)))
            harness_binary = work / "harness"
            build_harness = subprocess.run(["clang", *flags, str(harness), "-o", str(harness_binary)], capture_output=True, text=True)
            harness_record = dict(name="allocation-failure-and-list-links", build_stderr=build_harness.stderr, build_returncode=build_harness.returncode, passed=False)
            if build_harness.returncode == 0:
                run = subprocess.run([str(harness_binary)], capture_output=True, text=True, timeout=10)
                harness_record.update(stdout=run.stdout, stderr=run.stderr, returncode=run.returncode, passed=run.returncode == 0 and not run.stderr)
            report["cases"].append(harness_record)
    report["passed"] = sum(case["passed"] for case in report["cases"])
    report["total"] = len(report["cases"])
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"{report['passed']}/{report['total']} cases passed; build exit {report['build']['returncode']}")
    for case in report["cases"]:
        if not case["passed"]:
            print("FAIL:", case["name"])
    raise SystemExit(0 if report["total"] and report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    main()
