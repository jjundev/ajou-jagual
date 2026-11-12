---
name: ds-concept-check
description: 자구알 수업 하나에서 새로 배운 개념을 확인하는 즉시 채점 HTML(확인문제)을 기존 복습팩 근거로 만들 때 사용한다. /ds-concept-check <range>. 복습팩·문제설명·인터랙티브·채팅 퀴즈에는 사용하지 않는다.
---

# 자구알 확인문제

수업 하나가 끝난 뒤 그 수업에서 **처음 배운 개념**을 5~10분 안에 확인하는 오프라인 HTML 한 장을 만든다. 4지 객관식과 값 입력형을 섞고, 누르면 바로 채점하고 보기마다 설명을 보인다. 근거는 이미 있는 복습팩(STT 요약·manifest·정리노트 MD)이고, 복습팩은 다시 만들지 않는다. 중간에 묻지 않고 끝에 한 번 보고한다. 커밋은 제안만 한다.

- `ds-review-pack` 신규 모드가 8단계에서 이 절차(1~8단계)를 팩마다 부른다. 단독 실행(`/ds-concept-check <range>`)도 그대로 쓴다.
- 복습팩·기출 문제은행은 `ds-review-pack`, 기존 문제 해설은 `ds-problem-explain`, 코드·메모리 시뮬레이션은 `ds-interactive`다. 이 스킬은 그 파일들을 고치지 않는다.
- 하지 않는 것: 시험형(일괄 제출), 정리노트에서 들어오는 링크, 코드 작성형, 여러 팩 일괄 생성.

**인자**: `<range>` 하나 — `MMDD`(예 `/ds-concept-check 1102`) 또는 여러 날을 묶은 팩의 `MMDD-MMDD`. 폴더 `복습노트/<range>/`. `range`는 그 폴더 `manifest.json`의 `range`와 같다.

**산출물**
- 공개: `복습노트/<range>/확인문제_<range>_<slug>.html`. 팩 루트에는 이 `.html`만 더한다.
- 근거(`SRC`): `복습노트/<range>/.pack/자료_확인문제_<range>_<slug>/` — `objectives.json`, `items.json`, `blind-ledger.json`(블라인드 장부), `browser.json`.
- 화면: 복습문제와 같은 상단 바·좌우 패널, 한 화면 한 문항. 목표 근거(쪽 번호·개념 이름)는 화면에 찍지 않는다. 새로고침하면 답안·푼 문제 수가 초기화되고 테마는 남는다.

**경로 약속**
- 명령은 저장소 루트에서 실행한다(경로는 루트 기준 상대 경로). 셸이 다른 폴더에 있으면 같은 경로를 절대 경로로 바꿔 쓴다.
- `S` = `.agents/skills/ds-concept-check`
- `SRC` = `복습노트/<range>/.pack/자료_확인문제_<range>_<slug>`
- `RUN` = `<scratchpad>/ds-concept-check/<range>/` (저장소 밖. 블라인드 사본·답안표·작성자 초안·스크린샷·백업을 둔다)
- `python3` = homebrew `python3`(Playwright가 있다). 저장소 `.venv`에는 Playwright가 없다.

**에이전트**: 문항 작성자와 블라인드 풀이자는 각각 `general-purpose` 서브에이전트 1명, 모델 **opus**. fork가 아니라 새 에이전트로 띄운다(이 세션의 목표·정답을 물려받지 않게).

**진행 표시**: 단계마다 한 줄. 예: `3/9 문항 작성 중 (작성자 1명)`, `6/9 블라인드 r1 풀이 중`.

## 절차

### 1. 준비
- `복습노트/<range>/.pack/자료_복습팩/manifest.json`·`stt-summary.md`와 `.pack/정리노트_*.md`가 있는지 본다. 하나라도 없으면 “팩이 없어 근거가 없습니다”라고 보고하고 멈춘다(빌드·검사도 같은 말로 exit 1). 한글 폴더 이름은 macOS에서 NFD일 수 있으니 `ls`로 실제 이름을 확인한다.
- `range`·`slug`는 manifest에서 읽는다. `SRC`를 정한다.
- `mkdir -p RUN`. `SRC`나 공개 HTML이 이미 있으면 둘 다 `RUN/previous-<YYYYMMDD-HHMMSS>/`에 복사해 두고 새로 쓴다. 백업 경로는 보고에 적는다.

### 2. 확인 목표 (메인 에이전트)
- `stt-summary.md`(총평·절), manifest 토픽 순서, 정리노트 MD를 읽고 `SRC/objectives.json`을 쓴다. 모양·종류·제외 대상은 [item-rules.md](references/item-rules.md) 1~3절.
- 수업 흐름 순서로 6~16개가 보통이다(1102 ≈ 14). 6개 미만이면 만든 만큼 쓰고 보고에 사유를 적는다.

### 3. 문항 (작성자 1명, opus)
- 작성자에게 [item-rules.md](references/item-rules.md) 8절 “작성자 브리프”를 `<SRC>`·`<RUN>`·`<range>`·`<slug>`를 채워 넘기고, 이 파일 전체를 읽게 한다. 작성자가 읽는 것은 브리프에 적힌 것뿐이다.
- 오답 보기 오개념의 출처는 STT 절(`stt:`), 정리노트 토픽(`note:`), `from_the_past/기출/문제은행.json`의 같은 장 문항(`bank:`) 세 가지다.
- 작성자는 `RUN/items.json`만 쓴다. 메인 에이전트가 `SRC/items.json`으로 복사한다.

### 4. 규칙 검사
```
python3 .agents/skills/ds-concept-check/scripts/check.py SRC
```
- `OK`가 나와야 한다. 아니면 `[코드] <id>: <설명>` 줄을 모두 묶어 같은 작성자에게 되돌린다(SendMessage). 작성자가 고칠 때마다 `RUN/items.json`을 `SRC/items.json`으로 다시 복사한 뒤 check를 다시 돌린다. 이 RUN→SRC 복사는 4단계(작성자 수정)에서만 한다. 최대 2회. 그래도 남으면 메인 에이전트가 고치고 보고에 적는다.
- 코드 뜻은 item-rules.md의 `[코드]` 표시를 본다(`count`·`topic`·`source`·`format`·`mcq-shape`·`explain`·`title-leak`·`forbidden`·`compute`·`duplicate`·`style`·`balance`·`negative`·`steps`·`distance`).

### 5. 빌드
```
python3 .agents/skills/ds-concept-check/scripts/build.py SRC
```
- 출력 경로(`복습노트/<range>/확인문제_<range>_<slug>.html`)가 한 줄 찍힌다. 문항을 고칠 때마다 4→5를 다시 한다.

### 6. 블라인드 풀이 (풀이자 1명, opus)
```
python3 .agents/skills/ds-concept-check/scripts/blind.py make SRC RUN/blind-r1.md
```
- 사본은 학습자 화면과 같은 정보만 담는다. 트리는 그림처럼 `[그림: 트리 — 루트 A; A의 왼쪽 자식 B; …]`(칸 번호·빈 자리 목록 없음)로 적는다. 화면에 없는 목표 근거(쪽 번호·개념 이름)는 넣지 않는다.
- 장부 해시는 문항과 목표의 `concept`·`source.slide`를 함께 묶는다. 목표 이름이나 쪽을 바꾸면 그 목표의 문항이 `수정됨`이 된다.
- 풀이자에게 [blind-brief.md](references/blind-brief.md) 경로와 그 `---` 사이 브리프를 `<RUN>`·`<회차>`·`<range>`·`<slug>`를 채워 넘긴다. 풀이자가 읽는 것은 그 브리프, `RUN/blind-r<회차>.md`, `복습노트/<range>/.pack/정리노트_<range>_<slug>.md` 셋뿐이다. `SRC`, `items.json`, `objectives.json`, 이전 답안표 경로는 알려 주지 않는다.
- 풀이자는 `RUN/blind-answers-r<회차>.md`를 쓴다. 기록하고 상태를 본다:
```
python3 .agents/skills/ds-concept-check/scripts/blind.py record SRC RUN/blind-answers-r1.md SRC/blind-ledger.json --round 1
python3 .agents/skills/ds-concept-check/scripts/blind.py status SRC SRC/blind-ledger.json
```
- `status`가 `OK`면 끝. 아니면 줄마다 `장부에 없음`·`수정됨`·`답 불일치 (고른 답 ≠ 정답)`·`이의 — …`가 나온다. 단답은 쉼표·공백·화살표·대소문자 변형과 `accepted`를 정답으로 친다.
- 이의도 실패다(무시·기각하지 않는다). 답 불일치·이의가 나온 문항은 메인 에이전트가 `SRC/items.json`(목표 이름이면 `SRC/objectives.json`)에서 직접 고친다. 6단계부터는 **SRC가 원본**이다: 고친 뒤 `cp SRC/items.json RUN/items.json`으로 RUN을 맞추고, `check.py SRC`·`build.py SRC`만 다시 돌린다. 4단계의 RUN→SRC 복사는 하지 않는다(블라인드 수정을 옛 RUN 초안이 덮어쓴다). 그다음 고친 문항만 새 풀이자(새 에이전트)에게 다시 풀린다:
```
python3 .agents/skills/ds-concept-check/scripts/blind.py make SRC RUN/blind-r2.md --only q3,q7
python3 .agents/skills/ds-concept-check/scripts/blind.py record SRC RUN/blind-answers-r2.md SRC/blind-ledger.json --round 2
python3 .agents/skills/ds-concept-check/scripts/blind.py status SRC SRC/blind-ledger.json
```
- 문항을 고치면 장부의 그 문항 판정은 `수정됨`으로 무효가 된다. `--only`에는 `status`가 `장부에 없음`·`수정됨`으로 낸 문항을 모두 넣는다(답 불일치·이의로 고친 문항은 고친 뒤 `수정됨`이 된다). 재풀이는 최대 2회(r2·r3). r3 뒤에도 `status`에 남은 줄(답 불일치·이의 포함)은 모두 미해결로 보고한다.

### 7. 브라우저 검사
```
python3 .agents/skills/ds-concept-check/scripts/browser_check.py 복습노트/<range>/확인문제_<range>_<slug>.html --src SRC --out SRC/browser.json --shots RUN/shots
```
- 1280×900·375×812 × light·dark 4회. 객관식 오답→설명→`다시 풀기`→정답, 단답 변형 입력→`자동 일치`, 새로고침 뒤 초기화, 복기 버튼, 콘솔 오류·KaTeX 오류·가로 넘침을 본다. `browser: pass`여야 한다.
- 스크린샷(`RUN/shots/<폭>x<높이>-<테마>-<첫 문항>.png`, `…-last.png`) 8장을 Read로 직접 열어 겹침·잘림·트리 그림을 확인한다.
- HTML을 다시 빌드했으면 이 단계도 다시 한다(`browser.json`에 HTML 해시가 남는다).

### 8. 팩 배치 검사
```
python3 .agents/skills/ds-review-pack/scripts/pack_layout.py check --repo .
```
- `OK`여야 한다.

### 9. 보고
- 경로: 공개 HTML, `SRC`, 백업(있으면).
- 목표 수(6개 미만이면 사유), 문항 수(객관식 n · 입력 n), 객관식 정답 분포(A~D), 부정형 수.
- 블라인드 결과: 회차별 일치 수, 고친 문항과 이유, 남은 이의(미해결).
- 브라우저 결과: pass/fail, 스크린샷에서 본 것.
- 미해결.
- 커밋 제안: `git add 복습노트/<range> && git commit -m "docs(notes): add concept check <range>"`

## 테스트

```
python3 -m pytest .agents/skills/ds-concept-check/tests -q
```
테스트 도우미는 `tests/concept_util.py`, 가짜 팩은 `tests/fixtures/mini/`. 복사해 온 생명과학 상호작용 자산의 출처와 바꾼 곳은 `assets/SOURCE.md`.
