# 복습문제 4선 — 0928 수업 범위

기존 문제 **0개**를 유지하고 교과서 문제 **4개**를 추가했어요. 먼저 풀어 보고, 막히면 힌트와 풀이를 열어 보세요.

> 원문, 힌트, 풀이는 접혀 있어요. 먼저 풀어 보고 펼쳐 보세요.

**목차**

- [D. 교과서 연습문제](#partD)
  - [P1. 배열 크기를 sizeof로 비교](#p1)
  - [P2. 복소수 구조체 더하기](#p2)
  - [P3. 구조체를 동적으로 만들고 반납](#p3)
  - [P4. 배열 접근·전체 방문의 복잡도](#p4)

<a id="partD"></a>

## D. 교과서 연습문제

<a id="p1"></a>

### P1. 배열 크기를 sizeof로 비교

다음 배열 중에서 크기가 가장 큰 배열은?

(1)

int array1[10];

(2)

double array2[10];

(3)

char array3[40];

(4)

float array4[10];

비교 기준: 이 팩의 C 검산 환경은 int 4, double 8, char 1, float 4바이트예요.

<details><summary>교과서 원문 보기</summary>

3장 배열, 구조체, 포인터 · 03번 · 책 98쪽

다음 배열 중에서 크기가 가장 큰 배열은?

(1)

int array1[10];

(2)

double array2[10];

(3)

char array3[40];

(4)

float array4[10];

</details>

<details><summary>힌트 보기</summary>

원소 수만 비교하지 말고 원소 타입의 바이트 수도 곱해 보세요.

</details>

<details><summary>풀이 보기</summary>

1. 타입 크기는 실행 환경에 따라 달라요. 여기서는 검산한 환경의 int=4, double=8, char=1, float=4바이트를 기준으로 해요.
2. 각 보기의 sizeof는 40, 80, 40, 40바이트예요.
3. 따라서 이 환경에서는 2번이 가장 커요. C가 모든 환경에서 이 바이트 수를 보장하는 것은 아니에요.
4. 수업과의 연결: 0928 수업 정리노트의 “3. sizeof와 메모리 정렬” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

**정답:** (2) double array2[10] — 검산 환경 기준

</details>

---

<a id="p2"></a>

### P2. 복소수 구조체 더하기

복소수를 구조체로 표현해보자. 복소수 a와 복소수 b를 받아서 a+b를 계산하는 함수를 작성해보자. 함수는 구조체를 반환할 수 있다. 알다시피 복소수는 real+imag\*i와 같은 형태를 갖는다.

```
Complex complex_add(Complex a, Complex b) {
    ...
}
```

<details><summary>교과서 원문 보기</summary>

3장 배열, 구조체, 포인터 · 07번 · 책 98쪽

복소수를 구조체로 표현해보자. 복소수 a와 복소수 b를 받아서 a+b를 계산하는 함수를 작성해보자. 함수는 구조체를 반환할 수 있다. 알다시피 복소수는 real+imag\*i와 같은 형태를 갖는다.

```
Complex complex_add(Complex a, Complex b) {
    ...
}
```

</details>

<details><summary>힌트 보기</summary>

구조체가 담은 두 성분을 각각 더해 보세요.

</details>

<details><summary>풀이 보기</summary>

1. (1+2i)+(3+4i)=(4+6i)예요.
2. result.real=a.real+b.real, result.imag=a.imag+b.imag로 계산해요.
3. 구조체 값을 반환하므로 호출자가 두 결과를 함께 받아요.
4. 수업과의 연결: 0928 수업 정리노트의 “2. call by value와 전달 방식 고르기” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

```c
typedef struct { float real, imag; } Complex;
Complex complex_add(Complex a, Complex b) {
    Complex result;
    result.real = a.real + b.real;
    result.imag = a.imag + b.imag;
    return result;
}
```

**정답:** 실수부끼리, 허수부끼리 더한 Complex를 반환

</details>

---

<a id="p3"></a>

### P3. 구조체를 동적으로 만들고 반납

1개의 정수와 최대 크기가 20인 문자열로 이루어진 구조체를 저장할 수 있도록 동적 메모리를 할당받고 여기에 정수 100과 문자열 “just testing”을 저장한 다음, 동적 메모리를 반납하는 프로그램을 작성하라.

<details><summary>교과서 원문 보기</summary>

3장 배열, 구조체, 포인터 · 12번 · PDF 2쪽

1개의 정수와 최대 크기가 20인 문자열로 이루어진 구조체를 저장할 수 있도록 동적 메모리를 할당받고 여기에 정수 100과 문자열 “just testing”을 저장한 다음, 동적 메모리를 반납하는 프로그램을 작성하라.

</details>

<details><summary>힌트 보기</summary>

sizeof \*p로 전체 구조체 크기를 요청해 보세요.

</details>

<details><summary>풀이 보기</summary>

1. 문자열 최대 길이 20자를 담고 끝의 널 문자까지 보관하도록 21칸을 선택했어요.
2. malloc 결과가 NULL인지 확인한 뒤 -&gt;로 정수와 문자 배열을 채워요.
3. 저장한 값을 확인하고 free로 반납해요. 반납한 주소는 더 쓰지 않아요.
4. 수업과의 연결: 0928 수업 정리노트의 “4. 동적 메모리 할당 예제” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { int value; char text[21]; } Record;
int main(void) {
    Record *p = malloc(sizeof *p);
    if (p == NULL) return 1;
    p->value = 100;
    strcpy(p->text, "just testing");
    printf("%d %s\n", p->value, p->text);
    free(p);
    p = NULL;
    return 0;
}
```

**정답:** malloc → 값 100·just testing 저장 → free

</details>

---

<a id="p4"></a>

### P4. 배열 접근·전체 방문의 복잡도

배열에 정수가 들어 있다고 가정하고 다음의 작업의 최악, 최선의 시간복잡도를 빅오 표기법으로 말하라.

(1)

배열의 n번째 숫자를 화면에 출력한다.

(2)

배열안의 숫자 중에서 최소값을 찾는다.

(3)

배열의 모든 숫자를 더한다.

<details><summary>교과서 원문 보기</summary>

1장 자료구조와 알고리즘 · 17번 · 책 37쪽

배열에 정수가 들어 있다고 가정하고 다음의 작업의 최악, 최선의 시간복잡도를 빅오 표기법으로 말하라.

(1)

배열의 n번째 숫자를 화면에 출력한다.

(2)

배열안의 숫자 중에서 최소값을 찾는다.

(3)

배열의 모든 숫자를 더한다.

</details>

<details><summary>힌트 보기</summary>

인덱스로 바로 읽는 일과 모든 값을 읽는 일을 구별해 보세요.

</details>

<details><summary>풀이 보기</summary>

1. n번째 원소는 주소 계산으로 바로 접근하므로 배열 길이와 무관해요.
2. 최솟값은 비교 전에 모든 원소를 확인해야 해요. 처음 값으로 시작해 n-1번 비교해요.
3. 전체 합은 모든 n개 값을 한 번씩 읽어요. 배열 내용이 달라도 방문 횟수는 같아요.
4. 수업과의 연결: 0928 수업 정리노트의 “3. 배열과 포인터” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

**정답:** (1) 최선·최악 O(1), (2) 최선·최악 O(n), (3) 최선·최악 O(n)

</details>

---

출처: 기존 기출 문제은행·교과서 연습문제 JSON. 추가 문항의 원문은 추출·검수본이며 풀이와 정답은 직접 작성·검증했습니다.
