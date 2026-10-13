# 복습문제·답안 PDF

신규·lite·update-existing의 최종 검증된 복습문제 HTML **절대 경로**를 입력한다. 전자회로2 16:9 템플릿의 고정 복사본·글꼴·배율·Hint 띠/부록·하단 자막 여백을 사용한다. 문제지에는 풀이/정답이 없고 답안지에는 기존 `.solution` 전체와 정답이 있다. 별도 문제설명은 독립 산출물이다.

Python 3.10+, Playwright/설치된 Google Chrome, PyMuPDF가 필요하다. 자동 설치하지 않는다. RUN은 저장소 밖의 비어 있는 고유 절대 경로로 정한다.

```sh
python3 "$SKILL/scripts/review_pdf.py" build --review "$REVIEW" --run "$PDF_RUN"
python3 "$SKILL/scripts/review_pdf.py" check --run "$PDF_RUN"
```

`report.json`의 status=staged, checks.status=pass여야 한다. `stage/pages/{problems,answers}/*.png`의 **모든 페이지**를 실제로 열어 문제/답/힌트/코드/그림/표·계속 페이지·순서·하단 여백을 확인한다. 원본 source 및 stage PDF의 내용과 대응도 확인한다. 기계 검사만으로 browser=pass를 기록하지 않는다. 실패하면 생성기·adapter·분할을 고치고 새 RUN에서 다시 build한다. 템플릿/CSS를 바꾸거나 코드를 생략해서 통과시키지 않는다.

실제 검토를 끝낸 현재 RUN/review.json에 status=pass, reviewer, 구체적 evidence, `report_sha256`(report.json의 현재 SHA-256), `artifact_hashes`(검토한 report.json의 artifact_hashes 그대로)를 기록한다. 재생성/자산 변경 시 승인은 무효다.

```sh
python3 "$SKILL/scripts/review_pdf.py" publish --run "$PDF_RUN" --repo "$REPO"
```

발행 직전에 입력과 승인한 자산·PDF 해시를 재확인하고 팩 잠금 아래 문제/답안 PDF와 `자료_PDF/pdf-validation.json`만 백업·교체한다. 일반 저장 오류는 rollback한다. 여러 파일 교체의 OS 원자성·강제 종료 복구를 보장하지 않는다. 백업은 PDF_RUN/backups 아래 유지한다. 기존 prefix 기반 backup.py는 PDF도 포함한다.

기존 팩의 PDF만 추가할 때는 `update-existing`를 호출하지 않는다.

```sh
python3 "$SKILL/scripts/review_pdf.py" backfill --repo "$REPO" --target all --run "$PDF_RUN"
```

backfill은 팩별 stage/check 및 summary.json만 만든다. summary의 각 run에서 위 전체 화면 검토→publish를 수행한다. 날짜 한 팩은 --target MMDD, 저장된 통합 팩은 --target MMDD-MMDD를 쓴다. 같은 폴더 리뷰 둘은 공유 보고서 충돌이므로 자동 선택하지 않는다.

0문항은 skipped, 손상/잘림/누락/수식·자원 오류는 withheld다. 이전 PDF가 있는 재생성 실패는 stale이다. withheld/stale이면 CLI 종료 코드 1이며 다른 팩은 계속한다. PDF와 문제설명은 각각 발행/보류·이유를 보고하고, 한쪽 실패로 검증된 원 복습팩·문제설명·이전 PDF를 삭제하지 않는다. lite도 PDF 검증·실화면 검토를 생략하지 않는다.

## 자구알 배치 확장

전자회로2 원본 4개 파일은 해시 그대로 보존한다. `pdf_ds_layout.py`가 맞춤/넘침 측정 전에 빈 조건 블록을 제거하고 문제 코드의 좌측 `코드` 섹션을 만든다. 문장 안의 인라인 코드는 유지한다. 문제의 `<pre>` 블록은 내용·들여쓰기·줄바꿈을 보존한다.

작성용 표는 명시적으로 지정한 1012 P2·P3에 적용한다. 문제지에서는 원래 표를 중앙 작업 공간으로 옮기며, 답안지에서는 좌측에 유지한다. 답안의 풀이 표는 중앙에 그대로 둔다. 참고용 표는 옮기지 않는다. 확장 코드의 해시도 build/check/publish에서 검증한다.

## 블록 코드 가독성 계약 (code_style_version 1)

최종 1440×810pt PDF의 블록 코드는 실제 12pt(±0.05pt), JetBrains Mono Regular 400이다. 공식 v2.304 static TTF와 OFL-1.1 라이선스를 vendor/jetbrains-mono에 고정하며 manifest의 SHA256을 빌드·검사·게시 때 검증한다. 한글 주석은 번들 Pretendard로 출력하고 실제 PDF 글꼴도 검사한다. 온라인 또는 시스템 폰트 fallback은 통과 근거가 아니다.

줄 간격 1.45, 합자 비활성화, tab-size 4, 긴 줄 2ch 내어쓰기를 적용한다. 원문 개행·공백·탭은 변경하지 않으며 긴 코드는 문제/해설 공통 PageSlice로 이어진다. inline code에는 이 계약을 적용하지 않는다. 원래 EC2 템플릿 파일은 수정하지 않는다.

새 보고서에는 code_font와 code_style_version을 기록한다. 코드 영역 geometry와 최종 PDF의 실제 glyph font/size/text를 대조한다. 글꼴 누락·교체·잘못된 크기·내용 누락·경계 밖 줄은 빌드 실패다. 검토 후 자산이 바뀌면 게시 lock 안에서 거부하고 기존 PDF와 보고서를 보존한다. 구형 보고서에 새 필드가 없으면 기존 검증 경로를 유지한다. 실패 시 자산과 소스를 복구하고 새 RUN에서 다시 빌드·시각검토한다. 오래된 review.json을 재사용하지 않는다.
