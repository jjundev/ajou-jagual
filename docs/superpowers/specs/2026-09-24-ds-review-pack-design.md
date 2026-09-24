# 자구알 복습팩 스킬 (`ds-review-pack`) 설계

- 날짜: 2026-09-24
- 벤치마크: `머신러닝기초/.claude/skills/ml-review-pack` (커밋 `80307b8`)
- 상태: 확정 (N1~N4 사용자 확인)

## 의도
머신러닝기초의 `ml-review-pack`을 벤치마킹해, 자구알(자료구조및알고리즘이해, 이정원 교수님) 수업 녹음 전사(`STT/`)와
`자료구조_강의록_2026/`으로 ELI5 정리노트 HTML과 복습문제 HTML(+MD)을 만드는 스킬을 자구알 저장소에 둔다.
복습문제는 교과서 대신 `from_the_past/기출`의 기출문제로 채운다. 템플릿은 ML 것을 복사해 쓴다.
완료 기준: `/ds-review-pack 0921` → `복습노트/0921/`에 정리노트·복습문제 html·md 4개와 `figures_0921/`이 생기고,
기출 문항은 이번 범위 챕터에 맞게 골라졌으며, 정답은 실행으로 확인된 상태다.

분류: architectural — 자구알 저장소에 고칠 기존 흐름이 없고, 기출 문제은행이라는 새 데이터 구조가 필요하다.

## 완료 시 동작
- `/ds-review-pack bank`: 기출 원본 11개(텍스트 PDF 5, 스캔 PDF 1, 사진 묶음 1, hwp 3, cp949 txt 1)를 전사해
  `from_the_past/기출/문제은행.json`, 원본별 전사 기록 `from_the_past/기출/_전사/<source-id>.md`,
  정답 검증 스크립트 `from_the_past/기출/_정답검증/<source-id>.py`를 만든다.
  보고서에 `answer_origin: unverified` 문항과 검수 대기(사진·스캔) 원본을 나열한다.
- `/ds-review-pack [MMDD|MMDD-MMDD] [lite]`: ML과 같은 9단계. 산출물 `복습노트/<range>/`.
  카드에 `기출 원문 보기`·힌트·풀이, C 코드는 코드 블록.
- 실패 동작: 은행 없음 → "먼저 `/ds-review-pack bank`" 후 멈춤 / 기출 부족 → N1 정책 후 보고 /
  모범답안과 시뮬레이션 불일치 → 실행값 채택, 보고.

## 이번에 안 하는 것
- ML과 엔진 공유(옵션 B) — ML 스킬을 건드리지 않는다.
- 과제·실습을 문제 출처로 — 요청 범위는 기출.
- 주교재(천인국 *Data Structure in C*) — 저장소에 없다.
- ML 템플릿 변경 자동 동기화 — 복사본으로 굳힌다. 출처 커밋은 `assets/SOURCE.md`.

## 접근: A (포크 + 1회 구축 은행 JSON)
| 옵션 | 접근 | 선택 |
|---|---|---|
| A | ML 스킬을 자구알로 포크, 기출은 1회 구축한 은행 JSON에서 선별 | ✔ |
| B | ML 스킬을 과목 독립 엔진으로 일반화 | — |
| C | 포크하되 매 실행 원본 기출 파싱 | — |

## 은행 스키마 (`from_the_past/기출/문제은행.json`)
```json
{"version": 1,
 "sources": [{"id": "2016-final-ljw", "file": "<from_the_past/기출 기준 상대 경로>", "year": 2016, "exam": "기말",
              "professor": "이정원", "has_key": false, "transcribed_from": "photo", "reviewed": false}],
 "problems": [{"id": "2016-final-ljw-q3", "source": "2016-final-ljw", "number": "3", "chapters": [6],
               "type": "trace", "points": 4, "text": "…마크다운, 코드는 펜스…", "figure": null,
               "answer": "front=4, rear=2", "answer_origin": "verified", "duplicate_of": null}]}
```
- `year`: int 또는 null. `exam`: 중간·기말·모의·미상. `transcribed_from`: text·scan·photo·hwp·txt.
- `reviewed`: text·hwp·txt는 true, scan·photo는 사용자 검수 전 false (N4).
- `chapters`: 강의록 `Software_<N>` 번호 1~12. `type`: ox·blank·trace·code-read·code-write·short·essay.
- `answer_origin`: key(모범답안)·verified(실행 확인)·unverified.
- `duplicate_of`: 다른 원본의 같은 문항(예: 2021 모의의 "[2015-1 기출]")이면 원 문항 id.

## 선별
- 후보: 원본 `reviewed`, `duplicate_of` 없음, `chapters ⊆ taught`, `chapters ∩ range_ch ≠ ∅`, 이전 팩 `data-source`에 없음.
- 정렬: 출제자(이정원 > 미상 > 타 교수, N3) → 유형(trace·code-read > blank·short·code-write > essay > ox) → 최근 연도.
- OX는 최대 2개. 목표 8~12문항. 원본이 8개 미만이면 숫자만 바꾼 변형(`partC`)으로 8개까지, 최소 4문항(N1).
- parts: `partA` 이정원 교수님 기출, `partB` 다른 기출, `partC` 변형.

## 결정
### 확정
| # | 결정 | 답 |
|---|---|---|
| 0 | 접근 | A |
| 1 | 기출 처리 | 1회 구축 은행 JSON + `bank` 모드 |
| 2 | 은행 위치 | `from_the_past/기출/문제은행.json` + `_전사/` + `_정답검증/` |
| 3 | 챕터 키 | 강의록 `Software_<N>` 번호 |
| 4 | 정답 검증 | Python 시뮬레이션·`cc` 실행, 모범답안과 다르면 실행값 채택·보고 |
| 5 | 수식 | KaTeX 유지(템플릿이 `pre`/`code` 무시) |
| 6 | MD 변환 | `html2md.py`에 `pre` → 펜스 추가 |
| 7 | 과목명 | `assemble.py` 하드코딩 → manifest `course` |
| 8 | 스킬 | `ds-review-pack`, `자구알/.claude/skills/` |
| 9 | 레이어 | `eli5`/`formal`/`prof` 유지, `formal` = 정의·코드·추적·복잡도 |
| N1 | 기출 부족 | 변형 허용(`partC`), 최소 4문항 |
| N2 | 템플릿 | `pre` CSS + 스와이프 제외 + 문구 1줄("교과서 원문" → "기출 원문") |
| N3 | 출제자 | 이정원 > 미상 > 타 교수 |
| N4 | 은행 검수 | 사진·스캔 전사는 사용자가 훑어보고 `reviewed: true`로 확정 |
