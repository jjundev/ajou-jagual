# 2017-final-kdh

원본: `from_the_past/기출/자료구조및알고리즘이해 기출 소스/자료구조및알고리즘_기말고사 (모범답안), 2017 김도희.pdf`

머리: 2017년 1학기 Finalterm / Test time : 75 minutes / 자료구조및알고리즘 (70점 만점, 모범답안) / 반: C050 (화E 금E)

## 1번

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

## 2번

2. 다음 수들을 Quick sort 알고리즘을 사용하여 오름차순으로 sorting 하시오.(각 swap (자리교환)이 일어날 때마다의 과정을 반드시 적으시오). [5 points]

25, 3, 50, 72, 9, 46, 15

[그림: 첫 줄에 25 | 3 | 50 | 72 | 9 | 46 | 15 가 적힌 7칸 표, 그 아래 답을 적는 빈 줄]

**원본 답:**

| 25 | 3 | 50 | 72 | 9 | 46 | 15 |
| 25 | 3 | 15 | 72 | 9 | 46 | 50 |
| 25 | 3 | 15 | 9 | 72 | 46 | 50 |
| 9 | 3 | 15 | 25 | 72 | 46 | 50 |
| 3 | 9 | 15 | 25 | 72 | 46 | 50 |
| 3 | 9 | 15 | 25 | 50 | 46 | 72 |
| 3 | 9 | 15 | 25 | 46 | 50 | 72 |

## 3번

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

## 4번

4. 아래는 6개의 정점들(A,B,C,D,E,F)로 구성된 가중치 그래프를 인접행렬로 표현한 것이다.

|   | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| A | 0 | 4 | ∞ | ∞ | ∞ | 9 |
| B | 4 | 0 | 8 | ∞ | ∞ | 11 |
| C | ∞ | 8 | 0 | 2 | ∞ | ∞ |
| D | ∞ | ∞ | 2 | 0 | 6 | 7 |
| E | ∞ | ∞ | ∞ | 6 | 0 | 1 |
| F | 9 | 11 | ∞ | 7 | 1 | 0 |

(a.) 위 인접행렬이 나타내는 가중치 그래프를 그리시오. [5 points]

(b.) 위의 (a)에서 구해진 가중치 그래프를 가지고 Prim's algorithm을 사용하여 Minimum spanning tree(MST)를 구하시오. 정점 C에서부터 시작하며, Prim's algorithm을 사용하여 Minimum spanning tree(MST)를 만들 때, 정점과 간선들이 추가되는 순서대로 쓰시오.[5 points]

V ={ }
E ={ }

(c.) 위의 (a)에서 구해진 가중치 그래프를 가지고 최단 경로 알고리즘 (Dijkstra's algorithm)를 수행하여 정점 A에서 다른 모든 정점들로 가는 최단경로 길이를 구하시오. 즉, 시작 정점 A에서 최단경로가 발견된 정점들의 집합 S와 정점 A에서 다른 모든 정점들로의 최단경로길이를 저장하는 distance[]를 구하시오. 집합 S의 정점들이 구해지는 순서 중요.[5 points]

S ={ }

distance

| A | B | C | D | E | F |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

**원본 답:**

(a) 간선: A-B 4, A-F 9, B-C 8, B-F 11, C-D 2, D-E 6, D-F 7, E-F 1
(b) V ={ C, D, E, F, B, A }
E ={ (C, D), (D, E), (E, F), (C, B), (B, A) }
(c) S ={ A, B, F, E, C, D }
distance: A=0, B=4, C=12, D=14, E=10, F=9

## 5번

5. 다음 키들을 해쉬테이블에 저장하려고 할 때 다음 문제에 답하시오. [4 points]

66, 158, 8, 72 ,22, 24, 130, 35

해쉬 테이블은 11개의 bucket을 가지고 있고, 각 bucket은 1개의 slot을 가지고 있다고 가정하시오. 해쉬 함수(Hash function)는 h(k)=k % 11 를 사용하고, 충돌(collision) 해결기법으로는 선형조사법(linear probing)을 사용하였을 때, 해쉬테이블과 충돌횟수를 구하시오.

[그림: 첨자 0~10의 빈 해쉬테이블 칸]

충돌횟수:

**원본 답:**

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 66 | 22 | 24 | 35 | 158 |  | 72 |  | 8 | 130 |  |
충돌횟수: 2

## 6번

6. 아래의 문제들을 위해서 다음 수들을 이용하시오

55, 3, 7, 72, 9, 16

(a) 이진 탐색 트리(binary search tree)를 이용한 위의 6개의 수들을 순서대로 삽입하여 만들어진 트리를 그리시오. 또한 key 16을 찾기 위해서 방문한 노드를 적으시오 (16도 포함).[5 points]

(b) AVL 트리를 이용한 위의 6개의 수들을 순서대로 삽입하여 만들어진 트리를 그리시오. 또한 key 16을 찾기 위해서 방문한 노드를 적으시오 (16도 포함).[5 points]

**원본 답:**

(a) 트리: 55의 왼쪽 자식 3, 오른쪽 자식 72; 3의 오른쪽 자식 7; 7의 오른쪽 자식 9; 9의 오른쪽 자식 16. 레벨 순서: 55 / 3, 72 / 7 / 9 / 16
key 16을 찾기 위해서 방문한 노드들: 55, 3, 7, 9, 16
(b) * LR 회전 그리고 RL 회전을 함.
트리: 9의 왼쪽 자식 7, 오른쪽 자식 55; 7의 왼쪽 자식 3; 55의 왼쪽 자식 16, 오른쪽 자식 72. 레벨 순서: 9 / 7, 55 / 3, 16, 72
key 16을 찾기 위해서 방문한 노드들: 9, 55, 16

## 7번

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

## 8번

8. 다음의 코드에서는 배열 list는 100개의 난수들을 저장하고 있으며 배열 list에서 5번째로 큰 소수를 출력하는 프로그램을 작성하시오. 소수는 약수가 1과 자기 자신인 수.
(예: 2, 3, 5, 7,..) [8 points]

```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define MAX_SIZE 100
int main() {
int i;
int list[MAX_SIZE];

srand( (unsigned)time(NULL) );
for (i = 0; i<MAX_SIZE; i++)  list[i] = rand() % 10000+1;

return 0;
}
```

**원본 답:**

* 모든 코드를 실행을 시켜서 채점을 함.
* 논리적 및 문법적 오류 감점

```c
int j, n, most, temp, prime_flag, prime_count=0;

// 내림차순으로 정렬
for (i = 0; i < MAX_SIZE - 1; i++) {
	most = i;
	for (j = i + 1; j<MAX_SIZE; j++)
		if (list[j] > list[most]) most = j;

	temp = list[i];
	list[i] = list[most];
	list[most] = temp;
}
// 소수확인
for (i = 0; i < MAX_SIZE; i++){
	prime_flag = 1;
	for (j = 2; j < list[i]; j++)
		if (list[i] % j == 0) prime_flag = 0;

	if (prime_flag == 1) prime_count++;
	if (prime_count == 1) {
		printf("5번째 큰 소수:%d ", list[i]); break;
	}
}
```
(위 선언 줄은 int list[MAX_SIZE]; 다음에, 정렬·소수확인 부분은 rand 채우기 for문 다음·return 0; 앞에 들어간다.)
