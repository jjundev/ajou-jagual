# 1116 문항 원문 (메인 에이전트 작성)

## 2019-final-q2  (manifest id p1, variant false)
- 원본: 2019 기말 2번 · 2점 · 출제자 미상 — 자구알 기출/19-1 기말 복원.hwp
- 문제 글: 2. 단순 경로의 시작 정점과 종료 정점이 동일한 경로를 (          ) 이라고 한다. (2점)
- 그림: 없음
- 은행 정답: 사이클 (key)
- 변형 값: 없음
- 전사 기록:

2. 단순 경로의 시작 정점과 종료 정점이 동일한 경로를 (          ) 이라고 한다. (2점)

**원본 답:** 사이클

- 재계산 정답(answers.py, manifest answer): 사이클

## 2019-final-q5  (manifest id p2, variant false)
- 원본: 2019 기말 5번 · 2점 · 출제자 미상 — 자구알 기출/19-1 기말 복원.hwp
- 문제 글: 5. 10개의 정점을 가진 무방향 완전그래프의 간선의 수는 (          )개 이다. (2점)
- 그림: 없음
- 은행 정답: 45 (key)
- 변형 값: 없음
- 전사 기록:

5. 10개의 정점을 가진 무방향 완전그래프의 간선의 수는 (          )개 이다. (2점)

**원본 답:** 45

- 재계산 정답(answers.py, manifest answer): 45 (10 × 9 / 2, 공식 n(n-1)/2)

## 2017-final2-q8  (manifest id p3, variant false)
- 원본: 2017 기말 8번 · 6점 · 출제자 미상 — 자구알 기출/자료구조및알고리즘_기말고사_(공지용_모범답안).pdf
- 문제 글: 8. 그래프에서 주어진 경로가 사이클(cycle)인지를 확인하는 check_cycle() 함수를 구현하시오. check_cycle() 함수는 (무방향 그래프)인접행렬과 주어진 경로를 받아서 주어진 경로가 사이클(cycle)이면 문자 y를 반환하고 아니면 문자 n을 반환하는 함수. [6 points]
사이클(cycle): 단순경로의 시작정점과 종료정점이 동일한 경로.

```c
#include <stdio.h>
#include <string.h>
char check_cycle(int adj_matrix[6][6], char *path) {
    /* 빈칸: 함수 본문 */
}

int main(){
    int i, n;
    int adj_matrix[6][6] = {
    { 0, 0, 1, 0, 1, 0 },
    { 0, 0, 1, 0, 0, 0 },
    { 1, 1, 0, 1, 1, 0 },
    { 0, 0, 1, 0, 1, 1 },
    { 1, 0, 1, 1, 0, 0 },
    { 0, 0, 0, 1, 0, 0 } };

    if ( check_cycle(adj_matrix, "0240") == 'y' )
        printf("Cycle?: Yes");
    else
        printf("Cycle?: No");

    return 0;
}
```
- 그림: 주어진 코드 틀(함수 머리와 main)
- 은행 정답: ```c
char check_cycle(int adj_matrix[6][6], char *path) {
    int len, i, snode, enode;
    int a_m[6][6] = { 0 };  //간선을 지나간 적이 있는지 체크하기 위해서 사용

    len = strlen(path);

    // 시작정점과 종료정점이 다르면 ‘n'을 리턴
    if (path[0] != path[len - 1])                return 'n';

    for (i = 0; i < len - 1 ; i++){
        snode = path[i] - '0';
        enode = path[i + 1] - '0';

        // 두 정점이 연결되지 않으면 (간선이 없으면) ‘n'을 리턴
        if (adj_matrix[snode][enode] != 1)   return 'n';

        // 두 정점이 간선으로 연결되어 있지만 이 간선을 전에
        // 지나간 적이 있으면 ‘n'을 리턴
        if (a_m[snode][enode] == 1)         return 'n';
        else if (a_m[enode][snode] == 1)    return 'n';
        else {
            // 이 간선을 지나간 적이 없으면 이 번에 지나가면서
            // 지나간 것을 표시 (양 방향)
            a_m[snode][enode] = 1;
            a_m[enode][snode] = 1;
        }
    }

    return 'y';
}
```
(주어진 main 실행 결과: Cycle?: Yes) (key)
- 변형 값: 없음
- 전사 기록:

8. 그래프에서 주어진 경로가 사이클(cycle)인지를 확인하는 check_cycle() 함수를 구현하시오. check_cycle() 함수는 (무방향 그래프)인접행렬과 주어진 경로를 받아서 주어진 경로가 사이클(cycle)이면 문자 y를 반환하고 아니면 문자 n을 반환하는 함수. [6 points]
사이클(cycle): 단순경로의 시작정점과 종료정점이 동일한 경로.

```c
#include <stdio.h>
#include <string.h>
char check_cycle(int adj_matrix[6][6], char *path) {
    /* 빈칸: 함수 본문 */
}

int main(){
    int i, n;
    int adj_matrix[6][6] = {
    { 0, 0, 1, 0, 1, 0 },
    { 0, 0, 1, 0, 0, 0 },
    { 1, 1, 0, 1, 1, 0 },
    { 0, 0, 1, 0, 1, 1 },
    { 1, 0, 1, 1, 0, 0 },
    { 0, 0, 0, 1, 0, 0 } };

    if ( check_cycle(adj_matrix, "0240") == 'y' )
        printf("Cycle?: Yes");
    else
        printf("Cycle?: No");

    return 0;
}
```

**원본 답:**

```c
char check_cycle(int adj_matrix[6][6], char *path) {
    int len, i, snode, enode;
    int a_m[6][6] = { 0 };  //간선을 지나간 적이 있는지 체크하기 위해서 사용

    len = strlen(path);

    // 시작정점과 종료정점이 다르면 ‘n'을 리턴
    if (path[0] != path[len - 1])                return 'n';

    for (i = 0; i < len - 1 ; i++){
        snode = path[i] - '0';
        enode = path[i + 1] - '0';

        // 두 정점이 연결되지 않으면 (간선이 없으면) ‘n'을 리턴
        if (adj_matrix[snode][enode] != 1)   return 'n';

        // 두 정점이 간선으로 연결되어 있지만 이 간선을 전에
        // 지나간 적이 있으면 ‘n'을 리턴
        if (a_m[snode][enode] == 1)         return 'n';
        else if (a_m[enode][snode] == 1)    return 'n';
        else {
            // 이 간선을 지나간 적이 없으면 이 번에 지나가면서
            // 지나간 것을 표시 (양 방향)
            a_m[snode][enode] = 1;
            a_m[enode][snode] = 1;
        }
    }

    return 'y';
}
```
(주어진 main 실행 결과: Cycle?: Yes)

- 재계산 정답(answers.py, manifest answer): Cycle?: Yes (0-2, 2-4, 4-0 간선이 모두 있고 시작=끝, 간선·정점 반복 없음)

## textbook-ch10-q02  (manifest id p4, variant false, source_kind textbook)
- original_id: ch10-q02
- source_refs: [{"source_id": "s10", "pdf_page": 1, "book_page": 392}]
- JSON: 교과서/10_그래프 I_연습문제.json sha256 7829bc23a66c258a4e9b350940bdc70c4167f8f950537d6fc8c2228629e47fd9
- 검증 payload: review.status=verified (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "인접 행렬이 {0,1,0,0}, {1,0,1,1}, {0,1,0,0}, {0,1,0,0} 이라면 여기에 대응되는 인접 리스트를 그려라."}]
- options: []
- 직접 계산한 정답(answers.py): 0 → 1 → NULL; 1 → 0 → 2 → 3 → NULL; 2 → 1 → NULL; 3 → 1 → NULL
- textbook_blocks.render_question(catalog,'ch10-q02',prefix='p4-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p4-prob'로 다시 렌더):

```html
<p>인접 행렬이 {0,1,0,0}, {1,0,1,1}, {0,1,0,0}, {0,1,0,0} 이라면 여기에 대응되는 인접 리스트를 그려라.</p><div class="options"></div>
```

## textbook-ch10-q03  (manifest id p5, variant false, source_kind textbook)
- original_id: ch10-q03
- source_refs: [{"source_id": "s10", "pdf_page": 1, "book_page": 392}]
- JSON: 교과서/10_그래프 I_연습문제.json sha256 7829bc23a66c258a4e9b350940bdc70c4167f8f950537d6fc8c2228629e47fd9
- 검증 payload: review.status=verified (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "정점의 개수를 n, 간선의 개수를 e라고 할 때, 인접 행렬에서 특정 정점의 차수를 계산하는 연산의 시간 복잡도는?"}]
- options: [{"label": "1", "content": [{"type": "text", "text": "O(log₂ n)"}]}, {"label": "2", "content": [{"type": "text", "text": "O(n)"}]}, {"label": "3", "content": [{"type": "text", "text": "O(n+e)"}]}, {"label": "4", "content": [{"type": "text", "text": "O(e)"}]}]
- 직접 계산한 정답(answers.py): ② O(n)
- textbook_blocks.render_question(catalog,'ch10-q03',prefix='p5-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p5-prob'로 다시 렌더):

```html
<p>정점의 개수를 n, 간선의 개수를 e라고 할 때, 인접 행렬에서 특정 정점의 차수를 계산하는 연산의 시간 복잡도는?</p><div class="options"><div class="option"><p>(1)</p><p>O(log₂ n)</p></div><div class="option"><p>(2)</p><p>O(n)</p></div><div class="option"><p>(3)</p><p>O(n+e)</p></div><div class="option"><p>(4)</p><p>O(e)</p></div></div>
```

## textbook-ch10-q04  (manifest id p6, variant false, source_kind textbook)
- original_id: ch10-q04
- source_refs: [{"source_id": "s10", "pdf_page": 1, "book_page": 392}]
- JSON: 교과서/10_그래프 I_연습문제.json sha256 7829bc23a66c258a4e9b350940bdc70c4167f8f950537d6fc8c2228629e47fd9
- 검증 payload: review.status=verified (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "정점의 개수를 n, 간선의 개수가 e인 그래프를 인접 리스트로 표현하였을 경우, 인접 리스트 상의 총 노드의 개수는?"}]
- options: [{"label": "1", "content": [{"type": "text", "text": "e개"}]}, {"label": "2", "content": [{"type": "text", "text": "2e개"}]}, {"label": "3", "content": [{"type": "text", "text": "n개"}]}, {"label": "4", "content": [{"type": "text", "text": "2n개"}]}]
- 직접 계산한 정답(answers.py): ② 2e개
- textbook_blocks.render_question(catalog,'ch10-q04',prefix='p6-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p6-prob'로 다시 렌더):

```html
<p>정점의 개수를 n, 간선의 개수가 e인 그래프를 인접 리스트로 표현하였을 경우, 인접 리스트 상의 총 노드의 개수는?</p><div class="options"><div class="option"><p>(1)</p><p>e개</p></div><div class="option"><p>(2)</p><p>2e개</p></div><div class="option"><p>(3)</p><p>n개</p></div><div class="option"><p>(4)</p><p>2n개</p></div></div>
```

## textbook-ch10-q06  (manifest id p7, variant false, source_kind textbook)
- original_id: ch10-q06
- source_refs: [{"source_id": "s10", "pdf_page": 1, "book_page": 392}]
- JSON: 교과서/10_그래프 I_연습문제.json sha256 7829bc23a66c258a4e9b350940bdc70c4167f8f950537d6fc8c2228629e47fd9
- 검증 payload: review.status=verified (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "다음 그래프를 인접 행렬과 인접 리스트로 표현해보자."}, {"type": "figure", "asset_id": "ch10-q06-graph"}]
- options: []
- 직접 계산한 정답(answers.py): matrix 0 1 0 0 1 / 1 0 1 1 0 / 0 1 0 0 1 / 0 1 0 0 1 / 1 0 1 1 0 | list v0 → v1 → v4 → NULL; v1 → v0 → v2 → v3 → NULL; v2 → v1 → v4 → NULL; v3 → v1 → v4 → NULL; v4 → v0 → v2 → v3 → NULL
- textbook_blocks.render_question(catalog,'ch10-q06',prefix='p7-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p7-prob'로 다시 렌더):

```html
<p>다음 그래프를 인접 행렬과 인접 리스트로 표현해보자.</p><figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 430" role="img" aria-label="원문의 그래프" style="background:white;width:800px;max-width:none;height:auto"><title>원문의 그래프</title><g id="p7-orig-1-ch10-q06-graph-e0"><line x1="380" y1="70" x2="130" y2="190" stroke="#26394a" stroke-width="2" /><text x="255.0" y="118.0" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e0</text></g><g id="p7-orig-1-ch10-q06-graph-e1"><line x1="130" y1="190" x2="610" y2="150" stroke="#26394a" stroke-width="2" /><text x="370.0" y="158.0" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e1</text></g><g id="p7-orig-1-ch10-q06-graph-e2"><line x1="130" y1="190" x2="290" y2="350" stroke="#26394a" stroke-width="2" /><text x="210.0" y="258.0" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e2</text></g><g id="p7-orig-1-ch10-q06-graph-e3"><line x1="290" y1="350" x2="510" y2="320" stroke="#26394a" stroke-width="2" /><text x="400.0" y="323.0" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e3</text></g><g id="p7-orig-1-ch10-q06-graph-e4"><line x1="610" y1="150" x2="510" y2="320" stroke="#26394a" stroke-width="2" /><text x="560.0" y="223.0" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e4</text></g><g id="p7-orig-1-ch10-q06-graph-e5"><path d="M 380 70 Q 924.0970726666814 -54.130477786674334 510 320" fill="none" stroke="#26394a" stroke-width="2" /><text x="710" y="105" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e5</text></g><g id="p7-orig-1-ch10-q06-graph-v0"><circle cx="380" cy="70" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="380" y="70" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">v0</text></g><g id="p7-orig-1-ch10-q06-graph-v1"><circle cx="130" cy="190" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="130" y="190" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">v1</text></g><g id="p7-orig-1-ch10-q06-graph-v2"><circle cx="610" cy="150" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="610" y="150" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">v2</text></g><g id="p7-orig-1-ch10-q06-graph-v3"><circle cx="290" cy="350" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="290" y="350" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">v3</text></g><g id="p7-orig-1-ch10-q06-graph-v4"><circle cx="510" cy="320" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="510" y="320" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">v4</text></g></svg></div><figcaption>원문의 그래프 · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure><div class="options"></div>
```

- 문제 영역용 렌더(prefix p7-prob):

```html
<p>다음 그래프를 인접 행렬과 인접 리스트로 표현해보자.</p><figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 430" role="img" aria-label="원문의 그래프" style="background:white;width:800px;max-width:none;height:auto"><title>원문의 그래프</title><g id="p7-prob-1-ch10-q06-graph-e0"><line x1="380" y1="70" x2="130" y2="190" stroke="#26394a" stroke-width="2" /><text x="255.0" y="118.0" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e0</text></g><g id="p7-prob-1-ch10-q06-graph-e1"><line x1="130" y1="190" x2="610" y2="150" stroke="#26394a" stroke-width="2" /><text x="370.0" y="158.0" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e1</text></g><g id="p7-prob-1-ch10-q06-graph-e2"><line x1="130" y1="190" x2="290" y2="350" stroke="#26394a" stroke-width="2" /><text x="210.0" y="258.0" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e2</text></g><g id="p7-prob-1-ch10-q06-graph-e3"><line x1="290" y1="350" x2="510" y2="320" stroke="#26394a" stroke-width="2" /><text x="400.0" y="323.0" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e3</text></g><g id="p7-prob-1-ch10-q06-graph-e4"><line x1="610" y1="150" x2="510" y2="320" stroke="#26394a" stroke-width="2" /><text x="560.0" y="223.0" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e4</text></g><g id="p7-prob-1-ch10-q06-graph-e5"><path d="M 380 70 Q 924.0970726666814 -54.130477786674334 510 320" fill="none" stroke="#26394a" stroke-width="2" /><text x="710" y="105" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="19" fill="#17212b">e5</text></g><g id="p7-prob-1-ch10-q06-graph-v0"><circle cx="380" cy="70" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="380" y="70" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">v0</text></g><g id="p7-prob-1-ch10-q06-graph-v1"><circle cx="130" cy="190" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="130" y="190" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">v1</text></g><g id="p7-prob-1-ch10-q06-graph-v2"><circle cx="610" cy="150" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="610" y="150" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">v2</text></g><g id="p7-prob-1-ch10-q06-graph-v3"><circle cx="290" cy="350" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="290" y="350" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">v3</text></g><g id="p7-prob-1-ch10-q06-graph-v4"><circle cx="510" cy="320" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="510" y="320" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">v4</text></g></svg></div><figcaption>원문의 그래프 · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure><div class="options"></div>
```

## textbook-ch10-q08  (manifest id p8, variant false, source_kind textbook)
- original_id: ch10-q08
- source_refs: [{"source_id": "s10", "pdf_page": 2, "book_page": 393}]
- JSON: 교과서/10_그래프 I_연습문제.json sha256 7829bc23a66c258a4e9b350940bdc70c4167f8f950537d6fc8c2228629e47fd9
- 검증 payload: review.status=verified (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "정점 V={1,2,3,4,5}이고, 간선 E={<1,2>, <1,3>, <1,4>, <2,1>, <2,3>, <2,5>, <3,1>, <3,2>, <3,4>, <3,5>, <4,2>, <5,1>, <5,3>}으로 정의되는 방향 그래프를 그려라."}]
- options: []
- 직접 계산한 정답(answers.py): out 1 → 2, 3, 4; 2 → 1, 3, 5; 3 → 1, 2, 4, 5; 4 → 2; 5 → 1, 3 | 양방향 쌍 [(1, 2), (1, 3), (2, 3), (3, 5)] | 한 방향만 [(1, 4), (2, 5), (3, 4), (4, 2), (5, 1)]
- textbook_blocks.render_question(catalog,'ch10-q08',prefix='p8-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p8-prob'로 다시 렌더):

```html
<p>정점 V={1,2,3,4,5}이고, 간선 E={&lt;1,2&gt;, &lt;1,3&gt;, &lt;1,4&gt;, &lt;2,1&gt;, &lt;2,3&gt;, &lt;2,5&gt;, &lt;3,1&gt;, &lt;3,2&gt;, &lt;3,4&gt;, &lt;3,5&gt;, &lt;4,2&gt;, &lt;5,1&gt;, &lt;5,3&gt;}으로 정의되는 방향 그래프를 그려라.</p><div class="options"></div>
```

## textbook-ch10-q09  (manifest id p9, variant false, source_kind textbook)
- original_id: ch10-q09
- source_refs: [{"source_id": "s10", "pdf_page": 2, "book_page": 393}]
- JSON: 교과서/10_그래프 I_연습문제.json sha256 7829bc23a66c258a4e9b350940bdc70c4167f8f950537d6fc8c2228629e47fd9
- 검증 payload: review.status=verified (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "크기가 n×n인 방향 그래프 a가 n×n 인접 배열을 사용하여 표현되어 있다."}, {"type": "subquestions", "items": [{"id": "ch10-q09-s01", "label": "1", "content": [{"type": "text", "text": "주어진 정점의 진출차수(out-degree)을 계산하는 함수를 작성하라. 진출차수란 어떤 정점에서 출발하여 외부가 나가는 간선의 개수이다. 이 함수의 시간 복잡도는?"}]}, {"id": "ch10-q09-s02", "label": "2", "content": [{"type": "text", "text": "주어진 정점의 진입차수(in-degree)을 계산하는 함수를 작성하라. 진입차수란 어떤 정점으로 들어오는 간선의 개수이다. 이 함수의 시간 복잡도는?"}]}, {"id": "ch10-q09-s03", "label": "3", "content": [{"type": "text", "text": "그래프 안에 있는 간선들의 개수를 계산하는 함수를 작성하라. 이 함수의 시간 복잡도는?"}]}]}]
- options: []
- 직접 계산한 정답(answers.py): 1) 진출차수: j=0..n-1 의 a[v][j] 합, O(n) 2) 진입차수: i=0..n-1 의 a[i][v] 합, O(n) 3) 간선 수: 행렬 전체 합, O(n^2) (무방향 그래프라면 합/2)
- textbook_blocks.render_question(catalog,'ch10-q09',prefix='p9-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p9-prob'로 다시 렌더):

```html
<p>크기가 n×n인 방향 그래프 a가 n×n 인접 배열을 사용하여 표현되어 있다.</p><div class="subquestions"><div><p>(1)</p><p>주어진 정점의 진출차수(out-degree)을 계산하는 함수를 작성하라. 진출차수란 어떤 정점에서 출발하여 외부가 나가는 간선의 개수이다. 이 함수의 시간 복잡도는?</p></div><div><p>(2)</p><p>주어진 정점의 진입차수(in-degree)을 계산하는 함수를 작성하라. 진입차수란 어떤 정점으로 들어오는 간선의 개수이다. 이 함수의 시간 복잡도는?</p></div><div><p>(3)</p><p>그래프 안에 있는 간선들의 개수를 계산하는 함수를 작성하라. 이 함수의 시간 복잡도는?</p></div></div><div class="options"></div>
```

## textbook-ch10-q11  (manifest id p10, variant false, source_kind textbook)
- original_id: ch10-q11
- source_refs: [{"source_id": "s10", "pdf_page": 2, "book_page": 393}]
- JSON: 교과서/10_그래프 I_연습문제.json sha256 7829bc23a66c258a4e9b350940bdc70c4167f8f950537d6fc8c2228629e47fd9
- 검증 payload: review.status=verified (원문 검수일 뿐 정답 검증 아님)
- content: [{"type": "text", "text": "3개, 4개, 5개의 정점으로 된 무방향 완전 그래프를 그려보라. n개의 정점을 갖는 완전 그래프의 간선의 개수가 n(n−1)/2인지를 확인하라."}]
- options: []
- 직접 계산한 정답(answers.py): 3정점 3개, 4정점 6개, 5정점 10개
- textbook_blocks.render_question(catalog,'ch10-q11',prefix='p10-orig') 결과(원문 영역에 그대로 사용, 문제 영역에도 그림을 넣으면 prefix 'p10-prob'로 다시 렌더):

```html
<p>3개, 4개, 5개의 정점으로 된 무방향 완전 그래프를 그려보라. n개의 정점을 갖는 완전 그래프의 간선의 개수가 n(n−1)/2인지를 확인하라.</p><div class="options"></div>
```
## lecture-s10-p3-konigsberg  (manifest id p11, source_kind lecture-code)
- 근거: Software_10_Graph.pdf PDF 3쪽(그래프 역사: 쾨니히스베르크 다리 그림 (a)와 그래프 표현 (b), "오일러 경로: 정점에 연결된 간선의 개수가 짝수이면 존재"), 추가 근거 7쪽(차수 = 그 정점에 연결된 간선/인접 정점의 개수). 1116 STT Part 04–05에서 "모든 다리를 한 번만 건너 처음 출발한 곳으로 돌아올 수 있을까", 위치→정점, 다리→간선, "짝수이면 존재, 홀수이면 아무리 해도 못 찾는다"를 설명.
- 그림 (b)의 간선(다리 이름): A–C 두 개(c, d), A–B 두 개(a, b), A–D 하나(e), C–D 하나(g), B–D 하나(f). 땅 A는 섬(Kneiphof), B·C·D는 강가 땅.
- 카드는 standalone: 문제 본문에 위 다리 목록(또는 자체로 그린 SVG 그래프)을 직접 싣는다. 슬라이드·정리노트를 가리키지 않는다. 출처는 배지 문단 `<p><span class="badge">강의 예제 기반 자체 출제</span> S10 p3</p>`와 `details.original`(summary "강의 예제 보기")에만. 추가 근거 p7은 original 안에만.
- 자체 질문(예): (a) 땅을 정점, 다리를 간선으로 보고 정점·간선 수 (b) 각 정점의 차수 (c) 모든 다리를 한 번씩만 건너 출발한 곳으로 돌아올 수 있는지와 이유 (d) 다리를 하나 더 놓거나 하나 없애서 가능하게 하려면 최소 몇 개를 바꿔야 하는지는 묻지 않는다(범위 밖 일반화). 
- 정답(answers.py, 전수 탐색으로 불가능 확인): 정점 4개(A·B·C·D), 간선 7개, 차수 A=5 B=3 C=3 D=3, 홀수 차수 정점 4개 -> 불가능. 슬라이드 문구는 "오일러 경로"지만 이 문제(출발점으로 돌아오기)는 엄밀히 오일러 회로이며, 모든 정점 차수가 짝수(그리고 그래프가 이어져 있음)여야 한다는 점을 풀이에 한 줄 보충으로 밝힌다.
