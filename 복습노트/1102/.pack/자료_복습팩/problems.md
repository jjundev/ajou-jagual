# 1102 문항 원문 (기출)

## 2018-mid-c024-q11  (manifest id p1, variant false)
- 원본: 2018 중간 11번 · 8점 · 출제자 미상 — 자구알 기출/2018_2_자료구조및알고리즘_중간고사_C024_화B목A (공지용).hwp
- 문제 글: 다음의 이진트리를 이용한 문제들에 대해서 답을 작성하시오. [8 points]

[그림: 이진트리. 루트 A. A의 왼쪽 자식 B, 오른쪽 자식 F. B의 왼쪽 자식 C, 오른쪽 자식 D. D의 오른쪽 자식 E. F의 왼쪽 자식 G. G의 왼쪽 자식 H. (레벨 순서: A / B, F / C, D, G / E, H)]

(1) 위의 트리를 1차원 배열로 표현하시오. [2 points]

[그림: 인덱스 0~19의 빈 1차원 배열 칸]

(2) 위의 트리를 전위 순회한 결과를 쓰시오. [2 points]

(3) 위의 트리를 후위 순회한 결과를 쓰시오. [2 points]

(4) 위의 트리를 중위 순회한 결과를 쓰시오. [2 points]
- 그림: 8노드 이진트리 A(B(C, D(-, E)), F(G(H, -), -))와 인덱스 0~19 빈 배열 칸
- 은행 정답: (1) [1]=A, [2]=B, [3]=F, [4]=C, [5]=D, [6]=G, [11]=E, [12]=H, 나머지 빈칸 (원본 모범답안은 [12]=F로 적었으나 G의 왼쪽 자식 H가 들어간다)
(2) A, B, C, D, E, F, G, H
(3) C, E, D, B, H, G, F, A
(4) C, B, D, E, A, H, G, F (verified)
- 변형 값: 없음
- 전사 기록:

다음의 이진트리를 이용한 문제들에 대해서 답을 작성하시오. [8 points]

[그림: 이진트리. 루트 A. A의 왼쪽 자식 B, 오른쪽 자식 F. B의 왼쪽 자식 C, 오른쪽 자식 D. D의 오른쪽 자식 E. F의 왼쪽 자식 G. G의 왼쪽 자식 H. (레벨 순서: A / B, F / C, D, G / E, H)]

(1) 위의 트리를 1차원 배열로 표현하시오. [2 points]

[그림: 인덱스 0~19의 빈 1차원 배열 칸]

(2) 위의 트리를 전위 순회한 결과를 쓰시오. [2 points]

(3) 위의 트리를 후위 순회한 결과를 쓰시오. [2 points]

(4) 위의 트리를 중위 순회한 결과를 쓰시오. [2 points]

**원본 답:** (1) [1]=A, [2]=B, [3]=F, [4]=C, [5]=D, [6]=G, [11]=E, [12]=F, 나머지 빈칸 (원본 답 그대로. [12]는 G의 왼쪽 자식 H가 맞으며 원본의 F는 오기로 보임)
(2) A, B, C, D, E, F, G, H
(3) C, E, D, B, H, G, F, A
(4) C, B, D, E, A, H, G, F

## 2021-mock1-q6  (manifest id p2, variant false)
- 원본: 2021 모의 6번 · 10점 · 출제자 미상 — 자료구조및알고리즘이해 기출 소스/2021학년도 2학기 자료구조및알고리즘이해 기말고사 모의 1회.pdf
- 문제 글: 아래의 후위순회와 중위순회 결과를 생성할 수 있는 하나의 이진트리를 그리시오. (10점) [2016-1 기출]

후위순회: F, D, E, G, R, T, S, N, P, M, K, H
중위순회: D, F, G, E, H, R, T, N, S, M, P, K
- 그림: 없음
- 은행 정답: 루트 H. H의 왼쪽 G, 오른쪽 K. G의 왼쪽 D, 오른쪽 E. D의 오른쪽 F. K의 왼쪽 M(오른쪽 없음). M의 왼쪽 N, 오른쪽 P. N의 왼쪽 T, 오른쪽 S. T의 왼쪽 R. 레벨 순서: H / G K / D E M / F N P / T S / R. (verified)
- 변형 값: 없음
- 전사 기록:

아래의 후위순회와 중위순회 결과를 생성할 수 있는 하나의 이진트리를 그리시오. (10점) [2016-1 기출]

후위순회: F, D, E, G, R, T, S, N, P, M, K, H
중위순회: D, F, G, E, H, R, T, N, S, M, P, K

## 2019-mid-q11  (manifest id p3, variant false)
- 원본: 2019 중간 11번 · 13점 · 출제자 미상 — 자구알 기출/19-1 중간 복원.txt
- 문제 글: 아래의 중위순회와 후위순회 결과를 생성할 수 있는 하나의 이진트리를 배열로 표현하시오.
(트리를 그릴 필요가 없으며 배열로 표현만 하면 됨) (13점)

	중위순회 : G, F, H, E, K, C, B, D, O, M, R, P, T
	후위순회 : G, H, P, K, E, C, O, R, T, P, M, D, B

1	2	3	4	5	6	7	8	9	10
(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )

11	12	13	14	15	16	17	18	19	20
(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )

21	22	23	24	25	26	27	28	29	30
(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )

31	32	33	34	35	36	37	38	39	40
(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )
- 그림: 인덱스 1~40의 빈 배열 칸
- 은행 정답: 1:B, 2:C, 3:D, 4:E, 7:M, 8:F, 9:K, 14:O, 15:P, 16:G, 17:H, 30:R, 31:T (나머지 칸은 비어 있음) (key)
- 변형 값: 없음
- 전사 기록:

아래의 중위순회와 후위순회 결과를 생성할 수 있는 하나의 이진트리를 배열로 표현하시오.
(트리를 그릴 필요가 없으며 배열로 표현만 하면 됨) (13점)

	중위순회 : G, F, H, E, K, C, B, D, O, M, R, P, T
	후위순회 : G, H, P, K, E, C, O, R, T, P, M, D, B

1	2	3	4	5	6	7	8	9	10
(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )

11	12	13	14	15	16	17	18	19	20
(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )

21	22	23	24	25	26	27	28	29	30
(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )

31	32	33	34	35	36	37	38	39	40
(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )	(   )

**원본 답:** 1:B, 2:C, 3:D, 4:E, 7:M, 8:F, 9:K, 14:O, 15:P, 16:G, 17:H, 30:R, 31:T (나머지 칸은 비어 있음)

> 메모: 후위순회에 P가 두 번 나오고 F가 없다. 셋째 원소 P는 F의 오타로 보인다(F로 읽으면 원본 답과 맞는다). 원문대로 둔다.

## 2018-mid-c024-q12  (manifest id p4, variant false)
- 원본: 2018 중간 12번 · 7점 · 출제자 미상 — 자구알 기출/2018_2_자료구조및알고리즘_중간고사_C024_화B목A (공지용).hwp
- 문제 글: 다음의 전위순회와 중위순회 결과를 생성할 수 있는 이진트리를 그리시오. [7 points]
중위순회: D, B, A, E, G, C, F, H
후위순회: D, B, G, E, H, F, C, A
- 그림: 없음
- 은행 정답: 루트 A. A의 왼쪽 B, 오른쪽 C. B의 왼쪽 D. C의 왼쪽 E, 오른쪽 F. E의 오른쪽 G. F의 오른쪽 H. (레벨 순서: A / B, C / D, E, F / G, H) (key)
- 변형 값: 없음
- 전사 기록:

다음의 전위순회와 중위순회 결과를 생성할 수 있는 이진트리를 그리시오. [7 points]
중위순회: D, B, A, E, G, C, F, H
후위순회: D, B, G, E, H, F, C, A

**원본 답:** 루트 A. A의 왼쪽 B, 오른쪽 C. B의 왼쪽 D. C의 왼쪽 E, 오른쪽 F. E의 오른쪽 G. F의 오른쪽 H. (레벨 순서: A / B, C / D, E, F / G, H)

## 2018-mid-c024-q3  (manifest id p5, variant false)
- 원본: 2018 중간 3번 · 2점 · 출제자 미상 — 자구알 기출/2018_2_자료구조및알고리즘_중간고사_C024_화B목A (공지용).hwp
- 문제 글: 컴퓨터 디렉토리 폴더의 용량 계산에 가장 적합한 이진트리순회는 (          ) 이다.[2 points]
- 그림: 없음
- 은행 정답: 후위 순회 (key)
- 변형 값: 없음
- 전사 기록:

컴퓨터 디렉토리 폴더의 용량 계산에 가장 적합한 이진트리순회는 (          ) 이다.[2 points]

**원본 답:** 후위 순회

## 2017-mid-c050-q5  (manifest id p6, variant false)
- 원본: 2017 중간 5번 · 2점 · 출제자 미상 — 자구알 기출/자료구조및알고리즘_중간고사+(모범답안+공지용).pdf
- 문제 글: 5. 트리의 모든 노드들을 체계적으로 방문하는 순회에서 자손노드들 보다 루트노드를 먼저 방문하는 순회를 (          )라고 한다. [2 points]
- 그림: 없음
- 은행 정답: 전위순회/preorder traversal (key)
- 변형 값: 없음
- 전사 기록:

5. 트리의 모든 노드들을 체계적으로 방문하는 순회에서 자손노드들 보다 루트노드를 먼저 방문하는 순회를 (          )라고 한다. [2 points]

**원본 답:** 전위순회/preorder traversal

# 교과서 원문 (partD)

## textbook-ch08-q01  (manifest id p7, variant false, source_kind textbook)
- original_id: ch08-q01
- source_refs: [{"source_id": "s08", "pdf_page": 1, "book_page": 316}] (8장 트리 연습문제)
- JSON: 교과서/08_트리_연습문제.json sha256 ec6fcdcc25a12533816c1cd99219026860e55fd8f6b623654b1dbb8fa34990cf
- 검증 payload: review.status=verified payload_sha256=bf48e7a8253308a02a8ffdb49cf97deb1afa4608ff5782a082b4c1d2686b921b (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "다음 트리에 대한 중위 순회 결과는? [정보처리기사 기출문제]"}, {"type": "figure", "asset_id": "ch08-q01-tree"}]
- options: [{"label": "①", "content": [{"type": "text", "text": "A B D C E F"}]}, {"label": "②", "content": [{"type": "text", "text": "A B C D E F"}]}, {"label": "③", "content": [{"type": "text", "text": "D B E C F A"}]}, {"label": "④", "content": [{"type": "text", "text": "D B A E C F"}]}]
- 직접 계산한 정답(answers.py): ④ D B A E C F
- textbook_blocks.render_question(catalog,'ch08-q01',prefix='p7-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p7-prob'로 다시 렌더):

```html
<p>다음 트리에 대한 중위 순회 결과는? [정보처리기사 기출문제]</p><figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" aria-label="원문의 트리: A, B, C, D, E, F" style="background:white;width:800px;max-width:none;height:auto"><title>원문의 트리: A, B, C, D, E, F</title><g id="p7-orig-1-ch08-q01-tree-edge-A-left"><line x1="400.0" y1="45" x2="200.0" y2="130" stroke="#26394a" stroke-width="2" /></g><g id="p7-orig-1-ch08-q01-tree-edge-A-right"><line x1="400.0" y1="45" x2="600.0" y2="130" stroke="#26394a" stroke-width="2" /></g><g id="p7-orig-1-ch08-q01-tree-edge-B-left"><line x1="200.0" y1="130" x2="100.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p7-orig-1-ch08-q01-tree-edge-C-left"><line x1="600.0" y1="130" x2="500.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p7-orig-1-ch08-q01-tree-edge-C-right"><line x1="600.0" y1="130" x2="700.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p7-orig-1-ch08-q01-tree-A"><circle cx="400.0" cy="45" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="400.0" y="45" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">A</text></g><g id="p7-orig-1-ch08-q01-tree-B"><circle cx="200.0" cy="130" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="200.0" y="130" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">B</text></g><g id="p7-orig-1-ch08-q01-tree-C"><circle cx="600.0" cy="130" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="600.0" y="130" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">C</text></g><g id="p7-orig-1-ch08-q01-tree-D"><circle cx="100.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="100.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">D</text></g><g id="p7-orig-1-ch08-q01-tree-E"><circle cx="500.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="500.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">E</text></g><g id="p7-orig-1-ch08-q01-tree-F"><circle cx="700.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="700.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">F</text></g></svg></div><figcaption>원문의 트리: A, B, C, D, E, F · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure><div class="options"><div class="option"><p>(①)</p><p>A B D C E F</p></div><div class="option"><p>(②)</p><p>A B C D E F</p></div><div class="option"><p>(③)</p><p>D B E C F A</p></div><div class="option"><p>(④)</p><p>D B A E C F</p></div></div>
```

## textbook-ch08-q02  (manifest id p8, variant false, source_kind textbook)
- original_id: ch08-q02
- source_refs: [{"source_id": "s08", "pdf_page": 1, "book_page": 316}] (8장 트리 연습문제)
- JSON: 교과서/08_트리_연습문제.json sha256 ec6fcdcc25a12533816c1cd99219026860e55fd8f6b623654b1dbb8fa34990cf
- 검증 payload: review.status=verified payload_sha256=6a3190ffa0e72061911513c4d2b00ff3eac058dbb9974118448b171e360c578c (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "다음 트리를 전위 순회로 운행할 경우 다섯 번째로 탐색되는 것은? [정보처리기사 기출문제]"}, {"type": "figure", "asset_id": "ch08-q02-tree"}]
- options: [{"label": "①", "content": [{"type": "text", "text": "C"}]}, {"label": "②", "content": [{"type": "text", "text": "E"}]}, {"label": "③", "content": [{"type": "text", "text": "G"}]}, {"label": "④", "content": [{"type": "text", "text": "H"}]}]
- 직접 계산한 정답(answers.py): ② E
- textbook_blocks.render_question(catalog,'ch08-q02',prefix='p8-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p8-prob'로 다시 렌더):

```html
<p>다음 트리를 전위 순회로 운행할 경우 다섯 번째로 탐색되는 것은? [정보처리기사 기출문제]</p><figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" aria-label="원문의 트리: A, B, C, D, E, F, G, H" style="background:white;width:800px;max-width:none;height:auto"><title>원문의 트리: A, B, C, D, E, F, G, H</title><g id="p8-orig-1-ch08-q02-tree-edge-A-left"><line x1="400.0" y1="45" x2="200.0" y2="130" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch08-q02-tree-edge-A-right"><line x1="400.0" y1="45" x2="600.0" y2="130" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch08-q02-tree-edge-B-left"><line x1="200.0" y1="130" x2="100.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch08-q02-tree-edge-C-left"><line x1="600.0" y1="130" x2="500.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch08-q02-tree-edge-C-right"><line x1="600.0" y1="130" x2="700.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch08-q02-tree-edge-E-left"><line x1="500.0" y1="215" x2="450.0" y2="300" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch08-q02-tree-edge-E-right"><line x1="500.0" y1="215" x2="550.0" y2="300" stroke="#26394a" stroke-width="2" /></g><g id="p8-orig-1-ch08-q02-tree-A"><circle cx="400.0" cy="45" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="400.0" y="45" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">A</text></g><g id="p8-orig-1-ch08-q02-tree-B"><circle cx="200.0" cy="130" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="200.0" y="130" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">B</text></g><g id="p8-orig-1-ch08-q02-tree-C"><circle cx="600.0" cy="130" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="600.0" y="130" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">C</text></g><g id="p8-orig-1-ch08-q02-tree-D"><circle cx="100.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="100.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">D</text></g><g id="p8-orig-1-ch08-q02-tree-E"><circle cx="500.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="500.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">E</text></g><g id="p8-orig-1-ch08-q02-tree-F"><circle cx="700.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="700.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">F</text></g><g id="p8-orig-1-ch08-q02-tree-G"><circle cx="450.0" cy="300" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="450.0" y="300" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">G</text></g><g id="p8-orig-1-ch08-q02-tree-H"><circle cx="550.0" cy="300" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="550.0" y="300" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">H</text></g></svg></div><figcaption>원문의 트리: A, B, C, D, E, F, G, H · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure><div class="options"><div class="option"><p>(①)</p><p>C</p></div><div class="option"><p>(②)</p><p>E</p></div><div class="option"><p>(③)</p><p>G</p></div><div class="option"><p>(④)</p><p>H</p></div></div>
```

## textbook-ch08-q03  (manifest id p9, variant false, source_kind textbook)
- original_id: ch08-q03
- source_refs: [{"source_id": "s08", "pdf_page": 1, "book_page": 316}] (8장 트리 연습문제)
- JSON: 교과서/08_트리_연습문제.json sha256 ec6fcdcc25a12533816c1cd99219026860e55fd8f6b623654b1dbb8fa34990cf
- 검증 payload: review.status=verified payload_sha256=140c5e148af1d9ac1012be861c7b857f6ff2703a2d407e3853cbe2cb0765eb99 (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "다음 그림과 같은 이진트리를 후위 순회(postorder traversal)한 결과는? [정보처리기사 기출문제]"}, {"type": "figure", "asset_id": "ch08-q03-expression"}]
- options: [{"label": "①", "content": [{"type": "text", "text": "+ * * / A B C D E"}]}, {"label": "②", "content": [{"type": "text", "text": "A / B * C * D + E"}]}, {"label": "③", "content": [{"type": "text", "text": "+ * A B / * C D E"}]}, {"label": "④", "content": [{"type": "text", "text": "A B / C * D * E +"}]}]
- 직접 계산한 정답(answers.py): ④ A B / C * D * E +
- textbook_blocks.render_question(catalog,'ch08-q03',prefix='p9-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p9-prob'로 다시 렌더):

```html
<p>다음 그림과 같은 이진트리를 후위 순회(postorder traversal)한 결과는? [정보처리기사 기출문제]</p><figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" aria-label="원문의 트리: +, *, *, /, A, B, C, D, E" style="background:white;width:800px;max-width:none;height:auto"><title>원문의 트리: +, *, *, /, A, B, C, D, E</title><g id="p9-orig-1-ch08-q03-expression-edge-plus-left"><line x1="400.0" y1="45" x2="200.0" y2="130" stroke="#26394a" stroke-width="2" /></g><g id="p9-orig-1-ch08-q03-expression-edge-plus-right"><line x1="400.0" y1="45" x2="600.0" y2="130" stroke="#26394a" stroke-width="2" /></g><g id="p9-orig-1-ch08-q03-expression-edge-mul1-left"><line x1="200.0" y1="130" x2="100.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p9-orig-1-ch08-q03-expression-edge-mul1-right"><line x1="200.0" y1="130" x2="300.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p9-orig-1-ch08-q03-expression-edge-mul2-left"><line x1="100.0" y1="215" x2="50.0" y2="300" stroke="#26394a" stroke-width="2" /></g><g id="p9-orig-1-ch08-q03-expression-edge-mul2-right"><line x1="100.0" y1="215" x2="150.0" y2="300" stroke="#26394a" stroke-width="2" /></g><g id="p9-orig-1-ch08-q03-expression-edge-div-left"><line x1="50.0" y1="300" x2="25.0" y2="385" stroke="#26394a" stroke-width="2" /></g><g id="p9-orig-1-ch08-q03-expression-edge-div-right"><line x1="50.0" y1="300" x2="75.0" y2="385" stroke="#26394a" stroke-width="2" /></g><g id="p9-orig-1-ch08-q03-expression-plus"><circle cx="400.0" cy="45" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="400.0" y="45" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">+</text></g><g id="p9-orig-1-ch08-q03-expression-mul1"><circle cx="200.0" cy="130" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="200.0" y="130" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">*</text></g><g id="p9-orig-1-ch08-q03-expression-mul2"><circle cx="100.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="100.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">*</text></g><g id="p9-orig-1-ch08-q03-expression-div"><circle cx="50.0" cy="300" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="50.0" y="300" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">/</text></g><g id="p9-orig-1-ch08-q03-expression-A"><circle cx="25.0" cy="385" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="25.0" y="385" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">A</text></g><g id="p9-orig-1-ch08-q03-expression-B"><circle cx="75.0" cy="385" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="75.0" y="385" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">B</text></g><g id="p9-orig-1-ch08-q03-expression-C"><circle cx="150.0" cy="300" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="150.0" y="300" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">C</text></g><g id="p9-orig-1-ch08-q03-expression-D"><circle cx="300.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="300.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">D</text></g><g id="p9-orig-1-ch08-q03-expression-E"><circle cx="600.0" cy="130" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="600.0" y="130" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">E</text></g></svg></div><figcaption>원문의 트리: +, *, *, /, A, B, C, D, E · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure><div class="options"><div class="option"><p>(①)</p><p>+ * * / A B C D E</p></div><div class="option"><p>(②)</p><p>A / B * C * D + E</p></div><div class="option"><p>(③)</p><p>+ * A B / * C D E</p></div><div class="option"><p>(④)</p><p>A B / C * D * E +</p></div></div>
```

## textbook-ch08-q12  (manifest id p10, variant false, source_kind textbook)
- original_id: ch08-q12
- source_refs: [{"source_id": "s08", "pdf_page": 4, "book_page": null}] (8장 트리 연습문제)
- JSON: 교과서/08_트리_연습문제.json sha256 ec6fcdcc25a12533816c1cd99219026860e55fd8f6b623654b1dbb8fa34990cf
- 검증 payload: review.status=verified payload_sha256=5d6274cd350b2ab3c227e342606a8e205265372db7b9f529e090d2502f2ad627 (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "다음과 같은 함수가 아래에 표시된 이진트리의 루트 노드에 대해 호출된다고 하자. 함수가 반환하는 값은 무엇인가?"}, {"type": "figure", "asset_id": "ch08-q12-tree"}, {"type": "code", "language": "c", "text": "int mystery(TreeNode* p) {\n    if (p == NULL) return 0;\n    else if (p->left == NULL && p->right == NULL)\n        return p->data;\n    else\n        return max(mystery(p->left), mystery(p->right));\n}"}]
- options: []
- 직접 계산한 정답(answers.py): 8
- textbook_blocks.render_question(catalog,'ch08-q12',prefix='p10-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p10-prob'로 다시 렌더):

```html
<p>다음과 같은 함수가 아래에 표시된 이진트리의 루트 노드에 대해 호출된다고 하자. 함수가 반환하는 값은 무엇인가?</p><figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" aria-label="원문의 트리: 3, 5, 1, 4, 2, 8, 6" style="background:white;width:800px;max-width:none;height:auto"><title>원문의 트리: 3, 5, 1, 4, 2, 8, 6</title><g id="p10-orig-1-ch08-q12-tree-edge-3-left"><line x1="400.0" y1="45" x2="200.0" y2="130" stroke="#26394a" stroke-width="2" /></g><g id="p10-orig-1-ch08-q12-tree-edge-3-right"><line x1="400.0" y1="45" x2="600.0" y2="130" stroke="#26394a" stroke-width="2" /></g><g id="p10-orig-1-ch08-q12-tree-edge-5-left"><line x1="200.0" y1="130" x2="100.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p10-orig-1-ch08-q12-tree-edge-5-right"><line x1="200.0" y1="130" x2="300.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p10-orig-1-ch08-q12-tree-edge-1-left"><line x1="600.0" y1="130" x2="500.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p10-orig-1-ch08-q12-tree-edge-1-right"><line x1="600.0" y1="130" x2="700.0" y2="215" stroke="#26394a" stroke-width="2" /></g><g id="p10-orig-1-ch08-q12-tree-3"><circle cx="400.0" cy="45" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="400.0" y="45" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">3</text></g><g id="p10-orig-1-ch08-q12-tree-5"><circle cx="200.0" cy="130" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="200.0" y="130" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">5</text></g><g id="p10-orig-1-ch08-q12-tree-1"><circle cx="600.0" cy="130" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="600.0" y="130" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">1</text></g><g id="p10-orig-1-ch08-q12-tree-4"><circle cx="100.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="100.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">4</text></g><g id="p10-orig-1-ch08-q12-tree-2"><circle cx="300.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="300.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">2</text></g><g id="p10-orig-1-ch08-q12-tree-8"><circle cx="500.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="500.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">8</text></g><g id="p10-orig-1-ch08-q12-tree-6"><circle cx="700.0" cy="215" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="700.0" y="215" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">6</text></g></svg></div><figcaption>원문의 트리: 3, 5, 1, 4, 2, 8, 6 · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure><pre><code>int mystery(TreeNode* p) {
    if (p == NULL) return 0;
    else if (p-&gt;left == NULL &amp;&amp; p-&gt;right == NULL)
        return p-&gt;data;
    else
        return max(mystery(p-&gt;left), mystery(p-&gt;right));
}</code></pre><div class="options"></div>
```

# 강의 예제 기반 자체 출제 (partL, source_kind lecture-code)

## lecture-s07-p13-level-order  (manifest id p11)
- 근거: 자료구조_강의록_2026/Software_7_Tree.pdf pdf_page 13(레벨 순회, 큐 사용, 수식 트리 a*b + c/d 그림과 큐 변화), extra_pages [11, 14](같은 수식 트리 a*b + c/d 의 중위 순회, 수식 트리의 전위·중위·후위 표기). 1102 수업에서 학습.
- 카드 첫 문단: `<p><span class="badge">강의 예제 기반 자체 출제</span> S7 p13</p>`, 원문 영역 summary 는 `강의 예제 보기`(슬라이드 13쪽 그림을 자체 SVG 로 다시 그리고 "추가 근거 S7 p11, p14" 를 적는다).
- 전제(카드 본문에 직접 쓴다): 수식 a*b + c/d 를 나타내는 이진 트리 — 루트 +, + 의 왼쪽 *, 오른쪽 /, * 의 왼쪽 a·오른쪽 b, / 의 왼쪽 c·오른쪽 d. 레벨 순회 규칙: 큐에 루트를 넣고, 큐 앞에서 하나 꺼내 방문한 뒤 그 노드의 왼쪽·오른쪽 자식을 차례로 큐 뒤에 넣는 것을 큐가 빌 때까지 반복.
- 구할 것: (a) 레벨 순회 방문 순서 (b) * 를 방문(꺼냄)하고 자식을 넣은 직후 큐의 내용(앞→뒤) (c) 같은 트리의 전위·중위·후위 순회 결과
- 정답(answers.py): (a) + * / a b c d (b) [/ a b] (c) 전위 + * a b / c d, 중위 a * b + c / d, 후위 a b * c d / +
- 큐 상태: + 방문 후 [* /] → * 방문 후 [/ a b] → / 방문 후 [a b c d] → a 후 [b c d] → b 후 [c d] → c 후 [d] → d 후 []

## lecture-s07-p16-count-height  (manifest id p12)
- 근거: 자료구조_강의록_2026/Software_7_Tree.pdf pdf_page 16(get_node_count), extra_pages [17](get_height). 1102 수업에서 학습. 수업에서는 칠판 트리로 "맨 아래는 1, 1+1+1=3, 1+0+1=2, 3+2+1=6" 처럼 돌아오는 값을 더했다.
- 슬라이드 코드(카드 전제에 그대로 싣는다. 슬라이드에는 함수 몸체 중괄호가 생략돼 있으니 컴파일되게 중괄호를 보충했다고 밝힌다):
```c
int get_node_count(TreeNode *node)
{
    int count=0;
    if( node != NULL )
        count = 1 + get_node_count(node->left)+
                get_node_count(node->right);
    return count;
}

int get_height(TreeNode *node)
{
    int height=0;
    if( node != NULL )
        height = 1 + max(get_height(node->left),
                         get_height(node->right));
    return height;
}
```
- 전제 트리(카드 본문에 직접 쓰고 SVG 로 그린다): 루트 R. R 의 왼쪽 X, 오른쪽 Y. X 의 왼쪽 L1, 오른쪽 L2. Y 의 왼쪽 L3, 오른쪽 없음. (노드 6개)
- 구할 것: (a) get_node_count 가 X, Y, R 에서 각각 돌려주는 값 (b) get_height(R) 의 값 (c) get_height 에서 max(...) 에 1 을 더하는 이유를 한 문장으로
- 정답(answers.py): (a) X 3, Y 2, R 6 (b) 3 (c) 1 은 지금 노드(루트) 자신이 차지하는 한 층
