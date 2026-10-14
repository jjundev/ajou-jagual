# ds-problem-explain 문제 패널 이식 + 기존 문제설명 9개 재발행

## Intent
생명과학 `bio-problem-explain`(원래 ds 에서 이식, d631a5a)은 96c6d63 → be26a42 사이에 HTML 형식이 바뀌었다. 문제·원문이 본문에서 빠져 별도 문제 패널([문제 | 원문] 탭)로 가고, 패널을 왼쪽·오른쪽에 붙이거나 띄운 창으로 쓸 수 있다(이동·크기 조절·터치). 넓어진 패널 줄이기, 문제 인쇄, SVG 확대가 함께 들어갔고, 템플릿만 바뀐 발행분을 다시 내는 `rerender` 명령이 생겼다. 이 형식을 `ds-problem-explain` 에 들이고 이미 발행한 `복습노트/{0907…1012}/문제설명_*.html` 9개를 `rerender` 로 다시 발행한다. 끝나면 9개 모두 생명과학과 같은 패널 UI 로 열리고, ds 테스트와 delivery 테스트에 새 실패가 없다.

분류: bounded — 템플릿·build·publish 흐름은 그대로이고 CLI 에 하위 명령 하나를 더한다.

## Behavior when done
- 목차로 문항을 고르면 문제 패널에 그 문항이 뜬다. 원문이 있는 문항만 "원문" 탭이 보인다.
- 패널은 왼쪽(기본)·오른쪽에 붙이거나 띄울 수 있고, 띄운 창은 끌어 옮기고 크기를 바꾼다. 터치 드래그도 된다. 위치는 브라우저에 기억된다.
- 375px 와 라이트·다크에서 지금의 코드 블록 스타일과 테마 스크롤바가 유지된다.
- `mpe_cli.py rerender --repo . --target 1012 --run …` 은 발행된 `fragments/`·`evidence/` 로 build 한다. content·independent 는 재사용하고 source_visual·browser 는 재검토하라고 안내한다. 입력이 바뀐 팩은 "입력 변경: 네 검토 모두 다시 필요" 로 알린다.
- 9개 팩 모두 실제 브라우저 재검토를 통과한 뒤에만 publish 된다.

## Not in this round
- 선택지 판정 카드 — ds 복습문제에 `review-interaction-model` 이 없다. 템플릿 코드는 따라오지만 빈 model 로 꺼진 상태. **[confirmed]**
- `.assets` 이전 로직 — ds 는 이미 `.pack/`.
- forecast 프로필·`context_hashes` — 생명과학 전용.
- 0914 delivery 기존 실패 6건(b5e8f98) — 원인이 다르다. **[confirmed]**

## Implementation spec
1. **템플릿**: `git merge-file` 로 3-way 병합한다. ours = 현재 ds 템플릿, base = 생명과학 96c6d63 의 bio 템플릿, theirs = be26a42 의 bio 템플릿. 충돌은 없다(확인함). 이어서 `bio-problem-explain-tab` → `ds-problem-explain-tab` 으로 바꾸고 `bio-review-pack` 출처 주석을 정리한다. provenance 는 기존 관례대로 `local_overrides` 에 `replacements` 항목 하나로 기록한다. 원래 설계는 bio 바이트로 재고정하는 안이었지만, `test_skill_files.py` 가 단일 `source_commit`(ML 1e2d5f8)을 단언하므로 override 체인으로 바꿨다.
2. **render**: 문제 블록에서 `<h4>주어진 조건</h4>` 를 빼고, 원문은 `<details class="original" data-original-problem><summary>기출 원문 보기</summary>` 로 감싼 뒤 둘을 `<div class="problem-pane" data-problem-for>` 에 넣는다. 원문 scope 는 `'original'`(정적 그림 style 허용). SUBTITLE 은 bio 문구를 쓰고, `explain-choice-model` 은 항상 `{}`.
3. **rerender**: bio `mpe_cli.py` 의 rerender·git_blob·published_source·same_problems·carried_references 를 이식한다. `.assets` 분기는 빼고, 자료 폴더는 `.pack/자료_…` 다.
4. **재발행**: 9개 모두 fragments 가 그대로이고, 기록된 source digest 로 계산한 payload_hash 가 일치하며 원본 blob 1be9339 가 git 에 있고, references 27개의 hash 가 모두 일치한다(확인함). 팩마다 rerender → check → 실제 브라우저 검토 → publish 한 뒤 `.pack/migration-2026-10-14-problem-panel.json` 을 쓴다.
5. **문서**: SKILL "레이아웃만 바뀐 기존 발행분 재발행" 절, verification 의 browser 항목, authoring 의 원문 문장.
6. **테스트**: bio 의 render·rerender·browser acceptance 를 ds 에 맞게 옮긴다. 선택지 판정 부분과 `test_choice_feedback_copied_from_review_pack` 은 제외한다.
