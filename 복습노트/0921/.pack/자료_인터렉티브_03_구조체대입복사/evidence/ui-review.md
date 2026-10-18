# UI review — 구조체 대입

직접 본 캡처: evidence/browser/struct-assign-copy-1024-dark.png(b = a 6단계, b.height 미초기화 → 170), 작업 중 1440 light link 12단계(n1.link·c.link 두 화살표가 같은 n2.data를 가리킴, c.link 셀 점선 읽기 표시, n2.data 쓰기 강조).
- 상단 모드 버튼 세 개가 1024·1440에서 한 줄로 뷰포트 안. 입력 레이블 "첫 값 (a.age · n1.data)"이 두 줄로 줄바꿈되지만 겹치지 않음.
- copy 모드에서 main() 열은 a, b가 객체 열로 따로 그려져 비어 보이지만 정보 누락은 아님.
- 오른쪽 패널 제목 "c.link->data"가 Pretendard 합자로 화살표처럼 보이지만 코드 줄은 `->` 그대로(공통 폰트, 수정하지 않음).
- 자동 검사: browser_acceptance 6조합 474 Snapshot, browser_ui 6조합, browser_regressions 통과. 콘솔 오류·외부 요청 0.
