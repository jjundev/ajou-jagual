# 최종 복습문제의 문제설명 연결

bank는 이 절차를 실행하지 않는다. 신규·update-existing·lite는 모두 전체 절차를 실행한다. 생성 시작 전에 EXPLAIN_SKILL = SKILL의 형제 ds-problem-explain 절대 경로로 정하고 SKILL.md와 scripts/mpe_cli.py 존재를 확인한다. 누락 시 경로와 오류를 보고하며 시작하지 않는다.

검증·발행·MD 변환이 끝난 최종 복습문제 HTML의 절대 경로를 ABS_REVIEW로 받는다. REPO는 저장소 절대 경로, EXPLAIN_RUN은 팩마다 다른 비어 있는 작업 폴더다. 미해결 기계·내용·브라우저 검사나 0문항 팩은 발행하지 않는다. backfill은 기존 HTML만 입력으로 쓰며 update-existing all을 실행하지 않는다.

1. EXPLAIN_SKILL/SKILL.md와 references/authoring.md, references/verification.md를 읽고 해당 스킬을 실제 적용한다.
2. Python 3.10+로 `python3 ABS_CLI extract --repo ABS_REPO --target ABS_REVIEW --run EXPLAIN_RUN`을 실행한다. 모든 ABS 자리는 실제 절대 경로다. 날짜·최신 팩 선택에 맡기지 않는다.
3. source.json의 전체 문항·소문항을 읽고 원 기출·교과서·강의록·정리노트 관련 페이지를 실제로 대조한다. explanations/pN.html에 모든 문항의 일곱 구역과 요약을 저작한다. CLI는 설명을 자동 저작하지 않는다.
4. 독립 실행·시뮬레이션·논증으로 모든 소문항을 검산하고 evidence에 저장한다. 원자료 충돌·UB·비종료·모호함은 disputed로 보류한다.
5. `python3 ABS_CLI build --run EXPLAIN_RUN`과 `python3 ABS_CLI check --run EXPLAIN_RUN`을 실행한다. build는 검토를 not_run으로 초기화한다. machine PASS는 정답·실화면 승인과 다르다.
6. 현재 stage에 대해 source_visual/content/independent/browser를 실제 수행해 review.json에 기록한다. references의 절대 경로·현재 SHA-256, 모든 소문항, artifact_hashes를 대조한다. 테스트의 approved()나 합성 브라우저 결과를 실제 승인에 사용하지 않는다. lite도 생략하지 않는다. 1280×900·375×812의 light/dark에서 전체 문항·목차·pager·요약·수식·코드·그림·링크를 확인한다. 콘솔·KaTeX 오류·누락 자원·외부 요청·문서 overflow는 0이어야 한다. 끝나면 서버를 종료한다.
7. 네 실제 검토가 pass이면 `python3 ABS_CLI publish --run EXPLAIN_RUN`을 실행하고 최종 경로·현재 source hash·전체 문항 ID·원본 보존을 다시 확인한다. 원본이 바뀌면 extract부터, 조각이나 stage가 바뀌면 build와 전체 검토부터 다시 한다.

결과는 published 또는 withheld와 이유, HTML(날짜 폴더 루트)/MD(`.pack/`), EXPLAIN_RUN, 백업 경로로 보고한다. 실패 시 검증된 원 복습팩과 이전 해설을 보존하며 “복습팩 생성됨 / 문제설명 보류”로 보고한다. 독립된 다른 팩은 계속 처리한다. 설명 소유 파일만 백업·교체하며 과거 제작자료의 validation.json은 변경하지 않는다. 정리노트·복습문제에 링크를 삽입하지 않는다. 커밋·푸시는 별도 요청이 있을 때만 수행한다.

## 강의 예제·전역 검토 연동

신규·update-existing·revise-existing은 [공통 개편·검증 계약](review-overhaul.md)을 함께 적용한다. lecture-code는 실제 강의 페이지·해시·학습 근거와 자체 질문을 구분한다. 최종 전체 날짜 audit를 통과한 정확한 최종 HTML 경로만 설명·PDF 입력으로 사용한다. update-existing의 기존 카드 보존 계약은 유지한다.
