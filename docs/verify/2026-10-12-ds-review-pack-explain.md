# 복습팩 문제설명 자동 연결 및 기존 9팩 검증

2026-10-12, Native 실행. 9팩 64문항의 현재 복습문제 전체를 입력으로 문제설명 HTML·MD를 발행했다. 원 복습문제·정리노트·기존 그림·과거 제작자료·문제은행 256개 파일의 bytes/SHA-256이 작업 전과 같다. 1012의 기존 8문항 설명은 백업 후 현재 12문항 설명으로 교체했다.

신규·update-existing·lite 모드는 최종 리뷰의 정확한 절대 HTML 경로로 ds-problem-explain의 추출·전체 저작·독립 검산·조립·기계 검사·실자료/내용/브라우저 검토·발행을 이어 실행한다. bank는 기존 절차를 유지한다. 실패하면 원 리뷰와 이전 해설을 지키고 “복습팩 생성됨 / 문제설명 보류”로 보고한다.

| 날짜 | 문항 | HTML | MD | 네 검토 |
|---|---:|---|---|---|
| 0907 | 4 | [해설 HTML](../../복습노트/0907/문제설명_0907_Intro_DS_Algorithms.html) | [해설 MD](../../복습노트/0907/문제설명_0907_Intro_DS_Algorithms.md) | source/content/independent/browser pass |
| 0914 | 12 | [해설 HTML](../../복습노트/0914/문제설명_0914_Recursion.html) | [해설 MD](../../복습노트/0914/문제설명_0914_Recursion.md) | source/content/independent/browser pass |
| 0917 | 12 | [해설 HTML](../../복습노트/0917/문제설명_0917_Recursion.html) | [해설 MD](../../복습노트/0917/문제설명_0917_Recursion.md) | source/content/independent/browser pass |
| 0921 | 8 | [해설 HTML](../../복습노트/0921/문제설명_0921_ArrayStructureList.html) | [해설 MD](../../복습노트/0921/문제설명_0921_ArrayStructureList.md) | source/content/independent/browser pass |
| 0928 | 4 | [해설 HTML](../../복습노트/0928/문제설명_0928_ArrayStructureList.html) | [해설 MD](../../복습노트/0928/문제설명_0928_ArrayStructureList.md) | source/content/independent/browser pass |
| 1001 | 4 | [해설 HTML](../../복습노트/1001/문제설명_1001_List.html) | [해설 MD](../../복습노트/1001/문제설명_1001_List.md) | source/content/independent/browser pass |
| 1005 | 4 | [해설 HTML](../../복습노트/1005/문제설명_1005_List.html) | [해설 MD](../../복습노트/1005/문제설명_1005_List.md) | source/content/independent/browser pass |
| 1008 | 4 | [해설 HTML](../../복습노트/1008/문제설명_1008_Stack.html) | [해설 MD](../../복습노트/1008/문제설명_1008_Stack.md) | source/content/independent/browser pass |
| 1012 | 12 | [해설 HTML](../../복습노트/1012/문제설명_1012_Queue.html) | [해설 MD](../../복습노트/1012/문제설명_1012_Queue.md) | source/content/independent/browser pass |

검증 결과:

- ds-review-pack 전체: **156 passed, 137 subtests passed**. 납품·과거 보존·문자 표시 검사 23개 포함.
- ds-problem-explain 전체: **72 passed**. 원문 그림 스타일 보존과 위험 스타일/저작 스타일 거부 검사 포함.
- 실제 조립본: 1280×900·375×812, light/dark에서 64문항을 각각 확인(256회). 모든 목차·이전/다음·문항별 요약·수식·코드·표·그림을 검사. 콘솔/KaTeX/자원 오류, 외부 요청, 문서 가로 넘침 0.
- 발행 경로: 동일한 네 조합에서 모든 문항 이동·자원과 실제 원 문제 링크 HTTP200을 재확인. 발행 HTML이 검토한 최종 조립본 bytes와 같다. [브라우저 기록](2026-10-12-ds-review-pack-explain-browser.json).
- C11, -Wall -Wextra -Werror, ASan/UBSan으로 작성한 C 완성본과 선언을 검산. 별도 Python 상태 추적, GCD 양수 10000쌍, 반복문 n=0..20, 리스트 모든 삽입/삭제 위치, 재귀 반환과 후위식 계산을 대조. 증명은 불변식·종료 조건·공약수 보존과 성장률 논증을 포함한다.
- 그림 포함 교과서 실제 페이지를 렌더링해 대조했다. 기출 PDF·로컬 HWP BodyText·텍스트 원본·강의록·현재 정리노트와 대조했다. 기존 풀이/은행 답은 독립 검산을 대신하지 않았다.
- git diff --check 통과. 커밋·푸시는 수행하지 않았다.

원문과 조건의 구분:

- 0914 p2: 원문의 k<30 / i++는 k가 바뀌지 않아 n≥2에서 정상 종료/유한 T(n)을 보장하지 않는다. 리뷰가 명시한 k++ 가정 아래에서만 30n(n−1)/2, O(n²)을 설명한다. 원문 정상 실행값을 승인하지 않았다.
- 순환 결함 찾기: 비종료 코드의 정상 실행 결과 대신 감소·바닥 조건 누락을 분석한다.
- 십진→이진: 양수 입력의 코드이며 0은 출력 없음, 음수는 범위 밖이라고 밝힌다.
- sizeof: 명시한 검산 환경 조건을 유지한다. 입력 범위·overflow와 안전 검산 추가 코드를 원 빈칸 답과 구분한다.
- 1012 p2: 변환할 중위식 값25와 별도 표의 후위식 값31을 구별한다. 괄호 번호 문제의 두 번째 예시는 미닫힌 괄호가 남는 번호 출력 예시이다.

계획에서 조정한 사항:

1. 현재 강의 폴더의 최종 경로를 유지하려고 codex/ds-review-pack-explain 분기에서 작업했다. 비용: 현재 checkout에서 변경을 볼 수 있다. 원본은 해시로 보존했다.
2. 원문 그림의 정적 style 때문에 1005·1012 조립이 실패해 source에 한해 교과서 렌더러가 만든 정확한 표시 선언만 허용했다. 저작 style 금지·위험 마크업 거부는 유지한다. 비용: 허용 범위가 넓어지면 원치 않는 표시를 받을 수 있으므로 정확한 선언·수치 width와 회귀 검사로 제한했다.
3. 이식 기록의 기존 파일 해시는 유지하고 삽입을 제거하면 원 pinned bytes로 돌아가는 local_overrides를 추가했다. 비용: 잘못 기록하면 이식 증거가 깨지므로 bytes 복원 검사로 확인했다.
4. 원문 결함/조건부 해석은 결함 설명을 검증한 것으로 기록하며 literal 정상 실행 승인은 보류한다. 비용: 잘못 구분하면 원 코드의 실행 유효성을 과장할 수 있어 해설에 명시했다.
5. 과거 보존 예외는 보고서의 digest뿐 아니라 실제 백업 파일 bytes와 승인된 최신 납품을 검사한다. 과거 자료_복습팩/validation.json을 변경하지 않았다.

[발행·원본 보존·교체·RUN·백업 기록](2026-10-12-ds-review-pack-explain.json)에 절대 RUN과 backup 위치를 남겼다. 각 설명 소유 자료 폴더에 문항별 조각·검산·원자료 locator·화면 근거·현재 검토·manifest가 있다. 작업 폴더와 백업은 보존하며 Git 납품 범위에는 포함하지 않는다.

독립 최종 리뷰: gpt-6-astra가 64개 조각·현재 조건·다섯 Review Focus·보호 파일 256개·백업 bytes 14개·참조 해시·최종 HTML에 묶인 화면 검증 256건을 확인했다. 두 전체 테스트도 별도 프로세스로 다시 실행하여 통과했다. Critical/Important 없음, Declined to judge 없음.

기존 Minor 표시 문제는 사용자 요청에 따라 해결했다. 0914 p9, 1001 p1, 1012 p6·p12의 요약/재풀이 문자 이중 변환을 고쳤다. 본문 첫 여섯 설명 구역과 정답은 byte-identical이며 변경 조각은 정확히 이 네 개뿐이다. 3팩의 28문항 검산과 build/check를 다시 수행하고, 전체 문항을 네 화면 조합에서 재검토하여 발행했다. 수정된 표시를 브라우저 DOM 텍스트로 16개 조합에서 확인했고 대표 모바일 화면도 직접 확인했다. 발행 경로의 문항·자원·원 문제 링크를 네 조합에서 다시 확인했다.

새 회귀 검사 `test_summary_retry_render_code_characters_once`는 수정 전 실제 산출물에서 FAIL, 재발행 후 PASS를 확인했다. 전체 회귀 검사 156+72개, 하위 검사 137개가 통과했다. 보호 파일 256개의 해시도 다시 일치했다. 기존 백업과 이번 발행 전 백업을 함께 보존한다. 커밋·푸시는 하지 않았다.

수정 RUN: `tmp/ds-problem-explain/20261012-entity-fix/`. 현재 발행 JSON에 각 팩의 새 RUN·백업·수정 문항을 기록했고, 브라우저 JSON도 새 HTML 해시로 갱신했다. 초기 독립 리뷰 후 표시 수정은 별도 리뷰어를 다시 호출하지 않고 실패→통과 회귀 검사와 실제 화면 검사로 확인했다.

Git 발행 준비: 원문 복사 검토 파일 source-reading.txt의 원래 줄 끝 공백을 보존하기 위해 해당 경로만 .gitattributes의 whitespace 검사에서 제외했다. 원본·산출물의 hash는 변경하지 않았다.

커밋 직전 보존 확인: 최초 기준선 256개 중 Git 제외된 macOS 복습노트/.DS_Store 1개는 시스템 변경이 확인되었다. 학습 원본·제작자료·은행 255개는 모두 최초 SHA-256과 일치하며 .DS_Store는 커밋하지 않는다. 앞의 256개 일치 기록은 각 검증을 실행한 시점의 결과이다.
