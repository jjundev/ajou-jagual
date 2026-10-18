# Browser/visual review

자동 검사: browser_acceptance.py(실제 Chromium, file://, offline, 외부 요청 차단; 1440×900/1024×768/375×812 × light/dark, 기본·모든 preset·모든 Snapshot의 렌더 Cell 값과 Trace 대조, 코드 현재 줄, 입력 경계 -99/99·빈 값, 재생 중 입력, 속도, 자동 정지, 셀 선택, 키보드, 모바일 서랍), browser_ui.py(공통 셸 토큰·글꼴 400/500/600/700·패널·서랍·확대), browser_regressions.py. 결과는 browser.json, ui.json, browser-runs.log. 콘솔 오류 0, 외부 요청 0, 가로 넘침 0.

시각 확인: browser/·ui/의 1440·1024·375 light/dark 캡처와 주요 사례 최종 단계 캡처를 직접 읽었다. 패널·재생 바·메모리 카드 겹침 없음, 포인터 화살표가 실제 대상 카드로 이어짐, 수명 종료 카드는 흐리게 텍스트로 구분, 코드 아래 출처 안내가 자료별 문구로 표시됨(공통 기본 문구 "강의 swap 함수" 노출 문제를 provenance.note로 수정 후 재빌드). 375px 모드 버튼 줄바꿈이 어색해 라벨을 줄인 뒤 재검사했다(삭제 자료).

미확인 범위: 실제 모바일 기기·터치 제스처, Safari/Firefox, 스크린리더 음성 출력은 확인하지 않았다.
