# 복습팩 마지막 단계에 확인문제 붙이기 — 설계

2026-11-13 대화(`/grill-yourself`)에서 확정한 설계를 옮긴 문서다. 확인문제 스킬 자체의 설계는 [2026-11-12-ds-concept-check-design.md](2026-11-12-ds-concept-check-design.md).

## 의도

`/ds-review-pack MMDD`(신규 팩)를 돌리면 8단계의 PDF 다음에 `ds-concept-check`가 같은 실행 안에서 돌아 `확인문제_<range>_<slug>.html`까지 나온다. 확인문제가 실패해도 복습팩·문제설명·PDF는 발행된 채로 남고, 보고에 "확인문제 보류"와 이유가 적힌다.

분류: bounded — 기존 두 흐름을 잇는다(`ds-review-pack` 8단계에 하위 절차 하나 + `assemble.py`의 근거 파일 복사).

## 근거 사실

- 복습팩 스킬에는 `stt-summary.md`를 팩에 저장하라는 지시가 없다. 9단계 저장 목록도 manifest·selection·answers·validation·traces뿐이다. 1015·1029·1102·1109·1112에만 이 파일이 있는 것은 손으로 복사했기 때문이다.
- `ds-concept-check/scripts/build.py:49`는 `.pack/자료_복습팩/manifest.json`·`stt-summary.md`가 없으면 "팩이 없어 근거가 없습니다"로 멈춘다.
- `assemble.py:116-121`이 이미 `RUN/traces/*.json`을 `.pack/자료_복습팩/traces/`로 복사한다(선례).
- `update-existing`·`revise-existing`은 `assemble.py`를 쓰지 않는다(`update_review.build_revision`·`publish_update`).
- 문제설명 연결(`references/problem-explain.md`)은 "형제 스킬 SKILL.md를 읽고 그 절차를 실제로 따른다" 방식이고, 누락이면 생성 시작 전에 멈추며, 실패는 "복습팩 생성됨 / 문제설명 보류"로 격리한다.

## 끝났을 때 동작

- 신규 모드 8단계 순서: MD 변환 → 문제설명 → PDF → **확인문제** → `pack_layout` 검사.
- 진행 표시 `8/9 확인문제 중: …` 한 줄.
- 9단계 보고에 확인문제 줄(발행/보류, 문항 수, 블라인드, 브라우저, 경로, 보류 이유).
- 확인문제 검사 실패 → 새 확인문제 HTML·SRC를 확인문제 RUN의 `withheld-<시각>/`로 옮기고 이전 확인문제(있으면)를 되돌린다. 보고 제목 "복습팩 생성됨 / 확인문제 보류".
- `ds-concept-check` 스킬 누락 → 신규 모드 생성 시작 전에 멈춘다.

## 이번에 하지 않는 것

- 기존 15개 팩 일괄 적용(10개는 `stt-summary.md` 없음 — 별도 backfill).
- 정리노트·복습문제에서 확인문제로 가는 링크.
- 확인문제와 문제설명 병렬 실행.

## 확정 결정

| # | 결정 | 값 |
|---|---|---|
| 1 | 위치 | 8단계 PDF 다음, `pack_layout` 검사 전 |
| 2 | 근거 저장 | `assemble.py`가 조립 때마다 `manifest.json`·`stt-summary.md`를 `.pack/자료_복습팩/`에 쓴다 |
| 3 | 여러 날짜 | `RUN/summaries/stt-*.md`를 파일 이름순으로 `\n\n---\n\n`으로 이어 한 파일 |
| 4 | 실패 격리 | 확인문제 보류, 복습팩·설명·PDF 유지 |
| 5 | 스킬 누락 | 신규 모드 생성 시작 전에 중단 |
| 6 | 호출 방식 | 메인 에이전트가 `ds-concept-check/SKILL.md` 1~8단계를 그대로 따른다 |
| 7 | 모드 | 신규(`MMDD`·`MMDD-MMDD`)만. `update-existing`·`revise-existing`·`bank`는 만들지도 건드리지도 않는다 [confirmed] |
| 8 | `lite` | 생략·모델 변경 없음(작성자·블라인드 풀이자 opus) [confirmed] |
