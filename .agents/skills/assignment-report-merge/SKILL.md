---
name: assignment-report-merge
description: Use when a finished assignment report PDF must be combined with its cover into a submission PDF in this project. Not for editing or exporting the report body.
---

# 과제 보고서와 표지 합치기

완성된 보고서 PDF 앞에 표지 한 쪽을 붙여 `과제/과제n/제출용/HWn_학번_이름.pdf`를 만든다. 원본 보고서와 표지는 보존한다.

## 입력 확인

- 과제 번호 `n`, 보고서 PDF의 정확한 경로, 학번, 이름을 확인한다. 학번·이름은 [assignment-cover](../assignment-cover/SKILL.md)에 고정된 작성자 값을 쓰고 다시 묻지 않는다. 사용자가 보고서 경로를 주면 그것을 우선한다. 경로가 없을 때는 해당 과제 폴더와 사용자가 가리킨 위치에서 후보를 찾되, 여러 PDF 중 임의로 선택하지 않는다. `HWn.pdf` 같은 과제 지시문을 보고서로 취급하지 않는다.
- `과제/과제n/표지.pdf`가 있으면 첫 쪽에 적힌 과제 번호·학번·이름을 이번 요청과 대조한다. 다르면 병합하지 말고 정확한 값을 확인한다.
- 표지가 없으면 [assignment-cover](../assignment-cover/SKILL.md) 스킬을 사용해 같은 경로에 만든다. 그 스킬이 요구하는 과목명, 과제명, 주제, 학번, 이름은 이번 과제의 확인된 자료에서 얻는다. 모르는 값은 과거 과제나 예시에서 추정하지 않는다.

## 병합

스킬 폴더에서 다음을 실행한다. `--assignment-dir`은 실제 `과제n` 폴더이고, 보고서는 그 폴더 밖에 있어도 된다.

```bash
python3 scripts/merge_report.py \
  --report '<보고서 PDF 경로>' \
  --cover '<과제n 폴더>/표지.pdf' \
  --assignment-dir '<과제n 폴더>' \
  --assignment-number n \
  --student-id '<학번>' \
  --student-name '<이름>'
```

스크립트는 표지 1쪽, 읽을 수 있는 보고서, 파일명 값을 검사하고 임시 PDF를 만든다. 페이지 수와 각 쪽의 텍스트·크기가 원본 순서와 맞을 때만 `제출용/`에 저장한다. 결과 파일이 이미 있으면 그대로 둔다. 사용자가 그 제출본을 다시 만들라고 명시한 경우에만 `--replace`를 붙인다.

## 최종 확인

`pdfinfo`로 총 페이지 수가 `1 + 보고서 페이지 수`인지 확인한다. 결과의 첫 두 쪽을 렌더링해 표지와 보고서 시작 쪽의 순서, 글자, 잘림을 확인한다. 생성 경로와 검증 결과를 사용자에게 알린다. 병합이 실패하면 원본과 기존 제출본을 유지하고 문제 파일을 구체적으로 알린다.
