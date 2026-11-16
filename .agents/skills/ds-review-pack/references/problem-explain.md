# 최종 복습문제의 문제설명 연결

복습팩의 문제설명 담당자용이다. 모드·시작 시점·발행 담당은 [후속 작업](pack-followups.md)을 따른다. EXPLAIN_SKILL은 저장소의 `.agents/skills/ds-problem-explain` 절대 경로이고 ABS_CLI는 그 `scripts/mpe_cli.py`다.

검증·발행·MD 변환이 끝난 복습문제 JSON 원고의 절대 경로를 ABS_REVIEW로 받는다. REPO는 저장소 절대 경로, EXPLAIN_RUN은 팩마다 다른 비어 있는 작업 폴더다. 미해결 검사나 0문항 팩은 발행 대상에서 제외한다. backfill은 발행된 문항 원고를 입력으로 쓰며 update-existing all을 실행하지 않는다.

1. EXPLAIN_SKILL/SKILL.md와 references/authoring.md, references/verification.md를 읽고 저작·검증을 실제 적용한다. 이 호출의 범위는 작업본까지다. 형제 스킬의 발행 단계는 이 호출의 메인이 담당한다.
2. Python 3.10+로 `python3 ABS_CLI extract --repo ABS_REPO --target ABS_REVIEW --run EXPLAIN_RUN`을 실행한다. 모든 ABS 자리는 실제 절대 경로다. 날짜·최신 팩 선택에 맡기지 않는다.
3. source.json의 전체 문항·소문항을 읽고 원 기출·교과서·강의록·정리노트 관련 페이지를 실제로 대조한다. explanations/pN.html에 모든 문항의 일곱 구역과 요약을 저작한다. CLI는 설명을 자동 저작하지 않는다.
4. 독립 실행·시뮬레이션·논증으로 모든 소문항을 검산하고 evidence에 저장한다. 원자료 충돌·UB·비종료·모호함은 disputed로 보류한다.
5. `python3 ABS_CLI build --run EXPLAIN_RUN`과 `python3 ABS_CLI check --run EXPLAIN_RUN`을 실행한다. build는 검토를 not_run으로 초기화한다. machine PASS는 정답·실화면 승인과 다르다.
6. `python3 ABS_CLI preview --run EXPLAIN_RUN`이 출력한 로컬 URL을 열고 현재 stage에 대해 source_visual/content/independent/browser를 실제 수행해 review.json에 기록한다. references의 절대 경로·현재 SHA-256, 모든 소문항, artifact_hashes를 대조한다. 테스트의 approved()나 합성 브라우저 결과를 실제 승인에 사용하지 않는다. lite도 생략하지 않는다. 1280×900·375×812의 light/dark에서 전체 문항·목차·pager·요약·수식·코드·그림·링크를 확인한다. 원 문제·개념 링크는 발행 폴더 기준으로 실제 대상 파일을 열어 앵커를 대조한다. 콘솔·KaTeX 오류·누락 자원·외부 요청·문서 overflow는 0이어야 한다. 끝나면 서버를 종료한다.
7. 네 실제 검토가 통과하면 `ready`와 EXPLAIN_RUN·review.json 경로를 메인에게 반환한다. 검토가 미해결이면 `withheld`와 이유를 반환한다. 원본이 바뀌면 extract부터, 조각이나 stage가 바뀌면 build와 전체 검토부터 다시 한다.

담당자의 쓰기는 EXPLAIN_RUN 안으로 제한한다. 메인만 [후속 작업](pack-followups.md)에서 발행하며, 발행기는 설명 소유 파일만 백업·교체한다. 과거 제작자료의 validation.json과 기본 팩을 보존한다. 정리노트·복습문제에 링크를 삽입하지 않는다. 별도 backfill 요청에서는 발행된 문항 원고를 입력으로 해 같은 작업본·검토 절차를 수행하며, 호출 메인이 발행한다. backfill에 update-existing all을 호출하지 않는다.

## 강의 예제·전역 검토 연동

신규·update-existing·revise-existing은 [공통 개편·검증 계약](review-overhaul.md)을 함께 적용한다. lecture-code는 실제 강의 페이지·해시·학습 근거와 자체 질문을 구분한다. 전체 날짜 audit를 통과하고 발행된 정확한 JSON 경로를 해설 입력으로 사용한다. update-existing의 기존 카드 보존 계약은 유지한다.
