# 교과서 연습문제 검수 기록

원본 14개 PDF, 44쪽 → 213문항, 새 SVG 46개. 원본 커밋: `9845996`.

## 확인 범위

- 원본 44쪽 전체를 시각적으로 읽고 직접 전사했다. macOS Vision OCR은 대조용 초안에만 사용했다.
- 전체 페이지 OCR 대조와 코드·수식·인쇄 표현 차이 검토를 수행했으며 판독 차이는 원본 확대 확인으로 정리했다. 책 쪽번호를 직접 확정할 수 없는 위치는 null이다.
- 모든 46개 SVG 전체 렌더링과 원본 구조를 확인했다. 원본 크롭·이미지 삽입은 없으며 필기와 정답 표시도 넣지 않았다.
- 별도 리뷰어는 도구 전체와 일부 원본(ch06 p02–03, ch10 p02, ch11 p02)을 확인했다. 전체 213문항의 독립 전사 검증을 주장하지 않는다.
- 리뷰에서 발견한 표 잘림, 가중치 겹침, Heigh의 조용한 교정, snapshot 검증과 inode rollback 결함을 재현 테스트 후 수정했다. figure/table 종류, counts, 내부 symlink, self-loop, CSS escape도 보강했다.
- 자동 회귀 테스트: 38 passed. PyMuPDF 바인딩의 5개 deprecation warning이 있었고 기능 실패는 없었다.
- 실제 브라우저 1280×900 및 375×812, 밝은 색·어두운 색에서 각 213 article / 46 image / 로딩 실패 0 / 문서 가로 넘침 0 / console error·warn 0을 확인했다.
- 어두운 색은 같은 HTML의 dark CSS media 조건을 강제한 임시 harness로 확인했다. OS 설정을 변경하지 않았고 OS media 자동 전환 자체는 직접 검증하지 않았다.
- 넓은 코드·그림·표는 내부 가로 스크롤을 사용한다. 원본 PDF·그림 상대 링크를 확인했다.

## 장별 집계

| 장 | 문항 | 보기 | 소문항 | 그림 | 표 |
|---|---:|---:|---:|---:|---:|
| 01 자료구조와 알고리즘 | 17 | 16 | 3 | 0 | 1 |
| 02 순환 | 21 | 12 | 5 | 1 | 1 |
| 03 배열, 구조체, 포인터 | 12 | 12 | 0 | 0 | 0 |
| 04 스택 | 16 | 24 | 0 | 1 | 0 |
| 05 큐 | 12 | 20 | 3 | 3 | 0 |
| 06 연결 리스트 I | 24 | 20 | 0 | 6 | 0 |
| 07 연결 리스트 II | 7 | 8 | 0 | 1 | 0 |
| 08 트리 | 22 | 32 | 11 | 8 | 1 |
| 09 우선순위 큐 | 17 | 20 | 7 | 3 | 0 |
| 10 그래프 I | 15 | 16 | 12 | 5 | 0 |
| 11 그래프 II | 10 | 0 | 0 | 4 | 1 |
| 12 정렬 | 21 | 24 | 13 | 6 | 3 |
| 13 탐색 | 9 | 8 | 9 | 1 | 0 |
| 14 해싱 | 10 | 12 | 7 | 0 | 0 |

전체 집계: `{"chapters": 14, "sources": 14, "pages": 44, "questions": 213, "assets": 46, "options": 224, "subquestions": 70, "figures": 39, "tables": 7}`

## 원문 오류·외부 참조

- ch02-q12 [source-error]: 인쇄 코드의 putchar()에는 인수가 없으며 unknown()에 반환형이 명시되어 있지 않다. 원문 그대로 보존했다.
- ch02-q18 [source-error]: 일반적인 정의와 다른 A(m−2, A(m, n−1))이 인쇄되어 있다. m−1로 교정하지 않았다.
- ch02-q19 [external-context]: 비교 대상 프로그램은 제공된 연습문제 PDF 밖의 본문에 있다.
- ch02-q20 [source-error]: 소문항 (2)의 “문제의 어떻게”는 인쇄 표현 그대로 보존했다.
- ch04-q15 [external-context]: 수정 대상 미로 탐색 프로그램은 연습문제 PDF 밖의 본문에 있다.
- ch05-q10 [source-error]: 다시 넣는 값이 F(b)로 인쇄되어 있어 그대로 보존했다.
- ch06-q17 [source-error]: 원문 그림의 C는 a1→b1→a2→b2→NULL만 보여 주어 본문의 전체 이동 설명과 다르다. 원본 그림의 마지막 NULL을 보존했다.
- ch06-q20 [external-context]: 본문의 다항식 덧셈 프로그램은 연습문제 PDF 밖에 있다.
- ch08-q09 [source-error]: 표 첫 열 제목은 “삭제연산알고리즘”으로 인쇄되어 있다. 탐색연산·삽입연산 행과 함께 원문대로 보존했다.
- ch10-q15 [source-error]: 인쇄 인접 리스트 정점 A의 세 항목은 B, C, C이다. 마지막 항목을 D로 교정하지 않았다. 또한 보기 목록은 제공된 PDF에 없다.
- ch11-q04 [external-context]: 수정 대상 Prim 함수는 연습문제 PDF 밖의 본문에 있다.
- ch11-q07 [external-context]: 재작성 대상 Dijkstra 함수는 연습문제 PDF 밖의 본문에 있다.
- ch11-q08 [external-context]: 수정 대상 최단 경로 함수는 연습문제 PDF 밖의 본문에 있다.
- ch11-q09 [external-context]: 수정 대상 최단 경로 함수는 연습문제 PDF 밖의 본문에 있다.
- ch12-q08 [source-error]: 인쇄 예시의 네 번째 행은 앞 행과 값의 순서가 다르고, 마지막 행에는 73이 두 번 있다. 계산 결과로 교정하지 않았다.
- ch12-q08 [external-context]: 수정 대상 퀵정렬 함수는 연습문제 PDF 밖의 본문에 있다.
- ch14-q08 [external-context]: 수정 대상 hash_lp_search 소스는 연습문제 PDF 밖의 본문에 있다.

위 항목들은 완전히 전사한 인쇄 내용 또는 외부 참조를 non-blocking으로 공개한 것이다. 미해결 판독 불가·그림 불완전 항목은 0이다. answer와 printed_answer는 전체 null이다. 별도 공식 정답지는 원본에 없다.

## 출처 SHA256

- `origin/01_자료구조와 알고리즘_연습문제.pdf`: `d1f78d5cb573eb820fca6587b0f8219bce91c7b31c063bf4c2c132e1c572d696`
- `origin/02_순환_연습문제.pdf`: `25167006c3fde12ae9b65da97a9e4cdea43503b3d0c21a43d92514e5ca99bc99`
- `origin/03_배열, 구조체, 포인터_연습문제.pdf`: `caebe288a03103bf164f7e7d078cf87cbc412a8f666e228a4033b2cd556b5833`
- `origin/04_스택_연습문제.pdf`: `f8f13f78bd19aa317bec82cc1a08186174794cc2eb9814ca834f58ec676548d4`
- `origin/05_큐_연습문제.pdf`: `d8b1c2126f374f944d951e395e13174d1f6cde570bcf09e3380ac99518696649`
- `origin/06_연결 리스트 I_연습문제.pdf`: `41b2e3a32f786d28a632a70ac67d5bd1f6944de04a3ee36e618b0a31e0f33d14`
- `origin/07_연결 리스트 II_연습문제.pdf`: `b0819a964e2b8e86840dd6a23b940d31df98ea0b58dc1c30d7198c71ea91ef2d`
- `origin/08_트리_연습문제.pdf`: `951979ea3c17e2d63af83e7500ec3e8f6e3f7f8a039694c63efa593bd3b288fb`
- `origin/09_우선순위 큐_연습문제.pdf`: `4eaa7209c2874c6231010311bfa03e8046bb97e85fdf2307e58edbc6818c063c`
- `origin/10_그래프 I_연습문제.pdf`: `26792225682327af734a4e1befb7c50c50eda7120fcc32f0da6137971b203171`
- `origin/11_그래프 II_연습문제.pdf`: `61767ed623fd04cef4e298920d82e12b8e30bcea12a2da354e3732abc8ef7e10`
- `origin/12_정렬_연습문제.pdf`: `d4bc3d85c2dd91034d3760301fd6b51197fb5702039852e8acaf2cb0bcbaa7bc`
- `origin/13_탐색_연습문제.pdf`: `c2bd6883a1e3b26bfee93619df6a9a87e620e806e4b7653f20aa03ac15705dc5`
- `origin/14_해싱_연습문제.pdf`: `84e7b37b40a9733bed64fab57d328ae84b27ca37768f8fd68c64e8f7640d447c`

## 생명과학 참고 범위

원문·관찰 분리, 직접 SVG, 현재 바이트와 검토 연결, 검증 후 독점 확정 원칙을 참고했다. 단일선택형·평가일·배점·정답 필드는 가져오지 않았고 런타임 import도 없다.

- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/.agents/skills/web-quiz-extract/SKILL.md`: `19b2155c2555b79f460832d9fcf7485b8112f7d54795f5945fee874129299838`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/scripts/question_bank/model.py`: `37c0c3d4117108e3dadf5be4798945c7347503ef5a6b9ca884ce348c9dce2f92`
- `/Users/hyunjun_macbook_pro/Documents/Univ/생명과학/scripts/question_bank/svg.py`: `eccf99fd171a64de0e98c706b480d2fbeeb7d74724d650adef0cafa5f27cda80`

## 실행 중 결정

- 후보 package에서 도구와 데이터를 격리했다. 원본과 계획이 untracked이고 기존 추적 코드를 수정하지 않아 Git worktree 대신 후보 폴더를 사용했다. 잘못된 경우 후보 도구의 작업 위치를 이동해야 한다.
- 검증 도구와 회귀 테스트도 제작자료에 포함했다. 후보에서 구현했기 때문에 데이터와 함께 독점 생성한다. arbitrary scratch는 제외한다. 잘못된 경우 도구·테스트 경로를 별도로 재배치해야 한다.
- 어두운 색은 위에 명시한 CSS harness로 검수했다. 한계는 OS media 자동 전환이 직접 검증되지 않았다는 점이다.
- 작업용 원본 렌더·전사·실행 환경은 tmp/textbook-exercises에 보존하고 Git 로컬 exclude로 제외했다. 최종 자료에는 임시 크롭을 넣지 않았다. 비용은 임시 디스크 사용이다.

최종 게시 후 JSON·SVG·inventory·model·preview 동일 바이트와 완성도 검사를 다시 실행한다.

게시 후 확인: 최종 위치에서 --complete PASS(14장·14출처·44쪽·213문항·46자산), 38 tests passed, 후보/최종 fingerprint 동일, 브라우저 최종 213 article·46 image·221 source links·로딩 실패 0·넘침 0. 원본 커밋 blob의 SHA256도 14개 모두 초기 source SHA256과 같다.

## 2026-10-12 장별 파일 구조 전환

최종 데이터는 `[NN]_<장 제목>_연습문제.json` 14개다. 분할 전 후보와 장별 파일을 합친 데이터의 전체 필드·순서가 일치하고, 기존 패키지 검토 해시도 동일한 데이터·그림·미리보기 바이트로 재현됨을 확인했다. 전체 미리보기는 재생성 결과와 동일하며 변경하지 않았다. 원문·SVG·브라우저 검토 기록은 유지했다. `verification.json`의 `chapter_split`에 이전 패키지 해시와 파일 목록을 기록하고 현재 장별 배포 파일을 기준으로 패키지 해시를 갱신했다.

검증·미리보기·자산 생성 CLI는 교과서 폴더를 인자로 받고, 배포 도구는 지원 자료와 SVG 다음에 장별 JSON 14개를 복사한다. 통합 파일은 저장하지 않는다. 장별 잘못된 파일명·소속 장·출처·그림 참조·중복 ID, 변경 감지, 배포 실패 정리와 덮어쓰기 거부를 회귀 테스트로 확인한다.

장별 전환 후 재검증: `validate.py .. --complete` PASS, 전체 테스트 46개 통과. PyMuPDF의 SWIG 타입에서 DeprecationWarning 5건이 발생했다. 실제 임시 목적지 배포·패키지 재검증·미리보기 재생성 결과가 최종 파일과 동일함을 확인했다.
