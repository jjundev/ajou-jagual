# 기존 리뷰팩 교과서 추가

`/ds-review-pack update-existing [MMDD|all]`은 복습문제 원고·MD·PDF와 제작자료를 갱신한다. PDF는 날짜 폴더 루트, 원고·MD·그림·제작자료는 그 폴더의 `.pack/`에 있다. 노트와 기존 카드는 보존하고, 최종 리뷰 전체 문항의 문제설명은 다시 만든다. 생성 전 형제 해설 스킬·실행기의 존재를 확인한다.

1. 날짜 오름차순으로 리뷰·카드(id/source/raw HTML)·노트 HTML/MD·기존 SVG·문제설명·양쪽 은행의 SHA256을 기록한다. `backup.py`로 새 RUN 백업을 만들고 제작자료/문제설명도 별도 백업한다.
2. STT와 실제 강의록에서 배운 범위·예고·보충을 분리한다. 양쪽 출처 검증 후 이전 날짜 교과서 원문을 used에서 제외한다. 후보·제외 이유·문항별 대체 대응과 근거를 selection.json에 적는다.
3. 기존 문제는 유지하고 교과서 원문 4~8개씩 추가한다. 4개를 기본으로 핵심 개념 보충 시 8개까지. 부족하면 가능한 것만 쓰고 이유를 unresolved로 보고한다. 변형·예고·미학습 개념으로 수를 채우지 않는다.
4. 각 교과서 정답과 풀이를 직접 작성·검산한다. 이전 형식의 복습문제는 보존한 카드에서 manifest를 재구성한다. 교과서 partD와 source_kind를 추가한다. `textbook_blocks.render_question`으로 원문을 만든다.
5. `release_review.py prepare --repo REPO --range MMDD --run PACK_RUN --mode update-existing`으로 작업 폴더를 준비한다. `update_review.extract_cards`와 `build_update(existing_html, cards, title=..., intro=..., footer=...)`로 작업용 HTML을 갱신한다. 기존 마지막 pN 다음부터 부여한다. partD 재실행은 source→pN을 그대로 유지하여 교체한다. 노트/셸 JS/진행 저장 키·기존 링크를 보존한다. `check_preserved(before, after)`는 비어야 한다.
6. manifest.py, bank.py check-manifest --textbook-dir --textbook-python, check_html.py를 실행한다. `html2md.py REVIEW.html --check` 단일 리뷰 변환으로 노트 MD와 기존 SVG를 보존한다. 기존 그림과 다른 내용이 같은 파일명으로 생기면 실패한다. 전체 HTML 재조립과 두 HTML 동시 변환은 쓰지 않는다.
7. 작업 폴더의 `.pack/자료_복습팩/`에 `manifest.json`, `selection.json`, `answers.py`, `validation.json`을 준비하고 [브라우저 검증](browser-check.md)의 요청을 발급한다. 검사자는 1280×900·375×812, light/dark에서 모든 신규 카드·선택지·소문항·원문/힌트/풀이·TOC·pager·기존 링크를 검사한다. 실패 시 `where`별로 고치고 기계 검사·변환 후 요청을 갱신한다. 2회 수정 뒤 미해결이면 해당 팩 발행을 보류하고 기존 팩을 보존한다.
8. 검증한 작업용 복습문제 HTML로 [PDF](pdf-build.md)를 만들어 같은 작업 폴더에 발행한다. `release_review.py publish --repo REPO --run PACK_RUN`으로 팩을 발행하고 최종 경로를 확인한다. 발행한 JSON 원고의 정확한 경로를 사용해 [후속 작업](pack-followups.md)의 `update-existing` 분기를 실행한다.
9. 날짜별 기존/추가/총합, 부족 이유, 제외 후보, 검산·브라우저 결과, 보존·백업 경로와 문제설명 발행/보류·HTML/MD·검토·RUN·백업 경로를 보고한다. 설명 실패 시 검증된 리뷰를 유지하고 “복습팩 생성됨 / 문제설명 보류”와 이유를 적는다. PDF 두 경로·페이지·PDF_RUN·검증·백업 및 withheld/stale/skipped 이유도 보고한다. PDF 실패는 다른 산출물을 삭제하지 않는다. 커밋·푸시는 제안만 한다.

## 강의 예제·전역 검토 연동

신규·update-existing·revise-existing은 [공통 개편·검증 계약](review-overhaul.md)을 함께 적용한다. lecture-code는 실제 강의 페이지·해시·학습 근거와 자체 질문을 구분한다. 전체 날짜 audit를 통과한 작업용 HTML로 PDF를 만들고, 발행한 JSON 원고에서 문제설명을 만든다. update-existing의 기존 카드 보존 계약은 유지한다.
