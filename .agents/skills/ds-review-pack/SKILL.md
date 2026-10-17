---
name: ds-review-pack
description: 자구알(자료구조및알고리즘이해) 수업의 복습팩(정리노트·복습문제·문제설명)이나 기출 문제은행을 만들 때 사용한다. /ds-review-pack [bank | MMDD | MMDD-MMDD | update-existing MMDD/all | revise-existing MMDD/all] [lite]
---

# 자구알 복습팩

수업 녹음 전사(STT)와 강의록(`자료구조_강의록_2026/`), 기출 문제은행과 검증된 교과서 연습문제로 한 기간의 복습팩을 만든다. 문제은행은 `bank` 모드로 먼저 한 번 만들어 둔다. 중간에 사용자에게 묻지 않고(`bank` 모드의 hwp 외부 변환 허락만 B2 전에 한 번 묻는다) 끝에 한 번 보고한다. 커밋은 제안만 한다.

**공통 품질 기준**: 신규·두 갱신 모드는 [전체 문항 검토 지침](references/review-overhaul.md)의 강의 출처·coverage·전역 중복 검사를 적용한다. 핵심 범위 충족 우선이며 숫자 변형으로 문항 수를 채우지 않는다. 기존의 서로 다른 기출은 풀이 목표·개념·코드 구조가 비슷해도 전부 유지한다. 같은 기출의 반복 수록만 제거한다.

**모드**
- `revise-existing [MMDD|all] [lite]`: 기존 전체 문항을 검토·교체하고 문제설명·PDF까지 갱신한다. `references/review-overhaul.md`를 따른다.
- `bank`: 기출 원본을 전사해 문제은행을 만들거나 다시 만든다. 절차는 "문제은행 모드" B1~B4.
- `update-existing [MMDD|all]`: 기존 리뷰를 갱신하고 전체 문항의 문제설명도 다시 만든다. `references/textbook-update.md`를 따른다. 기존 카드와 노트는 보존하고 교과서 원문 4~8개를 추가한다.
- 그 밖(`[MMDD | MMDD-MMDD] [lite]`): 복습팩을 만든다. 절차는 "복습팩 절차" 0~9.

**산출물** (복습팩, `복습노트/<range>/`, 수업 날짜마다 폴더 하나):
- 루트: `정리노트_<range>_<slug>.html`, `복습문제_<range>_<slug>.html`, `문제설명_<range>_<slug>.html`, `복습문제_<range>_<slug>-문제.pdf`·`-답안.pdf`. 루트에는 HTML·PDF와 `.pack/`만 둔다.
- `.pack/`(숨김 폴더): 같은 이름의 `.md` 세 개, `figures_<range>/`, 설명 소유 그림·자료 폴더(`figures_문제설명_*`, `자료_문제설명_*`), `자료_복습팩/`, `자료_PDF/pdf-validation.json`. 검색 도구가 숨김 폴더를 건너뛸 수 있으니 `복습노트/<range>/.pack/<이름>` 경로를 직접 연다.

**인자**: `[bank | MMDD | MMDD-MMDD | update-existing MMDD/all | revise-existing MMDD/all] [lite]`
- `lite`: 작성자·요약·전사 에이전트를 가벼운 모델로, 6단계 리뷰를 생략한다. 기계 검사와 브라우저 검사는 그대로 한다. 문제설명 저작·독립 검산·실자료 검토·브라우저 검증은 생략하지 않는다.

**에이전트 모델** (작성자·요약·전사 공통, 모델은 여기서만 정한다):
| 실행 환경 | 기본 | `lite` |
|---|---|---|
| Claude | opus | sonnet |
| GPT 등 Claude 아님 | sol | luna |

**해설 연결**: bank 이외의 모드는 생성 시작 전에 형제 `ds-problem-explain/SKILL.md`와 실행기 존재를 확인한다. 정확한 최종 복습문제 HTML 경로로 [공통 문제설명 절차](references/problem-explain.md)를 실행한다.

**진행 표시**: 단계마다 한 줄만 쓴다. 예: `3/9 작성 중: 섹션 4개 + 카드 9개 (병렬)`, `B3 전사 중: 원본 11개 (병렬)`

**경로 약속**
- `SKILL` = 이 파일이 있는 폴더(`.agents/skills/ds-review-pack`)의 절대 경로
- `REPO` = 저장소 루트
- `TEXTBOOK` = NFC/NFD 실제 경로로 찾은 `REPO/교과서/`; `TEXTBOOK_PYTHON` = PyMuPDF·jsonschema가 설치된 Python 실행 파일(기본 sys.executable).
- `BANK` = `REPO/from_the_past/기출/문제은행.json`
- `RUN` = 복습팩은 `<scratchpad>/ds-review-pack/<range>/`, 문제은행은 `<scratchpad>/ds-bank/<YYYYMMDD-HHMMSS>/`
- 셸 상태는 Bash 호출 사이에 이어지지 않는다. 아래 명령의 `$SKILL`, `$RUN`, `$REPO`, `$BANK`는 실행할 때마다 실제 절대 경로로 바꿔 쓰거나, 같은 명령 앞에 `SKILL=… RUN=… REPO=… BANK=…`를 붙여 설정한다. `cd`는 쓰지 않고 파일도 절대 경로로 넘긴다.

## 문제은행 모드 (`bank`)

### B1. 준비
1. `REPO/from_the_past/기출/`이 있는지 확인한다. 없으면 "자구알 저장소에서만 동작합니다"라고 알리고 멈춘다.
2. 실행 폴더를 만든다: `mkdir -p "$RUN"/{parts,work} && ln -sfn "$REPO" "$RUN/repo"`
3. `BANK`가 이미 있으면 `RUN/previous-bank.json`으로 복사한다(`reviewed` 값을 이어받는 데 쓴다). 이전 은행에서 `reviewed: true`인 `scan`·`photo` 원본은 B2·B3을 건너뛰고, 그 원본의 `sources`·`problems` 항목과 `REPO/from_the_past/기출/_전사/<id>.md`를 그대로 가져온다(사용자 검수와 수정을 지킨다). 다시 전사하려면 사용자가 먼저 그 원본의 `reviewed`를 `false`로 바꾼다.
4. 원본 목록과 id는 `references/bank-build.md`의 원본 표를 따른다. 표에 없는 파일이 `from_the_past/기출/` 아래에 있으면(숨김 파일(`.DS_Store` 등)과 은행 산출물 `문제은행.json`, `_전사/`, `_정답검증/`은 빼고) 보고서 "새 원본"에 적고 이번에는 넣지 않는다.

### B2. 정규화
`references/bank-build.md`의 "정규화"대로 원본(B1에서 그대로 가져온 원본은 빼고)을 `RUN/work/`에 읽을 수 있는 형태로 만든다(cp949 → UTF-8, hwp → PDF, PDF → 텍스트·쪽 이미지).

### B3. 전사 (병렬)
B1에서 그대로 가져오지 않은 원본마다 전사 에이전트 1명을 **한 메시지에서 병렬로** 띄운다(모델은 "에이전트 모델" 표). 브리프는 `references/bank-build.md`의 "전사 브리프"이며 `<source-id>`, `<원본 경로들>`, `<RUN>`, `<SKILL>`을 채워 넘긴다. 각자 `RUN/parts/<source-id>.json`과 `RUN/parts/<source-id>.md`를 쓴다.

### B4. 합치기·검증·저장
1. 조각을 합쳐 `RUN/bank.json`(`{"version": 1, "sources": [...], "problems": [...]}`)을 만든다. `sources`는 원본 표 값에 조각의 `has_key`와 `reviewed` 규칙(`references/bank-build.md`)을 더한다. B1에서 가져온 원본의 `sources`·`problems` 항목은 바꾸지 않고 그대로 넣는다(2~4단계도 새로 전사한 원본에만 한다).
2. 챕터 태그를 `references/bank-build.md`의 챕터 표로 다시 본다.
3. 중복 문항(`duplicate_of`)을 `references/bank-build.md`의 "중복 문항"대로 채운다.
4. 정답을 `references/bank-build.md`의 "정답 검증"대로 확인해 `answer`, `answer_origin`을 정한다.
5. `python3 "$SKILL/scripts/bank.py" validate "$RUN/bank.json"` 결과가 `OK`여야 한다. 아니면 고치고 다시 검사한다.
6. 저장소에 쓴다(메인 에이전트만): `RUN/bank.json` → `BANK`, `RUN/parts/<id>.md` → `REPO/from_the_past/기출/_전사/<id>.md`(B1에서 가져온 원본의 `_전사/<id>.md`는 덮어쓰지 않는다), `RUN/work/verify_<id>.py` → `REPO/from_the_past/기출/_정답검증/<id>.py`(새로 전사한 원본만. B1에서 가져온 원본은 `verify_<id>.py`가 없고 저장소의 파일을 그대로 둔다).
7. 보고한다:
```
## 문제은행 완료
- 파일: from_the_past/기출/문제은행.json (원본 N개, 문항 M개), _전사/ N개, _정답검증/ N개
- 챕터별 문항 수: 1장 a · 2장 b · …
- 검수 대기(reviewed: false): 2015-ljw(스캔), 2016-final-ljw(사진) — _전사/<id>.md를 원본과 대조해 틀린 곳을 고치고, 문제은행.json의 그 원본 문항(`text`, `answer`(답을 바꾸면 `answer_origin`을 `unverified`로), `chapters`)도 똑같이 고친 뒤 그 원본 reviewed를 true로 바꿔 주세요
- unverified 문항: … (없으면 "없음")
- 모범답안과 다른 답: … (실행값 채택, 없으면 "없음")
- 에이전트 답과 다른 답: … (실행값 채택, 없으면 "없음")
- 빠진 원본·새 원본: … (없으면 "없음")
- 커밋 제안: git add from_the_past/기출/문제은행.json from_the_past/기출/_전사 from_the_past/기출/_정답검증 && git commit -m "data(bank): build past-exam bank"
```

## 복습팩 절차

### 0. 준비
1. `REPO`에 `STT/`, `자료구조_강의록_2026/`이 모두 있는지 확인한다. 없으면 "자구알 저장소에서만 동작합니다"라고 알리고 멈춘다.
2. `BANK`가 없으면 "먼저 `/ds-review-pack bank`로 문제은행을 만들어 주세요"라고 알리고 멈춘다. 있으면 `python3 "$SKILL/scripts/bank.py" validate "$BANK"`가 `OK`여야 한다. 아니면 오류를 보여 주고 멈춘다.
교과서도 `scripts/textbook.py`의 `load_textbook(Path(TEXTBOOK), python=TEXTBOOK_PYTHON)`로 검증한다. 다른 bank.py를 현재 프로세스에 import하지 않는다. 폴더·의존성 누락, 원본/자산/payload 검증 실패는 오류로 중단하며 기출 전용으로 대체하지 않는다. 정답 null은 아직 정답을 작성하지 않았다는 뜻이며 review.status=verified와 혼동하지 않는다.
3. STT 목록은 NFC로 읽는다. macOS에는 NFD 파일명이 섞여 있다.
   ```bash
   python3 -c "import os,unicodedata as u,re;n=[u.normalize('NFC',f) for f in os.listdir('$REPO/STT')];print(sorted(m.group(1) for f in n if f.endswith(' 자구알.md') and (m:=re.match(r'(\d{4})',f))))"
   ```
4. 기간을 정한다.
   - 인자가 있으면 그 기간을 쓴다.
   - 인자가 없으면 `복습노트/*/정리노트_<range>_*.html` 중 가장 늦은 끝 날짜를 찾고, 그 뒤의 STT를 모두 쓴다. `정리노트_*`가 하나도 없으면 STT 전부를 쓴다.
   - 해당 STT가 하나도 없으면 사용 가능한 날짜를 보여 주고 멈춘다.
   - `range`는 첫 STT 날짜 하나이거나 `첫-끝` 형식이다.
5. 실행 폴더를 만든다. 서브에이전트에게는 `RUN`, `RUN/repo`, `SKILL` 경로만 넘긴다.
   ```bash
   mkdir -p "$RUN"/{summaries,sections,cards,work} && ln -sfn "$REPO" "$RUN/repo"
   ```
   에이전트는 `RUN` 밖에 쓰지 않는다. 임시·보조 파일(그림 생성 스크립트, 초안, 복사본)은 `RUN/work/`에만 둔다. 저장소(`STT/`, `자료구조_강의록_2026/`, `from_the_past/`)에는 아무도 쓰지 않고, `복습노트/`에는 메인 에이전트만 쓴다.

### 1. 범위 파악
1. **먼저** 관련 강의록 텍스트를 쪽 번호와 함께 `RUN/slides.txt`에 추출한다. 요약 에이전트는 이 파일이 있다고 보고 시작하므로 추출이 끝난 뒤에 띄운다.
   - 관련 챕터: 이전 팩 정리노트(`복습노트/*/정리노트_*.html`)의 `<span class="tag slide">S<N> p<k>` 중 가장 큰 챕터(그 챕터 마지막 쪽까지 다뤘으면 그다음 챕터)부터 두 챕터. 이전 팩이 없으면 1~3장. 확실하지 않으면 넉넉히 넣는다.
   ```bash
   python3 "$SKILL/scripts/extract_slides.py" --repo "$REPO" --run "$RUN" --ch <관련 챕터 번호, 공백 구분>
   ```
   - 추출에 실패하면 STT만으로 진행하고 보고서에 적는다(브리프의 `slides.txt` 줄은 "없음"으로 바꿔 넘긴다).
2. 그다음 STT 날짜마다 요약 에이전트 1명을 **병렬로** 띄운다. 브리프는 `references/stt-summary-prompt.md`에 있다.
   - `<Software_N_*.pdf>`: 그 날짜가 다룬 쪽이 들어 있는 강의록(확실하지 않으면 관련 챕터의 강의록을 모두 적는다).
   - `<MMDD 자구알.md>`: NFC 목록에서 찾은 실제 파일명. `<YYYY-MM-DD>`: 연도는 이번 학기 연도(오늘 날짜 기준), 월·일은 `<MMDD>`.
3. 에이전트가 도는 동안 메인 에이전트는 관련 챕터로 후보 문항을 미리 본다(`references/problem-selection.md`의 `select` 명령, `--range-ch`와 `--taught`는 관련 챕터로 임시로).

### 2. manifest
- 요약들의 슬라이드 대조표로 `range_ch`(이번 범위에서 "다룸/일부"인 쪽이 있는 챕터)와 `taught`(1장부터 이번 범위의 마지막 챕터까지)를 정한다.
- 문제 선별은 `references/problem-selection.md`를 따른다.
  - 정답은 `RUN/answers.py`로 다시 계산한다.
  - 카드 작성자용 문항 원문은 `RUN/problems.md`에 모은다(형식은 `references/problem-selection.md`).
- 신규 팩은 핵심 범위 충족 우선으로 보통 8~12문항을 목표로 하며 적합한 교과서도 포함한다. 기존 추가 모드는 별도 4~8개 정책이다. 교과서 후보 장 대응은 검색용이며 보기·소문항 전체가 배운 범위여야 한다.
- `scripts/textbook_blocks.py`로 교과서 원문 content/options를 순서대로 렌더링한다. 원문은 숫자·코드·그림·오타를 보존하고 observations/printed_answer를 답으로 쓰지 않는다. 직접 풀이를 Python/C 실행 또는 강의 근거로 검산한다.
- manifest는 `references/manifest-guide.md`대로 `RUN/manifest.json`에 쓴다.
- 검증: 둘 다 `OK`여야 한다.
  ```bash
  python3 "$SKILL/scripts/manifest.py" "$RUN/manifest.json"
  python3 "$SKILL/scripts/bank.py" check-manifest "$BANK" "$RUN/manifest.json" --repo "$REPO" --textbook-dir "$TEXTBOOK" --textbook-python "$TEXTBOOK_PYTHON"
  ```

### 3. 작성
- 섹션마다 작성자 1명을 띄운다. 브리프는 `references/content-rules.md`, 위젯 규칙은 `references/widget-rules.md`에 있다.
- 문제 작성자 1명이 모든 카드를 쓴다. 브리프는 `references/card-rules.md`에 있다.
- 모두 **한 메시지에서 병렬로** 띄운다. 모델은 "에이전트 모델" 표를 따른다.
- 브리프의 `<…>` 자리는 실제 경로, id, 금지어 목록(`<forbidden 목록>`), 예고 토픽 id(`<preview_topic>`), 그리고 섹션 작성자에게는 manifest `links` 중 그 섹션 토픽에 속한 것만(`<이 섹션의 links 목록>`) 채워 넣는다.
- 위젯은 팩 전체에 0~2개다. 병렬 작성자끼리는 서로를 모르므로 **메인 에이전트가 띄우기 전에** 위젯을 둘 토픽(0~2개)을 정하고, 그 토픽의 섹션 작성자 브리프에만 `<위젯>` 자리에 "토픽 `<토픽 id>`에 위젯 1개: <무엇을 누르거나 움직이면 무엇이 보이는지>"를 적는다. 나머지 작성자의 `<위젯>` 자리에는 "위젯 없음"이라고 적는다. 정한 토픽과 이유는 보고서 "스킬이 정한 사항"에 적는다.

### 4. 조립
- **처음 조립할 때만**: `복습노트/<range>/`(또는 예전 형식인 `복습노트/` 바로 아래)에 이번 `range`의 산출물(루트의 `정리노트_<range>_*`·`복습문제_<range>_*`, `.pack/`의 같은 이름 `.md`와 `figures_<range>/`)이 하나라도 있으면 먼저 백업한다. 다시 조립할 때(5~8단계에서 돌아온 경우)는 백업하지 않는다. 이미 스킬이 만든 초안이 백업에 섞이기 때문이다.
  - 백업은 매번 새 폴더 `RUN/previous-<시각>-<임의>/`에 만든다. 종료 코드가 1이면 조립하지 말고 원인을 고친다. 백업 경로는 보고서에 적는다.
```bash
python3 "$SKILL/scripts/backup.py" --range <range> --repo "$REPO" --run "$RUN"
```
```bash
python3 "$SKILL/scripts/assemble.py" --run "$RUN" --out "$REPO/복습노트/<range>"
```

### 5. 기계 검사
```bash
python3 "$SKILL/scripts/check_html.py" --manifest "$RUN/manifest.json" --note "$REPO/복습노트/<range>/<정리노트>.html" --review "$REPO/복습노트/<range>/<복습문제>.html"
```
- `FAIL`이면 Problem의 `where`(토픽 id, 카드 id, 섹션 id)로 담당 작성자를 찾는다.
- 그 작성자에게 문제 목록을 보내 조각을 고치게 한다(SendMessage, 안 되면 같은 브리프로 새 에이전트).
- 고친 뒤 4단계부터 다시 한다. 최대 2회까지이며, 그래도 남으면 "미해결"로 보고한다.

### 6. 리뷰 (`lite`면 생략)
- 리뷰어 1명을 띄운다. 브리프는 `references/review-prompt.md`에 있다.
- Critical과 Important는 모두, Minor는 쉬운 것만 고친다.
- 담당 작성자별로 **한 번에 모아서** 수정을 요청한다. 수정은 한 번만 한다.
- 수정 후 4~5단계를 다시 한다. 반영하지 않은 항목은 보고서에 적는다.

### 7. 브라우저 검증
- `references/browser-check.md`대로 한다.
  - http.server를 빈 포트에 띄운다.
  - 확인: KaTeX 오류 0, 남은 `$` 없음, 375px에서 가로 스크롤 없음(코드 블록은 자체 스크롤), 다크모드, 위젯, 링크, 콘솔 오류
- 결함은 5단계와 같은 방식으로 작성자에게 되돌린다. 이것도 최대 2회 규칙에 포함된다.
- 끝나면 서버를 종료한다.

### 8. MD 변환과 문제설명·PDF
```bash
python3 "$SKILL/scripts/html2md.py" "$REPO/복습노트/<range>/<정리노트>.html" "$REPO/복습노트/<range>/<복습문제>.html" --check
```
- `OK`가 나와야 한다. `.md`와 `figures_<range>/`는 `복습노트/<range>/.pack/`에 생긴다.
- 누락이 나오면 대부분 HTML 조각의 마크업 문제다(수식이 `svg`나 `.controls` 안에 있는 경우 등). 조각을 고치고 4단계부터 다시 한다.

- MD 변환·기계·내용·브라우저 검증이 끝난 최종 복습문제 HTML의 절대 경로로 `references/problem-explain.md`를 실행한다. 미해결 검사가 있으면 설명 발행을 보류한다. 날짜·최신 팩으로 대상을 추측하지 않는다.

- 신규·`lite`·`update-existing` 모두 같은 최종 HTML 절대 경로로 [PDF 생성 절차](references/pdf-build.md)를 실행한다. PDF와 문제설명은 각각 검증·발행하며 한쪽 실패가 다른 쪽의 발행이나 이전 자료를 삭제하지 않는다. `lite`도 PDF 기계·전체 페이지 검토를 생략하지 않는다.

- 마지막으로 폴더 배치를 검사한다. `OK`가 아니면 루트에 남은 항목을 `.pack/`으로 옮기고 다시 검사한다. 옛 배치(루트에 md·그림·자료 폴더)인 팩은 `migrate`로 옮긴다(인자 없이는 계획만 출력, `--apply`로 실행).
```bash
python3 "$SKILL/scripts/pack_layout.py" check --repo "$REPO"
```

### 9. 보고
다음 형식으로 끝낸다.
```
## 복습팩 <range> 완료 (설명 보류 시: 복습팩 생성됨 / 문제설명 보류)
- 파일: 복습노트/<range>/… (루트 html 3·pdf 2, .pack/ 에 md 3, figures_<range>/ N개; 설명 소유 그림·자료 포함)
- 범위: 배운 쪽 S2 p1–20 … / 예고만: …
- 문제: P1 2016-final-ljw-q3 (2016 기말 3번, 이정원, trace) … / 변형 K개 (정답은 RUN/answers.py로 검증)
- 은행과 다른 답: … (없으면 "없음")
- 은행과 다른 문제 글: … (없으면 "없음")
- 검수 대기로 뺀 원본: … (없으면 "없음")
- 스킬이 정한 사항: slug, 섹션 구성, 위젯, 뺀 내용과 이유, 뺀 후보 문항과 이유
- 문제설명: 발행/보류, 전체 문항 수, HTML·MD·EXPLAIN_RUN·백업 경로, 네 검토 결과와 보류 이유
- PDF: 문제/답안 발행·보류·stale·skipped, PDF 두 경로·페이지 수·PDF_RUN·검증·백업·이유
- 미해결: … (없으면 "없음")
- 커밋 제안: git add 복습노트/<range> && git commit -m "docs(notes): add ds review pack <range>"
```
교과서 추가 개수·출처·검산 방법·제외 이유도 보고한다. `복습노트/<range>/.pack/자료_복습팩/`에 manifest.json, selection.json, answers.py, validation.json을 저장한다.
실행 폴더 경로(`RUN`)도 적는다. 수정이 필요하면 조각을 고쳐 4단계부터 다시 돌리면 된다.

## 오류 처리
본문 단계에 적힌 경우(저장소·은행·STT 없음, PDF 추출 실패, 백업, 검사 2회 실패) 말고는 이 표를 따른다.
| 상황 | 동작 |
|---|---|
| 후보 부족 | 핵심 목표를 확인하고 실제 강의 예제로 자체 출제한다. 숫자 변형으로 채우지 않으며 남은 목표와 제외 이유를 기록한다. |
| hwp 변환 실패·외부 변환 허락 없음(`bank`) | 그 원본을 빼고 진행, 보고서 "빠진 원본"에 적음 |
| 원본 판독 불가(`bank`) | `[?]`로 표시하고 보고서에 적음 |
| 포트 사용 중 | 다른 빈 포트 사용 |

| 해설 스킬·실행기 누락 | bank 외 생성 시작 전에 경로와 오류를 보고하고 중단 |
| 해설 저작·검산·검토·발행 실패 | 검증된 원 복습팩과 이전 해설 보존, “복습팩 생성됨 / 문제설명 보류”와 팩별 이유 보고; 다른 팩은 계속 |

| PDF 생성·검토·발행 실패 | 원 HTML·MD·그림·문제설명과 이전 PDF를 보존하고 팩별 withheld/stale 이유를 보고; 다른 팩은 계속 |
