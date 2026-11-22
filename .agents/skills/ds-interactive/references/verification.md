# 검토·저장 계약

RUN은 고유한 작업 디렉터리다. scenario.cjs,source.json,brief.md,trace.json,preview.html과 evidence/를 준비한다. 파일을 바꾸면 그에 영향을 받는 판정을 다시 수행한다.

`review.cjs` exports createReview/currentHashes/readReview/verifyReview. createReview(RUN)는 version1, 현재 SHA-256 맵, 네 개의 not_run을 반환한다. 자동 content/independent/browser 합격 기능은 없다. 실제 확인 후 JSON에 판정·증거·notes와 현재 해시를 함께 기록한다.

각 check는 `{status:'not_run'|'pass'|'fail'|'disputed',evidence:'evidence/파일',notes:'실제 관측한 이유'}`다. schema: 구조·기본/모든 preset. content: 코드 줄·중간 복사/읽기/쓰기·설명 원문 대조. independent: 엔진을 호출하지 않는 계산표 또는 실제 C 관찰과 비교. browser: 실제 브라우저 상호작용·시각 검토. 모두 pass여야 저장한다. 증거는 RUN 안의 해시 대상 파일이며 비어 있을 수 없다.

해시 대상은 scenario.cjs,source.json,source.c(있는 경우),brief.md,trace.json,preview.html,evidence/ 전체다. note-links.json은 발행 번호 치환용 매니페스트이므로 별도다. review.json 자신은 자기 해시를 갖지 않는다. evidence에 심볼릭 링크를 넣지 않는다. 공개 페이지와 preview는 각 위치에서 같은 공용 Pretendard를 가리키며, 그 상대 경로 외에는 바이트가 같아야 한다.

브라우저 자동 검사:

```
python "S/tests/browser_acceptance.py" "REPO / 날짜폴더 / RUN / HTML파일" "빈 SCRATCH"
```

자료 한 개부터 여러 개까지 검사한다. REPO는 모든 날짜의 공개 자료를, 날짜폴더는 해당 공개 HTML을, RUN은 preview를 찾는다. 특정 범위만 검사하려면 해당 폴더/파일을 넘긴다. 발행본과 보관용 preview의 일치, 해당 절에서 링크를 눌렀을 때 같은 탭에 정확한 파일이 열리는지, 뒤로 가면 원래 절로 돌아오는지는 다음 명령으로 확인한다. 1105의 중위 순회 링크는 Chromium 데스크톱과 모바일 터치 에뮬레이션에서 검사한다. 날짜를 생략하면 기존 0928 자료와 링크를 검사한다.

```
python "S/tests/final_paths.py" "REPO" "SCRATCH/final-paths-1105.json" --date 1105
```

실제 Chromium, file://, offline=True, 외부 HTTP 차단. 1440×900/1024×768/375×812 각각 light/dark, 기본·모든 preset과 각 단계, 재생 중 사례 전환, 속도·자동 정지·선택·키보드·모바일 서랍을 검사한다. 정수 입력 예제는 입력 경계와 빈 값도 확인한다. 콘솔·외부 요청·문서 가로 넘침은 0이어야 한다. 스크린샷을 직접 읽어 겹침·화살표·글씨 크기도 확인한다. HTTP 대체 시 미확인 범위를 적는다.

save.cjs RUN DEST NAME: 이름과 현재 검토 해시 확인 → 번호와 디렉터리 exclusive 예약 → 근거와 검토 bytes 복사 → 다시 해시 검증 → 두 위치의 글꼴 상대 경로 조정과 보관용 preview 해시 갱신. 보관본 review의 `reviewed_preview_sha256`에 검토 당시 RUN의 해시를 남긴다. 충돌은 새 번호, 실패는 자신이 생성한 경로만 복구한다. 공개 파일 또는 자료 폴더 하나만 있어도 덮어쓰지 않는다. NN은 최소 두 자리다. 자동 커밋·푸시·외부 게시하지 않는다.

## 트리 순회 검산

1105 예제는 `python3 "S/tests/inorder_oracle.py" "RUN/trace.json"`으로 호출·조건 검사·출력·반환을 실제 C 실행과 비교한다. C 포인터를 입력의 노드 ID에 대응시키고, 부모와 좌우 가지, 인자 Cell, 반환 뒤 호출자와 수명, 최종 stdout을 확인한다. 학습 화면에서는 왼쪽 NULL 진입 → 호출자의 출력 줄 → 키 출력, 오른쪽 NULL 진입 → 호출자의 닫는 중괄호를 직접 대조한다.

브라우저는 `c-tree`에서 각 단계의 실행 코드 위치, 선택된 기록 행과 설명, 활성 프레임, 출력과 트리 배치를 대조한다. 데스크톱과 모바일에서 0단계는 맨 위, 이후 단계는 가운데인지 확인한다. 데스크톱의 좌우 독립 토글, 드래그·키보드로 바꾼 너비의 새로고침 후 복원, 기본 너비 복원과 창 너비에 따른 중앙 400px 확보, 모바일에서 두 서랍을 닫은 초기 배치와 한쪽씩 열기, 다시 열었을 때 바로 보이는 줄 기록과 현재 행의 위치, 트리 직하단의 누적 출력을 확인한다. 좌우 NULL 복귀, 왼쪽 패널을 닫았을 때 설명 갱신, 수동 탐색과 자동 추적 재개, 출력 되감기, 노드 메모리, 호출 수명, 서랍 포커스와 너비 전환도 확인한다. 재생 바에서 팝업으로 마우스를 옮겨도 열린 상태를 유지하는지, 재생 중 배속 전환, 터치와 키보드 열기 및 닫기도 확인한다. 스크린샷에서 세 행의 가독성과 설명·트리의 간격을 검토한다. 모바일 첫 화면에서 트리·출력·재생 바를 확인하고, 짧은 화면에서 장면 스크롤로 나머지 내용에 접근하는지 확인한다.

## 공통 셸 UI 회귀

`python "S/tests/browser_ui.py" "RUN / 날짜폴더 / HTML파일" "SCRATCH"`로 공통 UI를 검사한다. 토큰 배경색·패널 접기·너비 키보드 조절·서랍 포커스·Escape/닫기·전체 단계 선택·속도 선택과 보기 옵션을 확인한다. 2D 확대는 포인터 자료에서 확인한다. 단계 실행의 의미와 독립인 보기 상태를 따로 검사한다. 주소와 화살표 옵션은 포인터 자료에서 확인한다. 포인터 자료의 정수 입력·Cell 포커스 회귀는 `browser_regressions.py HTML`로 확인한다. 화면의 실제 경계가 뷰포트를 넘지 않아야 한다. overflow:hidden으로 잘림을 숨긴 결과를 합격시키지 않는다.

## 명시적으로 요청받은 기존 자료 수정

신규 생성은 save의 덮어쓰기 금지를 유지한다. 사용자가 기존 자료 수정을 요청한 경우에는 해당 HTML과 전체 pack을 별도 고유 작업 폴더에 먼저 백업한다. 복사한 pack의 scenario로 새 preview를 빌드하고, 변경된 UI의 브라우저·시각 증거와 현재 schema/독립 검산을 갱신한다. 내용이 그대로면 scenario/trace/source의 기존 해시 일치와 내용 검토 근거를 확인한다. 수정된 preview에 과거 browser 증거만 붙여 합격 처리하지 않는다.

모든 증거를 확정한 뒤 review 해시를 다시 계산하고 check를 통과시킨다. 교체 직전 대상이 백업 시점과 같은지 확인하고, 같은 HTML 경로와 대응 pack을 갱신한다. 실패하면 이번 교체분만 백업으로 복원한다. 최종 HTML과 pack/preview가 같은 공용 글꼴을 가리키고 상대 경로 외의 바이트가 같은지, review가 유효한지 확인한다. 정리노트와 관련 없는 pack은 바꾸지 않는다. 링크는 그대로 왕복 확인한다. 검증 보고서에 백업 위치·대상 해시·실제 확인 범위를 남긴다.
