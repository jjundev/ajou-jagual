# 1119 문항 원문 (메인 에이전트 작성)

## 2016-final-ljw-q6  (manifest id p1, variant false)
- 원본: 2016 기말 6번 · 10점 · 이정원 — 자료구조및알고리즘이해 기출 소스/자료구조및알고리즘 기말 (2016이정원)/
- 문제 글: 6. 다음 그래프의 DFS(0) spanning tree와 BFS(0) spanning tree를 그려라. (* DFS(0)은 0번 노드로부터 시작한 깊이우선 신장트리, BFS(0)은 0번으로부터 시작한 너비우선 신장트리를 말하며, edge의 우선순위는 반드시 vertex 번호가 작은 것을 먼저 처리한다.) (10점)

[그림: 무방향 그래프, 정점 0~7. 간선 0-1, 0-2, 1-3, 1-4, 2-5, 2-6, 3-7, 4-7, 5-7, 6-7]

| DFS(0) spanning tree | BFS(0) spanning tree |
|---|---|
- 그림: 정점 0~7 무방향 그래프(0-1,0-2,1-3,1-4,2-5,2-6,3-7,4-7,5-7,6-7)와 답을 그릴 빈 2칸 표
- 은행 정답: DFS(0) 방문 순서 0,1,3,7,4,5,2,6 — 신장트리 간선 0-1, 1-3, 3-7, 7-4, 7-5, 5-2, 2-6. BFS(0) 방문 순서 0,1,2,3,4,5,6,7 — 신장트리 간선 0-1, 0-2, 1-3, 1-4, 2-5, 2-6, 3-7. (verified)
- 변형 값: 없음
- 전사 기록:

6. 다음 그래프의 DFS(0) spanning tree와 BFS(0) spanning tree를 그려라. (* DFS(0)은 0번 노드로부터 시작한 깊이우선 신장트리, BFS(0)은 0번으로부터 시작한 너비우선 신장트리를 말하며, edge의 우선순위는 반드시 vertex 번호가 작은 것을 먼저 처리한다.) (10점)

[그림: 무방향 그래프, 정점 0~7. 간선 0-1, 0-2, 1-3, 1-4, 2-5, 2-6, 3-7, 4-7, 5-7, 6-7]

| DFS(0) spanning tree | BFS(0) spanning tree |
|---|---|

학생 답안(채점됨): DFS: 0-1, 1-3, 3-7, 7-4, 7-5, 5-2, 2-6 / BFS: 0-1, 0-2, 1-3, 1-4, 2-5, 2-6, 3-7 (각 5점)

- 재계산 정답(answers.py, manifest answer): DFS(0) 방문 순서 0, 1, 3, 7, 4, 5, 2, 6 / 트리 간선 0-1, 1-3, 3-7, 7-4, 7-5, 5-2, 2-6 | BFS(0) 방문 순서 0, 1, 2, 3, 4, 5, 6, 7 / 트리 간선 0-1, 0-2, 1-3, 1-4, 2-5, 2-6, 3-7

## 2015-ljw-q6  (manifest id p2, variant false)
- 원본: 2015 미상 6번 · 10점 · 이정원 — 자료구조및알고리즘이해 기출 소스/자료구조및알고리즘 2015기출(이정원).pdf
- 문제 글: 6. 다음 그래프의 DFS(0) spanning tree와 BFS(0) spanning tree를 그려라. edge에 지그재그 선으로 진하게 나타내어라. (* DFS(0)은 0번 노드로부터 시작한 깊이우선 신장트리, BFS(0)은 0번으로부터 시작한 너비우선 신장트리를 말하며, edge의 우선순위는 반드시 vertex 번호가 작은 것을 먼저 처리한다.) (10점)
[그림: 무방향 그래프, 정점 0~7. 간선: 0-2, 0-5, 0-7, 1-7, 2-6, 3-4, 3-5, 4-5, 4-6, 4-7]
| DFS(0) spanning tree | BFS(0) spanning tree |
|---|---|
| [그림: 같은 그래프] | [그림: 같은 그래프] |
- 그림: 정점 0~7, 간선 10개 무방향 그래프
- 은행 정답: DFS(0): 방문 순서 0, 2, 6, 4, 3, 5, 7, 1 / 트리 간선 0-2, 2-6, 6-4, 4-3, 3-5, 4-7, 7-1
BFS(0): 방문 순서 0, 2, 5, 7, 6, 3, 4, 1 / 트리 간선 0-2, 0-5, 0-7, 2-6, 5-3, 5-4, 7-1 (key)
- 변형 값: 없음
- 전사 기록:

6. 다음 그래프의 DFS(0) spanning tree와 BFS(0) spanning tree를 그려라. edge에 지그재그 선으로 진하게 나타내어라. (* DFS(0)은 0번 노드로부터 시작한 깊이우선 신장트리, BFS(0)은 0번으로부터 시작한 너비우선 신장트리를 말하며, edge의 우선순위는 반드시 vertex 번호가 작은 것을 먼저 처리한다.) (10점)
[그림: 무방향 그래프, 정점 0~7. 간선: 0-2, 0-5, 0-7, 1-7, 2-6, 3-4, 3-5, 4-5, 4-6, 4-7]
| DFS(0) spanning tree | BFS(0) spanning tree |
|---|---|
| [그림: 같은 그래프] | [그림: 같은 그래프] |

**원본 답:** DFS(0): 방문 순서 0, 2, 6, 4, 3, 5, 7, 1 / 트리 간선 0-2, 2-6, 6-4, 4-3, 3-5, 4-7, 7-1
BFS(0): 방문 순서 0, 2, 5, 7, 6, 3, 4, 1 / 트리 간선 0-2, 0-5, 0-7, 2-6, 5-3, 5-4, 7-1

- 재계산 정답(answers.py, manifest answer): DFS(0) 방문 순서 0, 2, 6, 4, 3, 5, 7, 1 / 트리 간선 0-2, 2-6, 6-4, 4-3, 3-5, 4-7, 7-1 | BFS(0) 방문 순서 0, 2, 5, 7, 6, 3, 4, 1 / 트리 간선 0-2, 0-5, 0-7, 2-6, 5-3, 5-4, 7-1

## 2017-final-kdh-q3  (manifest id p3, variant false)
- 원본: 2017 기말 3번 · 3점 · 김도희 — 자료구조및알고리즘이해 기출 소스/자료구조및알고리즘_기말고사 (모범답안), 2017 김도희.pdf
- 문제 글: 3. 다음은 어떤 무방향그래프(undirected graph)를 인접리스트(adjacency list)로 표현한 것이다. 이것을 이용하여 정점 0에서부터 시작하여 breadth-first-search(너비 우선 탐색)을 하고 노드 방문순서를 적으시오. [3 points]

[그림: 인접리스트
0 → (1) → (5)
1 → (0) → (5) → (2)
2 → (1) → (3)
3 → (2) → (4) → (5)
4 → (3) → (5)
5 → (0) → (1) → (3) → (4)]

노드 방문순서 :
- 그림: 정점 0~5 무방향 그래프의 인접리스트 상자
- 은행 정답: 노드 방문순서 : 0, 1, 5, 2, 3, 4 (key)
- 변형 값: 없음
- 전사 기록:

3. 다음은 어떤 무방향그래프(undirected graph)를 인접리스트(adjacency list)로 표현한 것이다. 이것을 이용하여 정점 0에서부터 시작하여 breadth-first-search(너비 우선 탐색)을 하고 노드 방문순서를 적으시오. [3 points]

[그림: 인접리스트
0 → (1) → (5)
1 → (0) → (5) → (2)
2 → (1) → (3)
3 → (2) → (4) → (5)
4 → (3) → (5)
5 → (0) → (1) → (3) → (4)]

노드 방문순서 :

**원본 답:**

노드 방문순서 : 0, 1, 5, 2, 3, 4

- 재계산 정답(answers.py, manifest answer): 노드 방문순서 : 0, 1, 5, 2, 3, 4

## 2017-final-kdh-q7  (manifest id p4, variant false)
- 원본: 2017 기말 7번 · 5점 · 김도희 — 자료구조및알고리즘이해 기출 소스/자료구조및알고리즘_기말고사 (모범답안), 2017 김도희.pdf
- 문제 글: 7. 다음의 코드에서 connected_graph 함수를 구현하시오. connected_graph 함수는 (무방향 그래프를 나타내는) 인접행렬을 받아서 그래프가 연결그래프(connected graph)이면 문자 y를 반환하고 연결그래프가 아니면 문자 n을 반환하는 함수. [5 points]

```c
#include <stdio.h>
#define MAX_SIZE 6
char connected_graph( int adj_matrix[MAX_SIZE][MAX_SIZE] ) {

}
int main(){
	int adj_matrix[MAX_SIZE][MAX_SIZE] = { ..... };
	printf( "Graph is connected?(y/n): %c \n", connected_graph(adj_matrix) );
	return 0;
}
```
- 그림: 없음
- 은행 정답: 모범답안 코드는 level_nodes_count를 노드마다 0으로 되돌려, 한 레벨의 마지막 노드가 새 이웃이 없으면 탐색을 멈춘다(0-1,0-2,1-3,3-4,4-5 (2는 막다른 노드): 모범답안 n / 정답 y). 큐 BFS로 고친 답:
```c
char connected_graph( int adj_matrix[MAX_SIZE][MAX_SIZE] ) {
	int queue[MAX_SIZE], visited[MAX_SIZE] = { 0 };
	int front = 0, rear = 0, v, j, count = 0;
	queue[rear++] = 0;
	visited[0] = 1;
	while (front < rear) {
		v = queue[front++];
		count++;
		for (j = 0; j < MAX_SIZE; j++)
			if (adj_matrix[v][j] && !visited[j]) {
				visited[j] = 1;
				queue[rear++] = j;
			}
	}
	return (count == MAX_SIZE) ? 'y' : 'n';
}
``` (verified)
- 변형 값: 없음
- 전사 기록:

7. 다음의 코드에서 connected_graph 함수를 구현하시오. connected_graph 함수는 (무방향 그래프를 나타내는) 인접행렬을 받아서 그래프가 연결그래프(connected graph)이면 문자 y를 반환하고 연결그래프가 아니면 문자 n을 반환하는 함수. [5 points]

```c
#include <stdio.h>
#define MAX_SIZE 6
char connected_graph( int adj_matrix[MAX_SIZE][MAX_SIZE] ) {

}
int main(){
	int adj_matrix[MAX_SIZE][MAX_SIZE] = { ..... };
	printf( "Graph is connected?(y/n): %c \n", connected_graph(adj_matrix) );
	return 0;
}
```

**원본 답:**

* 모든 코드를 실행을 시켜서 채점을 함.
* 논리적인 부분에서는 연결/비연결 그래프를 구분하지 못하면 감점
(예, 노드 0,1,2,5 만 서로 연결되어 있고 노드 3,4만 서로 연결되어 있는 경우. 이 경우도 전체적으로 그래프가 연결이 되지 않아서 비연결그래프로 구분해야 됨.)
* 문법적인 오류에 대해서도 감점

```c
char connected_graph( int adj_matrix[MAX_SIZE][MAX_SIZE] ) {
	int j, node, level_num=0, level_nodes_count=1, sum = 0;
	int level[MAX_SIZE][MAX_SIZE] = { 0 };
	int visited[MAX_SIZE] = { 0 };

	level[level_num][0] = 1;
	visited[0] = 1;
	while (level_nodes_count > 0){
		for (node = 0; node < MAX_SIZE; node++){
			if ( level[level_num][node] == 1 ){
				level_nodes_count = 0;
				for (j = 0; j < MAX_SIZE; j++)
				if ( adj_matrix[node][j] && !visited[j] ) {
					level[level_num + 1][j] = 1;
					level_nodes_count++;
					visited[j] = 1;
				}
			}
		}
		level_num++;
	}
	for (j = 0; j < MAX_SIZE; j++) sum += visited[j];

	if (sum == MAX_SIZE) return 'y';
	else                 return 'n';
}
```

- 재계산 정답(answers.py, manifest answer): 큐 BFS(또는 DFS)로 0에서 도달한 정점 수가 MAX_SIZE이면 'y', 아니면 'n' | 실행: Graph is connected?(y/n): y  / Graph is connected?(y/n): n

## 2019-final-q1  (manifest id p5, variant false)
- 원본: 2019 기말 1번 · 2점 · 출제자 미상 — 자구알 기출/19-1 기말 복원.hwp
- 문제 글: 1. 간선에 비용이나 가중치가 할당된 그래프를 (          ) 라고 한다. (2점)
- 그림: 없음
- 은행 정답: 가중치 그래프 (key)
- 변형 값: 없음
- 전사 기록:

1. 간선에 비용이나 가중치가 할당된 그래프를 (          ) 라고 한다. (2점)

**원본 답:** 가중치 그래프

- 재계산 정답(answers.py, manifest answer): 가중치 그래프

## textbook-ch10-q05  (manifest id p6, variant false, 교과서)
- original_id: ch10-q05 · 장: ch10 그래프 I · 문항 05 · kind choice
- source_refs: [{"source_id": "s10", "pdf_page": 1, "book_page": 392}]
- review: verified payload_sha256 94b47a96b6c9b1775c421b69708a99782b02dabf19f26331ab45a5bbca4d959f
- issues: []
- content/options 원문 JSON:
```json
{
 "content": [
  {
   "type": "text",
   "text": "다음 중 큐를 사용하는 알고리즘은?"
  }
 ],
 "options": [
  {
   "label": "1",
   "content": [
    {
     "type": "text",
     "text": "깊이 우선 탐색"
    }
   ]
  },
  {
   "label": "2",
   "content": [
    {
     "type": "text",
     "text": "너비 우선 탐색"
    }
   ]
  },
  {
   "label": "3",
   "content": [
    {
     "type": "text",
     "text": "최단 거리 알고리즘"
    }
   ]
  },
  {
   "label": "4",
   "content": [
    {
     "type": "text",
     "text": "최소 비용 신장 트리"
    }
   ]
  }
 ]
}
```
- textbook_blocks.render_question(prefix='p6') 렌더링 (문제와 원문에 둘 다 넣을 때는 prefix를 'p6-q'·'p6-o'처럼 달리 해서 다시 렌더링):
```html
<p>다음 중 큐를 사용하는 알고리즘은?</p><div class="options"><div class="option"><p>(1)</p><p>깊이 우선 탐색</p></div><div class="option"><p>(2)</p><p>너비 우선 탐색</p></div><div class="option"><p>(3)</p><p>최단 거리 알고리즘</p></div><div class="option"><p>(4)</p><p>최소 비용 신장 트리</p></div></div>
```
- 재계산 정답(answers.py): ② 너비 우선 탐색

## textbook-ch10-q13  (manifest id p7, variant false, 교과서)
- original_id: ch10-q13 · 장: ch10 그래프 I · 문항 13 · kind mixed
- source_refs: [{"source_id": "s10", "pdf_page": 3, "book_page": null}]
- review: verified payload_sha256 247e392af53a7e988dcba271327af033d391393092dfa2ea0bf594ad68509f78
- issues: []
- content/options 원문 JSON:
```json
{
 "content": [
  {
   "type": "text",
   "text": "다음의 그래프에 대하여 답하라. 그래프는 인접행렬로 표현되어 있다고 가정하라."
  },
  {
   "type": "figure",
   "asset_id": "ch10-q13-graph"
  },
  {
   "type": "subquestions",
   "items": [
    {
     "id": "ch10-q13-s01",
     "label": "1",
     "content": [
      {
       "type": "text",
       "text": "정점 3에서 출발하여 깊이 우선탐색했을 경우의 방문순서"
      }
     ]
    },
    {
     "id": "ch10-q13-s02",
     "label": "2",
     "content": [
      {
       "type": "text",
       "text": "정점 6에서 출발하여 깊이 우선탐색했을 경우의 방문순서"
      }
     ]
    },
    {
     "id": "ch10-q13-s03",
     "label": "3",
     "content": [
      {
       "type": "text",
       "text": "정점 3에서 출발하여 너비 우선탐색했을 경우의 방문순서"
      }
     ]
    },
    {
     "id": "ch10-q13-s04",
     "label": "4",
     "content": [
      {
       "type": "text",
       "text": "정점 6에서 출발하여 너비 우선탐색했을 경우의 방문순서"
      }
     ]
    }
   ]
  }
 ],
 "options": []
}
```
- textbook_blocks.render_question(prefix='p7') 렌더링 (문제와 원문에 둘 다 넣을 때는 prefix를 'p7-q'·'p7-o'처럼 달리 해서 다시 렌더링):
```html
<p>다음의 그래프에 대하여 답하라. 그래프는 인접행렬로 표현되어 있다고 가정하라.</p><figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" role="img" aria-label="원문의 그래프" style="background:white;width:800px;max-width:none;height:auto"><title>원문의 그래프</title><g id="p7-1-ch10-q13-graph-e0"><line x1="240" y1="50" x2="240" y2="145" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-e1"><line x1="240" y1="145" x2="150" y2="235" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-e2"><line x1="240" y1="145" x2="330" y2="235" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-e3"><line x1="150" y1="235" x2="240" y2="335" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-e4"><line x1="330" y1="235" x2="240" y2="335" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-e5"><line x1="330" y1="235" x2="500" y2="235" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-e6"><line x1="500" y1="235" x2="630" y2="145" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-e7"><line x1="500" y1="235" x2="630" y2="335" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-e8"><line x1="630" y1="335" x2="630" y2="145" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-e9"><line x1="630" y1="145" x2="630" y2="50" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-e10"><line x1="630" y1="145" x2="740" y2="50" stroke="#26394a" stroke-width="2" /></g><g id="p7-1-ch10-q13-graph-0"><circle cx="240" cy="50" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="240" y="50" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">0</text></g><g id="p7-1-ch10-q13-graph-1"><circle cx="240" cy="145" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="240" y="145" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">1</text></g><g id="p7-1-ch10-q13-graph-2"><circle cx="150" cy="235" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="150" y="235" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">2</text></g><g id="p7-1-ch10-q13-graph-3"><circle cx="330" cy="235" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="330" y="235" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">3</text></g><g id="p7-1-ch10-q13-graph-4"><circle cx="240" cy="335" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="240" y="335" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">4</text></g><g id="p7-1-ch10-q13-graph-5"><circle cx="500" cy="235" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="500" y="235" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">5</text></g><g id="p7-1-ch10-q13-graph-6"><circle cx="630" cy="335" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="630" y="335" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">6</text></g><g id="p7-1-ch10-q13-graph-7"><circle cx="630" cy="145" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="630" y="145" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">7</text></g><g id="p7-1-ch10-q13-graph-8"><circle cx="630" cy="50" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="630" y="50" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">8</text></g><g id="p7-1-ch10-q13-graph-9"><circle cx="740" cy="50" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="740" y="50" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">9</text></g></svg></div><figcaption>원문의 그래프 · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure><div class="subquestions"><div><p>(1)</p><p>정점 3에서 출발하여 깊이 우선탐색했을 경우의 방문순서</p></div><div><p>(2)</p><p>정점 6에서 출발하여 깊이 우선탐색했을 경우의 방문순서</p></div><div><p>(3)</p><p>정점 3에서 출발하여 너비 우선탐색했을 경우의 방문순서</p></div><div><p>(4)</p><p>정점 6에서 출발하여 너비 우선탐색했을 경우의 방문순서</p></div></div><div class="options"></div>
```
- 재계산 정답(answers.py): 1) DFS(3): 3, 1, 0, 2, 4, 5, 6, 7, 8, 9 2) DFS(6): 6, 5, 3, 1, 0, 2, 4, 7, 8, 9 3) BFS(3): 3, 1, 4, 5, 0, 2, 6, 7, 8, 9 4) BFS(6): 6, 5, 7, 3, 8, 9, 1, 4, 0, 2

## textbook-ch10-q14  (manifest id p8, variant false, 교과서)
- original_id: ch10-q14 · 장: ch10 그래프 I · 문항 14 · kind code-write
- source_refs: [{"source_id": "s10", "pdf_page": 3, "book_page": null}]
- review: verified payload_sha256 164c7330be83dd64779d87253a8ef69080eaa0d3bea86877ba80ebcb2d1970af
- issues: []
- content/options 원문 JSON:
```json
{
 "content": [
  {
   "type": "text",
   "text": "연결된 그래프 G의 간선들 중에서 그 간선을 제거하면 연결이 끊어지는 간선 (u, v)를 브리지(bridge)라고 한다. 주어진 그래프에서 브리지를 찾아내는 함수를 작성하라."
  },
  {
   "type": "figure",
   "asset_id": "ch10-q14-graph"
  }
 ],
 "options": []
}
```
- textbook_blocks.render_question(prefix='p8') 렌더링 (문제와 원문에 둘 다 넣을 때는 prefix를 'p8-q'·'p8-o'처럼 달리 해서 다시 렌더링):
```html
<p>연결된 그래프 G의 간선들 중에서 그 간선을 제거하면 연결이 끊어지는 간선 (u, v)를 브리지(bridge)라고 한다. 주어진 그래프에서 브리지를 찾아내는 함수를 작성하라.</p><figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" role="img" aria-label="원문의 그래프" style="background:white;width:800px;max-width:none;height:auto"><title>원문의 그래프</title><g id="p8-1-ch10-q14-graph-e0"><line x1="240" y1="50" x2="240" y2="145" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-e1"><line x1="240" y1="145" x2="150" y2="235" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-e2"><line x1="240" y1="145" x2="330" y2="235" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-e3"><line x1="150" y1="235" x2="240" y2="335" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-e4"><line x1="330" y1="235" x2="240" y2="335" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-e5"><line x1="330" y1="235" x2="500" y2="235" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-e6"><line x1="500" y1="235" x2="630" y2="145" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-e7"><line x1="500" y1="235" x2="630" y2="335" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-e8"><line x1="630" y1="335" x2="630" y2="145" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-e9"><line x1="630" y1="145" x2="630" y2="50" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-e10"><line x1="630" y1="145" x2="740" y2="50" stroke="#26394a" stroke-width="2" /></g><g id="p8-1-ch10-q14-graph-0"><circle cx="240" cy="50" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="240" y="50" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">0</text></g><g id="p8-1-ch10-q14-graph-1"><circle cx="240" cy="145" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="240" y="145" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">1</text></g><g id="p8-1-ch10-q14-graph-2"><circle cx="150" cy="235" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="150" y="235" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">2</text></g><g id="p8-1-ch10-q14-graph-3"><circle cx="330" cy="235" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="330" y="235" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">3</text></g><g id="p8-1-ch10-q14-graph-4"><circle cx="240" cy="335" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="240" y="335" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">4</text></g><g id="p8-1-ch10-q14-graph-5"><circle cx="500" cy="235" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="500" y="235" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">5</text></g><g id="p8-1-ch10-q14-graph-6"><circle cx="630" cy="335" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="630" y="335" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">6</text></g><g id="p8-1-ch10-q14-graph-7"><circle cx="630" cy="145" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="630" y="145" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">7</text></g><g id="p8-1-ch10-q14-graph-8"><circle cx="630" cy="50" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="630" y="50" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">8</text></g><g id="p8-1-ch10-q14-graph-9"><circle cx="740" cy="50" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /><text x="740" y="50" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="22" fill="#17212b">9</text></g></svg></div><figcaption>원문의 그래프 · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure><div class="options"></div>
```
- 재계산 정답(answers.py): 브리지 (0, 1), (3, 5), (7, 8), (7, 9) | C 실행: (0, 1) (3, 5) (7, 8) (7, 9)

## textbook-ch11-q01  (manifest id p9, variant false, 교과서)
- original_id: ch11-q01 · 장: ch11 그래프 II · 문항 01 · kind short
- source_refs: [{"source_id": "s11", "pdf_page": 1, "book_page": 438}]
- review: verified payload_sha256 f60580f77f35bc63d14702e4c10bbee497ece4e0cd96f2fb8a305cc2bdcde58e
- issues: []
- content/options 원문 JSON:
```json
{
 "content": [
  {
   "type": "text",
   "text": "다음의 그래프에서 가능한 신장 트리를 모두 나열하라."
  },
  {
   "type": "figure",
   "asset_id": "ch11-q01-square"
  }
 ],
 "options": []
}
```
- textbook_blocks.render_question(prefix='p9') 렌더링 (문제와 원문에 둘 다 넣을 때는 prefix를 'p9-q'·'p9-o'처럼 달리 해서 다시 렌더링):
```html
<p>다음의 그래프에서 가능한 신장 트리를 모두 나열하라.</p><figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 430" role="img" aria-label="원문의 그래프" style="background:white;width:800px;max-width:none;height:auto"><title>원문의 그래프</title><g id="p9-1-ch11-q01-square-e0"><line x1="250" y1="70" x2="500" y2="70" stroke="#26394a" stroke-width="2" /></g><g id="p9-1-ch11-q01-square-e1"><line x1="500" y1="70" x2="500" y2="320" stroke="#26394a" stroke-width="2" /></g><g id="p9-1-ch11-q01-square-e2"><line x1="500" y1="320" x2="250" y2="320" stroke="#26394a" stroke-width="2" /></g><g id="p9-1-ch11-q01-square-e3"><line x1="250" y1="320" x2="250" y2="70" stroke="#26394a" stroke-width="2" /></g><g id="p9-1-ch11-q01-square-0"><circle cx="250" cy="70" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /></g><g id="p9-1-ch11-q01-square-1"><circle cx="500" cy="70" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /></g><g id="p9-1-ch11-q01-square-2"><circle cx="500" cy="320" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /></g><g id="p9-1-ch11-q01-square-3"><circle cx="250" cy="320" r="22" fill="#fff" stroke="#26394a" stroke-width="2" /></g></svg></div><figcaption>원문의 그래프 · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure><div class="options"></div>
```
- 재계산 정답(answers.py): 4개 (네 간선 중 하나씩 빼낸 경로 모양)

## lecture-s10-p17-connected-component  (manifest id p10, 강의 예제 기반 자체 출제)
- 근거: 자료구조_강의록_2026/Software_10_Graph.pdf PDF p17 (연결 성분, find_connected_component, `visited[i]=count;`), 추가 근거 p14(dfs_mat). sha256 d14a1223c5c792c7f0439a3cbdf89b0764bf3271278ce61fbb552ac793e24f10
- 수업: 1119 STT 요약 4절. 강의 예제 그래프는 간선 (0,1),(0,2),(3,4) → visited [1,1,1,2,2], count 2.
- 자체 출제 그래프: 정점 8개(0~7), 간선 (0,2),(0,5),(1,3),(2,5),(3,6),(4,6). 정점 7은 간선 없음.
- 코드(자체 harness, work/p10_component.c): dfs_mat의 `visited[v] = TRUE;`를 `visited[v] = count;`로 바꾼 것(슬라이드의 `visited[i]=count;` 지시를 반영), find_connected_component는 슬라이드 그대로. GraphType·main은 실행용으로 추가.
- 묻는 것: (a) 출력되는 정점 순서 (b) 끝난 뒤 visited 배열 (c) count
- 재계산 정답: (a) 출력 0 2 5 1 3 6 4 7 (b) visited = [1, 2, 1, 2, 2, 1, 2, 3] (c) count = 3
