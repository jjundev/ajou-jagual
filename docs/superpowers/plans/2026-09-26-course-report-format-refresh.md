# Course Report Format Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 현재 과제1 Notion 보고서에서 확인한 구조와 사용자가 승인한 간격 선택을 후속 과제용 반복 보고서 양식에 반영한다.

**Architecture:** 기존 `programming-assignment-report` 스킬의 과목 조건부 링크는 유지한다. 그 링크가 가리키는 Markdown 참고 파일의 제목·실행 사례·간격 설명만 현행본에 맞게 고치고, 과제별 지시 우선과 PDF 실물 확인 원칙은 보존한다.

**Tech Stack:** Markdown, 프로젝트 로컬 Codex skill, Notion Markdown 다운로드.

**Spec:** `docs/superpowers/specs/2026-09-26-course-report-format-refresh-design.md`

## Global Constraints

- 적용 범위는 `[2026-2] 자료구조 및 알고리즘 이해` 후속 프로그래밍 과제 보고서다.
- 새 과제의 공식 지시와 작성자의 새로운 명시적 선택이 다르면 이를 우선한다.
- 과제1의 함수명, 사례·스크린샷 수, 표 열 너비, 날짜, 점수를 후속 과제에 고정하지 않는다.
- 현재 `과제/과제1/보고서_노션.md`와 그 백업, Notion 페이지, 과제 코드·PDF를 수정하지 않는다.
- Markdown만으로 PDF의 페이지 배치·표 대응·이미지 가독성을 통과로 표시하지 않는다.
- 작업 트리의 기존 변경을 보존하고 이번 작업의 참조 파일만 대상으로 삼는다.

## Review Focus

| Input or condition | Expected behavior | Owning check |
|---|---|---|
| 후속 과제의 채점표가 다른 페이지 방향을 요구 | 과목 양식과 차이를 밝히고 새 지시를 따른다 | Task 1 Step 5 |
| 한 소단원 아래 실행 화면 여러 장 | 제목 3을 사용할 수 있고 각 화면을 사례와 연결한다 | Task 1 Step 5 |
| 공식 예제에 상태 표가 필요 없음 | 입력·실제 출력·화면·분석만으로 구성할 수 있다 | Task 1 Step 5 |
| 예외 사례 여러 건을 요약 표에 모음 | 표 뒤 이미지·설명을 사례 순서대로 둔다 | Task 1 Step 5 |
| Markdown 구조는 맞지만 PDF에서 코드 표의 좌우가 분리됨 | PDF를 통과로 표시하지 않고 PDF 실물을 별도 점검한다 | Task 1 Step 5 |

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `.agents/skills/programming-assignment-report/references/data-structures-course-format.md` | Modify | 이 과목의 재사용 가능한 보고서 양식 |
| `.agents/skills/programming-assignment-report/SKILL.md` | Read only | 적용 범위와 참고 파일 연결, PDF 검증 원칙 확인 |
| `과제/과제1/보고서_노션.md` | Read only | 현재 Notion 본문 구조의 근거 |
| `docs/superpowers/specs/2026-09-26-course-report-format-refresh-design.md` | Read only | 승인된 설계 결정 |

### Task 1: 과목 보고서 양식 참고 파일 갱신

**Files:**
- Modify: `.agents/skills/programming-assignment-report/references/data-structures-course-format.md:5-16`
- Read: `.agents/skills/programming-assignment-report/SKILL.md:16-21`
- Read: `과제/과제1/보고서_노션.md`

**Interfaces:**
- Consumes: 스킬 본문의 상대 링크 `references/data-structures-course-format.md`와 승인된 설계 문서.
- Produces: 같은 경로의 갱신된 Markdown 양식. 코드 인터페이스 변경은 없다.

- [ ] **Step 1: 기준 자료와 변경 상태 확인.**

```bash
git status --short
sed -n '1,120p' docs/superpowers/specs/2026-09-26-course-report-format-refresh-design.md
sed -n '1,120p' .agents/skills/programming-assignment-report/references/data-structures-course-format.md
```

Expected: 기존 참조 문서에는 제목 3 설명이 없고, 출력·이미지·분석 사이에 각각 한 칸을 요구한다. 다른 작업 트리 변경은 수정하지 않는다.

- [ ] **Step 2: 현재 양식과 현행 Notion 구조의 불일치를 재확인한다.** 검사는 현재 참조 문서에서 실패해야 한다.

```bash
python3 - <<'PY'
from pathlib import Path
f = Path('.agents/skills/programming-assignment-report/references/data-structures-course-format.md').read_text()
assert '제목 3' in f, '실행 화면 묶음의 제목 3 규칙 누락'
assert '출력 텍스트·이미지·분석 사이는 한 칸' not in f, '현행본과 다른 일률적 간격 규칙'
assert '화면과 해당 설명' in f, '다중 사례의 이미지·설명 대응 누락'
PY
```

Expected: 첫 번째 검사에서 `AssertionError`가 발생한다.

- [ ] **Step 3: 참고 파일의 `Notion 본문`과 `코드와 실행 근거` 문단을 고친다.** 기존 과목 제한, 별도 표지, PDF 확인 문단은 유지한다. 수정 문장은 다음 내용을 포함한다.

```markdown
- 본문은 자동 목차로 시작한다. 대단원은 번호 없는 제목 1, 소단원은 번호 없는 제목 2로 두고 목차에 둘 다 표시한다. 한 소단원 아래 여러 실행 화면을 묶을 때는 제목 3을 사용할 수 있다. 제목 이름과 개수는 과제 요구에 맞춘다.
- 목차와 첫 대단원 사이 빈 블록은 한 칸, 대단원 사이는 두 칸, 같은 대단원의 소단원 사이는 한 칸이다. 대단원 바로 뒤 첫 소단원에는 빈 블록을 더하지 않는다. 출력·이미지·표·분석 사이에는 빈 블록을 기계적으로 삽입하지 않는다. 작성자가 정한 수동 줄바꿈과 표 셀 안 항목 순서를 임의로 정리하지 않는다.
- 소스 분석은 함수별 편집 가능한 2열 표를 기본으로 한다. 왼쪽에 실제 소스와 일치하는 텍스트 코드, 오른쪽에 같은 행 코드의 기능 명세와 동작 원리 분석을 둔다. 긴 함수는 코드와 설명의 대응을 유지하면서 여러 행으로 나눌 수 있다. 전역 정의·매크로·구조체·함수 원형은 해당 과제 요구에 맞게 포함한다.
- 개별 실행 사례에는 입력, 실제 출력 텍스트, 실제 터미널 실행 화면, 필요한 경우 상태·계산 표, 결과 분석을 가까이 둔다. 화면은 인접한 제목이나 설명으로 사례를 식별할 수 있게 하고 읽을 수 있는 크기로 한 줄에 한 장씩 둔다. 여러 경계값·예외 사례를 한 표에 모았다면 표 아래에 화면과 해당 설명을 사례 순서대로 둔다. 사례 수와 이미지 수는 실제 과제와 검증 범위에서 정한다.
```

Expected: 위 문장들은 기존 관련 문장을 교체한다. 같은 규칙을 중복해서 덧붙이지 않는다. 기존 `코드의 원래 줄바꿈`, `스크린샷은 실행 근거`, `PDF 확인` 규칙은 그대로 남긴다.

- [ ] **Step 4: 불일치 검사와 형식 검사를 통과시킨다.**

```bash
python3 - <<'PY'
from pathlib import Path
f = Path('.agents/skills/programming-assignment-report/references/data-structures-course-format.md').read_text()
assert '제목 3' in f
assert '출력 텍스트·이미지·분석 사이는 한 칸' not in f
assert '화면과 해당 설명' in f
assert '새 과제의 공식 지시나 작성자의 새로운 선택' in f
assert '파일을 직접 확인하기 전에는 PDF 양식이나 제출을 통과로 표시하지 않는다' in f
assert '스크린샷은 실행 근거다. 제출 보고서의 소스코드는 이미지로 대체하지 않는다' in f
PY
python3 /Users/hyunjun_macbook_pro/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/programming-assignment-report
git diff --check
git diff -- .agents/skills/programming-assignment-report/references/data-structures-course-format.md
```

Expected: Python 검사 정상 종료, `Skill is valid!`, 공백 오류 없음. Diff는 참조 파일의 해당 문단만 보여준다.

- [ ] **Step 5: 다섯 사용 상황을 문장에 대입해 검토한다.** `Review Focus`의 각 행을 순서대로 읽고, 새 지시 우선·제목 3 허용·상태 표 선택 가능·요약 표 뒤 화면과 설명의 순서·PDF 별도 검증을 해당 문장에서 확인한다. 모호한 문장은 참조 파일에서만 바로잡고 Step 4를 다시 실행한다.

- [ ] **Step 6: 변경 범위를 확인하고 해당 참조 파일만 커밋한다.** 기존의 다른 변경이나 다운로드 Markdown은 스테이징하지 않는다.

```bash
git add -- .agents/skills/programming-assignment-report/references/data-structures-course-format.md
git diff --cached --check
git diff --cached --stat
git commit -m "docs: align course report format with current Notion report"
```

Expected: 커밋에는 참조 파일만 포함된다. 별도 사용자 요청 없이 푸시하지 않는다.
