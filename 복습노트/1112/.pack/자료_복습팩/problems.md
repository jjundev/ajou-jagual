# 1112 문항 원문 (메인 에이전트 작성)

## 2016-final-ljw-q4  (manifest id p1, variant false)
- 원본: 2016 기말 4번 · 10점 · 이정원 — 자료구조및알고리즘이해 기출 소스/자료구조및알고리즘 기말 (2016이정원)/
- 문제 글: 4. 어떤 문서에 총 100개의 문자가 들어 있으며, 다음 표와 같이 character의 빈도수가 결정 된다고 할 때, 다음에 답하여라. (10점)

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| 15% | 8% | 20% | 1% | 5% | 40% | 9% | 2% |

1) 본래는 7가지의 character를 표현해야 하므로 하나의 문자당 (    )bit가 필요하며, 총 (    ) bit가 필요하다.
2) 이를 허프만 코딩 방법을 이용하여 압축한다면 총 (    ) bit가 필요하다. 허프만 코딩 트리를 그리고 다음표의 code를 채워라. (단 left 0, right 1로 coding 할 것)

| Char | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| 빈도 | 15% | 8% | 20% | 1% | 5% | 40% | 9% | 2% |
| Code |  |  |  |  |  |  |  |  |
- 그림: 빈도 표 2개(문자 A~H, 두 번째 표는 Code 행이 빈칸)
- 은행 정답: 1) 3 bit, 300 bit (문제 글은 '7가지'이나 문자는 8개이고 3 bit가 필요) 2) 247 bit. 병합: D1+H2=3, 3+E5=8, B8+8=16, G9+A15=24, 16+C20=36, 24+36=60, F40+60=100. 코드 길이 F1, A·C·G 3, B 4, E 5, D·H 6. 코드 예(좌0 우1): F 0, A 100, G 101, C 110, B 1110, E 11110, H 111110, D 111111 (같은 트리에서 좌우 배치에 따라 비트는 바뀔 수 있으나 길이는 같다). (verified)
- 변형 값: 없음
- 전사 기록:

4. 어떤 문서에 총 100개의 문자가 들어 있으며, 다음 표와 같이 character의 빈도수가 결정 된다고 할 때, 다음에 답하여라. (10점)

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| 15% | 8% | 20% | 1% | 5% | 40% | 9% | 2% |

1) 본래는 7가지의 character를 표현해야 하므로 하나의 문자당 (    )bit가 필요하며, 총 (    ) bit가 필요하다.
2) 이를 허프만 코딩 방법을 이용하여 압축한다면 총 (    ) bit가 필요하다. 허프만 코딩 트리를 그리고 다음표의 code를 채워라. (단 left 0, right 1로 coding 할 것)

| Char | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| 빈도 | 15% | 8% | 20% | 1% | 5% | 40% | 9% | 2% |
| Code |  |  |  |  |  |  |  |  |

학생 답안(채점됨): 1) 3, 300 (채점자가 '7가지'를 8로 고침) 2) 247. Code A 100, B 1110, C 110, D 111111, E 11110, F 0, G 101, H 111110

- 재계산 정답(answers.py, manifest answer): 1) 3 bit, 300 bit (문제 글의 '7가지'는 오기, 문자는 8개) 2) 247 bit. 병합 1+2=3, 3+5=8, 8+8=16, 9+15=24, 16+20=36, 24+36=60, 40+60=100. 코드 길이 F 1, A·C·G 3, B 4, E 5, D·H 6. 코드 예(원본 시험지의 채점된 답안과 같은 배치): F 0, A 100, G 101, C 110, B 1110, E 11110, H 111110, D 111111 (합칠 때 좌우 배치에 따라 비트는 달라도 길이와 247은 같다)

## 2021-mock1-q5  (manifest id p2, variant false)
- 원본: 2021 모의 5번 · 10점 · 미상 — 자료구조및알고리즘이해 기출 소스/2021학년도 2학기 자료구조및알고리즘이해 기말고사 모의 1회.pdf
- 문제 글: 아래의 표는 105개의 글자(symbol)들 글에서 각 글자들의 빈도수를 나타낸 것이다. 이 symbol들로 이루어진 파일을 압축하는 허프만 코드(Huffman code)를 만들려고 한다. (총 10점) [2018-2 기출]

| symbol | 빈도수 |
|---|---|
| s | 16 |
| t | 35 |
| u | 4 |
| v | 8 |
| w | 23 |
| x | 19 |

1) 허프만 트리를 그리시오. (5점)
(허프만 트리에 0과 1의 표시도 하시오)

[그림: 빈 노드로 된 트리 틀. 루트의 왼쪽 자식은 내부 노드 L, 오른쪽 자식은 내부 노드 R. L의 왼쪽은 단말, 오른쪽은 내부 노드 L2. L2의 왼쪽은 내부 노드 L3, 오른쪽은 단말. L3의 왼쪽·오른쪽은 단말. R의 왼쪽·오른쪽은 단말.]

2) 각 symbol의 허프만 코드를 적으시오. (3점)

| symbol | 허프만 코드 |
|---|---|
| s | |
| t | |
| u | |
| v | |
| w | |
| x | |

3) 허프만 코딩에 의해서 105개의 글자(symbol)들을 압축하였을 경우에 총 비트의 수는? (2점)
(                       )bits
- 그림: 빈 허프만 트리 틀(루트-왼쪽 내부[단말, 내부[내부[단말,단말], 단말]], 오른쪽 내부[단말,단말])과 빈도표·빈 코드표
- 은행 정답: 1) 병합: u4+v8=12, 12+s16=28, x19+w23=42, 28+t35=63, 42+63=105. 틀에 맞춰(왼쪽 0, 오른쪽 1): 루트 105의 왼쪽 63, 오른쪽 42; 63의 왼쪽 t(35), 오른쪽 28; 28의 왼쪽 12, 오른쪽 s(16); 12의 왼쪽 u(4), 오른쪽 v(8); 42의 왼쪽 x(19), 오른쪽 w(23).
2) s=011, t=00, u=0100, v=0101, w=11, x=10 (0/1 배정 규칙에 따라 비트는 바뀔 수 있으나 길이는 s3, t2, u4, v4, w2, x2).
3) 16×3+35×2+4×4+8×4+23×2+19×2 = 250 bits (verified)
- 변형 값: 없음
- 전사 기록:

아래의 표는 105개의 글자(symbol)들 글에서 각 글자들의 빈도수를 나타낸 것이다. 이 symbol들로 이루어진 파일을 압축하는 허프만 코드(Huffman code)를 만들려고 한다. (총 10점) [2018-2 기출]

| symbol | 빈도수 |
|---|---|
| s | 16 |
| t | 35 |
| u | 4 |
| v | 8 |
| w | 23 |
| x | 19 |

1) 허프만 트리를 그리시오. (5점)
(허프만 트리에 0과 1의 표시도 하시오)

[그림: 빈 노드로 된 트리 틀. 루트의 왼쪽 자식은 내부 노드 L, 오른쪽 자식은 내부 노드 R. L의 왼쪽은 단말, 오른쪽은 내부 노드 L2. L2의 왼쪽은 내부 노드 L3, 오른쪽은 단말. L3의 왼쪽·오른쪽은 단말. R의 왼쪽·오른쪽은 단말.]

2) 각 symbol의 허프만 코드를 적으시오. (3점)

| symbol | 허프만 코드 |
|---|---|
| s | |
| t | |
| u | |
| v | |
| w | |
| x | |

3) 허프만 코딩에 의해서 105개의 글자(symbol)들을 압축하였을 경우에 총 비트의 수는? (2점)
(                       )bits

- 재계산 정답(answers.py, manifest answer): 1) 병합 4+8=12, 12+16=28, 19+23=42, 28+35=63, 42+63=105. 틀에 맞춰 루트 왼쪽 63(t 35, 28(12(u,v), s)), 오른쪽 42(x, w) 2) s 011, t 00, u 0100, v 0101, w 11, x 10 3) 250 bits

## textbook-ch09-q04  (manifest id p3, variant false, source_kind textbook)
- original_id: ch09-q04
- source_refs: [{"source_id": "s09", "pdf_page": 1, "book_page": 356}] (9장 우선순위 큐 연습문제)
- JSON: 교과서/09_우선순위 큐_연습문제.json sha256 700b10a8a7da3f8a848f0016d1bed2167cdea68ebfccaa13c63a1b70c63b4f8f
- 검증 payload: review.status=verified (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "다음 중 히프 정렬이 특히 유용하게 사용될 수 있는 경우는?"}]
- options: [{"label": "①", "content": [{"type": "text", "text": "데이터 100개 중에서 오름차순으로 20개만 뽑고자 할때"}]}, {"label": "②", "content": [{"type": "text", "text": "비교적 데이터의 개수가 적을 때"}]}, {"label": "③", "content": [{"type": "text", "text": "정렬의 대상이 되는 레코드의 크기가 클 때"}]}, {"label": "④", "content": [{"type": "text", "text": "데이터가 역순으로 정렬되어 있을 때"}]}]
- 직접 계산한 정답(answers.py): ① 데이터 100개 중에서 오름차순으로 20개만 뽑고자 할 때
- textbook_blocks.render_question(catalog,'ch09-q04',prefix='p3-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p3-prob'로 다시 렌더):

```html
<p>다음 중 히프 정렬이 특히 유용하게 사용될 수 있는 경우는?</p><div class="options"><div class="option"><p>(①)</p><p>데이터 100개 중에서 오름차순으로 20개만 뽑고자 할때</p></div><div class="option"><p>(②)</p><p>비교적 데이터의 개수가 적을 때</p></div><div class="option"><p>(③)</p><p>정렬의 대상이 되는 레코드의 크기가 클 때</p></div><div class="option"><p>(④)</p><p>데이터가 역순으로 정렬되어 있을 때</p></div></div>
```

## textbook-ch09-q10  (manifest id p4, variant false, source_kind textbook)
- original_id: ch09-q10
- source_refs: [{"source_id": "s09", "pdf_page": 2, "book_page": null}] (9장 우선순위 큐 연습문제)
- JSON: 교과서/09_우선순위 큐_연습문제.json sha256 700b10a8a7da3f8a848f0016d1bed2167cdea68ebfccaa13c63a1b70c63b4f8f
- 검증 payload: review.status=verified (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "다음의 파일에 대하여 다음 물음에 답하시오."}, {"type": "text", "text": "10, 40, 30, 5, 12, 6, 15, 9, 60"}, {"type": "subquestions", "items": [{"id": "ch09-q10-s01", "label": "1", "content": [{"type": "text", "text": "위의 파일을 순차적으로 읽어서 최대 히프트리를 구성하라. 공백 트리에서 최대 히프트리가 만들어지는 과정을 보여라."}]}, {"id": "ch09-q10-s02", "label": "2", "content": [{"type": "text", "text": "구성된 최대 히프트리가 저장된 배열의 내용을 표시하라."}]}, {"id": "ch09-q10-s03", "label": "3", "content": [{"type": "text", "text": "구성된 최대 히프트리에서 최대값을 제거한 다음 재정비하는 과정을 설명하라."}]}]}]
- options: []
- 직접 계산한 정답(answers.py): 1) 삽입마다 10 → 40 10 → 40 10 30 → 40 10 30 5 → 40 12 30 5 10 → 40 12 30 5 10 6 → 40 12 30 5 10 6 15 → 40 12 30 9 10 6 15 5 → 60 40 30 12 10 6 15 5 9 2) 배열 [1..9] = 60 40 30 12 10 6 15 5 9 3) 루트 60 삭제, 마지막 9를 루트로 올리고 큰 자식과 교환(40, 12)해 40 12 30 9 10 6 15 5
- textbook_blocks.render_question(catalog,'ch09-q10',prefix='p4-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p4-prob'로 다시 렌더):

```html
<p>다음의 파일에 대하여 다음 물음에 답하시오.</p><p>10, 40, 30, 5, 12, 6, 15, 9, 60</p><div class="subquestions"><div><p>(1)</p><p>위의 파일을 순차적으로 읽어서 최대 히프트리를 구성하라. 공백 트리에서 최대 히프트리가 만들어지는 과정을 보여라.</p></div><div><p>(2)</p><p>구성된 최대 히프트리가 저장된 배열의 내용을 표시하라.</p></div><div><p>(3)</p><p>구성된 최대 히프트리에서 최대값을 제거한 다음 재정비하는 과정을 설명하라.</p></div></div><div class="options"></div>
```

## textbook-ch09-q17  (manifest id p5, variant false, source_kind textbook)
- original_id: ch09-q17
- source_refs: [{"source_id": "s09", "pdf_page": 3, "book_page": 358}] (9장 우선순위 큐 연습문제)
- JSON: 교과서/09_우선순위 큐_연습문제.json sha256 700b10a8a7da3f8a848f0016d1bed2167cdea68ebfccaa13c63a1b70c63b4f8f
- 검증 payload: review.status=verified (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "다음과 같이 각 글자들의 빈도가 있을 때, 호프만 코드를 계산해보자. 생성되는 트리를 그려보자."}, {"type": "text", "text": "a:1 b:1 c:2 d:3 e:5 f:8 g:13 h:21"}]
- options: []
- 직접 계산한 정답(answers.py): 병합 1+1=2, 2+2=4, 3+4=7, 5+7=12, 8+12=20, 13+20=33, 21+33=54. 코드 길이 h 1, g 2, f 3, e 4, d 5, c 6, a·b 7 (먼저 꺼낸 쪽을 왼쪽(0)에 두면 h 0, g 10, f 110, e 1110, d 11110, c 111110, a 1111110, b 1111111 — 좌우 배치에 따라 비트는 달라도 길이는 같다). 총 132 bit (고정 3비트면 162 bit)
- textbook_blocks.render_question(catalog,'ch09-q17',prefix='p5-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p5-prob'로 다시 렌더):

```html
<p>다음과 같이 각 글자들의 빈도가 있을 때, 호프만 코드를 계산해보자. 생성되는 트리를 그려보자.</p><p>a:1 b:1 c:2 d:3 e:5 f:8 g:13 h:21</p><div class="options"></div>
```

## lecture-s08-p15-heap-sort  (manifest id p6, source_kind lecture-code)
- 근거: Software_8_Heap.pdf PDF 15쪽(heap_sort 프로그램, "오름차순으로 a[i] 정렬"), 추가 근거 14쪽(삽입·삭제 각 O(log n), 전체 O(n log n)). 녹음(1112 Part 01)에서 "insert n번, delete n번 하면 저절로 소팅" 설명. 입력 1, 23, 7, 8, 20 은 1109 수업 칠판 예제 숫자(1109 STT).
- 카드에 실을 코드: 슬라이드 15쪽 heap_sort·init·typedef 는 **글자 그대로**(원 코드 발췌라고 밝힘). insert_max_heap·delete_max_heap 은 슬라이드 10·13쪽 의사코드의 C 판으로 **자체 작성**한 것임을 밝힘(work/verify_heapsort.c 와 같은 코드, 오른쪽 자식이 없으면 왼쪽 자식을 고름).
```c
// 우선순위 큐인 히프를 이용한 정렬  (슬라이드 15쪽 그대로)
void heap_sort(element a[], int n)
{
  int i;
  HeapType h;
  init(&h);
  for(i=0;i<n;i++){
    insert_max_heap(&h, a[i]);
  }
  for(i=(n-1);i>=0;i--){
    a[i] = delete_max_heap(&h);
  }
}
void init(HeapType *h)
{
  h -> heap_size = 0;
}
```
  자체 C 판(카드에 함께 싣고 "슬라이드 10·13쪽 의사코드를 C로 옮긴 자체 코드"라고 표시):
```c
void insert_max_heap(HeapType *h, element item) {
  int i = ++(h->heap_size);
  while ((i != 1) && (item.key > h->heap[i / 2].key)) {
    h->heap[i] = h->heap[i / 2];
    i /= 2;
  }
  h->heap[i] = item;
}
element delete_max_heap(HeapType *h) {
  int parent = 1, child = 2;
  element item = h->heap[1], temp = h->heap[(h->heap_size)--];
  while (child <= h->heap_size) {
    if ((child < h->heap_size) && (h->heap[child].key < h->heap[child + 1].key)) child++;
    if (temp.key >= h->heap[child].key) break;
    h->heap[parent] = h->heap[child];
    parent = child; child *= 2;
  }
  h->heap[parent] = temp;
  return item;
}
```
  힙 배열은 1번 칸부터 쓴다(heap[0] 비움).
- 자체 질문:
  (a) a[] = {1, 23, 7, 8, 20}, n = 5 로 heap_sort 를 부를 때 첫 for 루프가 끝난 직후 h.heap[1..5] 를 쓴다.
  (b) 두 번째 for 루프의 반복마다 i, a[i] 에 저장되는 값, 남은 힙 배열을 쓰고 최종 a[] 를 쓴다.
  (c) 두 번째 루프가 i 를 n-1 부터 0 까지 **내려가며** 채우는 이유(최대 힙이 큰 값부터 꺼내므로 뒤부터 채워야 오름차순)와 heap_sort 전체 시간 복잡도 O(n log n) 의 근거.
- 정답(answers.py, C11 work/verify_heapsort.c, -Wall -Wextra ASan/UBSan): (a) 23 20 7 1 8 (삽입마다 1 → 23 1 → 23 1 7 → 23 8 7 1 → 23 20 7 1 8) (b) i=4: a[4]=23, 힙 20 8 7 1 → i=3: a[3]=20, 힙 8 1 7 → i=2: a[2]=8, 힙 7 1 → i=1: a[1]=7, 힙 1 → i=0: a[0]=1, 힙 빔. 최종 1 7 8 20 23 (c) 위 설명, insert·delete 각 O(log n) × n번씩 → O(n log n)
- C 실행 출력: work/verify_heapsort-output.txt


## lecture-s08-p17-huffman-etnis  (manifest id p7, source_kind lecture-code)
- 근거: Software_8_Heap.pdf PDF 17쪽(etnis 빈도 15·12·8·6·4, 45글자, 3bit면 135bits, 허프만이면 100bits), 18쪽(오름차순 단말 노드화 → 가장 작은 두 빈도를 자식으로 하는 root 구성 → 다시 정렬 반복, 10·18·27·45), 19쪽(비트 코드 e 00, t 01, n 10, i 110, s 111, 100bits, 26% 줄임). 같은 sha256. 녹음 1112 Part 02–03.
- 강의 예제 보기에 실을 원 자료: 빈도표 e 15, t 12, n 8, i 6, s 4 와 슬라이드 19쪽 표(Character / Bit code / Frequency / Number of bit: e 00 15 30, t 01 12 24, n 10 8 16, i 110 6 18, s 111 4 12), 식 15*2+12*2+8*2+6*3+4*3 = 100bits, "135 bits 에서 35 bit, 즉 26% 줄임".
- 자체 질문(문제 본문에 빈도표를 직접 쓴다. 최소 힙 배열은 1번 칸부터, 삽입은 upheap·삭제는 downheap):
  (a) 다섯 글자를 같은 길이 코드로 나타내려면 글자당 몇 비트, 45글자 전체는 몇 비트인가?
  (b) 빈도 4, 6, 8, 12, 15 를 이 순서로 빈 최소 힙에 삽입한 뒤, "삭제 두 번 → 두 값의 합을 삽입"을 원소가 하나 남을 때까지 반복한다. 반복마다 합친 두 값과 그 직후 최소 힙 배열을 쓴다.
  (c) 만들어진 트리에서 왼쪽 0·오른쪽 1(먼저 꺼낸 작은 쪽을 왼쪽)로 각 글자의 코드를 쓰고 총 비트 수, 줄어든 비트 수와 비율을 쓴다.
- 정답(answers.py): (a) 3비트(2^2=4 < 5 ≤ 8), 45 × 3 = 135 bit (b) 삽입 후 4 6 8 12 15 → 4+6=10 후 8 10 15 12 → 8+10=18 후 12 15 18 → 12+15=27 후 18 27 → 18+27=45 후 45 (c) 45 = 18(왼쪽) + 27(오른쪽)? 주의: 먼저 꺼낸 작은 쪽 18을 왼쪽에 두면 n 00, s 010, i 011, t 10, e 11 이 된다. 슬라이드 19쪽은 27(e,t)을 왼쪽에 둔 배치(e 00, t 01, n 10, i 110, s 111)다. 어느 배치든 코드 길이(e·t·n 2, i·s 3)와 총 100 bit 는 같다. 35 bit 절약, 35/135 ≈ 25.9% (슬라이드는 반올림해 26%).
  → 카드 작성자 지시: (c)는 "왼쪽 0·오른쪽 1, 배치는 슬라이드처럼 큰 합(27)을 왼쪽에" 로 정해 묻지 말고, **코드 길이와 총 비트 수**를 묻고, 코드 예시로 슬라이드 배치(e 00, t 01, n 10, i 110, s 111)를 풀이에 제시하며 배치가 바뀌면 비트가 달라질 수 있음을 밝힌다.
- 덧붙임(풀이 보충): 허프만 트리 자체는 힙(완전 이진 트리)이 아니고, 힙은 "가장 작은 두 빈도"를 꺼내는 데 쓰인다. 허프만 코드는 어떤 코드도 다른 코드의 앞부분이 아닌 접두어 코드라 구분자 없이 복호화된다(교수님 "delimiter가 있어야" 발언에 대한 보충 — 보충임을 밝힌다).


## lecture-s08-p16-event-sim  (manifest id p8, source_kind lecture-code)
- 근거: Software_8_Heap.pdf PDF 16쪽(히프 응용2: 이산 이벤트 시뮬레이션 — 많은 이벤트, 우선순위에 따른 처리, 아이스크림 가게: 손님 도착 arrival(남은 의자 수 > 도착 인원이면 의자 수 감소, 의자가 더 적으면 주문 없이 나감), 주문 order(주문 후 leave 이벤트 발생), 떠남 leave(의자 수 증가)). 녹음 1112 Part 01–02: "줄 서기는 queue로 모델링, 그런데 이벤트가 여러 개고 우선순위가 있어 하나의 queue로 표현 못 함 → priority queue". 교수님은 실제 코드는 책을 보라고 미룸.
- 이 문제의 시각 규칙(order 는 착석 1분 뒤, leave 는 order 3분 뒤)과 숫자는 **자체 설정**이다. 슬라이드의 "남은 의자 수 > 도착 인원" 은 문제에서 "남은 의자 수가 도착 인원 이상이면 앉는다"로 명시해 경계를 정했음을 밝힌다(이 문제 데이터에서는 같은 경우가 나오지 않아 답이 같다).
- 자체 질문(standalone):
  가게 의자는 처음 5개. 이벤트는 (시각, 종류, 인원)이고, 시각이 가장 이른 이벤트부터 꺼내는 최소 우선순위 큐에 들어 있다. 시작할 때 도착 이벤트가 (6, arrival, 2), (1, arrival, 3), (8, arrival, 4), (3, arrival, 3) 순서로 삽입돼 있다. 처리 규칙:
  - arrival(t, k): 남은 의자 ≥ k 이면 의자를 k 줄이고 (t+1, order, k) 를 큐에 넣는다. 아니면 k명은 주문 없이 나간다.
  - order(t, k): (t+3, leave, k) 를 큐에 넣는다.
  - leave(t, k): 의자를 k 늘린다.
  (a) 이벤트를 넣은 순서대로 꺼내는 보통의 큐(FIFO)로는 이 시뮬레이션이 왜 틀리는지 한두 문장.
  (b) 큐가 빌 때까지 꺼내지는 이벤트 순서(시각, 종류)와 각 단계 뒤 남은 의자 수.
  (c) 주문 없이 나간 손님 수와 마지막 남은 의자 수.
- 정답(answers.py heapq 시뮬레이션): (a) 나중에 생긴 order·leave 이벤트(예: t=2 order, t=5 leave)가 먼저 넣어 둔 도착(t=6, t=8)보다 먼저 일어나야 하므로, 넣은 순서가 아니라 시각이 가장 이른 것을 꺼내야 한다 (b) t=1 arrival 3명 착석(의자 2) → t=2 order 3명 → t=3 arrival 3명 그냥 나감(의자 2) → t=5 leave 3명(의자 5) → t=6 arrival 2명 착석(의자 3) → t=7 order 2명 → t=8 arrival 4명 그냥 나감(의자 3) → t=10 leave 2명(의자 5) (c) 7명, 5개

