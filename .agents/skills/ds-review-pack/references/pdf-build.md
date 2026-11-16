# 복습문제·답안 PDF

## 생성과 기계 검사

생성·갱신에서는 검증된 작업용 복습문제 HTML의 절대 경로를 입력한다. 발행된 팩에서 PDF만 다시 만들 때는 `.pack/자료_복습팩/복습문제_<range>_<slug>.json`의 절대 경로를 입력한다. 전자회로2 16:9 템플릿의 고정 복사본·글꼴·배율·Hint 띠/부록·하단 자막 여백을 사용한다. 문제지에는 풀이/정답이 없고 답안지에는 기존 `.solution` 전체와 정답이 있다. 별도 문제설명은 독립 산출물이다.

Python 3.10+, Playwright/설치된 Google Chrome, PyMuPDF가 필요하다. 자동 설치하지 않는다. RUN은 저장소 밖의 비어 있는 고유 절대 경로로 정한다.

```sh
python3 "$SKILL/scripts/review_pdf.py" build --review "$REVIEW" --run "$PDF_RUN"
python3 "$SKILL/scripts/review_pdf.py" check --run "$PDF_RUN"
```

## 쪽별 실화면 검토

메인은 `report.json`의 `status`가 `skipped`이면 PDF 발행을 건너뛴다. `staged`이고 `checks.status`가 `pass`이며 `check`까지 통과하면 새 검사 서브에이전트에게 `PDF_RUN`의 절대 경로와 이 절의 경로를 넘긴다. 검사자는 `PDF_RUN`에만 기록한다. 원고, 작업 폴더, `PDF_RUN/stage/`는 읽기 전용 입력으로 다룬다.

검사자는 `stage/pages/{problems,answers}/*.png`의 **모든 페이지**를 실제로 열어 원고 및 stage PDF와 대조한다. 문제·답·힌트·코드·그림·표, 계속 페이지, 순서, 하단 여백을 확인한다. 확인한 쪽의 경로 집합이 두 폴더의 PNG 전체와 일치하고 결함이 없을 때 `pass`를 기록한다. 기계 검사만 끝낸 상태는 미검토다.

`PDF_RUN/review.json`에 `status`, 검사자 이름 `reviewer`, `report_sha256`(검토를 시작할 때 읽은 report.json의 SHA-256), 그 보고서의 `artifact_hashes`를 기록한다. `evidence`에는 `{"page": "stage/pages/problems/001.png", "observation": "..."}`처럼 쪽마다 실제 관찰 한 줄을 남긴다. 결함은 해당 쪽과 이유를 적고 `status`를 `fail`로 기록한다. 메인에는 상태, 문제지·답안지 쪽 수, 문제 쪽과 사유, 기록 경로만 돌려준다. 검사자가 이미지를 열 수 없으면 메인이 동일한 검사와 기록을 맡는다. 메인도 열 수 없으면 보류한다.

실패하면 생성기·adapter·분할을 고치고 새 RUN에서 다시 빌드하고 검토한다. 템플릿과 코드 내용은 유지한다. 재생성이나 자산 변경 뒤에는 이전 승인이 무효다.

## 발행

실화면 검토를 통과한 RUN을 메인이 발행한다.

```sh
python3 "$SKILL/scripts/review_pdf.py" publish --run "$PDF_RUN" --repo "$REPO"
```

발행 직전에 입력과 승인한 자산·PDF 해시를 재확인하고 팩 잠금 아래 루트의 문제/답안 PDF와 `.pack/자료_PDF/pdf-validation.json`을 백업·교체한다. 발행된 팩의 문제지 쪽 배치가 바뀌면 정리노트와 문제설명의 문항 링크도 같은 잠금 아래 갱신한다. 일반 저장 오류는 rollback한다. 여러 파일 교체의 OS 원자성·강제 종료 복구를 보장하지 않는다. 백업은 PDF_RUN/backups 아래 유지한다. 기존 prefix 기반 backup.py는 PDF도 포함한다.

0문항은 skipped, 손상/잘림/누락/수식·자원 오류는 withheld다. 이전 PDF가 있는 재생성 실패는 stale이다. withheld/stale이면 CLI 종료 코드 1이며 다른 팩은 계속한다. PDF와 문제설명은 각각 발행/보류·이유를 보고하고, 한쪽 실패로 검증된 원 복습팩·문제설명·이전 PDF를 삭제하지 않는다. lite도 PDF 검증·실화면 검토를 생략하지 않는다.

## backfill

기존 팩의 PDF만 추가할 때는 `update-existing`를 호출하지 않는다.

```sh
python3 "$SKILL/scripts/review_pdf.py" backfill --repo "$REPO" --target all --run "$PDF_RUN"
```

backfill은 팩별 stage/check 및 summary.json만 만든다. summary의 각 `staged` RUN에 같은 쪽별 실화면 검토와 메인 발행 절차를 적용한다. 날짜 한 팩은 --target MMDD, 저장된 통합 팩은 --target MMDD-MMDD를 쓴다. 같은 폴더 리뷰 둘은 공유 보고서 충돌이므로 자동 선택하지 않는다.

## 자구알 배치 확장

전자회로2 원본 4개 파일은 해시 그대로 보존한다. `pdf_ds_layout.py`가 맞춤/넘침 측정 전에 빈 조건 블록을 제거하고 문제 코드의 좌측 `코드` 섹션을 만든다. 문장 안의 인라인 코드는 유지한다. 문제의 `<pre>` 블록은 내용·들여쓰기·줄바꿈을 보존한다.

작성용 표는 source ID 2018-mid-c024-q9, 2017-mid-c050-q6에 적용하며 문항 번호 변경과 무관하다. 문제지에서는 원래 표를 중앙 작업 공간으로 옮기며, 답안지에서는 좌측에 유지한다. 답안의 풀이 표는 중앙에 그대로 둔다. 참고용 표는 옮기지 않는다. 확장 코드의 해시도 build/check/publish에서 검증한다.

## 강의 코드 문제 분해

`data-source-kind="lecture-code"` 카드만 `pdf_lecture.split_lecture_problem`으로 문제 prose를 `조건`(문장마다 `<p>`)과 `구할 것`(`<ol class="ds-asks">`)으로 나눈다. HTML/MD 원본은 바꾸지 않는다.
`class="badge"`를 포함한 배지 문단은 문제·답안 PDF에서 삭제한다. 배지 문단에 배지와 `S4 p5 · 추가 근거 p2,3` 형식 출처 외의 글이 있으면 `PdfError`다. `후속 수업 보충:` 문단은 조건 맨 위 `<p class="ds-source">` 캡션으로 남긴다.
문장 분리는 `[.?!]` 직후 공백에서만, 열린 HTML 요소가 없고 `$…$` 밖일 때만 한다. 질문은 끝 괄호주석을 뺀 뒤 `(세요|시오|하라|보라)[.)]?$` 또는 `?$`로 끝나는 문장이며, 질문 뒤에 있던 조건 문장도 조건으로 올라간다.
문제 끝에 연속된 `<ol>`/`<ul>` 블록이 있고 그 앞에 조건 문단이 있으면, 앞 문단은 조건에 두고 목록 항목은 하나의 `<ol class="ds-asks">`로 합친다. 모든 항목이 `(a)` 같은 표지로 시작하면 `ds-labeled`를 붙여 목록 숫자를 숨긴다. 목록 뒤에 문단이 더 있거나, 목록만 있거나, 질문이 0개면 배지만 빼고 원래 문단을 구할 것에 둔다. 문장 분리 또는 배치에서 글자가 달라지면 `PdfError`로 빌드를 멈춘다.

## 블록 코드 가독성 계약 (code_style_version 1)

최종 1440×810pt PDF의 블록 코드는 실제 12pt(±0.05pt), JetBrains Mono Regular 400이다. 공식 v2.304 static TTF와 OFL-1.1 라이선스를 vendor/jetbrains-mono에 고정하며 manifest의 SHA256을 빌드·검사·게시 때 검증한다. 한글 주석은 번들 Pretendard로 출력하고 실제 PDF 글꼴도 검사한다. 온라인 또는 시스템 폰트 fallback은 통과 근거가 아니다.

줄 간격 1.45, 합자 비활성화, tab-size 4, 긴 줄 2ch 내어쓰기를 적용한다. 원문 개행·공백·탭은 변경하지 않으며 긴 코드는 문제/해설 공통 PageSlice로 이어진다. inline code에는 이 계약을 적용하지 않는다. 원래 EC2 템플릿 파일은 수정하지 않는다.

새 보고서에는 code_font와 code_style_version을 기록한다. 코드 영역 geometry와 최종 PDF의 실제 glyph font/size/text를 대조한다. 글꼴 누락·교체·잘못된 크기·내용 누락·경계 밖 줄은 빌드 실패다. 검토 후 자산이 바뀌면 게시 lock 안에서 거부하고 기존 PDF와 보고서를 보존한다. 구형 보고서에 새 필드가 없으면 기존 검증 경로를 유지한다. 실패 시 자산과 소스를 복구하고 새 RUN에서 다시 빌드·시각검토한다. 오래된 review.json을 재사용하지 않는다.

한글 블록 코드에는 시스템 local()을 우선하는 일반 Pretendard face 대신 `DS Pretendard` 별칭을 사용한다. 별칭은 고정된 Regular woff2 URL만 사용하며, loaded FontFace를 확인한다. 기존 vendor/provenance를 빌드 전에 검사하고 새 보고서의 vendor_hashes를 검사·게시 시 다시 확인한다. 최종 PDF도 `JetBrainsMono-Regular`와 `Pretendard-Regular`를 정확히 요구하여 동명 Bold/다른 face를 거부한다.

## 강의 예제·전역 검토 연동

신규·update-existing·revise-existing은 [공통 개편·검증 계약](review-overhaul.md)을 함께 적용한다. lecture-code는 실제 강의 페이지·해시·학습 근거와 자체 질문을 구분한다. 전체 날짜 audit를 통과한 작업용 HTML로 PDF를 만들고 발행된 JSON 원고에서 문제설명을 만든다. update-existing의 기존 카드 보존 계약은 유지한다.
