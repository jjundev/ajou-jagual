# Browser / visual review — array-stack

- `browser.json`: tests/browser_acceptance.py, file:// + offline=True, 외부 요청 0, 콘솔 오류 0. 1440×900·1024×768·375×812 × light/dark 6조합에서 기본·전체 preset의 모든 Snapshot을 슬라이더로 선택해 코드 줄·메모리 Cell 값이 Trace와 같은지, 입력 경계(-99/99)·빈 값 오류·재생 중 입력 변경·속도·자동 정지·선택·키보드·모바일 서랍을 확인. preview sha256은 browser.json의 값과 현재 preview.html이 같다.
- `ui.json`: tests/browser_ui.py 6조합 통과(토큰 배경·패널 접기/너비 조절·서랍 포커스·Escape·단계 목록·속도·보기 옵션·2D 확대). tests/browser_regressions.py 통과.
- 직접 본 캡처(`browser/`, `ui/`, `visual/`): 오류 예의 최종/진단 단계, 정상 흐름 중간 단계, 1024 폭, 375 폭 다크를 읽었다. 코드·메모리·설명 패널 겹침 없음, 화살표가 대상 Cell(노드 시작 Cell 또는 &s)로 향함, 진단 문구가 오른쪽 패널에 표시, 수명 종료 프레임은 흐린 점선으로 구별. 375 폭에서 모드 버튼은 단어 단위로 줄바꿈되고 뷰포트 안에 있다(긴 기호 레이블 `(s->top)++`를 `후위 ++`로 줄여 기호 중간 줄바꿈을 없앰).
- 공용 player.js의 코드 아래 안내문이 0928 문구("강의 swap 함수…")로 고정되어 있던 문제를 provenance.note로 대체 가능하게 고쳤고, 이 자료는 각 소스의 note를 표시함을 캡처로 확인. 스킬 node 테스트 27/27 통과(`node-tests.log`).
- 확인하지 못한 범위: 실제 Safari/Firefox, 실기기 터치, 스크린리더 음성 출력.
