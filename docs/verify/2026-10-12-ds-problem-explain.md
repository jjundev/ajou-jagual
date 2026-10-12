# 자구알 문제설명 스킬 검증 기록

2026-10-12. 원본 커밋 `1e2d5f81813a5481c78341545a13ab300f2d82c5`. 동봉 템플릿 SHA-256 `d0fe664a773920cf017ccf69fc9e7b69ef9a7c6b0b066601da36aaf1f338ba50`는 원본 Git blob과 일치한다. assets/vendor도 원본과 바이트 동일하며 모든 파일 해시는 assets/port-provenance.json에 기록했다.

## 자동·실자료 확인

저장소 기본 `pytest -q` 14 tests, 신규 스킬 66 tests, 기존 ds-review-pack 100 tests 및 129 subtests. CLI --help와 독립 스킬 복사본의 실행은 정상이다. 실자료는 읽기만 수행해 0914 8문항, 0917 8문항, 0921 4문항을 추출했고 최신 1008은 문항 없음으로 중단한다. 0917의 p2/p7과 p6/p8은 원문/변형이라 출처 공유를 허용하고 카드 ID 중복·출처 누락은 거부한다.

## 화면 수용 검사

Playwright Chromium 153.0.8010.12. 합성 자료를 로컬 HTTP 서버로 렌더링했다. 실제 강의 문제설명을 저작하거나 발행하지 않았다. fixture의 C 문장은 문자 보존·가로 스크롤 검사 용도이며 C 의미 검증 결과가 아니다.

| 화면 | 테마 | 콘솔/KaTeX 오류 | 누락 자원 | 외부 요청 | 문서 가로 넘침 |
|---|---|---|---|---|---|
|1280×900|light|0|0|0|0|
|1280×900|dark|0|0|0|0|
|375×812|light|0|0|0|0|
|375×812|dark|0|0|0|0|

두 문항의 목차, 다음/이전, 요약 열기/닫기, 데스크톱 패널 키보드 resize, viewport resize, 테마 전환을 확인했다. 긴 코드의 `<`, `&`, `$`, 연산 상태 표, inline 수식, SVG, 로컬 raster 이미지와 요약을 확인했다. 모바일에서는 drawer 닫기를 검사했고 패널 resize는 데스크톱에만 적용했다. 실제 원 문제 링크와 anchor는 발행 기준 원 파일에 대해 기계 검사로 별도 대조했다.

## 재현

테스트 환경은 pytest와 playwright가 있는 임시 venv다. 실행기는 Python 3.10+ 표준 라이브러리만 필요하다.

```sh
python3 -m pytest .agents/skills/ds-problem-explain/tests -q
python3 .agents/skills/ds-problem-explain/tests/browser_acceptance.py /tmp/ds-explain-acceptance-new
python3 -m pytest .agents/skills/ds-review-pack/tests -q
```

브라우저 명령은 비어 있는 scratch 경로를 요구하고 results.json 및 4개 스크린샷을 만든 뒤 서버와 브라우저를 종료한다. 실제 수업 저작 시에는 각 문항의 source_visual/content/independent/browser 검토를 다시 수행해야 한다. 과제 카드·PDF는 지원하지 않는다.

## 독립 리뷰와 수정

별도 리뷰에서 Important 3건을 재현하고 실패 테스트를 먼저 추가한 뒤 수정했다. 디코딩된 C 텍스트를 HTML로 재파싱하던 원문 보존 비교를 고쳤다. 원문/설명 SVG는 각각 source/explain namespace로 분리했다. `(a) push(1), (b) pop()` 같은 순수 연산 목록은 단일 질문으로 유지하고 질문/연산이 섞인 불명확한 경우는 보류한다. 원문의 소문항 누락과 문단형 (a)/(b)도 회귀 검사에 추가했다.

수정 후 0914·0917·0921 전체 팩을 scratch에서 합성 설명으로 조립한 기계 보존 검사 20문항이 통과했다. 이것은 실제 수업 설명의 정답 승인이 아니다. 실제 수업 폴더에는 발행하지 않았다.

## 실행 중 판단과 비용

- Unicode 경로 테스트는 문자열 표기 동일성 대신 samefile을 사용했다. macOS의 NFC/NFD 동등 경로 처리 때문이며, 표기 문자열 자체는 보장하지 않는다.
- 시스템/동봉 Python에 pytest가 없어 임시 venv를 사용했다. 실행기 의존성은 늘리지 않았으며 테스트 환경 준비 비용만 생긴다.
- 동봉 html2md의 수식 보존 검사도 pre/code와 Markdown code를 제외했다. 코드의 `$`를 본문 수식과 짝짓는 오류를 막으며 코드 블록 안의 수식 검사는 수행하지 않는다.
- 서로 다른 카드의 기출 출처 공유를 허용했다. 실제 0917 원문/변형 사례 때문이며 의미적 중복 판별은 사람이 검토해야 한다.
- browser_acceptance.py를 테스트 도구로 보관했다. /tmp 스크립트 없이 재현 가능하게 하며 테스트 전용 파일 하나가 추가된다.
- 리뷰가 판단 제외한 실제 수업 정답·UB 해석은 설치 범위에 저작된 실제 설명이 없어 그대로 제외했다. 앞으로 실제 호출할 때 각 문제의 의미 검토가 필요하다.

Minor 보류 항목 없음. 커밋·푸시 없이 검증된 신규 파일을 주 작업 폴더에도 복사해 로컬 스킬을 사용할 수 있게 했다. 격리 작업 공간은 보존했다.
