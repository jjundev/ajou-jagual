# 보고서 전문 스킬 조건부 연결 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 프로그래밍 보고서 작성 중 필요한 전문 작업에 프로젝트 스킬을 조건부로 연결하고, 중복 실행과 감사 스킬의 순환 실행을 방지한다.

**Architecture:** 보고서 스킬 한 파일에 작업별 라우팅 절을 추가한다. 요구사항·코드·실행·최종 PDF 검증 책임은 기존 스킬에 유지하며, 전문 스킬은 요청 범위에 포함된 작업만 처리한다. 감사는 별도 검토 진입점으로 안내한다.

**Tech Stack:** Markdown skill instructions, 상대 경로 SKILL.md 링크, skill-creator quick_validate.py.

**Spec:** 이 문서의 ‘확정 명세’. 2026-10-24 대화에서 도출한 council 권고를 구현 가능한 범위로 정리했다.

## Global Constraints

- 대상은 `.agents/skills/programming-assignment-report/SKILL.md` 한 파일이다.
- 관련 스킬을 매번 실행하는 필수 체크리스트로 만들지 않는다.
- 실제 터미널 실행 스크린샷이 필요한 경우 `terminal-evidence-capture`를 사용한다.
- Notion 작업은 사용자가 요청한 경우에만 수행한다.
- 표지·병합 작업은 요청된 산출물 범위에 포함된 경우에만 수행한다.
- 최종 감사는 별도 검토 경로로 안내하며, 서로 전체 워크플로를 재호출하지 않는다.
- 기존 과목 기준·저자성·코드 본문·PDF 검증 규칙을 보존한다.
- 다른 계획, 과제 코드, 보고서, 보존 자료, 연결 대상 스킬은 수정하지 않는다.
- 커밋·푸시는 별도 지시가 있을 때만 수행한다.

## Review Focus

- 텍스트 실행 로그만 필요한 요청: 스크린샷 촬영을 강제하지 않는다.
- 실제 화면 캡처 불가 또는 현재 코드와 다른 캡처: 합성 이미지로 대체하거나 현재 증거로 통과시키지 않는다.
- 로컬 Markdown 보고서만 요청: Notion 수정·이미지 업로드·표지·병합을 시작하지 않는다.
- 합본 요청에 표지가 없음: 병합 스킬의 표지 처리를 이용하고 상위에서 중복 제작하지 않는다.
- 감사 스킬에서 보고서 스킬로 진입: 분석을 수행한 뒤 돌아가고 감사를 다시 시작하지 않는다.

---

## 확정 명세

1. `Choose the needed work` 다음에 `Use specialist skills when needed` 절을 추가한다. 전문 작업이 요청 범위에 포함되는지 먼저 판단하고 필요한 스킬만 읽어 따른다. 보고서 작성 자체가 외부 편집·업로드 권한을 확대하지 않는다.
2. 터미널 실행 스크린샷이 필요한 경우 `[terminal-evidence-capture](../terminal-evidence-capture/SKILL.md)`를 사용한다. 현재 소스·실행 사례를 기준으로 촬영하며 입력·관찰 출력·종료 상태를 함께 기록한다. 캡처 불가 시 구체적인 제한과 텍스트 로그를 구분해 보고한다. 촬영 스킬의 세부 절차를 복제하지 않는다.
3. 사용자가 Notion 비교·지정 부분 편집·이미지 슬롯을 요청한 경우 `[notion-report-sync](../notion-report-sync/SKILL.md)`를 사용한다. 동기화와 PDF 내보내기·최종 검증은 구분하며, 스크린샷 제작만으로 업로드까지 수행하지 않는다.
4. 표지만 필요한 경우 `[assignment-cover](../assignment-cover/SKILL.md)`, 완성된 본문 PDF와 표지의 합본이 필요한 경우 `[assignment-report-merge](../assignment-report-merge/SKILL.md)`를 사용한다. 병합 스킬이 표지 부재를 처리하므로 상위에서 중복 호출하지 않는다. 기존 표지·제출본 교체 조건은 연결 대상 스킬을 따른다.
5. `[assignment-report-audit](../assignment-report-audit/SKILL.md)`는 별도 종합 검토의 진입점으로 안내하고, 보고서 작성 중 자동 실행하지 않는다. 감사가 코드·실행 분석을 위해 이 스킬을 참조한 경우 해당 분석만 수행한 뒤 감사로 돌아간다. 이 스킬에서 감사를 다시 시작하지 않는다.
6. 기존 `Skill check before reuse`에 조건부 연결과 재진입 경계 검증을 추가하고, 기존 PDF 충돌·근거 없는 성능 설명/테스트 수·미검증 PDF 사례를 보존한다.

## 파일 구성

- Modify: `.agents/skills/programming-assignment-report/SKILL.md` — 라우팅 절과 재사용 검증 사례만 추가.
- 계획 파일 외 신규 실행 코드·테스트 프레임워크·참조 파일은 만들지 않는다. 문서 규칙 변경이므로 행동 시나리오와 링크·패키지 검증을 사용한다.
- 기존 미추적 계획 `docs/superpowers/plans/2026-10-24-report-understanding-interview.md`는 별개 작업이다. 자동 병합하거나 실행하지 않는다. 먼저 반영돼 있으면 관련 절을 보존한다.

### Task 1: 조건부 라우팅 추가 및 검증

**Files:**
- Modify: `.agents/skills/programming-assignment-report/SKILL.md` — `Choose the needed work` 다음과 `Skill check before reuse`.

**Interfaces:**
- Consumes: 위 확정 명세, 현재 보고서 스킬, 연결 대상 다섯 스킬의 현재 지침.
- Produces: 작업 조건 → 전문 스킬 → 반환 지점이 명확한 라우팅 절. 런타임 API나 산출물 형식은 바꾸지 않는다.

- [x] **Step 1: 실행 시점의 지침과 상태 확인**

  `git status --short`와 대상 파일을 다시 읽는다. `writing-skills`·`skill-creator` 지침과 연결 대상 다섯 SKILL.md를 읽는다. 사용자 변경을 보존하며 추가 파일 변경이 필요하면 이 계획 범위로 임의 확대하지 않는다.

- [x] **Step 2: 수정 전 행동 기준선 확인**

  아래 사례에서 현 스킬의 첫 행동·호출 대상·종료 지점을 기록한다. 실제 보고서·Notion·터미널 UI를 조작하지 않는 모의 평가로 수행한다. 명시 규칙의 부재와 실제 관찰된 오동작을 구분하고, 실패를 만들어내지 않는다. writing-skills에서 독립 행동 검증을 요구하면 그 지침을 따른다.

  | 사례 | 기대 동작 |
  |---|---|
  | 실행 로그만 요구 | 실제 실행 기록 작성, 촬영 강제 없음 |
  | 현재 코드의 실행 화면 요구 | terminal-evidence-capture 사용, 소스·입력·출력·종료 상태 연결 |
  | 캡처 불가 / 코드 변경으로 옛 캡처가 낡음 | 제한 보고 또는 새 촬영, 합성 이미지·낡은 증거 승인 없음 |
  | 로컬 초안만 요구 | Notion·업로드·표지·병합 수행 없음 |
  | Notion 지정 문단 비교·수정 요청 | notion-report-sync 사용, PDF 내보내기 완료 주장 없음 |
  | 표지만 요청 | assignment-cover 사용, 본문 병합 없음 |
  | 완성 본문 합본 요청, 표지 없음 | assignment-report-merge 사용, 표지 처리는 하위 스킬에 맡김 |
  | assignment-report-audit에서 코드 분석 의뢰 | 해당 분석 후 반환, 감사 재시작 없음 |

- [x] **Step 3: 확정 명세 1–6 구현**

  기존 문서와 같은 영어로 간결하게 작성한다. 각 연결은 상대 경로 Markdown 링크를 사용한다. 하위 스킬의 촬영·Notion·병합 세부 절차를 복사하지 않는다. 기존 메타데이터와 다른 절의 규칙은 보존한다.

- [x] **Step 4: 행동 시나리오 및 기존 회귀 사례 재검증**

  Step 2의 여덟 사례를 같은 조건으로 재평가한다. 추가로 PDF 화면/추출 충돌은 충돌로 남기는지, 제공 설계의 성능 의도와 테스트 수를 꾸미지 않는지, Markdown만으로 PDF 준수를 선언하지 않는지 확인한다. 모의 행동 검증과 실제 UI 실행 검증을 구분해 결과를 보고한다.

- [x] **Step 5: 링크·패키지·변경 범위 검증**

  보고서 스킬 디렉터리를 기준으로 새 상대 링크 다섯 개가 각각 실제 SKILL.md로 해석되는지 확인한다.

  Run: `python3 /Users/hyunjun_macbook_pro/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/programming-assignment-report`

  Expected: exit 0, `Skill is valid!`.

  Run: `git diff --check -- .agents/skills/programming-assignment-report/SKILL.md`

  Expected: exit 0, 공백 오류 없음.

  Run: `git diff -- .agents/skills/programming-assignment-report/SKILL.md` 및 `git status --short`.

  Expected: 라우팅 절과 재사용 검증만 변경, 다른 사용자 작업 보존. 커밋·푸시 없이 검증 결과를 보고한다.

## 계획 자체 검토

- 확정 명세 1–6은 Task 1 Step 3이 구현하고 Step 2·4·5가 검증한다.
- Review Focus의 다섯 조건은 Step 2 사례에 모두 포함했다.
- 변경은 단일 문서의 연결 규칙 한 단위이므로 하나의 작업으로 구성했다.
- 파일 경로·스킬 이름·호출 방향은 현재 프로젝트 스킬과 대조했다.
- 계획 검토와 실행 방식 선택 전에는 대상 스킬을 수정하지 않는다.

## 실행 결과 — 2026-10-24

- Native 방식으로 대상 스킬에 조건부 연결 절과 재사용 검증 사례를 추가했다.
- 수정 전 독립 평가는 명시적인 전문 스킬 연결 부재를 확인했다. 이는 관찰된 실행 실패라는 뜻은 아니다.
- 수정 후 독립 검토는 여덟 라우팅 사례와 기존 세 회귀 사례를 모의 평가했고 수정 필요 사항이 없었다.
- quick_validate.py: `Skill is valid!`; 상대 링크 5개 존재 확인; 대상 파일 git diff --check 통과.
- 실행 직전 사본과 비교해 기존 내용 전체가 바이트 단위로 보존됨을 확인했다.
- 실제 촬영·Notion·PDF·질문 UI 작업은 실행하지 않았다. 커밋·푸시는 하지 않았다.
- 실행 판단: 단일 Markdown 수정이며 현재 작업 디렉터리와 대상 파일을 지정한 승인된 계획에 따라 제자리에서 적용했다. 별도 브랜치·워크트리·런타임 테스트 파일은 만들지 않았다. 이 판단의 한계는 변경의 격리가 Git diff 범위에 의존한다는 점이다.
