---
name: assignment-cover
description: Create a one-page A4 landscape assignment-report cover PDF using the bundled Pretendard HTML template. Use when asked to make or remake a course assignment cover; not for the report body or PDF merging.
---

# 과제 표지 만들기

`assets/cover.html`이 디자인 원본이다. 이 스킬은 그 HTML을 채워 PDF 한 페이지로 출력한다. 템플릿은 기존 자료구조 과제 표지의 흰 배경, 상단 과목명과 선, 중앙 과제명, 하단 학번·이름 배치를 재현한다. Pretendard Regular·SemiBold와 라이선스는 `assets/fonts/`에 포함돼 있다.

## 필요한 값

`course`, `assignment_label`, `assignment_topic`, `student_id`, `student_name` 문자열 다섯 개가 필요하다. 사용자 말이나 현재 과제 원문에서 확인된 값을 사용한다. 이전 산출물의 학번·이름이나 템플릿의 예시 값을 새 표지에 재사용하지 않는다. 확인할 수 없는 값은 묻고, 제출일·교수명·페이지 번호는 사용자가 별도로 요청하지 않는 한 추가하지 않는다.

## 생성

1. 다섯 값을 UTF-8 JSON 파일에 저장한다. 개인 정보가 담긴 입력 파일은 작업용 임시 위치에 두고 생성 후 제거한다.
2. 스킬 폴더를 기준으로 `python3 scripts/assignment_cover.py --data <입력.json> --output <표지.pdf>`를 실행한다. 지정 출력이 이미 있고 사용자가 교체를 요청한 경우에만 `--force`를 붙인다. 스크립트는 빈 값, `미제공`, 한 줄을 넘는 값, 배치 영역 초과를 거부하며 실패 시 기존 PDF를 보존한다.
3. PDF를 렌더링해 글자·정렬·잘림을 눈으로 확인한다. `pdfinfo`에서 A4 가로 1페이지, `pdftotext`에서 다섯 값, `pdffonts`에서 Pretendard 임베딩을 확인한다. PDF 자체를 제공하고 임시 JSON·검사 이미지는 정리한다.

입력 형식:

```json
{
  "course": "[2027-1] 운영체제",
  "assignment_label": "과제 2",
  "assignment_topic": "Process scheduling",
  "student_id": "123456789",
  "student_name": "홍길동"
}
```

Python 패키지 `playwright`, `pypdf`와 Playwright Chromium이 필요하다. 브라우저가 없다는 오류가 나오면 해당 환경에 Chromium을 설치한 뒤 재실행한다. 사용자의 실제 학번·이름을 채팅 답변에 불필요하게 반복하지 않는다.
