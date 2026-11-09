# 1109 문항 원문 (메인 에이전트 작성)

## 2015-ljw-q4  (manifest id p1, variant false)
- 원본: 2015 미상 4번 · 10점 · 이정원 — 자료구조및알고리즘이해 기출 소스/자료구조및알고리즘 2015기출(이정원).pdf
- 문제 글: 4. 다음과 같은 순서의 숫자가 하나씩 입력된다고 할 때, 각각에 답하시오. (10 점)
15, 16, 18, 17, 19, 20, 12
1) Max Heap을 구성하라. (요소 하나씩 삽입되면서 어떻게 upheap되는지 보이시오.)

2)에서 구성된 Max Heap을 이용하여 힙정렬하시오. (반드시 단계별로 7개의 요소가 제거되면서 정렬되는 모습을 보이시오.)
- 그림: 없음
- 은행 정답: 1) 삽입마다 배열(레벨 순서): [15] → [16,15] → [18,15,16] → [18,17,16,15] → [19,18,16,15,17] → [20,18,19,15,17,16] → [20,18,19,15,17,16,12]
2) 삭제마다 남은 힙(레벨 순서): 20 제거 → [19,18,16,15,17,12] / 19 제거 → [18,17,16,15,12] / 18 제거 → [17,15,16,12] / 17 제거 → [16,15,12] / 16 제거 → [15,12] / 15 제거 → [12] / 12 제거 → [].
제거 순서 20, 19, 18, 17, 16, 15, 12 → 정렬 결과 12, 15, 16, 17, 18, 19, 20 (key)
- 변형 값: 없음
- 전사 기록:

4. 다음과 같은 순서의 숫자가 하나씩 입력된다고 할 때, 각각에 답하시오. (10 점)
15, 16, 18, 17, 19, 20, 12
1) Max Heap을 구성하라. (요소 하나씩 삽입되면서 어떻게 upheap되는지 보이시오.)

2)에서 구성된 Max Heap을 이용하여 힙정렬하시오. (반드시 단계별로 7개의 요소가 제거되면서 정렬되는 모습을 보이시오.)

**원본 답:** 1) 삽입마다 배열(레벨 순서): [15] → [16,15] → [18,15,16] → [18,17,16,15] → [19,18,16,15,17] → [20,18,19,15,17,16] → [20,18,19,15,17,16,12]
2) 삭제마다 남은 힙(레벨 순서): 20 제거 → [19,18,16,15,17,12] / 19 제거 → [18,17,16,15,12] / 18 제거 → [17,15,16,12] / 17 제거 → [16,15,12] / 16 제거 → [15,12] / 15 제거 → [12] / 12 제거 → [].
제거 순서 20, 19, 18, 17, 16, 15, 12 → 정렬 결과 12, 15, 16, 17, 18, 19, 20

## 2017-final-kdh-q1  (manifest id p2, variant false)
- 원본: 2017 기말 1번 · 20점 · 김도희 — 자료구조및알고리즘이해 기출 소스/자료구조및알고리즘_기말고사 (모범답안), 2017 김도희.pdf
- 문제 글: 1. 최대 히프 트리(max heap)를 구성하기 위해서 다음 숫자들을 차례대로 이용하시오. [20 points]

16, 28, 41, 20, 25

(a.) 위의 숫자들로 구성된 최대 히프 트리를 그리시오.[5 points]

(b.) 위의 (a)에서 구성된 최대 히프 트리에 30를 삽입한 결과로 만들어지는 최대 히프 트리를 그리시오.[5 points]

(c.) 위의 (b)에서 구성된 최대 히프 트리에서 최대값을 제거한 결과로 만들어지는 최대 히프 트리를 그리시오.[5 points]

(d.) 위의 (c)에서 구성된 최대 히프 트리를 배열로 구현하시오. [5 points]

[그림: 첨자 [0]~[12]의 빈 배열 칸]
- 그림: 최대 히프 트리 답 그림 3개와 첨자 [0]~[12] 배열 칸
- 은행 정답: (a) 레벨 순서: 41 / 25, 28 / 16, 20 (41의 자식 25·28, 25의 자식 16·20). 배열: [41, 25, 28, 16, 20]
(b) 레벨 순서: 41 / 25, 30 / 16, 20, 28 (30의 왼쪽 자식 28). 배열: [41, 25, 30, 16, 20, 28]
(c) 레벨 순서: 30 / 25, 28 / 16, 20. 배열: [30, 25, 28, 16, 20]
(d) [0] 비움, [1]=30, [2]=25, [3]=28, [4]=16, [5]=20, [6]~[12] 비움
* 최대 히프 트리의 배열구현에서 루트노드는 첨자 1에서 시작해야 하며 그래야 부모노드와 자식노드가 서로를 찾는 관계가 정확히 이루어짐. 첨자 0에서 시작하면 감점. (key)
- 변형 값: 없음
- 전사 기록:

1. 최대 히프 트리(max heap)를 구성하기 위해서 다음 숫자들을 차례대로 이용하시오. [20 points]

16, 28, 41, 20, 25

(a.) 위의 숫자들로 구성된 최대 히프 트리를 그리시오.[5 points]

(b.) 위의 (a)에서 구성된 최대 히프 트리에 30를 삽입한 결과로 만들어지는 최대 히프 트리를 그리시오.[5 points]

(c.) 위의 (b)에서 구성된 최대 히프 트리에서 최대값을 제거한 결과로 만들어지는 최대 히프 트리를 그리시오.[5 points]

(d.) 위의 (c)에서 구성된 최대 히프 트리를 배열로 구현하시오. [5 points]

[그림: 첨자 [0]~[12]의 빈 배열 칸]

**원본 답:**

(a) 레벨 순서: 41 / 25, 28 / 16, 20 (41의 자식 25·28, 25의 자식 16·20). 배열: [41, 25, 28, 16, 20]
(b) 레벨 순서: 41 / 25, 30 / 16, 20, 28 (30의 왼쪽 자식 28). 배열: [41, 25, 30, 16, 20, 28]
(c) 레벨 순서: 30 / 25, 28 / 16, 20. 배열: [30, 25, 28, 16, 20]
(d) [0] 비움, [1]=30, [2]=25, [3]=28, [4]=16, [5]=20, [6]~[12] 비움
* 최대 히프 트리의 배열구현에서 루트노드는 첨자 1에서 시작해야 하며 그래야 부모노드와 자식노드가 서로를 찾는 관계가 정확히 이루어짐. 첨자 0에서 시작하면 감점.

## 2017-final2-q1  (manifest id p3, variant false)
- 원본: 2017 기말 1번 · 10점 · 미상 — 자구알 기출/자료구조및알고리즘_기말고사_(공지용_모범답안).pdf
- 문제 글: 1. 최대 히프(max heap)트리를 구성하기 위해서 다음 숫자들을 차례대로 이용하시오. [10 points]

10, 40, 30, 5, 12, 6, 60, 15

(a.) 위의 숫자들로 구성된 최대 히프 트리를 그리시오. [5 points]

(b.) 위의 (a)에서 구성된 최대 히프 트리에서 히프삭제를 한 결과로 만들어지는 최대 히프 트리를 그리시오. [5 points]
- 그림: 없음
- 은행 정답: (a) * 완전이진트리에 노드를 추가할 때 마다 부모노드 키값이 작으면 upheap 연산수행.
레벨 순서(배열): [60, 15, 40, 12, 10, 6, 30, 5] — 60의 자식 15·40, 15의 자식 12·10, 40의 자식 6·30, 12의 왼쪽 자식 5
(b) 레벨 순서(배열): [40, 15, 30, 12, 10, 6, 5] — 40의 자식 15·30, 15의 자식 12·10, 30의 자식 6·5 (key)
- 변형 값: 없음
- 전사 기록:

1. 최대 히프(max heap)트리를 구성하기 위해서 다음 숫자들을 차례대로 이용하시오. [10 points]

10, 40, 30, 5, 12, 6, 60, 15

(a.) 위의 숫자들로 구성된 최대 히프 트리를 그리시오. [5 points]

(b.) 위의 (a)에서 구성된 최대 히프 트리에서 히프삭제를 한 결과로 만들어지는 최대 히프 트리를 그리시오. [5 points]

**원본 답:**

(a) * 완전이진트리에 노드를 추가할 때 마다 부모노드 키값이 작으면 upheap 연산수행.
레벨 순서(배열): [60, 15, 40, 12, 10, 6, 30, 5] — 60의 자식 15·40, 15의 자식 12·10, 40의 자식 6·30, 12의 왼쪽 자식 5
(b) 레벨 순서(배열): [40, 15, 30, 12, 10, 6, 5] — 40의 자식 15·30, 15의 자식 12·10, 30의 자식 6·5

## 2019-final-q6  (manifest id p4, variant false)
- 원본: 2019 기말 6번 · 10점 · 미상 — 자구알 기출/19-1 기말 복원.hwp
- 문제 글: 6. 다음의 나열된 키(값)를 주어진 순서대로 추가 및 삭제했을 때의 최대 히프트리를 그리시오. (10점)
(키 값 정확치는 않음)

16    9    50    41    48    24    31
                  삭제 1번
     53    71    50    68    64
                  삭제 2번
- 그림: 없음
- 은행 정답: 레벨 순서(배열): [64, 53, 48, 50, 24, 16, 31, 9, 41]. 루트 64 / 64의 자식 53, 48 / 53의 자식 50, 24, 48의 자식 16, 31 / 50의 자식 9, 41. (중간 과정: 7개 삽입 후 [50,48,31,9,41,16,24], 삭제 1번(50) 후 [48,41,31,9,24,16], 5개 삽입 후 [71,68,48,50,64,16,31,9,41,24,53], 삭제 71, 68) (verified)
- 변형 값: 없음
- 전사 기록:

6. 다음의 나열된 키(값)를 주어진 순서대로 추가 및 삭제했을 때의 최대 히프트리를 그리시오. (10점)
(키 값 정확치는 않음)

16    9    50    41    48    24    31
                  삭제 1번
     53    71    50    68    64
                  삭제 2번

## unk-final-ltk-q5  (manifest id p5, variant false)
- 원본: 연도 미상 기말 5번 · 10점 · 이태권 — 자료구조및알고리즘이해 기출 소스/자료구조 기말(이태권).pdf
- 문제 글: 다음의 나열된 키(값)를 주어진 순서대로 6 개의 키를 삽입하고 한 번 삭제하여 만들어진 최소 히프(min heap)트리를 그리시오. [10 점]

삽입(삽입되는 키 순서): 90, 85, 80, 75, 70, 65
삭제: ( 한 번 삭제 )
- 그림: 없음
- 은행 정답: 삽입 후 [65, 75, 70, 90, 80, 85], 한 번 삭제(65) 후 배열 [70, 75, 85, 90, 80]. 트리: 70(왼 75, 오 85); 75(왼 90, 오 80) (verified)
- 변형 값: 없음
- 전사 기록:

다음의 나열된 키(값)를 주어진 순서대로 6 개의 키를 삽입하고 한 번 삭제하여 만들어진 최소 히프(min heap)트리를 그리시오. [10 점]

삽입(삽입되는 키 순서): 90, 85, 80, 75, 70, 65
삭제: ( 한 번 삭제 )

## textbook-ch09-q02  (manifest id p6, variant false, source_kind textbook)
- original_id: ch09-q02
- source_refs: [{"source_id": "s09", "pdf_page": 1, "book_page": 356}] (9장 우선순위 큐 연습문제)
- JSON: 교과서/09_우선순위 큐_연습문제.json sha256 700b10a8a7da3f8a848f0016d1bed2167cdea68ebfccaa13c63a1b70c63b4f8f
- 검증 payload: review.status=verified payload_sha256=3a780b20c76e7c541e5d0683b41c1032c8d96f741fd0010ce97ec1b8e2169161 (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "히프를 배열로 표현할 수 있는 이유는 무엇인가?"}]
- options: [{"label": "①", "content": [{"type": "text", "text": "완전 이진 트리이기 때문에"}]}, {"label": "②", "content": [{"type": "text", "text": "어느 정도 정렬되어 있기 때문에"}]}, {"label": "③", "content": [{"type": "text", "text": "이진 트리이기 때문에"}]}, {"label": "④", "content": [{"type": "text", "text": "히프 조건을 만족하기 때문에"}]}]
- 직접 계산한 정답(answers.py): ① 완전 이진 트리이기 때문에
- textbook_blocks.render_question(catalog,'ch09-q02',prefix='p6-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p6-prob'로 다시 렌더):

```html
<p>히프를 배열로 표현할 수 있는 이유는 무엇인가?</p><div class="options"><div class="option"><p>(①)</p><p>완전 이진 트리이기 때문에</p></div><div class="option"><p>(②)</p><p>어느 정도 정렬되어 있기 때문에</p></div><div class="option"><p>(③)</p><p>이진 트리이기 때문에</p></div><div class="option"><p>(④)</p><p>히프 조건을 만족하기 때문에</p></div></div>
```

## textbook-ch09-q07  (manifest id p7, variant false, source_kind textbook)
- original_id: ch09-q07
- source_refs: [{"source_id": "s09", "pdf_page": 1, "book_page": 356}] (9장 우선순위 큐 연습문제)
- JSON: 교과서/09_우선순위 큐_연습문제.json sha256 700b10a8a7da3f8a848f0016d1bed2167cdea68ebfccaa13c63a1b70c63b4f8f
- 검증 payload: review.status=verified payload_sha256=3b8598a6fd03584104ae4e248d41b2f0df6066081f9f378da3f1c09c38121889 (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "10개의 데이터를 저장하고 있는 히프트리의 높이는?"}]
- options: []
- 직접 계산한 정답(answers.py): 4
- textbook_blocks.render_question(catalog,'ch09-q07',prefix='p7-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p7-prob'로 다시 렌더):

```html
<p>10개의 데이터를 저장하고 있는 히프트리의 높이는?</p><div class="options"></div>
```

## textbook-ch09-q12  (manifest id p8, variant false, source_kind textbook)
- original_id: ch09-q12
- source_refs: [{"source_id": "s09", "pdf_page": 2, "book_page": null}] (9장 우선순위 큐 연습문제)
- JSON: 교과서/09_우선순위 큐_연습문제.json sha256 700b10a8a7da3f8a848f0016d1bed2167cdea68ebfccaa13c63a1b70c63b4f8f
- 검증 payload: review.status=verified payload_sha256=1e6117321f93d49757dea4f7b8eb5a634f317dbb4deed24a8c3a4e38a296586d (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "아래의 이진트리는 최소 히프트리인가? 그 이유는?"}, {"type": "figure", "asset_id": "ch09-q12-tree"}]
- options: []
- 직접 계산한 정답(answers.py): 아니다. 6(레벨 순서 5번째 노드)의 왼쪽 자식 5가 6보다 작아 부모 ≤ 자식 조건을 어긴다
- textbook_blocks.render_question(catalog,'ch09-q12',prefix='p8-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p8-prob'로 다시 렌더):

```html
<p>아래의 이진트리는 최소 히프트리인가? 그 이유는?</p><figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" aria-label="원문의 트리: 1, 2, 10, 4, 6, 11, 12, 6, 7, 5, 9" style="background:white;width:800px;max-width:none;height:auto"><title>원문의 트리: 1, 2, 10, 4, 6, 11, 12, 6, 7, 5, 9</title><g id="p8-orig-1-ch09-q12-tree-edge-a-left"><line x1="400.0" y1="45" x2="200.0" y2="130" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch09-q12-tree-edge-a-right"><line x1="400.0" y1="45" x2="600.0" y2="130" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch09-q12-tree-edge-b-left"><line x1="200.0" y1="130" x2="100.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch09-q12-tree-edge-b-right"><line x1="200.0" y1="130" x2="300.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch09-q12-tree-edge-c-left"><line x1="600.0" y1="130" x2="500.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch09-q12-tree-edge-c-right"><line x1="600.0" y1="130" x2="700.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch09-q12-tree-edge-d-left"><line x1="100.0" y1="215" x2="50.0" y2="300" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch09-q12-tree-edge-d-right"><line x1="100.0" y1="215" x2="150.0" y2="300" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch09-q12-tree-edge-e-left"><line x1="300.0" y1="215" x2="250.0" y2="300" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch09-q12-tree-edge-e-right"><line x1="300.0" y1="215" x2="350.0" y2="300" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch09-q12-tree-a"><circle cx="400.0" cy="45" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="400.0" y="45" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">1</text></g><g id="p8-orig-1-ch09-q12-tree-b"><circle cx="200.0" cy="130" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="200.0" y="130" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">2</text></g><g id="p8-orig-1-ch09-q12-tree-c"><circle cx="600.0" cy="130" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="600.0" y="130" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">10</text></g><g id="p8-orig-1-ch09-q12-tree-d"><circle cx="100.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="100.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">4</text></g><g id="p8-orig-1-ch09-q12-tree-e"><circle cx="300.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="300.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">6</text></g><g id="p8-orig-1-ch09-q12-tree-f"><circle cx="500.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="500.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">11</text></g><g id="p8-orig-1-ch09-q12-tree-g"><circle cx="700.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="700.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">12</text></g><g id="p8-orig-1-ch09-q12-tree-h"><circle cx="50.0" cy="300" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="50.0" y="300" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">6</text></g><g id="p8-orig-1-ch09-q12-tree-i"><circle cx="150.0" cy="300" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="150.0" y="300" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">7</text></g><g id="p8-orig-1-ch09-q12-tree-j"><circle cx="250.0" cy="300" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="250.0" y="300" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">5</text></g><g id="p8-orig-1-ch09-q12-tree-k"><circle cx="350.0" cy="300" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="350.0" y="300" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">9</text></g></svg></div><figcaption>원문의 트리: 1, 2, 10, 4, 6, 11, 12, 6, 7, 5, 9 · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure><div class="options"></div>
```

## textbook-ch09-q13  (manifest id p9, variant false, source_kind textbook)
- original_id: ch09-q13
- source_refs: [{"source_id": "s09", "pdf_page": 3, "book_page": 358}] (9장 우선순위 큐 연습문제)
- JSON: 교과서/09_우선순위 큐_연습문제.json sha256 700b10a8a7da3f8a848f0016d1bed2167cdea68ebfccaa13c63a1b70c63b4f8f
- 검증 payload: review.status=verified payload_sha256=10ce27fec526cfb842f3bdc4874f8b6fe827e6c9ac6da067861f8d097f4cf8c1 (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "히프트리가 비어있는 상태에서 다음의 연산들을 차례대로 수행한 후의 최소 히프트리의 모습을 그려라."}, {"type": "text", "text": "insert(20), insert(12), insert(3), insert(2), delete(), insert(5), insert(16),\ndelete(), insert(1), is_empty()"}]
- options: []
- 직접 계산한 정답(answers.py): 레벨 순서 1 5 12 20 16 (is_empty() = 거짓)
- textbook_blocks.render_question(catalog,'ch09-q13',prefix='p9-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p9-prob'로 다시 렌더):

```html
<p>히프트리가 비어있는 상태에서 다음의 연산들을 차례대로 수행한 후의 최소 히프트리의 모습을 그려라.</p><p>insert(20), insert(12), insert(3), insert(2), delete(), insert(5), insert(16),
delete(), insert(1), is_empty()</p><div class="options"></div>
```

## lecture-s08-p04-pq-implementations  (manifest id p10, source_kind lecture-code)
- 근거: 자료구조_강의록_2026/Software_8_Heap.pdf PDF 4쪽(S8 p4 구현 비교표), 추가 근거 2쪽(스택·큐·우선순위 큐가 삭제하는 요소), 7쪽(배열 인덱스 식). sha256 5ff0a712c9f93120ba297e6a6f4a81b3fe30bfb694b67062e4f4c7176f982492. 1109 수업에서 다룸(STT 요약 4·7절).
- 자체 질문(원문 문제가 아님. 카드에 "강의 예제 기반 자체 출제"):
  (a) 순서 없는 배열, 순서 없는 연결 리스트, 정렬된 배열, 정렬된 연결 리스트, 히프 다섯 가지로 우선순위 큐를 만들 때 삽입·삭제 시간복잡도를 표로 채운다(삭제는 "가장 우선순위가 높은 요소를 찾아 꺼내는 것까지"로 센다).
  (b) 한쪽이 O(1)인 정렬된 배열 대신 둘 다 O(log n)인 히프를 고르는 이유를 수업의 기준(예측 가능성, n이 커져도 log n은 완만하게 증가, 정렬된 배열은 삽입 때 자리 이동이 n개까지)으로 쓴다.
  (c) 노드 10개(인덱스 1~10, 0번 비움)를 배열에 담은 힙에서 인덱스 5 노드의 왼쪽 자식·오른쪽 자식·부모 인덱스를 구한다(없으면 "없음").
- 정답(answers.py): (a) 순서 없는 배열·연결 리스트 삽입 O(1)·삭제 O(n), 정렬된 배열·연결 리스트 삽입 O(n)·삭제 O(1), 히프 삽입·삭제 O(log n) (b) 예측 가능성: 최악에도 높이 O(log n)만큼만 움직이고, O(n) 쪽은 n이 커지면 한 번의 연산이 n에 비례해 커진다 (c) 왼쪽 10, 오른쪽 없음(11 > 10), 부모 2

## lecture-s08-p13-delete-max-heap  (manifest id p11, source_kind lecture-code)
- 근거: Software_8_Heap.pdf PDF 13쪽(delete_max_heap 의사코드), 추가 근거 11·12쪽(삭제 절차·예제 그림: 배열 9 7 6 5 4 3 2 2 1 3에서 9 삭제 → 7 5 6 3 4 3 2 2 1). 같은 sha256.
- 카드에 실을 의사코드(슬라이드 13쪽 글자 그대로, 주석 포함):
```
delete_max_heap(A)
item ← A[1];                       // root를삭제
A[1] ← A[heap_size];            // 맨마지막에있는요소를root로
heap_size←heap_size-1;        // 삭제하고맨마지막요소를올렸으니, 1개감소
i ← 2; 
// (child =2) 
while i ≤ heap_size do
if i < heap_size and A[i] > A[i+1]      // left_child > right_child
then largest ← i;
else largest ← i+1;
if A[PARENT(largest)] > A[largest] 
// 부모노드와largest 비교
then break;
A[PARENT(largest)] ↔ A[largest];       // 한단계내려가기
i ← CHILD(largest); // left_child of largest
return item;
```
  PARENT(i) = i/2(정수 나눗셈), CHILD(i) = i*2. 배열은 1번부터 쓴다.
- 자체 질문:
  (a) A[1..10] = 9 7 6 5 4 3 2 2 1 3 (heap_size=10)에 한 번 호출할 때 반복마다 (i, largest, 교환/break)와 끝난 뒤 배열을 쓴다.
  (b) A[1..5] = 50 40 30 20 10 (heap_size=5)에 의사코드를 글자 그대로 실행하면 결과 배열은? 최대 힙인가? 원인(오른쪽 자식이 없을 때 i == heap_size 인데 else 로 largest ← i+1, 힙 밖 칸 A[5]의 옛 값 10을 읽음)과 고친 조건을 쓴다.
- 정답(answers.py, C11 harness work/verify_lecture.c): (a) (2,2,교환) → (4,4,교환) → (8,8,break), 결과 7 5 6 3 4 3 2 2 1, 리턴 9 (b) 글자 그대로: (2,2,교환) → (4,5, A[2]=10 > A[5]=10 거짓이라 교환) 후 끝, 결과 40 10 30 20 → 10의 자식 20 때문에 최대 힙 아님. 고침: `if i < heap_size and A[i+1] > A[i] then largest ← i+1 else largest ← i` (오른쪽이 없으면 왼쪽 i) → 40 20 30 10
- C 실행 출력: work/verify_lecture-output.txt
