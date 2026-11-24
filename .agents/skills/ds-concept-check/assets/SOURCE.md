# 복사 출처

복사 날짜: 2026-11-12. 원본 저장소 `생명과학` 커밋 `bae20be8`(작업 트리 변경 없음).

| 이 스킬 파일 | 원본 |
|---|---|
| `scripts/interaction.py` | `생명과학/.claude/skills/bio-review-pack/scripts/review_interaction.py` |
| `assets/review-interaction.js` | `생명과학/.claude/skills/bio-review-pack/assets/review-interaction.js` (그대로) |
| `assets/review-interaction.css` | `생명과학/.claude/skills/bio-review-pack/assets/review-interaction.css` + 끝에 한 줄 |
| `assets/review-prompt.js` | `생명과학/.claude/skills/bio-review-pack/assets/review-prompt.js` (그대로) |

## 바꾼 곳

1. `interaction.py` import·경로 — `html2md` 는 `_paths.DS_REVIEW_PACK/scripts` 를 `sys.path` 에 넣은 뒤 가져오고, `SKILL` 은 `_paths.SKILL`(이 스킬 폴더)이다. `load_overrides()` 는 `{}` 를 돌려준다.
2. `review-interaction.js`의 `historyStore`는 방문별 브라우저 이력에 답안과 진행을 기록한다. 이력으로 돌아오면 복원하고 새로고침은 빈 상태에서 시작한다.
3. `review-interaction.css` 끝 — `생명과학/.agents/skills/bio-exam-forecast/scripts/exam_practice.py` 63행의 `.short-input` 규칙을 붙였다.
4. `review-interaction.js`는 객관식과 단답형에 같은 기록 형식을 사용한다. 복원 시 마지막 문항을 제출한 기록이 있으면 복기 열기 버튼을 표시한다.
5. `interaction.py`의 `patch_solved_history`는 푼 문제 표시를 답안과 동일한 브라우저 이력에 연결한다.

6. `interaction.py` `main()`·`argparse` — 지웠다. 원본 CLI(`--root … --write`)는 `*/복습문제_*.html`을 덮어써서 ds-review-pack 산출물을 고칠 수 있다. 이 스킬은 `install`·`build_model`만 import 해 쓴다.

7. `review-interaction.css` 끝 — `.note-link` 규칙을 붙였다. `render.py` 가 풀이 끝에 넣는 정리노트 토픽 링크의 간격이다.

8. `review-interaction.css` 2~3행 사이 — `.review-ready .problem > .choices { margin-top:var(--s6); }` 를 넣었다. 문제 문장과 첫 보기 카드 사이를 카드끼리 간격(`--s3`)보다 넓힌다. 문제 `<p>` 아래 마진과 `ol` 위 마진은 겹치므로 기본 1em 보다 큰 토큰이어야 보인다.

9. `review-interaction.css` 8번 규칙 아래 — 보기 카드 앞에 `(A)` `(B)` … 를 CSS 카운터(`counter(opt, upper-alpha)`)로 붙였다. 확인문제 보기 식별자는 언제나 A~D 순서라 목록 순번과 같다. 카드 글자·`data-choice`·정답·해설은 건드리지 않는다.

단답 대소문자 무시: `review-interaction.js` 의 `grade` 는 `window.ReviewShortCasefold` 지도가 없으면 글자마다 `toLowerCase()` 를 쓴다. 이 스킬의 답은 라틴 문자·숫자라 지도를 넣지 않는다.
