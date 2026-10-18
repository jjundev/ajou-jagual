# UI review — factorial 호출 프레임

직접 본 캡처: evidence/browser/factorial-frames-1440-dark.png(6단계: f1 실행 중, main 대기, n-1 계산 읽기 점선), 작업 중 1440 light 22단계(f1~f4 프레임과 반환 칸 `factorial(3)` 등 "이름 없는 값 · 주소 없음" 표시), 375 nobase 마지막 단계(LIMIT_REACHED, 서랍 닫힘, 재생 바가 장면을 가리지 않음).
- 상단 모드 버튼 두 개(바닥 조건 있음/없음)가 1440·1024에서 한 줄, 375에서는 줄바꿈되어 뷰포트 안에 있음.
- 프레임 상태(실행 중/대기/수명 종료)와 미초기화 표시가 텍스트로 구별됨. 겹침·잘림 없음.
- 코드 패널 아래 보충 안내(빠진 ; 보충)가 보임.
- 자동 검사: browser_acceptance 6조합 3792 Snapshot, browser_ui 6조합, browser_regressions 통과. 콘솔 오류·외부 요청 0.
