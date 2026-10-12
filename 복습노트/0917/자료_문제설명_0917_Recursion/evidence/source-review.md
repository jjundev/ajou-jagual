# 원자료 대조와 내용 검토

검토자: Codex (원자료 읽기와 별도 내용 검토 pass).
source-locators.json의 실제 원 기출·교과서 페이지와 현재 조건·보기·소문항·코드·그림을 대조했다. 교과서 스캔 페이지는 PNG로 렌더링하여 직접 읽었다. 강의록의 관련 페이지 텍스트와 실제 정리노트를 대조하여 factorial 바닥 n<=1, 배열 0-based, 스택 top=-1과 FIFO/LIFO를 확인했다. HWP 기출은 로컬 OLE BodyText를 읽었으며 외부 업로드를 하지 않았다. 은행의 참고 답은 검산을 대신하지 않았다.

설명은 모든 문항의 understand/recall/start/solve/verify/pitfall/retry와 요약을 포함한다. 원문 변형 카드는 현재 카드 상수로 계산한다. 0914 p2의 literal i++는 정상 종료/유한 시간 복잡도 승인 대상이 아니며, 리뷰가 명시한 k++ 가정의 조건부 답과 구분했다. recursive 결함 찾기는 결함을 판단한 설명이지 위험 코드의 정상 답 승인이 아니다. 1012 p6은 유효·길이 제한·overflow 없는 입력의 빈칸 답이며 원 오류 분기 보장과 추가 안전 검산을 구분한다. 1012 p2의 서로 다른 입력 두 가지와 괄호 번호 출력의 미닫힘 사례를 각각 설명했다.

independent-results.json은 정의·불변식·별도 시뮬레이션과 실제 C11/ASan/UBSan 실행에 따른 검토 결과이다. proof의 일반 근거는 공약수 집합 보존, 감소량, prefix invariant, 삼각수 항의 짝짓기 또는 임의 미방문값 반례이며 숫자 예제를 증명으로 대신하지 않았다. source_visual/content는 작성 후 별도 읽기 검토, independent는 참고 답 대신 독립 계산이다. 브라우저의 실제 현행 stage 재검증은 browser-frozen/results.json에 기록한다.
