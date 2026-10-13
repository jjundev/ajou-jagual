# 테마 스크롤바 설계 (2026-10-13)

생명과학 bio-interactive `66939ad` 의 테마 스크롤바를 자구알 화면용 HTML 템플릿 3개와 이미 발행한 결과물 27개에 넣는다.

## 대상
- 템플릿: `.agents/skills/ds-review-pack/assets/note-template.html`, `.agents/skills/ds-review-pack/assets/review-template.html`, `.agents/skills/ds-problem-explain/assets/note-template.html`
- 결과물: `복습노트/*/{정리노트,복습문제,문제설명}_*.html` (9팩 × 3)
- 제외: `assignment-cover/assets/cover.html`, `ds-review-pack/assets/pdf/ec2/*.html`(인쇄용), `tests/fixtures/**`, `math-pan`(일부러 숨김)

## CSS
`.panel-inner { flex: 1 1 auto; … }` 줄 바로 아래에 한 덩어리로 넣는다. 토큰을 기존 테마 블록에 흩지 않는 이유: ds-problem-explain 템플릿은 `port-provenance.json` 의 `local_overrides[].inserted_text`(연속 삽입 한 덩어리)로만 원본 대비 변경을 허용한다(`tests/test_render.py:36-42`).

- 토큰: 라이트 `--scroll: #c9d0db; --scroll-hover: #9aa3b2;`, 다크 `--scroll: #3f414b; --scroll-hover: #5b5e6a;` — `:root`, `@media (prefers-color-scheme: dark) :root:not([data-theme="light"])`, `:root[data-theme="dark"]` 세 곳
- 세로: `.content`, `.panel-inner` 폭 8px
- 가로: `pre`, `.table-wrap`, `.katex-display` 높이 8px (ds-problem-explain 은 `table` 추가)
- 트랙 투명, 막대 둥근 8px, 막대 테두리 2px `var(--bg)`(단 `pre` 는 배경이 `--surface` 라 `var(--surface)`), hover `var(--scroll-hover)`
- Firefox: `@supports (scrollbar-color: auto)` 안에서 `scrollbar-width: thin; scrollbar-color: var(--scroll) transparent;`
- `--scrollbar: 16px`(패널 폭 계산)은 그대로 둔다.

## provenance
ds-problem-explain `assets/port-provenance.json` 의 `local_overrides` 에 `assets/note-template.html` 항목을 하나 추가한다(`base_sha256` = 현재 파일 해시, `current_sha256` = 삽입 후, `inserted_text` = 조각). `files[]` 는 바꾸지 않는다.

## 결과물과 해시 기록
- 이력 JSON(`docs/verify/*.json`, `.pack/**/{validation,manifest,selection,pdf-validation}.json` 등)은 바꾸지 않는다.
- 팩마다 `.pack/migration-2026-10-13-scrollbar.json` 에 `{date, reason, moved: [], rewritten: {<파일명>: {before, after}}}` 를 쓴다. `pack_layout.current_digest` 가 이 체인을 따라 옛 해시를 지금 해시로 바꾼다.
- `current_digest` 는 기록을 파일명 순서로 한 번만 훑는데 `migration-2026-10-13-scrollbar.json` 이 `migration-2026-10-13.json` 보다 먼저 정렬된다. 고정점까지 반복하도록 고친다.
- 해시를 직접 비교하는 검사 3곳을 `current_digest` 경유로 바꾼다: `tests/test_pdf_delivery.py:13`, `tests/explanation_delivery_checks.py:27`, `tests/test_textbook_delivery.py:26`.
- PDF 는 다시 만들지 않는다(스크롤바 CSS 는 인쇄에 영향 없음).

## 완료 기준
- 템플릿 3개·결과물 27개에 조각이 정확히 1번
- 결과물 diff 는 추가 줄뿐, 이력 JSON diff 없음
- 기준선(ds-review-pack 20 실패·브라우저 의존 / ds-problem-explain 79 통과) 대비 새 실패 없음
- 브라우저에서 `data-theme` 전환에 따라 `scrollbarColor` 가 바뀜
