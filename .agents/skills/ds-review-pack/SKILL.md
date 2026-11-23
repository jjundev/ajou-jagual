---
name: ds-review-pack
description: 자구알(자료구조및알고리즘이해) 수업의 복습팩(정리노트·복습문제·문제설명)이나 기출 문제은행을 만들 때 사용한다. /ds-review-pack [bank | MMDD | MMDD-MMDD | update-existing MMDD/all | revise-existing MMDD/all]
---

# 자구알 복습팩

수업 녹음 전사(STT)와 강의록(`자료구조_강의록_2026/`), 기출 문제은행과 검증된 교과서 연습문제로 한 기간의 복습팩을 만든다. 문제은행은 `bank` 모드로 먼저 한 번 만들어 둔다. 중간에 사용자에게 묻지 않고(`bank` 모드의 hwp 외부 변환 허락만 B2 전에 한 번 묻는다) 끝에 한 번 보고한다. 커밋은 제안만 한다.

**공통 품질 기준**: 신규·두 갱신은 단계별 강의 출처·coverage·전역 중복 검사를 적용한다. 실제 학습 범위와 서로 다른 기출의 보존 기준은 공통 선별 절에 있다.

**모드**
- `revise-existing [MMDD|all]`: 기존 전체 문항을 검토·교체하고 문제설명·PDF까지 갱신한다.
- `bank`: 기출 원본을 전사해 문제은행을 만들거나 다시 만든다. 절차는 "문제은행 모드" B1~B4.
- `update-existing [MMDD|all]`: 기존 카드와 노트를 보존하고 교과서 원문 4~8개를 추가한다. 전체 문항의 문제설명도 다시 만든다.
- 그 밖(`[MMDD | MMDD-MMDD]`): 복습팩을 만든다. 절차는 "복습팩 절차" 0~9.

**산출물** (복습팩, `복습노트/<range>/`, 수업 날짜마다 폴더 하나):
- 루트: `정리노트_<range>_<slug>.html`, `문제설명_<range>_<slug>.html`, `복습문제_<range>_<slug>-문제.pdf`·`-답안.pdf`, `확인문제_<range>_<slug>.html`(신규 모드만). 루트에는 HTML·PDF와 `.pack/`만 둔다.
- `.pack/`(숨김 폴더): 같은 이름의 `.md` 세 개, `figures_<range>/`, 설명 소유 그림·자료 폴더(`figures_문제설명_*`, `자료_문제설명_*`), `자료_복습팩/`의 `복습문제_<range>_<slug>.json`(문항 원고), `자료_PDF/pdf-validation.json`, `자료_확인문제_<range>_<slug>/`. 검색 도구가 숨김 폴더를 건너뛸 수 있으니 `복습노트/<range>/.pack/<이름>` 경로를 직접 연다.

**인자**: `[bank | MMDD | MMDD-MMDD | update-existing MMDD/all | revise-existing MMDD/all]`

**에이전트 모델** (작성자·요약·전사 공통, 모델은 여기서만 정한다):
| 실행 환경 | 모델 |
|---|---|
| Claude | opus |
| GPT 등 Claude 아님 | sol |

**메인 참조 읽기** — `rg -n '^#{1,6} '`로 링크 이름과 같은 제목을 찾고, 다음 동급·상위 본문 제목 직전까지 읽는다. 코드 펜스 안 제목은 건너뛴다. 이미 읽은 절은 재사용하고 담당자용 문서는 경로로 넘긴다.

**후속 작업 준비** — 메인 읽기 (bank 이외 모드) [준비](references/pack-followups.md). 생성 전에 이번 모드의 형제 스킬과 실행기를 확인한다.

실제 해설의 저작과 네 검토는 담당자에게 [공통 문제설명 절차](references/problem-explain.md) 경로로 넘긴다.

**진행 표시**: 단계마다 한 줄만 쓴다. 예: `3/9 작성 중: 섹션 4개 + 카드 9개 (병렬)`, `B3 전사 중: 원본 11개 (병렬)`

**경로 약속**
- `SKILL` = 이 파일이 있는 폴더(`.agents/skills/ds-review-pack`)의 절대 경로
- `REPO` = 저장소 루트
- `TEXTBOOK` = NFC/NFD 실제 경로로 찾은 `REPO/교과서/`; `TEXTBOOK_PYTHON` = PyMuPDF·jsonschema가 설치된 Python 실행 파일(기본 sys.executable).
- `BANK` = `REPO/from_the_past/기출/문제은행.json`
- `RUN` = 복습팩은 `<scratchpad>/ds-review-pack/<range>/`, 문제은행은 `<scratchpad>/ds-bank/<YYYYMMDD-HHMMSS>/`
- 셸 호출마다 변수를 절대 경로로 먼저 설정하거나 명령에 실제 경로를 넣는다. `cd` 없이 실행한다.
- 은행 명령은 종료 코드 0과 `OK`를 확인한다. `FAIL: 오류 …`면 이번 JSON의 `errors`에서 조치할 항목을 읽는다. 보고서 저장 실패나 실행 오류면 해결 후 재실행한다. 이전 보고서는 판정 근거에서 제외한다.

## 기존 복습팩 갱신

- `update-existing`의 메인 읽기 — [준비·선별](references/textbook-update.md), [작성·검증](references/textbook-update.md), [발행·보고](references/textbook-update.md)를 해당 단계에서 차례로 연다.
- `revise-existing`의 메인 읽기 — [개편 준비](references/review-overhaul.md)로 시작한다. 선별·작성 시 [선별: 핵심 범위 충족 우선](references/review-overhaul.md)과 [강의 예제 근거](references/review-overhaul.md)를 적용한다. 이어서 [개편 기계 검사](references/review-overhaul.md), [Stage와 전역 검사](references/review-overhaul.md), [발행·파생 산출물](references/review-overhaul.md)을 순서대로 적용한다.

## 문제은행 모드 (`bank`)

### B1. 준비
- 메인 읽기 — [원본 표](references/bank-build.md).

1. `REPO/from_the_past/기출/`이 있는지 확인한다. 없으면 "자구알 저장소에서만 동작합니다"라고 알리고 멈춘다.
2. 실행 폴더를 만든다: `mkdir -p "$RUN"/{parts,work} && ln -sfn "$REPO" "$RUN/repo"`
3. `BANK`가 이미 있으면 `RUN/previous-bank.json`으로 복사한다(`reviewed` 값을 이어받는 데 쓴다). 이전 은행에서 `reviewed: true`인 `scan`·`photo` 원본은 B2·B3을 건너뛰고, 그 원본의 `sources`·`problems` 항목과 `REPO/from_the_past/기출/_전사/<id>.md`를 그대로 가져온다(사용자 검수와 수정을 지킨다). 다시 전사하려면 사용자가 먼저 그 원본의 `reviewed`를 `false`로 바꾼다.
4. 원본 목록과 id는 원본 표를 따른다. 표에 없는 파일이 `from_the_past/기출/` 아래에 있으면(숨김 파일(`.DS_Store` 등)과 은행 산출물 `문제은행.json`, `_전사/`, `_정답검증/`은 빼고) 보고서 "새 원본"에 적고 이번에는 넣지 않는다.

### B2. 정규화
- 메인 읽기 — [정규화 (메인 에이전트, 결과는 `RUN/work/`)](references/bank-build.md).

새로 전사할 원본만 `RUN/work/`에서 정규화한다.

### B3. 전사 (병렬)
- 메인 읽기 — [전사 브리프 (원본마다 1명, 병렬, 모델은 SKILL.md "에이전트 모델")](references/bank-build.md).

B1에서 그대로 가져오지 않은 원본마다 전사 에이전트 1명을 **한 메시지에서 병렬로** 띄운다(모델은 "에이전트 모델" 표). 브리프의 `<source-id>`, `<원본 경로들>`, `<RUN>`, `<SKILL>`을 채워 넘긴다. 각자 `RUN/parts/<source-id>.json`과 `RUN/parts/<source-id>.md`를 쓴다.

### B4. 합치기·검증·저장
- 메인 읽기 — [챕터 표 (강의록 `자료구조_강의록_2026/Software_<N>_*.pdf`)](references/bank-build.md), [중복 문항](references/bank-build.md), [정답 검증 (메인 에이전트)](references/bank-build.md).

1. 조각을 합쳐 `RUN/bank.json`(`{"version": 1, "sources": [...], "problems": [...]}`)을 만든다. `sources`는 B1에서 읽은 원본 표 값에 조각의 `has_key`와 `reviewed` 규칙을 더한다. B1에서 가져온 원본의 `sources`·`problems` 항목은 바꾸지 않고 그대로 넣는다(2~4단계도 새로 전사한 원본에만 한다).
2. 챕터 태그를 챕터 표로 다시 본다.
3. "중복 문항" 절에 따라 `duplicate_of`를 채운다.
4. "정답 검증" 절에 따라 확인해 `answer`, `answer_origin`을 정한다.
5. `python3 "$SKILL/scripts/bank.py" validate "$RUN/bank.json" --out "$RUN/bank-validation.json"` 결과가 `OK`여야 한다. 실패하면 RUN 보고서의 오류를 고치고 다시 검사한다.
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
2. `BANK`가 없으면 "먼저 `/ds-review-pack bank`로 문제은행을 만들어 주세요"라고 알리고 멈춘다.
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
6. `python3 "$SKILL/scripts/bank.py" validate "$BANK" --out "$RUN/bank-validation.json"`가 `OK`여야 한다. 실패하면 현재 실행의 오류를 보고하고 멈춘다. 교과서도 `scripts/textbook.py`의 `load_textbook(Path(TEXTBOOK), python=TEXTBOOK_PYTHON)`로 검증한다. 다른 bank.py를 현재 프로세스에 import하지 않는다. 폴더·의존성 누락, 원본/자산/payload 검증 실패는 오류로 중단하며 기출 전용으로 대체하지 않는다. 정답 null은 아직 정답을 작성하지 않았다는 뜻이며 review.status=verified와 혼동하지 않는다.
7. 사용할 Python 절대 경로로 `"$LAYOUT_PYTHON" "$SKILL/scripts/preview_layout.py" preflight`를 실행한다. 출력에서 Python 경로와 설치된 Chrome 버전을 확인하고 이 Python 경로를 작성자와 브라우저 검사자 브리프에 넘긴다. 실패하면 사용 가능한 다른 Python을 확인한다. 성공한 경로가 없으면 브리프에 `unavailable`과 이유를 적고 7단계의 실화면 도구로 검사한다.
8. 메인 읽기 — [변경 전 전역 목록](references/review-overhaul.md). 조립에 앞서 기준 목록을 RUN에 저장한다.

### 1. 범위 파악
- 메인 읽기 — [후보 추출](references/problem-selection.md). 날짜별 요약 브리프는 [STT 요약 에이전트 지시문](references/stt-summary-prompt.md)의 날짜와 경로 자리만 확인해 담당자에게 넘긴다.

1. **먼저** 관련 강의록 텍스트를 쪽 번호와 함께 `RUN/slides.txt`에 추출한다. 요약 에이전트는 이 파일이 있다고 보고 시작하므로 추출이 끝난 뒤에 띄운다.
   - 관련 챕터: 이전 팩 정리노트(`복습노트/*/정리노트_*.html`)의 `<span class="tag slide">S<N> p<k>` 중 가장 큰 챕터(그 챕터 마지막 쪽까지 다뤘으면 그다음 챕터)부터 두 챕터. 이전 팩이 없으면 1~3장. 확실하지 않으면 넉넉히 넣는다.
   ```bash
   python3 "$SKILL/scripts/extract_slides.py" --repo "$REPO" --run "$RUN" --ch <관련 챕터 번호, 공백 구분>
   ```
   - 추출에 실패하면 STT만으로 진행하고 보고서에 적는다(브리프의 `slides.txt` 줄은 "없음"으로 바꿔 넘긴다).
2. 그다음 STT 날짜마다 요약 에이전트 1명을 **병렬로** 띄운다.
   - `<Software_N_*.pdf>`: 그 날짜가 다룬 쪽이 들어 있는 강의록(확실하지 않으면 관련 챕터의 강의록을 모두 적는다).
   - `<MMDD 자구알.md>`: NFC 목록에서 찾은 실제 파일명. `<YYYY-MM-DD>`: 연도는 이번 학기 연도(오늘 날짜 기준), 월·일은 `<MMDD>`.
3. 에이전트가 도는 동안 `select`로 후보를 미리 뽑는다. `--range-ch`와 `--taught`는 관련 챕터로 임시 지정하고 `CANDIDATE_REPORT=candidates-preview.json`을 사용한다.

### 2. manifest
- 메인 읽기 — 문제 선별의 [원칙](references/problem-selection.md), [순서](references/problem-selection.md), [parts](references/problem-selection.md), [level](references/problem-selection.md), [문항 원문 모으기](references/problem-selection.md), [정답](references/problem-selection.md), [교과서 후보 검토](references/problem-selection.md).
- 메인 읽기 — 공통 [선별: 핵심 범위 충족 우선](references/review-overhaul.md)과 강의 예제를 쓸 때 [강의 예제 근거](references/review-overhaul.md), [강의 예제·전역 검토 연동](references/manifest-guide.md).
- 메인 읽기 — manifest의 [최상위](references/manifest-guide.md), [sections / topics](references/manifest-guide.md), [parts / problems](references/manifest-guide.md), [links](references/manifest-guide.md), [검증](references/manifest-guide.md).
- 요약들의 슬라이드 대조표로 `range_ch`(이번 범위에서 "다룸/일부"인 쪽이 있는 챕터)와 `taught`(1장부터 이번 범위의 마지막 챕터까지)를 정한다.
- 1단계 명령을 확정 범위와 `CANDIDATE_REPORT=candidates.json`으로 다시 실행한다. 원문과 검산은 지정한 절에 따라 `RUN/problems.md`, `RUN/answers.py`에 쓴다.
- `scripts/textbook_blocks.py`로 교과서 원문의 숫자·코드·그림·오타와 보기 순서를 보존한다. observations/printed_answer를 답으로 쓰지 않는다.
- `RUN/manifest.json`에 신규 `"rules": ["trace-v1", "layout-v2"]`를 넣는다. 두 갱신 모드는 기존 rules를 보존한다.
- "검증" 절의 두 명령이 모두 `OK`여야 한다. 출처 검사 보고서는 `RUN/bank-manifest-check.json`이다.

### 3. 작성
- 메인 읽기 — 브리프의 [작성자 브리프 (메인 에이전트가 섹션마다 1명, 병렬, 모델은 SKILL.md "에이전트 모델")](references/content-rules.md), [작성자 브리프 (메인 에이전트가 1명, 모델은 SKILL.md "에이전트 모델")](references/card-rules.md)와 위젯 배정의 [언제](references/widget-rules.md). 섹션·카드의 세부 작성 규칙과 위젯·trace 문서는 담당자에게 경로로 넘긴다.
- 정리노트 HTML·동반 Markdown·제작 manifest의 `links`에 PDF 링크를 넣지 않는다. 강의록·실습·과제는 자료명이나 강의록 쪽 번호를 텍스트로 적는다. 문제지·답안지 PDF는 날짜 폴더에 발행한다.
- 정리노트 HTML의 본문·인용·요약·푸터에 녹음 시각, Part 번호, 시각 미제공 등 위치 표시와 그 안내 문장을 싣지 않는다. 토픽 머리의 수업 날짜 태그(`tag date`)·강의록 페이지·푸터 일반 출처는 유지하되 인용 끝 `(MMDD)`는 붙이지 않고, 위치 근거는 내부 STT 요약에만 둔다. 신규·기존 갱신 모드 모두 `recording-locator`·`quote-date` 검사 통과가 필수다.
- 섹션마다 작성자 1명과 전체 카드를 맡을 작성자 1명을 띄운다.
- 신규 작성자는 [섹션 브리프](references/content-rules.md) 또는 [카드 브리프](references/card-rules.md)의 `preview_layout.py author` 명령으로 실제 템플릿을 확인한다. `fail`이면 보고서에 표시된 영역·수치를 기준으로 해당 조각을 고치고 다시 실행한다. `unavailable`이면 영향을 받는 섹션·카드와 사유를 7단계 검사자에게 넘긴다. 메인은 판정, `layout.json` 경로, 남은 결함만 받는다.
- 추적 토픽 작성자에게 `<RUN>/traces/` 와 [trace 생성기](references/trace-figures.md)를 알려 준다.
- 모두 **한 메시지에서 병렬로** 띄운다. 모델은 "에이전트 모델" 표를 따른다.
- 브리프의 `<…>` 자리는 실제 경로, id, 금지어 목록(`<forbidden 목록>`), 예고 토픽 id(`<preview_topic>`), 그리고 섹션 작성자에게는 manifest `links` 중 그 섹션 토픽에 속한 것만(`<이 섹션의 links 목록>`) 채워 넣는다.
- 메인은 작성자를 띄우기 전에 위젯 토픽(0~2개)을 정한다. 해당 작성자의 `<위젯>`에 토픽 id와 조작 시 보이는 내용을 적고, 나머지에는 "위젯 없음"을 적는다. 배정과 이유는 "스킬이 정한 사항"에 남긴다.

### 4. 조립
메인 읽기 — [영속 제작자료](references/manifest-guide.md). 조립·검증 시 제작자료와 증거를 이 계약에 맞춰 기록한다.

새 작업 폴더에서 검증·PDF를 준비한다. `STAGE`는 복습노트 아래의 숨김 작업 폴더다. 다시 조립할 때는 처음 준비한 `STAGE`를 쓴다. 신규 팩의 그림과 파생 자료도 `STAGE/.pack/` 아래에 둔다. 작성자가 `RUN/.pack/`에 준비한 그림을 참조했다면 검증 전에 `STAGE/.pack/`의 같은 상대 경로에 복사한다.

```bash
STAGE=$(python3 "$SKILL/scripts/release_review.py" prepare --repo "$REPO" --run "$RUN" --range <range>)
python3 "$SKILL/scripts/assemble.py" --run "$RUN" --out "$STAGE"
```

### 5. 기계 검사
```bash
python3 "$SKILL/scripts/check_html.py" --manifest "$RUN/manifest.json" --note "$STAGE/<정리노트>.html" --review "$STAGE/<복습문제>.html"
```
- `FAIL`이면 Problem의 `where`(토픽 id, 카드 id, 섹션 id)로 담당 작성자를 찾는다.
- 그 작성자에게 문제 목록을 보내 조각을 고치게 한다(SendMessage, 안 되면 같은 브리프로 새 에이전트).
- 고친 뒤 4단계부터 다시 한다. 최대 2회까지이며, 그래도 남으면 "미해결"로 보고한다.

### 6. 리뷰
- 리뷰어 1명을 띄운다. `references/review-prompt.md` 경로와 브리프의 RUN·HTML 경로를 넘긴다.
- Critical과 Important는 모두, Minor는 쉬운 것만 고친다.
- 담당 작성자별로 **한 번에 모아서** 수정을 요청한다. 수정은 한 번만 한다.
- 수정 후 4~5단계를 다시 한다. 반영하지 않은 항목은 보고서에 적는다.

### 7. MD 변환과 브라우저 검증

- 메인 읽기 — [Stage와 전역 검사](references/review-overhaul.md). 발행 이력이 없는 범위에만 먼저 [새 날짜의 감사 입력](references/review-overhaul.md)을 적용한다. 최종 작업용 HTML을 포함한 전역 audit가 통과한 뒤 변환·실화면 검사로 넘어간다.
- 메인 읽기 — [검사 요청과 결과](references/browser-check.md). 검사자가 직접 열 수 없어 메인이 맡을 때만 [서버](references/browser-check.md)부터 [패널 제목과 요약 계약](references/browser-check.md)까지의 검사 절을 순서대로 적용한다.

```bash
python3 "$SKILL/scripts/html2md.py" "$STAGE/<정리노트>.html" "$STAGE/<복습문제>.html" --check
python3 "$SKILL/scripts/release_review.py" browser-request --repo "$REPO" --run "$RUN"
```

- 먼저 MD 변환에서 `OK`를 확인한다. `.md`와 `figures_<range>/`는 `STAGE/.pack/`에 생긴다. 누락이 있으면 HTML 조각을 고치고 4단계부터 다시 한다.
- 새 검사 서브에이전트에게 `REPO`, `RUN`, 요청 JSON, `LAYOUT_PYTHON`과 브라우저 지침의 절대 경로, 작성 단계에서 확인하지 못한 영역을 넘긴다. 검사자는 신규 v2 요청의 전 영역을 측정하고 아래 지침에 따라 실제 화면을 열어 승인 기록을 쓴다.
- 메인은 측정 기록과 실화면 승인을 확인한 뒤 PDF로 넘어간다. 판정과 결함 목록은 해당 요청 경로와 함께 받는다.
- 결함은 5단계와 같은 방식으로 `where`별로 모아 담당 작성자에게 돌려보낸다. 기존 최대 2회 수정 한도를 적용한다. 수정 뒤에는 다시 조립·검사·감사·변환하고 요청을 새로 만든다. 끝내 통과하지 못하면 새 발행을 보류하고 이전 팩이 있으면 보존한다.

### 8. PDF·기본 팩 발행과 후속 작업

- 메인 읽기 (문항이 있을 때) — [생성과 기계 검사](references/pdf-build.md), [쪽별 실화면 검토](references/pdf-build.md), [발행](references/pdf-build.md). PDF만 소급 생성할 때는 [backfill](references/pdf-build.md), 생성기를 고칠 때는 관련 배치·강의 코드·글꼴 절을 추가로 본다.
- 7단계 브라우저 승인을 받은 작업용 복습문제 HTML을 `REVIEW`로 지정해 전체 PDF를 만든다. 새 검사 서브에이전트가 `PDF_RUN`의 모든 쪽을 실제로 열어 검토한다. 메인은 판정을 받아 PDF를 같은 작업 폴더에 발행한다. 0문항이면 PDF를 건너뛴다.
- 아래 명령으로 정리노트, 문항 원고·MD·그림과 PDF 쌍을 함께 발행한다. 발행기는 정리노트 HTML·동반 Markdown·제작 manifest에 PDF 링크가 있으면 중단한다. 발행에 성공하면 작업 폴더를 정리한다. 중단한 작업 폴더는 같은 인자로 `release_review.py discard`를 실행해 지운다.

```bash
python3 "$SKILL/scripts/release_review.py" publish --repo "$REPO" --run "$RUN"
```

- 위 발행 뒤 메인 읽기 — [병렬 시작](references/pack-followups.md), 판정을 받은 뒤 [발행](references/pack-followups.md), 중계 요청을 받을 때만 [블라인드 중계](references/pack-followups.md). 신규는 문제설명과 확인문제를 병렬로 맡긴다. 메인은 담당자의 판정과 기록 경로를 받아 작업본을 각각 발행한다.

- 마지막으로 폴더 배치를 검사한다. `OK`가 아니면 루트에 남은 항목을 `.pack/`으로 옮기고 다시 검사한다. 옛 배치(루트에 md·그림·자료 폴더)인 팩은 `migrate`로 옮긴다(인자 없이는 계획만 출력, `--apply`로 실행).
```bash
python3 "$SKILL/scripts/pack_layout.py" check --repo "$REPO"
```

### 9. 보고
다음 형식으로 끝낸다.
```
## 복습팩 <range> 완료 (설명 보류 시: 복습팩 생성됨 / 문제설명 보류, 확인문제 보류 시: 복습팩 생성됨 / 확인문제 보류)
- 파일: 복습노트/<range>/… (정리노트·문제설명 HTML과 PDF 2, .pack/ 에 md 3, figures_<range>/ N개; 설명 소유 그림·자료 포함)
- 범위: 배운 쪽 S2 p1–20 … / 예고만: …
- 문제: P1 2016-final-ljw-q3 (2016 기말 3번, 이정원, trace) … / 변형 K개 (정답은 RUN/answers.py로 검증)
- 은행과 다른 답: … (없으면 "없음")
- 은행과 다른 문제 글: … (없으면 "없음")
- 검수 대기로 뺀 원본: … (없으면 "없음")
- 스킬이 정한 사항: slug, 섹션 구성, 위젯, 뺀 내용과 이유, 뺀 후보 문항과 이유
- 문제설명: 발행/보류, 전체 문항 수, HTML·MD·EXPLAIN_RUN·백업 경로, 네 검토 결과와 보류 이유
- PDF: 문제/답안 발행·보류·stale·skipped, PDF 두 경로·페이지 수·PDF_RUN·검증·백업·이유
- 확인문제: 발행/보류, 목표 n·문항 n(객관식 n·입력 n), 블라인드 회차별 일치, 브라우저 pass/fail, HTML·SRC·확인문제 RUN·백업 경로, 보류 이유
- 미해결: … (없으면 "없음")
- 커밋 제안: git add 복습노트/<range> && git commit -m "docs(notes): add ds review pack <range>"
```
교과서 추가 개수·출처·검산 방법·제외 이유도 보고한다. `복습노트/<range>/.pack/자료_복습팩/`에 manifest.json, stt-summary.md(4단계 조립이 쓴다), selection.json, answers.py, validation.json, traces/(trace 생성기 JSON, 있을 때)를 저장한다.
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

| PDF 생성·검토·발행 실패 | 기존 팩과 PDF를 보존하고 팩별 withheld/stale 이유를 보고; 다른 팩은 계속 |
| 확인문제 스킬 누락 | 신규 모드 생성 시작 전에 경로를 보고하고 중단 |
| 확인문제 근거 없음 | 확인문제만 “복습팩 생성됨 / 확인문제 보류”(이유: 근거 파일 없음)로 보고하고 배치 검사·9단계 보고는 계속 |
| 확인문제 검사 실패 | 작업본을 확인문제 RUN에 보존하고 “복습팩 생성됨 / 확인문제 보류”와 이유 보고. 이전 확인문제와 기본 팩·문제설명·PDF는 보존 |

## 패널 제목과 요약 계약
중앙 제목과 고정 패널 제목을 유지하고 오른쪽의 중복 주제·문항 제목은 출력하지 않는다. `sum-for`는 `.sums` 컨테이너의 유일한 ID로 보존하며 `aid-for`와 제거한 제목의 JavaScript 참조는 두지 않는다.

요약 항목 수에 고정 상한을 두지 않는다. 같은 토픽 본문의 핵심 개념·원리·성립 조건·혼동 구분을 압축하고, 본문에 없는 사실을 추가하지 않는다. 보충의 범위·출처·불확실성을 유지한다. 모든 학습 토픽의 일반·강조·주의·보충 핵심을 본문 주장, 대응 요약, 판정 또는 생략 이유로 대조한다. 누락은 unresolved로 기록하고 보완된 실제 요약을 다시 읽은 뒤 pass로 바꾼다. 기존 동반 MD와 실제 생성 원고를 동기화하고 동반 MD가 없으면 새 형식을 만들지 않는다.

브라우저는 HTTP 임시 stage에서 1280×900, 375×812 각각 light/dark로 검사한다. 요약·풀이 패널을 열어 중앙 제목 표시, 우측 중복 제목 없음, 토픽별 요약 하나와 정확한 내용, 표지 안내, 이전 요약 숨김, 수식 오류와 페이지 오류 0을 확인한다. 문제·원문 탭, 이전/다음, 힌트·풀이, 푼 문제 토글과 기존 read/solved 저장 키를 유지한다. missing-sum 실패 탐지와 no-panel legacy 검사를 유지한다.
