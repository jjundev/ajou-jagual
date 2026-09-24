# Practice 1 Comment and Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the completed Catalan-path C program while adding useful Korean comments and creating a source-grounded Markdown report worksheet that covers every grading requirement.

**Architecture:** Treat the C source and report as separate deliverables. First characterize and preserve the executable behavior while changing comments only; then build the report in three layers: fixed structure, function-by-function code analysis prompts, and verified execution evidence. The Markdown remains an editable draft whose paired code/analysis sections map directly to a later two-column Notion/PDF layout.

**Tech Stack:** C11, Clang or GCC, POSIX shell, Markdown, `rg`, `awk`

**Spec:** `docs/superpowers/specs/2026-09-21-practice1-report-design.md`

## Global Constraints

- Preserve the signatures and behavior of `combination`, `catalan_comb`, `catalan`, and `main` exactly.
- Preserve every existing prompt and result string in `Practice 1.c` exactly.
- Limit C changes to Korean comments; do not change executable statements.
- Analyze all four functions, including the three functions supplied with the exercise.
- Keep source code in the report as selectable text, never as screenshots.
- Explain function purpose and operating principle instead of translating code line by line.
- Keep the report as Markdown in this plan; Notion upload and PDF conversion are outside scope.
- Use verified facts, equations, and writing questions; do not produce submission prose that falsely represents the user's authorship.
- Stage only the exact files named by each task because the repository already contains unrelated changes.
- Add no dependencies and create no permanent test harness.

---

## File Structure

- Modify: `실습/실습1/Practice 1.c` — completed implementation plus concise explanatory comments.
- Create: `실습/실습1/실습1_보고서.md` — editable report worksheet containing problem facts, all four source functions, analysis questions, verified output, and a final checklist.
- Read: `실습/실습1/Practice 1.pdf` — authoritative exercise definition and examples.
- Read: `과제/과제1/과제 채점기준.pdf` — provisional report layout and content standard.
- Read: `docs/superpowers/specs/2026-09-21-practice1-report-design.md` — implementation constraints and accepted decisions.

### Task 1: Preserve Behavior and Improve Source Comments

**Files:**
- Modify: `실습/실습1/Practice 1.c:1-63`
- Test: one-off compiler and shell checks; create no repository test file

**Interfaces:**
- Consumes: existing signatures `long long combination(int n, int r)`, `long long catalan_comb(int x, int y)`, `int catalan(int x, int y)`, and `int main(void)`.
- Produces: the same signatures and output strings, with comments that Task 3 can use as factual cues.

- [ ] **Step 1: Characterize the current implementation across the PDF's coordinate range**

Run:

```bash
verify_dir=$(mktemp -d /tmp/practice1-before.XXXXXX)
cc -std=c11 -Wall -Wextra -Wpedantic -fsanitize=address,undefined \
  './실습/실습1/Practice 1.c' -o "$verify_dir/practice1"
for x in 0 1 2 3 4 5 6 7; do
  y=0
  while [ "$y" -le "$x" ]; do
    printf '%s %s\n' "$x" "$y"
    y=$((y + 1))
  done
done > "$verify_dir/input.txt"
printf '2 4\n' >> "$verify_dir/input.txt"
"$verify_dir/practice1" < "$verify_dir/input.txt" > "$verify_dir/output.txt"
awk '
/using combination formula:/ { formula=$NF; pairs++ }
/using recursion:/ {
  recursion=$NF
  if (formula != recursion) {
    mismatches++
    print "MISMATCH", formula, recursion
  }
}
/Invalid input:/ { invalid_exit++ }
END {
  printf("valid_pairs=%d mismatches=%d invalid_exit=%d\n",
         pairs, mismatches+0, invalid_exit+0)
}
' "$verify_dir/output.txt"
```

Expected:

```text
valid_pairs=36 mismatches=0 invalid_exit=1
```

- [ ] **Step 2: Replace sparse comments with concise function and branch explanations**

Use `apply_patch` to make only the following comment-level changes. Keep every declaration and executable statement byte-for-byte unchanged.

```c
#include <stdio.h>

/* 조합 nCr을 반복 계산으로 구한다. 대칭성을 이용해 반복 횟수를 줄인다. */
long long combination(int n, int r) {
  if (r < 0 || r > n)
    return 0;

  /* nCr과 nC(n-r)은 같으므로 더 작은 쪽만 계산한다. */
  if (r > n - r)
    r = n - r;

  long long result = 1;

  /* 팩토리얼을 직접 만들지 않고 항을 하나씩 곱하고 나눈다. */
  for (int i = 1; i <= r; i++) {
    result = result * (n - r + i) / i;
  }

  return result;
}

/* 전체 경로에서 경계 x < y를 넘는 경로를 빼서 기준값을 구한다. */
long long catalan_comb(int x, int y) {
  if (y < 0 || y > x)
    return 0;
  return combination(x + y, y) - combination(x + y, y - 1);
}

/* 왼쪽 좌표와 아래쪽 좌표의 경로 수를 더하는 재귀 함수이다. */
int catalan(int x, int y) {
  int result = 0;

  /* 허용 영역을 벗어난 좌표에서는 경로를 만들 수 없다. */
  if (y < 0 || x < y) {
    return 0;
  }

  /* x축 위에서는 오른쪽으로만 이동하므로 경로가 하나이다. */
  if (y == 0) {
    return 1;
  }

  /* 현재 좌표로 들어오는 두 방향의 경로 수를 합친다. */
  result = catalan(x - 1, y) + catalan(x, y - 1);
  return result;
}

/* 좌표를 반복 입력받아 조합식과 재귀식의 결과를 함께 출력한다. */
int main(void) {
```

After the `main` header comment, leave lines 43-63 unchanged.

- [ ] **Step 3: Compile the commented source with strict warnings**

Run:

```bash
cc -std=c11 -Wall -Wextra -Wpedantic -fsyntax-only \
  './실습/실습1/Practice 1.c'
```

Expected: exit status 0 and no compiler output.

- [ ] **Step 4: Re-run the behavioral characterization after the comment edit**

Run:

```bash
verify_dir=$(mktemp -d /tmp/practice1-after.XXXXXX)
cc -std=c11 -Wall -Wextra -Wpedantic -fsanitize=address,undefined \
  './실습/실습1/Practice 1.c' -o "$verify_dir/practice1"
for x in 0 1 2 3 4 5 6 7; do
  y=0
  while [ "$y" -le "$x" ]; do
    printf '%s %s\n' "$x" "$y"
    y=$((y + 1))
  done
done > "$verify_dir/input.txt"
printf '2 4\n' >> "$verify_dir/input.txt"
"$verify_dir/practice1" < "$verify_dir/input.txt" > "$verify_dir/output.txt"
awk '
/using combination formula:/ { formula=$NF; pairs++ }
/using recursion:/ {
  recursion=$NF
  if (formula != recursion) {
    mismatches++
    print "MISMATCH", formula, recursion
  }
}
/Invalid input:/ { invalid_exit++ }
END {
  printf("valid_pairs=%d mismatches=%d invalid_exit=%d\n",
         pairs, mismatches+0, invalid_exit+0)
}
' "$verify_dir/output.txt"
```

Expected:

```text
valid_pairs=36 mismatches=0 invalid_exit=1
```

- [ ] **Step 5: Commit only the comment change**

```bash
git add -- './실습/실습1/Practice 1.c'
git diff --cached --check
git diff --cached -- './실습/실습1/Practice 1.c'
git commit -m "docs: explain practice 1 catalan code"
```

### Task 2: Create the Markdown Report Structure

**Files:**
- Create: `실습/실습1/실습1_보고서.md`
- Test: structural checks with `test` and `rg`

**Interfaces:**
- Consumes: the accepted report rules in `docs/superpowers/specs/2026-09-21-practice1-report-design.md`.
- Produces: stable section headings and left/right mapping labels used by Tasks 3 and 4.

- [ ] **Step 1: Verify that the report file does not already exist**

Run:

```bash
test -f './실습/실습1/실습1_보고서.md'
```

Expected: exit status 1. If it exists, stop and inspect it before making any change.

- [ ] **Step 2: Create the report skeleton**

Use `apply_patch` to create the file with this exact initial content:

````markdown
# 실습 1. Recursion 보고서

- 이름: ____________________
- 학번: ____________________
- 과목: 자료구조 및 알고리즘 이해

> 이 문서는 보고서 작성을 위한 초안이다. 각 `내 설명` 항목은 코드를 보지 않고도 설명할 수 있는 자기 문장으로 작성한 뒤 검토한다.

## 1. 실습 목적

### 작성 질문

- 이 실습에서 재귀 호출로 구하려는 값은 무엇인가?
- 조합식으로 계산한 값을 함께 출력하는 이유는 무엇인가?

## 2. 문제 정의

- 시작점은 `(0,0)`이다.
- 한 번에 오른쪽 또는 위쪽으로 한 칸 이동한다.
- 허용 좌표는 `x >= y`, `y >= 0`이다.
- `y == 0`일 때 경로 수는 1이다.
- 허용 영역 밖의 좌표에서 경로 수는 0이다.
- 일반 좌표에서는 `f(x,y) = f(x-1,y) + f(x,y-1)`을 사용한다.

### 내 설명

- 좌표 제한이 필요한 이유:
- 재귀식에서 두 값을 더하는 이유:
- 종료 조건이 없으면 생기는 문제:

## 3. 함수별 소스코드 분석

각 함수는 최종 Notion/PDF에서 `왼쪽 칸: 소스 코드`, `오른쪽 칸: 기능 및 동작 원리`로 배치한다.

## 4. 실행 결과 및 분석

## 5. 시간·공간 복잡도와 구현 한계

## 6. 제출 전 확인

- [ ] 네 함수의 소스 코드가 모두 텍스트로 들어 있다.
- [ ] 네 함수의 목적과 동작 원리를 각각 설명했다.
- [ ] 실행 결과와 값이 나온 이유를 함께 설명했다.
- [ ] 코드 캡처 이미지를 사용하지 않았다.
- [ ] 최종 변환 시 함수별 왼쪽 코드·오른쪽 분석 형식을 적용했다.
- [ ] 이름과 학번을 확인했다.
````

- [ ] **Step 3: Verify every required top-level section**

Run:

```bash
report='./실습/실습1/실습1_보고서.md'
for heading in \
  '# 실습 1. Recursion 보고서' \
  '## 1. 실습 목적' \
  '## 2. 문제 정의' \
  '## 3. 함수별 소스코드 분석' \
  '## 4. 실행 결과 및 분석' \
  '## 5. 시간·공간 복잡도와 구현 한계' \
  '## 6. 제출 전 확인'
do
  rg -Fq "$heading" "$report" || exit 1
done
printf 'report_structure=PASS\n'
```

Expected:

```text
report_structure=PASS
```

- [ ] **Step 4: Commit the report structure**

```bash
git add -- './실습/실습1/실습1_보고서.md'
git diff --cached --check
git diff --cached -- './실습/실습1/실습1_보고서.md'
git commit -m "docs: scaffold practice 1 report"
```

### Task 3: Add All Function Sources and Analysis Questions

**Files:**
- Modify: `실습/실습1/실습1_보고서.md`
- Read: `실습/실습1/Practice 1.c`
- Test: function and analysis coverage checks with `rg`

**Interfaces:**
- Consumes: the four unchanged C signatures and the `## 3. 함수별 소스코드 분석` heading from Task 2.
- Produces: four paired sections whose `왼쪽 칸` contains selectable code and whose `오른쪽 칸` contains concrete self-explanation questions.

- [ ] **Step 1: Insert the `combination` pair under Section 3**

Insert this block immediately after the paragraph under `## 3. 함수별 소스코드 분석`:

````markdown
### 3.1 `combination`

#### 왼쪽 칸 — 소스 코드

```c
long long combination(int n, int r) {
  if (r < 0 || r > n)
    return 0;

  if (r > n - r)
    r = n - r;

  long long result = 1;

  for (int i = 1; i <= r; i++) {
    result = result * (n - r + i) / i;
  }

  return result;
}
```

#### 오른쪽 칸 — 기능 및 동작 원리

작성할 내용:

- 입력 `n`, `r`과 반환값이 각각 무엇을 뜻하는지 설명한다.
- `r < 0 || r > n`에서 0을 반환하는 이유를 설명한다.
- `nCr = nC(n-r)` 대칭성을 이용하면 반복 횟수가 왜 줄어드는지 설명한다.
- 팩토리얼 세 개를 따로 계산하지 않고 항을 하나씩 곱하고 나누는 방식을 설명한다.

내 설명:

````

- [ ] **Step 2: Insert the `catalan_comb` pair after Section 3.1**

````markdown
### 3.2 `catalan_comb`

#### 왼쪽 칸 — 소스 코드

```c
long long catalan_comb(int x, int y) {
  if (y < 0 || y > x)
    return 0;
  return combination(x + y, y) - combination(x + y, y - 1);
}
```

#### 오른쪽 칸 — 기능 및 동작 원리

작성할 내용:

- 이 함수가 재귀 함수 결과를 확인하는 기준값이라는 점을 설명한다.
- 좌표 제한을 무시한 전체 경로 수가 `C(x+y,y)`가 되는 이유를 설명한다.
- 경계 `x < y`를 넘는 경로 수를 `C(x+y,y-1)`로 계산하여 빼는 의미를 설명한다.
- `(3,2)`에서 `C(5,2)-C(5,1)=10-5=5`가 되는 과정을 확인한다.

내 설명:

````

- [ ] **Step 3: Insert the `catalan` pair after Section 3.2**

````markdown
### 3.3 `catalan`

#### 왼쪽 칸 — 소스 코드

```c
int catalan(int x, int y) {
  int result = 0;

  if (y < 0 || x < y) {
    return 0;
  }

  if (y == 0) {
    return 1;
  }

  result = catalan(x - 1, y) + catalan(x, y - 1);
  return result;
}
```

#### 오른쪽 칸 — 기능 및 동작 원리

작성할 내용:

- 이 함수가 `(0,0)`에서 `(x,y)`까지 갈 수 있는 허용 경로 수를 반환한다는 점을 설명한다.
- `y < 0` 또는 `x < y`인 좌표에서 0을 반환하는 이유를 설명한다.
- `y == 0`에서는 오른쪽으로만 이동할 수 있어 경로가 하나라는 점을 설명한다.
- `(x,y)`에 도착하는 마지막 이동이 `(x-1,y)` 또는 `(x,y-1)`에서 온다는 점으로 재귀식을 설명한다.
- 금지 좌표 검사 뒤에 재귀 호출을 두어 호출이 종료되는 흐름을 설명한다.

내 설명:

````

- [ ] **Step 4: Insert the `main` pair after Section 3.3**

````markdown
### 3.4 `main`

#### 왼쪽 칸 — 소스 코드

```c
int main(void) {
  int x, y;
  int result;
  long long answer;

  while (1) {
    printf("Enter the values of x and y (or invalid value to exit): ");
    scanf("%d %d", &x, &y);

    if (x < y || y < 0) {
      printf("Invalid input: y cannot be greater than x or y cannot be "
             "negative. Exiting the program.\n");
      break;
    }

    result = catalan(x, y);
    answer = catalan_comb(x, y);
    printf("Catalan number C(%d, %d) using combination formula: %lld\n", x, y,
           answer);
    printf("Catalan number C(%d, %d) using recursion: %d\n", x, y, result);
  }
}
```

#### 오른쪽 칸 — 기능 및 동작 원리

작성할 내용:

- 잘못된 좌표가 입력될 때까지 반복하는 전체 흐름을 설명한다.
- 입력 조건 `x < y || y < 0`이 실습의 허용 좌표와 어떻게 연결되는지 설명한다.
- 같은 좌표를 `catalan`과 `catalan_comb`으로 각각 계산하는 이유를 설명한다.
- 두 결과가 같으면 재귀 구현을 확인할 수 있다는 점을 설명한다.

내 설명:

````

- [ ] **Step 5: Verify source and analysis coverage for all four functions**

Run:

```bash
report='./실습/실습1/실습1_보고서.md'
for marker in \
  '### 3.1 `combination`' \
  '### 3.2 `catalan_comb`' \
  '### 3.3 `catalan`' \
  '### 3.4 `main`' \
  '#### 왼쪽 칸 — 소스 코드' \
  '#### 오른쪽 칸 — 기능 및 동작 원리'
do
  rg -Fq "$marker" "$report" || exit 1
done
test "$(rg -c '^내 설명:$' "$report")" -eq 4
printf 'function_sections=4 analysis_slots=4 status=PASS\n'
```

Expected:

```text
function_sections=4 analysis_slots=4 status=PASS
```

- [ ] **Step 6: Commit the function-analysis worksheet**

```bash
git add -- './실습/실습1/실습1_보고서.md'
git diff --cached --check
git diff --cached -- './실습/실습1/실습1_보고서.md'
git commit -m "docs: add practice 1 function analysis worksheet"
```

### Task 4: Add Verified Execution Evidence and Complete QA

**Files:**
- Modify: `실습/실습1/실습1_보고서.md`
- Read: `실습/실습1/Practice 1.c`
- Test: compiler, sanitizer, output, report coverage, whitespace, and scoped staging checks

**Interfaces:**
- Consumes: report Sections 4 and 5 from Task 2 and the unchanged executable behavior from Task 1.
- Produces: text execution evidence, case-specific analysis questions, complexity facts, and a report that passes every mechanical coverage check.

- [ ] **Step 1: Generate the exact representative output from the current source**

Run:

```bash
evidence_dir=$(mktemp -d /tmp/practice1-evidence.XXXXXX)
cc -std=c11 -Wall -Wextra -Wpedantic \
  './실습/실습1/Practice 1.c' -o "$evidence_dir/practice1"
printf '5 2\n5 4\n4 2\n2 4\n' | "$evidence_dir/practice1" \
  > "$evidence_dir/output.txt"
cat "$evidence_dir/output.txt"
```

Expected output values:

```text
C(5, 2): formula 14, recursion 14
C(5, 4): formula 42, recursion 42
C(4, 2): formula 9, recursion 9
(2, 4): invalid input and program exit
```

The full verified prompt text is reproduced in Step 2 and must be inserted without rewriting it.

- [ ] **Step 2: Fill Section 4 with the captured output and case-specific questions**

Replace the empty `## 4. 실행 결과 및 분석` section body with this exact structure and verified terminal output:

````markdown
## 4. 실행 결과 및 분석

### 4.1 실행 입력

```text
5 2
5 4
4 2
2 4
```

### 4.2 실제 실행 출력

```text
Enter the values of x and y (or invalid value to exit): Catalan number C(5, 2) using combination formula: 14
Catalan number C(5, 2) using recursion: 14
Enter the values of x and y (or invalid value to exit): Catalan number C(5, 4) using combination formula: 42
Catalan number C(5, 4) using recursion: 42
Enter the values of x and y (or invalid value to exit): Catalan number C(4, 2) using combination formula: 9
Catalan number C(4, 2) using recursion: 9
Enter the values of x and y (or invalid value to exit): Invalid input: y cannot be greater than x or y cannot be negative. Exiting the program.
```

### 4.3 결과별 분석 질문

#### `(5,2)`의 결과가 14인 경우

- 재귀식에서 어떤 두 좌표의 결과가 합쳐지는가?
- 조합식 결과와 재귀 결과가 같은 것이 무엇을 확인해 주는가?

내 설명:

#### `(5,4)`의 결과가 42인 경우

- 대각선 경계에 가까운 좌표에서도 `x >= y` 조건이 어떻게 유지되는가?
- PDF의 경로 수 표와 실제 출력이 일치하는가?

내 설명:

#### `(4,2)`의 결과가 9인 경우

- `(3,2)`와 `(4,1)`의 경로 수를 이용해 9를 설명할 수 있는가?

내 설명:

#### `(2,4)`가 잘못된 입력인 경우

- `x < y`가 어떤 좌표 영역을 뜻하는가?
- 프로그램이 결과 계산 대신 종료하는 흐름을 설명할 수 있는가?

내 설명:
````

- [ ] **Step 3: Fill Section 5 with verified complexity and limitation facts**

Replace the empty `## 5. 시간·공간 복잡도와 구현 한계` section body with:

```markdown
## 5. 시간·공간 복잡도와 구현 한계

### 확인된 사실

- `combination`은 `r`과 `n-r` 중 작은 값만큼 반복하므로 시간 복잡도는 `O(min(r,n-r))`, 추가 공간은 `O(1)`이다.
- `catalan`은 같은 좌표를 여러 번 다시 계산하므로 호출 수가 빠르게 증가한다. 단순 상한은 `O(2^(x+y))`로 볼 수 있다.
- 재귀 호출 깊이는 한 경로에서 최대 `x+y`에 비례하므로 호출 스택 공간은 `O(x+y)`이다.
- `catalan`의 반환형이 `int`이므로 좌표가 커지면 표현 범위를 넘을 수 있다.

### 내 설명

- 이 실습이 효율적인 최적화보다 재귀식의 이해에 초점을 둔다고 판단한 근거:
- 같은 좌표를 반복 계산하는 예:
- 큰 좌표를 입력할 때 생길 수 있는 문제:
```

- [ ] **Step 4: Verify report completeness and exact output evidence**

Run:

```bash
report='./실습/실습1/실습1_보고서.md'
for marker in \
  '### 3.1 `combination`' \
  '### 3.2 `catalan_comb`' \
  '### 3.3 `catalan`' \
  '### 3.4 `main`' \
  '### 4.1 실행 입력' \
  '### 4.2 실제 실행 출력' \
  '### 4.3 결과별 분석 질문' \
  '## 5. 시간·공간 복잡도와 구현 한계' \
  '## 6. 제출 전 확인'
do
  rg -Fq "$marker" "$report" || exit 1
done
rg -Fq 'Catalan number C(5, 2) using combination formula: 14' "$report" || exit 1
rg -Fq 'Catalan number C(5, 4) using recursion: 42' "$report" || exit 1
rg -Fq 'Catalan number C(4, 2) using recursion: 9' "$report" || exit 1
rg -Fq 'Invalid input: y cannot be greater than x or y cannot be negative. Exiting the program.' "$report" || exit 1
test "$(rg -c '^내 설명:$' "$report")" -eq 8
printf 'report_coverage=PASS analysis_slots=8 output_evidence=PASS\n'
```

Expected:

```text
report_coverage=PASS analysis_slots=8 output_evidence=PASS
```

- [ ] **Step 5: Run the final C verification**

Run:

```bash
final_dir=$(mktemp -d /tmp/practice1-final.XXXXXX)
cc -std=c11 -Wall -Wextra -Wpedantic -fsanitize=address,undefined \
  './실습/실습1/Practice 1.c' -o "$final_dir/practice1"
for x in 0 1 2 3 4 5 6 7; do
  y=0
  while [ "$y" -le "$x" ]; do
    printf '%s %s\n' "$x" "$y"
    y=$((y + 1))
  done
done > "$final_dir/input.txt"
printf '2 4\n' >> "$final_dir/input.txt"
"$final_dir/practice1" < "$final_dir/input.txt" > "$final_dir/output.txt"
awk '
/using combination formula:/ { formula=$NF; pairs++ }
/using recursion:/ {
  recursion=$NF
  if (formula != recursion) mismatches++
}
/Invalid input:/ { invalid_exit++ }
END {
  if (pairs != 36 || mismatches != 0 || invalid_exit != 1) exit 1
  printf("c_verification=PASS valid_pairs=%d mismatches=%d invalid_exit=%d\n",
         pairs, mismatches+0, invalid_exit+0)
}
' "$final_dir/output.txt"
git diff --check -- './실습/실습1/Practice 1.c' './실습/실습1/실습1_보고서.md'
```

Expected:

```text
c_verification=PASS valid_pairs=36 mismatches=0 invalid_exit=1
```

- [ ] **Step 6: Inspect only the intended final diff**

Run:

```bash
git diff -- './실습/실습1/Practice 1.c' './실습/실습1/실습1_보고서.md'
git status --short -- './실습/실습1/Practice 1.c' './실습/실습1/실습1_보고서.md'
```

Expected: the C diff contains comments only; the report diff contains the worksheet, exact text output, analysis questions, and complexity facts. No other path appears in the scoped status output.

- [ ] **Step 7: Commit the verified execution and QA additions**

```bash
git add -- './실습/실습1/실습1_보고서.md'
git diff --cached --check
git diff --cached -- './실습/실습1/실습1_보고서.md'
git commit -m "docs: add verified practice 1 report evidence"
```

## Self-Review Results

- Spec coverage: Task 1 covers comment-only C changes and behavior preservation; Tasks 2 and 3 cover report structure and all four functions; Task 4 covers execution analysis, complexity, and final validation.
- Scope coverage: Notion upload, PDF conversion, algorithm optimization, and input-flow changes remain excluded.
- Interface consistency: every task uses the original four function signatures and the same report path.
- Authorship boundary: the report contains facts and concrete self-explanation questions, while the user's own analysis text remains their responsibility.
