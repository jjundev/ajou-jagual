# ds-interactive 생명과학 UI 일치 검증 — 2026-10-17

사용자가 승인한 설계와 후속 지시(글꼴·서식도 동일)에 따라 공통 스킬과 기존0928 HTML3개를 같은 파일명으로 갱신했다. 코드는 왼쪽, 메모리는 중앙, 설명은 오른쪽이다. 생명과학 저장소는 수정하지 않았다. 신규 생성 save의 덮어쓰기 금지는 유지하며, 명시적인 기존 자료 수정만 백업·재검증 후 갱신한다.

## UI·서식

생명과학 `bio-interactive/assets/template.dc.html`의 현재 CSS와 테마·치수를 기준으로 Native DOM 셸을 구현했다. 원본 해시는 스킬 assets/vendor/provenance.json에 기록했다. 상단 SVG 토글·모드·테마, 좌우 접기/너비 조절, 단계 목록, 하단 재생/속도, 모바일 단일 서랍/가림막/포커스/닫기를 적용했다. 메모리는 기존2D DOM/SVG를 사용한다. 긴 모드 이름은 모바일에서 같은14px 글꼴로 줄바꿈한다.

생명과학 builder는 `pretendard@1.3.9` static CSS를 참조한다. 동일 버전의 로컬 Pretendard를 HTML에 내장했다. font name table의 Version1.309와 실제 OS/2 굵기400/500/600/700을 확인했다. Regular 하나를 가변 굵기로 등록하던 방식을 실제 Regular/Medium/SemiBold/Bold로 바꿨다. OFL도 함께 포함했다. 코드·주소만 고정폭 글꼴이다.

| 공통 요소 | 실제 computed style |
|---|---|
| 본문 | Pretendard, 16px / 400 / 행간25.6px |
| 상단 제목 | 17px / 700 / 행간27.2px |
| 절 제목 | 19px / 700 / 행간26.6px |
| 현재 설명 | 15px / 400 / 행간24px |
| 꼭 기억해요 본문 | 15px / 400 / 행간25.5px |

각 HTML은 약4.23MB이며 폰트·CSS·JS가 모두 포함된다. 폰트4종의 실제 loaded 상태와 computed style을 UI18조합에서 검사했다.

## 실행 결과

- Node 스킬 테스트27/27 통과: `node-tests.log`. 실제 폰트4종 등록 회귀 포함.
- 독립 Python 검산38조건·144 bind/write 통과: `independent.json`. C 컴파일러는 없으므로 C 실행 검증을 주장하지 않는다.
- 실제 Chromium 오프라인 전체 실행18조합·852 Snapshot 통과: `browser.json`. 모든 preset, 코드 줄, Cell 값, 단계, 입력 경계/빈 값, 재생 중 편집, 속도, 자동 정지, 선택, 키보드 확인. 외부 요청0·콘솔 오류0.
- UI18조합 통과: `ui.json`. 1440×900/1024×768/375×812 각각 light/dark. 패널/너비 조절/재개방/모바일→데스크톱 전환, 중앙 최소320px, 실제 화면 경계, 서랍 포커스와 Escape/닫기, 전체 단계 선택, 보기 옵션, 2D 확대 확인.
- 최종 공개3파일과 pack/preview 바이트 일치, 최종 파일 재생·폰트, 노트4곳 현재 탭 이동/뒤로가기 통과: `final-paths.json`.
- 원본 엔진/예제/scenario/trace/정리노트13개 사전 해시 보존: `preservation.json`. 재연결 dry-run은 changed:false: `relink.json`.
- 최종3개 pack의 review 현재 해시 및 네 검사(schema/content/independent/browser) 모두 pass. 스킬 quick_validate와 git diff --check 통과.

최종 캡처는 각 pack의 evidence/browser와 evidence/ui에 있다. 데스크톱/모바일/1024·라이트/다크의 대표 캡처에서 글꼴·클리핑·화살표·재생 바를 직접 확인했다. 생명과학 실제 file:// 화면 열기는 브라우저 정책으로 차단되어 우회하지 않았고 원본 CSS로 대조했다. 생명과학 화면과의 실브라우저 픽셀 일치나 다른 브라우저/실기기/스크린리더까지 검증했다는 주장은 하지 않는다. 저장소 전체 pytest는 이번 UI 범위에서 재실행하지 않았다.

## 회귀와 리뷰

1. 기존 화면에서 missing biology topbar 실패를 먼저 확인했다.
2. overflow:hidden이 숨긴 모바일 min-content 클리핑을 실제 stage/header 경계 검사로 재현하고 수정했다.
3. -99/99/빈 값/사례 초기화 후 숫자 blur가 재생 클릭을 삼키는 현상을 재현했다. 동일 값 input/change 중복 처리를 막아 회귀 통과했다.
4. 실제 font-face400 누락과 상단 제목 행간 차이를 각각 RED→GREEN으로 확인했다.
5. 새 컨텍스트 gpt-6-astra 최종 리뷰에서 Important1건(한쪽 패널 확대 후 반대편 재개방 시1024px 밖으로 밀림)을 받았다. 실제 경계 RED→GREEN 후 전체 테스트를 재실행했다. 재개방·반응형 전환 모두 중앙320px를 보존하도록 조정했다. Critical/미해결 Minor 없음.
6. 리뷰어는 코드 내부 스크롤, 1.8배 확대의 포인터 양 끝 좌표(2px 이내), destroy 이후 resize/타이머 정리도 확인했다. 최종 해시·전달·링크는 위 executor 검증으로 마쳤다.

## 진행 중 판단

- Windows에서 사용할 수 없는 Bash 래퍼 대신 PowerShell/Python으로 계획·수동 장부를 기록했다. 비용: 수동 기록 관리.
- 동일 UI가 기준이므로 생명과학 원본의 패널 width transition을 유지했다. detector의 layout-transition 경고2건은 이 동작이다. 비용: 짧은 접기 애니메이션 동안 레이아웃 계산. reduced-motion에서는 제거된다.
- 굵기와 오프라인 표시를 함께 보존하기 위해 실제 폰트4종을 포함했다. 비용: HTML이 기존 약1.06MB에서 약4.23MB로 커졌다.
- 커밋/푸시 없이 기존 워크트리와 백업 작업 폴더를 유지했다. 비용: 로컬 백업 공간. 백업은 `.superpowers/sdd/2026-10-17-ds-ui/backups/`에 기존 HTML3개와 전체 pack3개가 있으며 전달 전 모든 기존 바이트가 백업과 같은지 검사했다.

파일별 최종 SHA-256·크기·백업 위치는 delivery.json에 있다. 커밋·푸시·외부 게시 없음.
