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
2. `interaction.py` 부트 — `let storage = null; try { storage = window.sessionStorage; } catch {}` 를 `const storage = null;` 로 바꿨다. 새로고침하면 답안·진행이 초기화된다.
3. `review-interaction.css` 끝 — `생명과학/.agents/skills/bio-exam-forecast/scripts/exam_practice.py` 63행의 `.short-input` 규칙을 붙였다.
4. `interaction.py` `ANSWER_EVENT` — 원본의 `tabStore.set(KEY, Array.from(solved));` 줄을 지웠다. ds-review-pack 템플릿엔 `tabStore` 가 없어 답할 때마다 `ReferenceError` 가 났고, 템플릿의 `store`(localStorage)로 바꾸면 새로고침 뒤에도 진행이 남는다. 답한 문항은 메모리에만 기록한다.
5. `interaction.py` `drop_solved_persistence`(새로 추가, `patch_review_shell` 에서 호출) — 렌더된 페이지의 `setupReview` 에서 `store.get(KEY, [])` 를 `[]` 로, `store.set(KEY, Array.from(solved));` 를 주석으로 바꾼다. '푼 문제로 표시' 버튼은 메모리에서만 동작하고 새로고침하면 진행이 0이 된다. 테마(`od-theme`) 저장은 그대로다. 두 문자열이 정확히 한 번씩 없으면 `ValueError`. ds-review-pack 템플릿 파일은 손대지 않는다.

단답 대소문자 무시: `review-interaction.js` 의 `grade` 는 `window.ReviewShortCasefold` 지도가 없으면 글자마다 `toLowerCase()` 를 쓴다. 이 스킬의 답은 라틴 문자·숫자라 지도를 넣지 않는다.
