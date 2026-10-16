# 자구알 standalone 내보내기 구현 계획

**Goal:** 자구알 HTML 3종과 기존 문제·답안 PDF를 오프라인 공유용으로 내보내는 프로젝트 스킬을 만든다.

**Architecture:** 독립된 프로젝트 스킬에 표준 라이브러리 Python CLI와 고정 버전 vendor 자원을 동봉한다. HTML 의존성을 인라인하고 선택 문서 간 링크를 재작성한 뒤 검증된 결과만 최종 경로에 교체한다.

**Tech Stack:** Python 3, HTMLParser, pathlib, zipfile, pytest, Playwright(검증 전용).

**Spec:** 2026-10-17 채팅의 grill-yourself 설계. #5는 사용자 확정: 기본 묶음에 기존 문제·답안 PDF도 포함한다.

## 제약과 결정

- 원본 복습노트와 기존 스킬을 수정하지 않는다. 커밋·푸시는 하지 않는다.
- 기본 all은 HTML 3종과 기존 PDF 2종. --kind로 단일 HTML 종류를 지정하면 PDF는 제외한다. --no-pdf도 지원한다.
- 날짜 범위는 실제 팩 폴더를 선택한다. --kind 명시 시 누락은 실패하고 all의 누락은 보고한다.
- HTML 파일 직접 지정도 지원한다. 날짜 없는 호출은 후보를 보여주고 실패한다.
- 외부 표시 자원은 동봉 CDN 매핑만 허용한다. 일반 웹 이동 링크는 유지한다.
- 포함된 노트/PDF 링크와 fragment는 유지하고, 제외된 로컬 문서는 span으로 바꿔 보고한다.
- 최종 결과 검증 전 기존 출력은 건드리지 않는다. 출력 경로가 원본 파일과 겹치면 실패한다.
- 검증은 네트워크 차단 file://를 우선하고 HTTP 대체 확인은 구분한다.

## 파일과 작업

### 1. 선택·묶음·오류의 계약
- [x] `.agents/skills/export-standalone-note/tests/test_export_standalone_note.py`에 날짜·범위·종류·PDF 바이트 보존·충돌·실패 시 기존 결과 보존 테스트 작성.
- [x] pytest로 구현 전 실패 확인.
- [x] `scripts/export_standalone_note.py`에 선택, 인라인, 링크, 검증, 원자적 게시 구현.
- [x] 테스트 통과 확인.

### 2. 스킬과 자원
- [x] SKILL.md에 사용법·기본 PDF 동봉·실패 판단·브라우저 확인 기록.
- [x] 동봉 KaTeX 0.16.11·Pretendard 1.3.9와 라이선스·해시 기록 복사. 실행 시 다른 스킬에 의존하지 않는다.
- [x] `.claude/skills/export-standalone-note` 링크와 UI 메타데이터 추가.
- [x] skill-creator quick_validate 실행.

### 3. 실제 팩 검증
- [x] 실제 1015 팩과 all을 scratch에 내보내고 원본 해시 불변·ZIP 링크·PDF 바이트 대조.
- [x] 네트워크 차단 브라우저에서 3종 렌더·상호작용·형제 링크 확인.
- [x] 결과와 남은 제한을 보고한다.

## 검증 결과

- 단위 테스트 20개 통과. 실제 실패를 재현한 회귀 항목: KaTeX 내부 fetch 오인, window.fetch, file URI 링크, SVG fragment, script onload와 onclick 동적 로딩.
- skill-creator quick_validate 통과.
- 실제 all: 날짜 팩 10개, HTML 30개 + 기존 PDF 20개 = 총 50개. ZIP 219,274,815 bytes. PDF 원본 바이트 동일, 원본 복습노트 전체 파일 SHA-256 불변.
- Windows Chromium에서 네트워크 차단 file://로 1015 HTML 3종 확인. 수식 오류 0, 깨진 그림 0, 외부 요청 0, pageerror 0, Pretendard 로드 확인.
- 테마 전환, 모바일 풀이 펼치기, 문제설명 SVG 확대, 원 문제 문항 이동, 0907 큐·스택 위젯 enqueue 상태 변경 확인.
- 브라우저 검증의 초기 실패 두 가지는 테스트 전제 오류였다: TeX가 없는 복습문제에 수식 개수를 요구한 것과 풀이 패널·위젯 토픽을 열기 전에 클릭한 것. 실제 UI를 열어 검증하도록 테스트만 수정했다.
- 검증용 산출물은 OS 임시 폴더 jagual-standalone-acceptance-20261017-v3에 보존했다. 탐색기 수동 더블클릭 및 별도 태블릿은 미확인.
- 커밋·푸시하지 않음.
