# UI review — 다항식 덧셈 인덱스

직접 본 캡처: evidence/ui/poly-add-index-1024-dark.png(사례 선택 "5차 + 3차"와 k 입력이 잘리지 않음), 작업 중 1440 light 25단계(degree_a 쓰기 강조, A 객체 칸 표시), cancel 마지막 단계(C.degree 2 · 최고차 계수 0 설명), evidence/browser/poly-add-index-375-light.png(모바일 2열 셀, 재생 바).
- 첫 수정본에서 사례 선택 상자 이름이 잘려("차수 5 + 3 (노…") 이름을 "5차 + 3차" 등으로 줄이고 전체 브라우저 검사를 다시 실행함.
- A, B, C 객체와 main 스칼라가 기호 주소(&A.degree (= &A))와 함께 표시. 읽기 점선·쓰기 강조 정상.
- 자동 검사: browser_acceptance 6조합 4554 Snapshot, browser_ui 6조합, browser_regressions 통과. 콘솔 오류·외부 요청 0.
