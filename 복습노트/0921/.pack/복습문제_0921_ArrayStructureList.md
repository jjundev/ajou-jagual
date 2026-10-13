# 복습문제 8선 — 0921 수업 범위

기존 문제 **4개**를 유지하고 교과서 문제 **4개**를 추가했어요. 먼저 풀어 보고, 막히면 힌트와 풀이를 열어 보세요.

> 원문, 힌트, 풀이는 접혀 있어요. 먼저 풀어 보고 펼쳐 보세요.

**목차**

- [B. 다른 기출](#partB)
  - [P1. 함수 foo가 하는 일](#p1)
  - [P2. 순환 함수 gcd 구현하기](#p2)
  - [P3. 자기 자신을 다시 부르는 기법](#p3)
  - [P4. 순환 함수 dec_to_bin 구현하기](#p4)
- [D. 교과서 연습문제](#partD)
  - [P5. 2차원 배열의 바이트 수](#p5)
  - [P6. 배열에 2의 거듭제곱 저장](#p6)
  - [P7. 사람 정보를 구조체로](#p7)
  - [P8. typedef로 complex 만들기](#p8)

<a id="partB"></a>

## B. 다른 기출

<a id="p1"></a>

### P1. 함수 foo가 하는 일

아래에 함수 foo의 코드가 있어요. 이 함수를 호출(사용)했을 때 무엇을 하는 함수인지 답해 보세요.

함수 foo는 ( ) 함수이다.

```c
int foo (int x, int y){
    if (x % y == 0) return y;
    else
        return foo(y, x % y);
}
```

<details><summary>기출 원문 보기</summary>

2019 중간 8번 · 2점 · 출제자 미상

"아래에는 함수 foo에 대한 코드가 있으며 이 함수를 호출(사용)하였을 때 무엇을 하는 함수인지에 대해서 답을 하시오.<br>함수 foo는 ( ) 함수이다. (2점)"

```c
int foo (int x, int y){
    if (x % y == 0) return y;
    else
        return foo(y, x % y);
}
```

</details>

<details><summary>힌트 보기</summary>

foo(48, 18)을 직접 따라가 보고, 돌려준 값이 48·18과 어떤 관계인지 보세요.

</details>

<details><summary>풀이 보기</summary>

1. 바닥 조건은 `x % y == 0`이에요. y가 x를 나누어떨어지게 하면 y가 x와 y를 둘 다 나누는 가장 큰 수라서, 더 부르지 않고 y를 답으로 내놓아요.
2. 아니면 `foo(y, x % y)`를 불러요. 나머지 `x % y`는 y보다 작으니 부를 때마다 두 수가 줄어들어요.
3. `foo(48, 18) → foo(18, 12)` (48 % 18 = 12)
4. `foo(18, 12) → foo(12, 6)` (18 % 12 = 6)
5. `foo(12, 6)`: 12 % 6 == 0 → 6을 돌려줘요. 48과 18의 최대공약수가 6이에요.
6. x를 y로 나눈 나머지로 바꿔도 최대공약수는 그대로예요: $\gcd(x, y) = \gcd(y,\ x \bmod y)$. 이렇게 나머지로 바꿔 가며 최대공약수를 구하는 방법을 유클리드 호제법이라고 불러요. 그래서 foo는 x와 y의 최대공약수를 구해 주는 함수예요.
7. 수업과의 연결: 0921 순환 복습의 두 조건 그대로예요. 호출할 때마다 문제가 줄어들어 바닥을 치고, 바닥 조건에서는 "그 바닥이 답이 뭐다라고 제시"해요(0921 00:14). foo의 바닥 답은 y예요.

**정답:** 최대공약수

</details>

---

<a id="p2"></a>

### P2. 순환 함수 gcd 구현하기

임의의 두 양의 정수의 최대 공약수를 구해 주는 gcd를 순환 함수로 구현해 보세요. (main함수에서 임의의 두 양의 정수를 입력해요.)

```c
#include <stdio.h>
int gcd(int i, int j){

}
int main(){
    int i, j;
    printf("임의의 두 양의 정수 입력:");
    scanf("%d %d", &i, &j);
    printf("gcd:%d\n", gcd(i, j));
    return 0;
}
```

<details><summary>기출 원문 보기</summary>

2018 중간 15번 · 5점 · 출제자 미상

"임의의 두 양의 정수의 최대 공약수를 구해주는 gcd를 순환 함수로 구현하시오.<br>( main함수에서 임의의 두 양의 정수를 입력 ) [5 points]"

```c
#include <stdio.h>
int gcd(int i, int j){

}
```

(중략)

</details>

<details><summary>힌트 보기</summary>

i를 j로 나눈 나머지로 바꿔도 최대공약수는 그대로예요: $\gcd(i, j) = \gcd(j,\ i \bmod j)$. 나머지가 0이 되는 순간이 바닥이고, 그때 남은 수가 답이에요.

</details>

<details><summary>풀이 보기</summary>

1. 바닥 조건: j가 0이면 더 부르지 않고 i를 답으로 돌려줘요. 0은 어떤 수로도 나누어떨어지니 i와 0의 최대공약수는 i예요.
2. 그 밖에는 `gcd( j, i%j )`를 불러요. `i%j`는 j보다 작아서 부를 때마다 두 번째 인자가 줄어들고, 결국 0에 닿아요.
3. 채운 함수 전체예요.

   ```c
   #include <stdio.h>
   int gcd(int i, int j){
       if ( j == 0 ) return i;
       else return gcd( j, i%j );
   }
   int main(){
       int i, j;
       printf("임의의 두 양의 정수 입력:");
       scanf("%d %d", &i, &j);
       printf("gcd:%d\n", gcd(i, j));
       return 0;
   }
   ```
4. `gcd(48, 18) → gcd(18, 12)` (48 % 18 = 12)
5. `gcd(18, 12) → gcd(12, 6)` (18 % 12 = 6)
6. `gcd(12, 6) → gcd(6, 0)` (12 % 6 = 0)
7. `gcd(6, 0)`: j == 0 → 6을 돌려줘요. 돌아오는 길에 6이 그대로 main까지 전해져요.
8. 실행 예(입력 `48 18`):

   ```
   임의의 두 양의 정수 입력:48 18
   gcd:6
   ```
9. 수업과의 연결: 0921 순환 복습의 두 조건이에요. 호출할 때마다 문제가 줄어들어 바닥을 치고(j가 0까지 줄어요), 바닥 조건에서는 "그 바닥이 답이 뭐다라고 제시"해요(0921 00:14). 여기서 바닥의 답은 i예요.

**정답:** `if ( j == 0 ) return i; else return gcd( j, i%j );`

</details>

---

<a id="p3"></a>

### P3. 자기 자신을 다시 부르는 기법

함수가 수행 도중에 자기 자신을 다시 호출하여 문제를 해결하는 기법을 ( ) 이라고 해요. 빈칸을 채워 보세요.

<details><summary>기출 원문 보기</summary>

2018 중간 1번 · 2점 · 출제자 미상

"1. 함수가 수행 도중에 자기 자신을 다시 호출하여 문제를 해결하는 기법을 ( ) 이라고 한다. [2 points]"

</details>

<details><summary>힌트 보기</summary>

하노이 탑 함수가 몸 안에서 hanoi_tower를 다시 불렀던 걸 떠올려 보세요. 강의록 S2 p2의 제목 낱말이에요.

</details>

<details><summary>풀이 보기</summary>

1. 함수가 자기 자신을 다시 부르는 기법을 순환(recursion)이라고 해요.
2. 순환 함수가 끝나려면 두 조건이 필요해요. 호출할 때마다 문제가 줄어들어 바닥을 칠 수 있어야 하고, 바닥에서 답을 바로 내놓는 바닥 조건이 있어야 해요.
3. 같은 뜻으로 재귀(recursion)라고도 해요. 이 과목 강의록은 '순환'으로 써요.
4. 수업과의 연결: 0921 수업은 이 두 조건을 다시 짚고 하노이 탑으로 순환을 마무리했어요. 바닥 조건에서는 "더 이상 리커시브하게 부르지 않고" 답을 제시해요(0921 00:14).

**정답:** 순환

</details>

---

<a id="p4"></a>

### P4. 순환 함수 dec_to_bin 구현하기

다음 코드에서 순환 함수 dec_to_bin을 구현해 보세요. (예: 십진수 입력:10 , 1010 )

```c
#include <stdio.h>

void dec_to_bin(int n){

}

int main(){
    int decimal;

    printf("십진수 입력:");
    scanf("%d", &decimal);

    dec_to_bin(decimal);

    return 0;
}
```

<details><summary>기출 원문 보기</summary>

2017 중간 11번 · 5점 · 출제자 미상

"11. 다음의 코드에서 순환 함수 dec_to_bin을 구현하시오. [5 points]<br>(예: 십진수 입력:10 , 1010 )"

```c
#include <stdio.h>

void dec_to_bin(int n){

}
```

(중략)

</details>

<details><summary>힌트 보기</summary>

2로 나눈 나머지 n % 2가 이진수의 맨 끝자리이고, n / 2가 그 끝자리를 뗀 앞부분이에요. 앞부분을 먼저 찍어야 하니, 무엇을 먼저 부르고 무엇을 나중에 찍을지 생각해 보세요.

</details>

<details><summary>풀이 보기</summary>

1. 바닥 조건: n이 0이면 찍을 자리가 없으니 아무것도 하지 않고 돌아가요.
2. 그 밖에는 앞부분(n / 2)을 먼저 순환으로 다 찍고, 돌아와서 끝자리(n % 2)를 찍어요. 부를 때마다 n이 반으로 줄어 결국 0에 닿아요.
3. 채운 함수 전체예요.

   ```c
   #include <stdio.h>

   void dec_to_bin(int n){
       if (n == 0) return;
       else{
           dec_to_bin(n / 2);
           printf("%d", n % 2);
       }
   }

   int main(){
       int decimal;

       printf("십진수 입력:");
       scanf("%d", &decimal);

       dec_to_bin(decimal);

       return 0;
   }
   ```
4. `dec_to_bin(10)` 호출 추적이에요. 바닥까지 내려갔다가 돌아오면서 찍어요.

   | 순서 | 일어나는 일 | 지금까지 출력 |
   |---|---|---|
   | 1 | `dec_to_bin(10)` → `dec_to_bin(5)` 부름 | (없음) |
   | 2 | `dec_to_bin(5)` → `dec_to_bin(2)` 부름 | (없음) |
   | 3 | `dec_to_bin(2)` → `dec_to_bin(1)` 부름 | (없음) |
   | 4 | `dec_to_bin(1)` → `dec_to_bin(0)` 부름 | (없음) |
   | 5 | `dec_to_bin(0)`: n == 0, 바닥이라 그냥 돌아가요 | (없음) |
   | 6 | `dec_to_bin(1)`로 돌아와 1 % 2 = 1 찍기 | 1 |
   | 7 | `dec_to_bin(2)`로 돌아와 2 % 2 = 0 찍기 | 10 |
   | 8 | `dec_to_bin(5)`로 돌아와 5 % 2 = 1 찍기 | 101 |
   | 9 | `dec_to_bin(10)`으로 돌아와 10 % 2 = 0 찍기 | 1010 |
5. 실행 예(입력 `10`):

   ```
   십진수 입력:10
   1010
   ```
6. printf를 dec_to_bin(n / 2)보다 먼저 쓰면 끝자리부터 찍혀 0101이 나와요. 순서가 답을 가려요.
7. 수업과의 연결: 0921 하노이 탑도 `hanoi_tower(n-1, from, to, tmp);`를 먼저 부르고 돌아와서 원판 이동을 출력했어요(S2 p19). dec_to_bin도 n / 2를 먼저 부르고 돌아와서 n % 2를 찍어요.

**정답:** `if (n == 0) return; else { dec_to_bin(n / 2); printf("%d", n % 2); }`

</details>

---

<a id="partD"></a>

## D. 교과서 연습문제

<a id="p5"></a>

### P5. 2차원 배열의 바이트 수

int a[10][20]에서 배열이 차지하는 메모리 공간의 크기는 얼마인가? int형은 4바이트라고 하자.

(1)

200바이트

(2)

400바이트

(3)

600바이트

(4)

800바이트

<details><summary>교과서 원문 보기</summary>

3장 배열, 구조체, 포인터 · 01번 · 책 98쪽

int a[10][20]에서 배열이 차지하는 메모리 공간의 크기는 얼마인가? int형은 4바이트라고 하자.

(1)

200바이트

(2)

400바이트

(3)

600바이트

(4)

800바이트

</details>

<details><summary>힌트 보기</summary>

행 수 × 열 수 × 원소 크기를 계산해 보세요.

</details>

<details><summary>풀이 보기</summary>

1. 10×20=200개의 int 원소가 있어요.
2. 문제에서 int는 4바이트라고 정했어요.
3. 200×4=800바이트예요. 행이 바뀌어도 원소들이 연속으로 놓여요.
4. 수업과의 연결: 0921 수업 정리노트의 “1차원·2차원 배열의 메모리 배치” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

**정답:** (4) 800바이트

</details>

---

<a id="p6"></a>

### P6. 배열에 2의 거듭제곱 저장

크기가 10인 배열 two[]를 선언하고 여기에 2의 제곱 값들을 저장해보자. 즉 배열의 첫 번째 요소에는 2⁰을 저장하고 두 번째 요소에는 2¹값을 저장한다. 마지막 요소에는 2⁹값을 저장한다. for 루프를 이용하여 two[] 배열의 전체 요소의 값을 출력하는 프로그램을 작성하라.

<details><summary>교과서 원문 보기</summary>

3장 배열, 구조체, 포인터 · 04번 · 책 98쪽

크기가 10인 배열 two[]를 선언하고 여기에 2의 제곱 값들을 저장해보자. 즉 배열의 첫 번째 요소에는 2⁰을 저장하고 두 번째 요소에는 2¹값을 저장한다. 마지막 요소에는 2⁹값을 저장한다. for 루프를 이용하여 two[] 배열의 전체 요소의 값을 출력하는 프로그램을 작성하라.

</details>

<details><summary>힌트 보기</summary>

처음 값을 1로 두고 직전 값에 2를 곱해 보세요.

</details>

<details><summary>풀이 보기</summary>

1. two[0]에는 2⁰=1을 넣어요.
2. i=1..9에서 직전 원소의 두 배를 저장해요.
3. 마지막 for문이 two[0]부터 two[9]까지 모두 출력해요.
4. 수업과의 연결: 0921 수업 정리노트의 “1차원·2차원 배열의 메모리 배치” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

```c
#include <stdio.h>

int main(void) {
    int two[10];
    two[0] = 1;
    for (int i = 1; i < 10; ++i) two[i] = 2 * two[i - 1];
    for (int i = 0; i < 10; ++i)
        printf("%d%s", two[i], i == 9 ? "\n" : " ");
    return 0;
}
```

**정답:** 1 2 4 8 16 32 64 128 256 512

</details>

---

<a id="p7"></a>

### P7. 사람 정보를 구조체로

person이라는 구조체를 만들어보자. 이 구조체에는 문자 배열로 된 이름, 사람의 나이를 나타내는 정수 값, 각 개인의 월급을 나타내는 float 값 등이 변수로 들어가야 한다.

<details><summary>교과서 원문 보기</summary>

3장 배열, 구조체, 포인터 · 05번 · 책 98쪽

person이라는 구조체를 만들어보자. 이 구조체에는 문자 배열로 된 이름, 사람의 나이를 나타내는 정수 값, 각 개인의 월급을 나타내는 float 값 등이 변수로 들어가야 한다.

</details>

<details><summary>힌트 보기</summary>

서로 다른 타입을 같은 구조체의 멤버로 묶어 보세요.

</details>

<details><summary>풀이 보기</summary>

1. name은 문자 배열, age는 int, salary는 float로 선언해요.
2. 이름의 배열 길이는 문제에 정해져 있지 않아 100칸으로 선택했어요.
3. 서로 다른 타입을 하나의 person 객체로 다룰 수 있어요.
4. 수업과의 연결: 0921 수업 정리노트의 “구조체와 typedef” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

```c
struct person {
    char name[100];
    int age;
    float salary;
};
```

**정답:** struct person { char name[100]; int age; float salary; };

</details>

---

<a id="p8"></a>

### P8. typedef로 complex 만들기

C언어의 typedef을 이용하여 complex라고 하는 새로운 자료형을 정의하라. complex 자료형은 구조체로서 float형인 real 변수와 역시 float형인 imaginary 변수를 갖는다. complex 자료형으로 변수 c1과 c2를 선언하여보라.

<details><summary>교과서 원문 보기</summary>

3장 배열, 구조체, 포인터 · 06번 · 책 98쪽

C언어의 typedef을 이용하여 complex라고 하는 새로운 자료형을 정의하라. complex 자료형은 구조체로서 float형인 real 변수와 역시 float형인 imaginary 변수를 갖는다. complex 자료형으로 변수 c1과 c2를 선언하여보라.

</details>

<details><summary>힌트 보기</summary>

구조체 타입의 끝에 붙이는 별명이 무엇인지 생각해 보세요.

</details>

<details><summary>풀이 보기</summary>

1. real과 imaginary를 float 멤버로 선언해요.
2. typedef로 이 구조체 타입에 complex라는 별명을 붙여요.
3. complex c1, c2;로 같은 타입의 두 변수를 선언해요.
4. 수업과의 연결: 0921 수업 정리노트의 “구조체와 typedef” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

```c
typedef struct {
    float real;
    float imaginary;
} complex;
complex c1, c2;
```

**정답:** typedef struct { float real; float imaginary; } complex; complex c1, c2;

</details>

---

출처: 기존 기출 문제은행·교과서 연습문제 JSON. 추가 문항의 원문은 추출·검수본이며 풀이와 정답은 직접 작성·검증했습니다.
