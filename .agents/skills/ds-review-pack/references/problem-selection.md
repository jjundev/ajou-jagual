# 문제 선별 규칙 (기출·교과서)

## 원칙
- 기출 문제은행·검증된 교과서 JSON·실제 강의 예제를 사용한다. 강의 예제 기반 자체 출제는 review-overhaul.md의 출처·검산 계약을 따른다.
- 같은 기출의 반복 수록과 원문까지 동일한 재수록만 날짜 전체에서 한 번으로 합친다. 서로 다른 기출 원문은 숫자·변수명·코드 구조·풀이 목표가 비슷해도 유지한다. 자체 제작한 숫자 변형으로 문제 수를 채우지 않는다.
- 수업에서 배운 내용만으로 풀 수 있어야 한다. `bank.py select`의 챕터 조건이 먼저 거르고, 메인 에이전트가 문항 글을 읽어 수업에서 안 다룬 개념(같은 챕터라도 슬라이드 대조표에서 "안 다룸"인 연산 등)이 한 단계라도 필요하면 뺀다. 뺀 문항과 이유는 보고서 "스킬이 정한 사항"에 적는다.
- 신규 팩은 총 보통 8~12문항(핵심 범위 충족 우선)이며 적합한 교과서 원문 최소 2개를 포함한다. 기존 리뷰 갱신은 기존 문항을 전부 유지하고 교과서 원문 4~8개를 추가하며 총 12개 상한은 적용하지 않는다. 기본 4개, 핵심 개념 누락을 채울 때 최대 8개.

## 후보 추출

신규 팩 1단계의 예비 추출에는 `CANDIDATE_REPORT=candidates-preview.json`, 2단계 확정 추출에는 `CANDIDATE_REPORT=candidates.json`을 명령과 같은 셸 호출에서 설정한다.

```bash
python3 "$SKILL/scripts/bank.py" select "$BANK" --range-ch <range_ch> --taught <taught> --used-dir "$REPO/복습노트" --this-range <range> --textbook-dir "$TEXTBOOK" --textbook-python "$TEXTBOOK_PYTHON" --out "$RUN/$CANDIDATE_REPORT"
```

이미 쓴 문항은 빠진다. `--this-range`는 같은 range를 다시 만들 때 그 팩이 쓴 문항을 후보로 남긴다. `OK`를 확인한 뒤 보고서의 `candidates`에서 현재 단계의 선별에 필요한 행만 가져온다. 행에는 id·출제자·유형·챕터·정답 출처가 있다. 이미 우선순위 순이다(출제자 이정원 > 미상 > 그 밖, 유형 trace·code-read > blank·short·code-write > essay > ox, 최근 연도, OX 최대 2개). 문항 원문은 선별에 필요한 ID의 은행 항목에서 찾는다.

## 순서
1. 기출 우선순위를 유지하되 교과서 최소 2개와 범위 개념 균형을 먼저 확보한 뒤 12개까지 고른다. 개념 균형과 권장 개수는 기존의 서로 다른 기출을 제외하는 이유가 될 수 없다. 기출 유지에 필요하면 권장 개수를 초과한다. 교과서·자체 출제 후보는 개념 균형을 고려한다.
   고른 문항의 은행 `text`에 manifest `forbidden_outside_preview` 단어가 있으면 빼고, 뺀 문항과 이유를 보고서 "스킬이 정한 사항"에 적는다.
2. 후보가 부족하면 실제 강의 예제 기반 자체 출제를 검토한다. `review-overhaul.md`의 lecture-code 출처 계약과 전역 검사로 검증한다. 핵심 범위 충족 우선이며 숫자만 바꿔 수를 채우지 않는다.
3. 같은 source와 원문 동일성이 확인된 duplicate_of는 전체 날짜에서 한 번만 수록한다. 서로 다른 기출을 유사한 풀이 때문에 duplicate_of로 묶거나 제외하지 않는다. 모든 소문항의 학습 근거와 coverage를 기록한다.

## parts
| id | title | short | 들어가는 문항 |
|---|---|---|---|
| `partA` | `A. 이정원 교수님 기출` | `A 이정원 기출` | 출제자 이정원, 원본 그대로 |
| `partB` | `B. 다른 기출` | `B 다른 기출` | 출제자 미상·그 밖, 원본 그대로 |
| `partD` | `D. 교과서 연습문제` | `D 교과서` | `textbook-chNN-qNN`, 교과서 원문 |
| `partC` | `C. 기출 변형` | `C 변형` | `variant: true` |

문항이 0개인 part는 뺀다.

## level
| level | 유형 |
|---|---|
| 1 | `ox`, `blank` |
| 2 | `trace`, `code-read`, `short` |
| 3 | `code-write`, `essay`, 또는 배점 10점 이상 |

## 문항 원문 모으기
카드 작성자가 볼 `<RUN>/problems.md`를 메인 에이전트가 만든다. 기출 문항마다(교과서는 아래 교과서 브리프 형식):
```
## <은행 문항 id>  (manifest id pN, variant true/false)
- 원본: <연도> <시험> <번호>번 · <배점>점 · <출제자> — <sources.file>
- 문제 글: <은행 text 그대로>
- 그림: <은행 figure 또는 "없음">
- 은행 정답: <answer> (<answer_origin>)
- 변형 값: <변형이면 바꾼 숫자, 아니면 "없음">
- 전사 기록: <from_the_past/기출/_전사/<source-id>.md 에서 그 번호 절 그대로>
```
- 은행 `text`와 전사 기록이 다르면 전사 기록을 따르고(`문제 글`에도 전사 기록을 쓴다) 보고서 "은행과 다른 문제 글"에 적는다. 은행 파일은 고치지 않는다.

## 정답
- 모든 정답을 `<RUN>/answers.py`에서 다시 계산한다. 자료구조 연산은 Python으로 그대로 시뮬레이션하고(리스트로 만든 스택·큐·힙, 딕셔너리로 만든 트리), C 코드를 읽는 문제는 `<RUN>/work/`에서 `cc -std=c11 -Wall -o <이름> <이름>.c`로 컴파일해 실행한다.
- 은행 `answer`와 다르면 실행값을 쓰고 보고서 "은행과 다른 답"에 적는다. 은행 파일은 고치지 않는다(다음 `bank` 실행 때 반영).
- 그림으로 답하는 문제(트리 그리기 등)는 결과를 순회 순서나 배열 표현 같은 글자로도 적어 manifest `terms`에 넣는다(예: 레벨 순서 `60 40 30 15 12 6 10 5`).

## 교과서 후보 검토
장 대응: 교과서 1→S1, 2→S2, 3→S3, 4→S5, 5→S6, 6·7→S4, 8→S7, 9→S8, 10·11→S10, 12→S9, 13→S12, 14→S11. 이것은 후보 검색용이며 학습 허용 범위를 뜻하지 않는다.
`textbook_candidates(..., concept_overrides={question_id: [강의록 번호]})`의 문항별 대체 대응은 실제 STT/강의록 근거를 selection.json에 기록한 경우만 쓴다. 예: 배열 삽입·삭제 ch03-q08~q11은 S4 배열 리스트 근거로 조회할 수 있다. 연결 리스트 장 전체를 배웠다고 처리하지 않는다.
verified 원문만 후보에 넣고 blocking/unreadable/figure-incomplete/external-context는 제외한다. 의미를 불확실하게 만드는 source-error도 제외하며 의미 없는 오타의 포함은 근거를 남긴다. 선행 문항을 참조하면 함께 싣거나 제외한다. 원문 재사용은 다른 날짜에서 제외하고 날짜 오름차순으로 고른다.
교과서 choice/단순 확인 level 1, trace/code-read/short level 2, 구현/essay level 3, mixed는 실제 요구의 최고 level을 사용한다.
원문 브리프에는 original_id, source_refs, JSON 경로·해시, 검증 payload, content/options 전체와 `scripts/textbook_blocks.py` 렌더링 결과를 준다. answer=null에서 직접 정답을 작성한다. Python 계산/추적, C11 실행, 개념의 강의 근거를 구분하고 검증 결과가 pass인 것만 저장한다.
