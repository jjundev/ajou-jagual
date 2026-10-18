# 강의노트 기반 복습문제 standalone화 — 설계

## Intent
10개 복습팩(0907–1015)의 `source_kind: lecture-code` 문항 47개의 문제 본문·힌트·풀이·정답을 다시 써서, 카드 하나만 읽고 답을 도출할 수 있게 한다. "강의 p47", "강의의 person", "기존 insert_node" 같은 다른 문제·강의노트 참조를 제거하고, 참조가 대신하던 정의·코드·조건을 문제 안에 직접 적는다. 같은 규칙을 `check_html.py` lint와 스킬 문서에 넣어 이후 팩에서 재발을 막는다.

분류: bounded — 기존 `revise-existing` 개편 흐름(`.agents/skills/ds-review-pack/references/review-overhaul.md`) 안의 카드 내용 수정 + 검사기 규칙 추가.

## 확정 결정
| # | 결정 | 값 |
|---|---|---|
| 1 | 대상 | lecture-code 47개 전부 (0907 p4,p5,p6,p7 / 0914 p6,p7,p8 / 0917 p5,p6 / 0921 p5–p11 / 0928 p5–p9 / 1001 p1–p5 / 1005 p3–p11 / 1008 p2–p5 / 1012 p7,p8,p9 / 1015 p4–p8) |
| 2 | 경로 | revise-existing Stage: build_revision → check_html → review_audit(--baseline) → publish_update |
| 3 | 대체 방식 | 참조를 지우지 않고 그 내용(함수 계약·코드·규칙·값)을 본문에 넣는다 |
| 4 | 정리 범위 | 카드의 problem(배지 문단 제외)·hint·solution·answer |
| 5 | 번호·정답 | 유지. 단 카드 내용이 바뀌면 `stamp_revision`이 revision 해시를 바꿔 해당 팩의 풀이 완료 표시는 초기화된다(계약상 정상 동작) |
| 6 | 재발 방지 | `check_html.check_review`에 `lecture-standalone` lint + review-overhaul.md·card-rules.md 규칙 + 테스트 |
| 7 | 파생 산출물 | 바뀐 팩의 MD·문제설명·PDF 재생성 |
| 8 | 출처 메타데이터 | 배지 인용(`S4 p48 · 추가 근거 p28,47`)과 `details.original`("강의 예제 보기")은 출처로 유지, lint 대상 아님 |

## 확인된 위반 (본문)
| 팩 | 문항 | 위반 |
|---|---|---|
| 0907 | p4 | "강의 코드에서" |
| 0914 | p7 | "강의 규칙처럼" |
| 0921 | p5, p7, p10, p11 | "강의 그림의 행렬 A", "강의의 내림차순 계수 저장 규칙", "강의의 두 저장 방식", "S3 p8에서", "강의의 person" |
| 0928 | p7, p9 | "강의 개념을 확인하는", "강의의 struct" |
| 1001 | p3 | "강의 사용 예의" |
| 1005 | p7 | "강의의 head는" |
| 1008 | p2, p4, p5 | "강의 p47… p28의 remove_node"(코드 없음), "기존 insert_node", "강의 예처럼", 풀이의 "강의 원문의 결함" |
| 1012 | p9 | "강의 eval의 일부" |
| 1015 | p4, p5 | "강의 그림을 바탕으로", "강의 루프의 일부" |

나머지 문항도 "본문만 보고 풀 수 있는가" 검토를 거친다.

## 제외
- 기출·교과서 문항(A·C 섹션) — 원문 보존 계약.
- 정답·출제 의도 변경, 문항 추가·삭제.
