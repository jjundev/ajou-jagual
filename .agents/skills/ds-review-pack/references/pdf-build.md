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
