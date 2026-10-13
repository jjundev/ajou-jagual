# 문제설명 코드 블록 최종 검증

브랜치: `codex/ds-code-blocks`. 기준 커밋: `d631a5a573a32c9406b139e319bc9c7c2d328098`.

9팩·64문항의 코드/출력 103개 pre에 테마 배경·테두리·16px 패딩·고정폭 글꼴을 적용했다. HTML은 CSS 외 바이트가 동일하고 MD는 바이트 단위로 동일하다. 코드 문자·공백·탭·빈 줄, 인라인 코드, 보호 파일 536개와 과거 발행 보고서는 보존됐다. 스킬 저작 지침과 구조 검증을 함께 갱신했다.

## 별도 리뷰와 수정

새 문맥의 gpt-6-astra 리뷰어가 기준 커밋부터 `4f4f77f`까지 읽기 전용으로 검토했다. Critical 0, Important(P2) 1, Minor 0. P2는 저장된 검산/브라우저 코드가 이전 RUN에 의존하여 새 checkout에서 재실행하기 어렵고, 입력 0개인 독립 검증이 성공으로 끝나는 문제였다.

`rerun-ds-code-blocks.py`를 추가해 저장소 상대 경로의 현재 원문·fragments·발행 HTML 및 해시를 읽도록 수정했다. 입력이 없거나 문항이 빠지면 실패하며, 검산용 폴더는 별도 출력 디렉터리에만 재구성한다. 기존 승인 근거를 덮어쓰지 않는다. `test_replay_uses_published_inputs_without_original_run`, `test_saved_verification_rejects_zero_question_inputs`가 수정 전 실패, 수정 후 통과했다. 빈 팩 집합 거부도 검사했다.

기존 RUN을 실제로 삭제한 뒤 다음 명령으로 발행 파일만 사용해 독립 검산 64문항과 브라우저 256개 문항·화면·테마 조합을 다시 통과했다.

```sh
uv run --with playwright python docs/verify/rerun-ds-code-blocks.py --kind all --output /tmp/ds-code-blocks-replay
```

출력 디렉터리는 비어 있어야 한다. C 컴파일러와 Playwright Chromium이 필요하다. 재실행기는 원본 RUN 경로를 읽지 않는다. P2 수정은 별도 재리뷰 대신 위 실패→통과 검사와 전체 테스트로 검증했다.

## 최종 테스트

- `uv run --with pytest python -m pytest .agents/skills/ds-problem-explain/tests -q`: 78 passed.
- `uv run --with pytest python -m pytest .agents/skills/ds-review-pack/tests -q`: 159 passed, 4 skipped, 137 subtests passed.
- `uv run --with pytest --with pymupdf --with jsonschema --with pyyaml python -m pytest -q --ignore=tmp`: 60 passed, PyMuPDF SWIG deprecation warnings 5개.
- `git diff --check`: 통과. 관련 두 스킬을 한 pytest 프로세스에 넣으면 기존 동일 테스트 모듈명이 충돌하므로 별도 프로세스로 실행했다. 기본 저장소 테스트의 초기 의존성 누락은 uv 임시 의존성을 추가하여 해결했다.
- 브라우저: 1280×900 / 375×812, light/dark. 모든 문항·목차·이전/다음·요약·테마·자원·수식·코드 표시 검사. 오류·외부 요청·문서 가로 넘침 0.

## 실행 중 판단과 제약

1. 문서 문자열을 고정하는 테스트 대신 실제 구조/렌더링 검사와 스킬 지침 수동 검토를 사용했다. 테스트 지침이 문서 문구 변경 감지 검사를 금지하기 때문이다. 비용: 이후 지침의 문구 퇴행은 자동 문구 검사로 잡지 못한다.
2. CSS만 바뀐 원자료 검토는 본문/MD/코드의 정확한 동일성, 현재 화면, 독립 검산으로 수행했고 과거 페이지 대조 근거를 보존했다. 변경되지 않은 모든 PDF를 새로 읽지는 않았다. 비용: 기존 원자료 해석 오류가 있다면 남을 수 있다. 별도 리뷰어가 범위 밖으로 둔 전체 원자료 재판정도 같은 근거로 제외했다.
3. 과거 checkout 경로는 상대 위치와 원문 해시가 일치할 때만 현재 저장소에서 해석하고, 변경 파일의 실제 이전 바이트와 교체 연결을 설명 소유 evidence에 보존했다. 비용: 연결 검사에 결함이 있다면 누락된 이전 파일을 놓칠 수 있어 잘못된 해시·가짜/누락 백업·연속 이력 거부 테스트를 추가했다.
4. 기존 테스트 이름 충돌로 스킬별 테스트 프로세스를 분리했다. 비용: 한 프로세스에서의 모듈 import 상호작용은 검증하지 않았다. 저장소 의존성은 변경하지 않았다.

미해결 Critical/Important 및 보류 Minor는 없다. main에는 쓰지 않았으며 merge/push하지 않았다. 워크트리와 브랜치는 유지한다.
