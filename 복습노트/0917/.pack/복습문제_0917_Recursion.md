# 복습문제 7선 — 0917 수업 범위

서로 다른 기출은 풀이 목표가 비슷해도 모두 유지하고, 교과서와 강의 예제 코드를 함께 복습해요.

> 원문, 힌트, 풀이는 접혀 있어요. 먼저 풀어 보고 펼쳐 보세요.

**목차**

- [A. 검토한 기출·교과서 문제](#partA)
  - [P1. 최대 공약수 gcd를 순환 함수로](#p1)
  - [P2. 십진수를 이진수로 찍는 순환 함수](#p2)
  - [P3. 3씩 줄어드는 호출](#p3)
  - [P4. 재귀 합을 반복문으로](#p4)
- [B. 강의 예제 코드](#partB)
  - [P5. 거듭제곱: 홀수 분기와 호출 크기](#p5)
  - [P6. 피보나치의 중복 호출과 반복 상태](#p6)
- [C. 복구한 기출 원문](#partRestored)
  - [P7. 함수 foo는 무엇을 할까요](#p7)

<a id="partA"></a>

## A. 검토한 기출·교과서 문제

<a id="p1"></a>

### P1. 최대 공약수 gcd를 순환 함수로

임의의 두 양의 정수의 최대 공약수를 구해주는 gcd를 순환 함수로 구현해 보세요. 두 양의 정수는 main 함수에서 입력받아요.

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

> "임의의 두 양의 정수의 최대 공약수를 구해주는 gcd를 순환 함수로 구현하시오.<br>( main함수에서 임의의 두 양의 정수를 입력 ) [5 points]
>
> ```c
> #include <stdio.h>
> int gcd(int i, int j){
>
>
>
> }
> (중략)
> ```
>
> "

</details>

<details><summary>힌트 보기</summary>

i를 j로 나눈 나머지를 쓰면 두 수가 점점 작아져요. j가 0이 되는 순간을 멈추는 부분으로 삼아 보세요.

</details>

<details><summary>풀이 보기</summary>

1. 멈추는 부분: j가 0이면 i를 그대로 돌려줘요. `if ( j == 0 ) return i;`
2. 순환 호출하는 부분: 아니면 (j, i를 j로 나눈 나머지)로 다시 불러요. `else return gcd( j, i%j );`
3. 48 18을 입력해 따라가 볼게요. gcd(48, 18) → 48%18 = 12 → gcd(18, 12)
4. gcd(18, 12) → 18%12 = 6 → gcd(12, 6)
5. gcd(12, 6) → 12%6 = 0 → gcd(6, 0)
6. gcd(6, 0): j == 0이라 6을 돌려줘요. 화면에는 `gcd:6`이 찍혀요. 6은 48과 18의 최대 공약수가 맞아요.
7. i &lt; j로 넣어도 돼요. gcd(18, 48)은 18%48 = 18이라 gcd(48, 18)을 불러 두 수 자리가 바뀌고, 그다음은 위와 같아요.
8. 완성한 함수예요.

   ```c
   int gcd(int i, int j){
       if ( j == 0 ) return i;
       else return gcd( j, i%j );
   }
   ```
9. 수업과의 연결: 0917 수업의 순환 알고리즘 두 조건 그대로예요. 순환을 멈추는 부분(`j == 0`)이 있고, 순환 호출은 나머지가 j보다 작아서 둘째 인자가 계속 줄어 0으로 수렴해요.

**정답:** `if ( j == 0 ) return i; else return gcd( j, i%j );` (48 18 → gcd:6)

</details>

---

<a id="p2"></a>

### P2. 십진수를 이진수로 찍는 순환 함수

풀이 조건: 입력은 0 이상의 int예요. 0도 한 자리 0으로 출력하세요. 음수 표기 방식은 이번 문제 범위에서 제외해요.

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

> "11. 다음의 코드에서 순환 함수 dec_to_bin을 구현하시오. [5 points]<br>(예: 십진수 입력:10 , 1010 )
>
> ```c
> #include <stdio.h>
>
>
>
> void dec_to_bin(int n){
>
>
>
>
> }
> (중략)
> ```
>
> "

</details>

<details><summary>힌트 보기</summary>

n % 2는 이진수의 맨 끝 자리, n / 2는 그 앞자리들이에요. 앞자리를 먼저 찍게 하려면 printf를 순환 호출보다 뒤에 두어 보세요.

</details>

<details><summary>풀이 보기</summary>

1. 앞자리 n/2를 먼저 출력하고 마지막 자리 n%2를 뒤에 출력해요.
2. n이 0 또는 1이면 더 호출하지 않고 그 숫자를 출력해요. 이 조건은 0 입력도 처리해요.
3. 10→5→2→1로 호출하고 1,0,1,0을 차례로 출력해요.

```c
void dec_to_bin(int n) {
    if(n >= 2) dec_to_bin(n/2);
    printf("%d",n%2);
}
```

**정답:** n&gt;=2일 때 dec_to_bin(n/2)를 먼저 호출한 뒤 n%2를 출력. 10→1010, 0→0.

n==0이면 바로 return하는 구현은 양수 예시는 통과하지만 0 입력에는 아무것도 출력하지 않아요.

</details>

---

<a id="p3"></a>

### P3. 3씩 줄어드는 호출

다음 함수를 recursive(10)로 호출하였을 때, 화면에 출력되는 내용과 함수의 반환값을 구하라.

```
int recursive(int n)
{
    printf("%d\n", n);
    if( n<1) return -1;
    else return( recursive(n-3)+1 );
}
```

<details><summary>교과서 원문 보기</summary>

2장 순환 · 09번 · 책 64쪽

다음 함수를 recursive(10)로 호출하였을 때, 화면에 출력되는 내용과 함수의 반환값을 구하라.

```
int recursive(int n)
{
    printf("%d\n", n);
    if( n<1) return -1;
    else return( recursive(n-3)+1 );
}
```

</details>

<details><summary>힌트 보기</summary>

출력은 호출 직후, +1은 돌아올 때 실행돼요.

</details>

<details><summary>풀이 보기</summary>

1. 호출 인수와 출력은 10 → 7 → 4 → 1 → -2예요. 각각 별도 줄에 나와요.
2. -2는 n&lt;1이므로 -1을 반환해요.
3. 돌아올 때 recursive(1)=0, recursive(4)=1, recursive(7)=2, recursive(10)=3이에요.
4. 수업과의 연결: 0917 수업 정리노트의 “2. 순환 알고리즘의 두 조건” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

**정답:** 출력: 10 7 4 1 -2 / 반환값: 3

</details>

---

<a id="p4"></a>

### P4. 재귀 합을 반복문으로

다음의 순환적인 프로그램을 반복 구조를 사용한 비순환적 프로그램으로 바꾸시오.

```
int sum(int n)
{
    if(n == 1 ) return 1;
    else return (n + sum(n-1));
}
```

<details><summary>교과서 원문 보기</summary>

2장 순환 · 16번 · 책 65쪽

다음의 순환적인 프로그램을 반복 구조를 사용한 비순환적 프로그램으로 바꾸시오.

```
int sum(int n)
{
    if(n == 1 ) return 1;
    else return (n + sum(n-1));
}
```

</details>

<details><summary>힌트 보기</summary>

재귀에서 돌아오며 더하던 수를 반복문으로 누적해 보세요.

</details>

<details><summary>풀이 보기</summary>

1. 원문 sum의 입력 조건은 n≥1이에요.
2. 반복문은 1부터 n까지 각 수를 total에 더해요.
3. n=5에서 1 → 3 → 6 → 10 → 15가 되어 같은 답을 반환해요.
4. 수업과의 연결: 0917 수업 정리노트의 “3. 순환 대 반복” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

```c
int sum_iter(int n) {
    int total = 0;
    for (int i = 1; i <= n; ++i) total += i;
    return total;
}
```

**정답:** total=0에서 1..n을 더해 반환

</details>

---

<a id="partB"></a>

## B. 강의 예제 코드

<a id="p5"></a>

### P5. 거듭제곱: 홀수 분기와 호출 크기

**강의 예제 기반 자체 출제** S2 p10

n≥0이고 중간 계산이 double 범위 안에 있다고 가정해요. 홀수 분기를 가리고 반환식을 다시 쓰세요. power(2,5)의 (x,n) 호출 순서와 최종 반환값을 적고, 한 번씩 x를 곱하는 slow_power와 시간복잡도를 비교하세요.

```c
double power(double x, int n)
{
    if(n==0) return 1;
    else if((n%2)==0) return power(x*x,n/2);
    else return /* 빈칸 */;
}
```

<details><summary>강의 예제 보기</summary>

S2 p10 · Software_2_Recursion.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

```c
double power(double x, int n)
{
    if(n==0) return 1;
    else if((n%2)==0) return power(x*x,n/2);
    else return x*power(x*x,(n-1)/2);
}
```

</details>

<details><summary>힌트 보기</summary>

홀수 n=2k+1이면 x^n=x×(x²)^k예요. 이 항등식에서 홀수 분기의 식이 나와요.

</details>

<details><summary>풀이 보기</summary>

1. 홀수 n=2k+1이면 x^n=x×(x²)^k예요. 이 항등식에서 홀수 분기의 식이 나와요.
2. (2,5)는 2×power(4,2)를 기다리고, (4,2)는 power(16,1)을 기다려요.
3. (16,1)은 16×power(256,0)을 기다려요. 마지막 호출이 1을 반환하면 16,16,32로 돌아와요.
4. 지수가 매번 절반으로 줄어 호출 깊이가 로그로 늘어요. 한 번에 1씩 줄이는 반복 곱셈은 n번 수행해요.

**정답:** 홀수 분기 x\*power(x\*x,(n-1)/2). 호출 (2,5)→(4,2)→(16,1)→(256,0), 반환 1→16→16→32. power는 O(log n), slow_power는 O(n)이다(n≥1).

짝수 분기를 power(x,n/2)로 쓰면 밑을 제곱하지 않아 원래 거듭제곱과 달라져요.

</details>

---

<a id="p6"></a>

### P6. 피보나치의 중복 호출과 반복 상태

**강의 예제 기반 자체 출제** S2 p12 · 추가 근거 p13,14

fib(6)의 값과 실행 중 fib(3)이 호출되는 횟수를 구하세요. 반복 구현에서 last=F(i-2), current=F(i-1)인 상태를 다음 단계로 갱신하려고 해요. tmp를 사용한 세 대입문을 쓰고, 왜 순환 구현에서 같은 부분 문제가 반복되는지 설명하세요.

```c
int fib(int n)
{
    if(n==0) return 0;
    if(n==1) return 1;
    return fib(n-1)+fib(n-2);
}
```

<details><summary>강의 예제 보기</summary>

S2 p12 · 추가 근거 p13,14 · Software_2_Recursion.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

```c
int fib(int n)
{
    if(n==0) return 0;
    if(n==1) return 1;
    return fib(n-1)+fib(n-2);
}
```

</details>

<details><summary>힌트 보기</summary>

F(0)=0,F(1)=1이고 두 앞 항을 더하므로 0,1,1,2,3,5,8을 얻어요.

</details>

<details><summary>풀이 보기</summary>

1. F(0)=0,F(1)=1이고 두 앞 항을 더하므로 0,1,1,2,3,5,8을 얻어요.
2. fib(6)의 자식 fib(5),fib(4)를 나누어 그려요. fib(5) 쪽에서 fib(3)이 2번, fib(4) 쪽에서 1번 호출돼요.
3. 반복에서는 이전 current를 tmp에 먼저 보관해요. current에 last를 더해 새 항을 만들고 last를 이전 current로 옮겨요.
4. last를 먼저 current로 바꿔 버리면 서로 다른 두 항의 합을 유지하지 못해요. 반복은 이미 구한 두 항을 재사용해요.

**정답:** fib(6)=8, fib(3)은 3회. tmp=current; current+=last; last=tmp;. 두 자식 호출의 하위 호출이 겹치고 계산 결과를 저장하지 않기 때문이다.

값 F(3)=2와 fib(3)의 호출 횟수 3회를 혼동하지 마세요.

</details>

---

<a id="partRestored"></a>

## C. 복구한 기출 원문

<a id="p7"></a>

### P7. 함수 foo는 무엇을 할까요

입력 조건: x와 y는 양의 정수예요. y=0은 이 함수의 유효 입력이 아니에요.

아래에 함수 foo의 코드가 있어요. 이 함수를 호출하면 무엇을 하는 함수인지 답해 보세요.

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

> "아래에는 함수 foo에 대한 코드가 있으며 이 함수를 호출(사용)하였을 때 무엇을 하는 함수인지에 대해서 답을 하시오. 함수 foo는 ( ) 함수이다. (2점)"

```c
int foo (int x, int y){
    if (x % y == 0) return y;
    else
        return foo(y, x % y);
}
```

</details>

<details><summary>힌트 보기</summary>

`foo(12, 18)`을 손으로 따라가 보세요. 나머지가 0이 되는 순간 무엇을 돌려주는지 보면 돼요.

</details>

<details><summary>풀이 보기</summary>

1. 끝나는 조건부터 봐요. `x % y == 0`이면, 즉 y가 x를 나누어떨어지게 하면 y를 돌려주고 끝나요. 이때 y는 x와 y를 둘 다 나누는 수 중 가장 커요.
2. 아니면 `foo(y, x % y)`를 다시 불러요. `x % y`는 y보다 작아서 두 번째 값이 부를 때마다 줄어들어요. 그래서 언젠가 나누어떨어지는 순간이 와요.
3. `foo(12, 18)`: `12 % 18 = 12`, 0이 아니에요 → `foo(18, 12)`
4. `foo(18, 12)`: `18 % 12 = 6` → `foo(12, 6)`
5. `foo(12, 6)`: `12 % 6 = 0` → 6을 돌려줘요.
6. 돌아올 때는 받은 6을 그대로 위로 넘겨요. `foo(12, 6)` → `foo(18, 12)` → `foo(12, 18)` 모두 6이에요. 12와 18을 둘 다 나누는 가장 큰 수가 6이에요.
7. 왜 답이 바뀌지 않을까요? $x = q \cdot y + r$ ($r$은 $x$를 $y$로 나눈 나머지)이면, $x$와 $y$를 둘 다 나누는 수는 $r$도 나누고, $y$와 $r$을 둘 다 나누는 수는 $x$도 나눠요. 그래서 $(x, y)$와 $(y, r)$의 공약수가 같아요.
8. 수업과의 연결: 0914 수업(60:20–61:16)에서 말한 순환의 두 조건, "끝나는 조건"과 부를 때마다 "크기가 줄어든다"를 foo가 그대로 갖췄어요.

**정답:** x와 y의 최대공약수를 구해주는 (함수)

</details>

---

기출·교과서 원문과 강의 예제 기반 자체 출제. 강의 코드는 발췌 여부를 표시했으며 질문·풀이·실행 검산은 별도로 작성했습니다.
