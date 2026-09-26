# 자료구조 보고서 반복 양식 스킬 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 이 과목의 후속 프로그래밍 과제 보고서에 합의한 Notion 작성 양식을 재사용하되 과제별 지시와 실제 PDF 검증을 우선한다.

**Architecture:** 기존 프로젝트 로컬 스킬은 일반 보고서 검토 흐름을 유지한다. 짧은 조건부 링크로 이 과목의 양식 참조 문서를 읽게 하고, 참조 문서에는 반복되는 레이아웃·입출력 증거·PDF 점검만 기록한다.

**Tech Stack:** Markdown, Codex skill package, Notion Markdown export, PDF 검토 도구.

**Spec:** `docs/superpowers/specs/2026-09-26-course-report-format-skill-design.md` — 실행자는 계획과 설계를 모두 읽는다.

## Global Constraints

- 적용 범위는 **[2026-2] 자료구조 및 알고리즘 이해**의 후속 프로그래밍 과제 보고서다.
- 후속 과제의 공식 지시와 사용자의 새로운 명시적 선택이 다르면 차이를 밝히고 해당 과제 요구사항을 따른다.
- 과제1의 함수명, 사례 수, 스크린샷 8장, 점수와 날짜를 재사용 규칙으로 고정하지 않는다.
- 기존 스킬의 작성자 본인 설명, 실제 실행 근거, 최종 PDF 실물 검증 규칙을 보존한다.
- 현재 보고서, Notion 페이지, C 소스, PDF와 무관한 작업 트리 변경을 수정하지 않는다.
- 스킬 수정은 Notion 편집·PDF 내보내기·아주BB 제출을 수행하거나 완료로 표시하지 않는다.

## Review Focus

| Input or condition | Expected behavior | Owning check |
|---|---|---|
| 다른 과목의 프로그래밍 보고서 | 과목 양식을 자동 적용하지 않고 해당 과제 지시를 읽는다 | Task 1 Step 5 |
| 같은 과목이지만 새 채점표가 A4 세로를 요구 | 기존 A4 가로 기본값과의 충돌을 밝히고 새 지시를 따른다 | Task 1 Step 5 |
| Notion 화면은 정상이지만 PDF에서 한 표 행의 좌우가 갈라짐 | 양식 검증을 통과로 표시하지 않고 PDF 배치를 조정한다 | Task 1 Step 5 |
| 실행 스크린샷에 코드가 보이나 텍스트 코드가 없음 | 텍스트 코드 의무를 충족했다고 판단하지 않는다 | Task 1 Step 5 |
| 다음 과제의 실행 사례가 3건 또는 12건 | 8장으로 맞추지 않고 실제 분석·검증 사례에 맞춘다 | Task 1 Step 5 |

---

## 파일 구조

| Path | Action | Responsibility |
|---|---|---|
| `.agents/skills/programming-assignment-report/SKILL.md` | Modify | 과목 조건과 참조 링크만 추가; 공통 원칙 유지 |
| `.agents/skills/programming-assignment-report/references/data-structures-course-format.md` | Create | 반복 양식과 PDF 확인 기준 |
| `docs/superpowers/specs/2026-09-26-course-report-format-skill-design.md` | Read | 범위·근거·우선순위 |
| `과제/과제1/과제 채점기준.pdf`, `과제/과제1/보고서_노션.md` | Read only | 공식 양식과 현재 Notion 구조의 근거 |

### Task 1: 이 과목의 반복 양식을 조건부 참조로 추가

**Files:**
- Modify: `.agents/skills/programming-assignment-report/SKILL.md:16-20`
- Create: `.agents/skills/programming-assignment-report/references/data-structures-course-format.md`
- Read: `docs/superpowers/specs/2026-09-26-course-report-format-skill-design.md`

**Interfaces:**
- Consumes: 기존 스킬의 과제별 계약 확인과 최종 PDF 검증 원칙.
- Produces: 스킬 본문의 상대 링크 `references/data-structures-course-format.md`. 이 과목에서만 읽는 양식 참조 문서이며, 후속 자동화 코드는 없다.

- [x] **Step 1: 기준 상태 확인.** 프로젝트 루트에서 설계와 스킬을 읽고 현재 작업 트리의 다른 변경을 확인한다.

~~~bash
git status --short
sed -n '1,110p' docs/superpowers/specs/2026-09-26-course-report-format-skill-design.md
sed -n '1,100p' .agents/skills/programming-assignment-report/SKILL.md
~~~

Expected: 스킬은 일반 보고서 검토·PDF 검증을 설명하며, 과목별 참조 파일은 아직 없다. 이미 파일이 존재한다면 덮어쓰기 전에 그 내용을 검토한다.

- [x] **Step 2: 참조 문서 작성.** 다음 내용을 `.agents/skills/programming-assignment-report/references/data-structures-course-format.md`에 쓴다. 과제별 함수명과 고정 사례 수를 추가하지 않는다.

~~~markdown
# 자료구조 및 알고리즘 이해: 반복 보고서 양식

이 문서는 [2026-2] 자료구조 및 알고리즘 이해의 후속 프로그래밍 과제 보고서에만 적용한다. 새 과제의 공식 지시나 작성자의 새로운 선택이 다르면 차이를 밝히고 그 과제의 요구를 따른다. 과제1의 함수명, 사례 수, 날짜, 점수는 재사용하지 않는다.

## Notion 본문

- 본문은 자동 목차로 시작한다. 대단원은 제목 1, 소단원은 제목 2로 두며 번호를 붙이지 않는다. 목차에는 두 수준을 모두 표시한다.
- 목차와 첫 대단원 사이 빈 블록은 한 칸, 대단원 사이는 두 칸, 같은 대단원의 소단원 사이는 한 칸이다. 대단원 바로 뒤 첫 소단원에는 빈 블록을 더하지 않는다. 작성자가 정한 수동 줄바꿈과 표 셀 안 항목 순서를 임의로 정리하지 않는다.
- 학번·이름·보고서 제목은 별도 표지에 둔다. 상세 실행 환경은 실제 빌드 근거와 확인 범위에 맞춰 기록한다. 본문 첫머리에 학생 정보나 기계적인 실행 방식 안내를 자동 복원하지 않는다.

## 코드와 실행 근거

- 소스 분석은 함수별 편집 가능한 2열 표를 기본으로 한다. 왼쪽에 실제 소스와 일치하는 텍스트 코드, 오른쪽에 같은 행 코드의 기능 명세와 동작 원리 분석을 둔다. 전역 정의·매크로·구조체·함수 원형은 해당 과제 요구에 맞게 포함한다.
- 코드의 원래 줄바꿈을 보존한다. PDF에서 폭 때문에 생기는 추가 자동 줄바꿈은 줄이되 코드 내용을 바꾸지 않는다. 여러 페이지에 걸친 표는 행 사이에서 넘길 수 있으나 같은 행의 코드와 분석을 서로 다른 페이지에 두지 않는다.
- 실행 사례에는 입력·실제 출력 텍스트와 실제 터미널 스크린샷을 함께 둔다. 스크린샷에 사례명을 붙여 읽을 수 있는 크기로 한 줄에 한 장씩 둔다. 개별 예제는 결과 분석 가까이에, 여러 사례를 한 표에 모았다면 이미지들을 표 아래에 행 순서대로 둔다. 출력 텍스트·이미지·분석 사이는 한 칸, 다음 사례 전은 소단원 간격을 따른다. 사례 수와 이미지 수는 실제 과제와 검증 범위에서 정한다.
- 스크린샷은 실행 근거다. 제출 보고서의 소스코드는 이미지로 대체하지 않는다.

## PDF 확인

- Notion에서 본문을 A4 가로 PDF로 내보낸다. 별도의 A4 가로 표지를 만든 뒤 병합한다. 페이지 번호는 넣지 않는다.
- 내보낸 PDF에서 코드와 분석의 좌우 대응, 텍스트 코드의 선택·추출, 코드 자동 줄바꿈, 행 분리, 머리행 반복 여부, 제목만 남는 페이지, 넓은 표와 스크린샷의 가독성을 확인한다. 필요하면 정한 간격을 유지하면서 페이지 나누기·열 너비·행 높이를 조정한다.
- Notion 화면, Markdown, 본문 PDF, 병합 PDF, 실제 제출을 서로 다른 상태로 기록한다. 파일을 직접 확인하기 전에는 PDF 양식이나 제출을 통과로 표시하지 않는다.
~~~

- [x] **Step 3: 기존 스킬에 조건부 링크 추가.** `SKILL.md`의 “Establish the assignment contract”에서 과제별 지시 확인 문단 뒤에 첫 문장을 추가한다. 기존의 “다른 과제에 이 프로젝트 양식을 적용하지 말라”는 문장은 두 번째 문장으로 바꿔 과목 기본값과 새 채점표 확인이 충돌하지 않게 한다. 다른 검증 원칙은 삭제하거나 완화하지 않는다.

~~~markdown
- For follow-up programming reports in this workspace's **[2026-2] 자료구조 및 알고리즘 이해** course, read [the course report format](references/data-structures-course-format.md). Treat it as the author's recurring format, then compare it with the new assignment's official instructions and explicit choices. Do not apply it to other courses or turn HW1-specific counts into defaults.
- Separate requirements for code, report content, document layout, and submission. Do not carry an assignment's page layout, point values, or examples into another assignment without checking its rubric; only the linked course format is a reusable layout default within its stated scope.
~~~

- [x] **Step 4: 스킬 형식과 파일 상태 검증.**

~~~bash
python3 /Users/hyunjun_macbook_pro/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/programming-assignment-report
git diff --check
git status --short
~~~

Expected: `Skill is valid!`; whitespace 오류 없음; 이 작업에서 바뀐 파일은 스킬 본문과 새 참조 문서뿐이다. 기존 사용자 변경은 그대로다.

- [x] **Step 5: 다섯 실제 사용 상황을 수동 검토.** `Review Focus`의 각 행을 미래 요청으로 가정하고 스킬 본문과 참조 문서를 함께 읽는다. 다른 과목에는 링크를 적용하지 않는지, 새 채점표가 우선인지, PDF를 보지 않고 통과라고 하지 않는지, 스크린샷으로 텍스트 코드를 대체하지 않는지, 사례 수를 고정하지 않는지 각각 확인한다. 하나라도 모호하면 두 문서의 해당 문장만 고친 뒤 Step 4를 다시 실행한다.

- [x] **Step 6: 범위가 맞으면 해당 파일만 스테이징하고 기록한다.** 기존 `.agents/` 전체나 과제1·임시 파일은 스테이징하지 않는다.

~~~bash
git add -- .agents/skills/programming-assignment-report/SKILL.md .agents/skills/programming-assignment-report/references/data-structures-course-format.md docs/superpowers/specs/2026-09-26-course-report-format-skill-design.md docs/superpowers/plans/2026-09-26-course-report-format-skill.md
git diff --cached --check
git diff --cached --stat
git commit -m "docs: record recurring course report format"
~~~

Expected: 커밋에는 위 네 문서만 포함되고 과제 원고, C 코드, Notion 페이지와 PDF는 포함되지 않는다. 푸시는 별도 요청 전까지 수행하지 않는다.
