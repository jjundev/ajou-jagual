# 복습문제 9선 — 0928 수업 범위

강의노트의 핵심 개념과 예제 코드를 함께 복습해요. 먼저 직접 풀고 원문·힌트·풀이를 확인하세요.

> 복습문제_0928_ArrayStructureList.html를 마크다운으로 옮겼어요. 원문, 힌트, 풀이는 접혀 있어요. 먼저 풀어 보고 펼쳐 보세요.

**목차**

- [A. 검토한 기출·교과서 문제](#partA)
  - [P1. 배열 크기를 sizeof로 비교](#p1)
  - [P2. 복소수 구조체 더하기](#p2)
  - [P3. 구조체를 동적으로 만들고 반납](#p3)
  - [P4. 배열 접근·전체 방문의 복잡도](#p4)
- [B. 강의노트 기반 생성문제](#partB)
  - [P5. swap: 주소 전달과 값 전달](#p5)
  - [P6. 동적 구조체 배열의 두 원소](#p6)
  - [P7. 역참조·후위 증가·이중 포인터 추적](#p7)
  - [P8. 포인터 초기화·void 포인터와 할당 방식](#p8)
  - [P9. sizeof·패딩과 배열 원소 수](#p9)

<a id="partA"></a>

## A. 검토한 기출·교과서 문제

<a id="p1"></a>

### P1. 배열 크기를 sizeof로 비교

다음 배열 중에서 크기가 가장 큰 배열은?

(1)

int array1\[10\];

(2)

double array2\[10\];

(3)

char array3\[40\];

(4)

float array4\[10\];

비교 기준: 이 팩의 C 검산 환경은 int 4, double 8, char 1, float 4바이트예요.

<details><summary>교과서 원문 보기</summary>

3장 배열, 구조체, 포인터 · 03번 · 책 98쪽

다음 배열 중에서 크기가 가장 큰 배열은?

(1)

int array1\[10\];

(2)

double array2\[10\];

(3)

char array3\[40\];

(4)

float array4\[10\];

</details>

<details><summary>힌트 보기</summary>

원소 수만 비교하지 말고 원소 타입의 바이트 수도 곱해 보세요.

</details>

<details><summary>풀이 보기</summary>

1. 타입 크기는 실행 환경에 따라 달라요. 여기서는 검산한 환경의 int=4, double=8, char=1, float=4바이트를 기준으로 해요.
2. 각 보기의 sizeof는 40, 80, 40, 40바이트예요.
3. 따라서 이 환경에서는 2번이 가장 커요. C가 모든 환경에서 이 바이트 수를 보장하는 것은 아니에요.
4. 수업과의 연결: 0928 수업 정리노트의 “3. sizeof와 메모리 정렬” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

**정답:** (2) double array2\[10\] — 검산 환경 기준

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

<a id="partB"></a>

## B. 강의노트 기반 생성문제

<a id="p5"></a>

### P5. swap: 주소 전달과 값 전달

**강의 예제 기반 자체 출제** S3 p22

호출자(`main`)에 `int a = 1, b = 2;`가 선언되어 있고, 아래 포인터 매개변수 함수 `swap`으로 두 변수의 값을 교환하려고 해요.

```c
void swap(int *px, int *py)
{
    int tmp;
    tmp = *px;
    *px = *py;
    *py = tmp;
}
```

- (a) `a`와 `b`의 값을 바꾸기 위해 `swap`을 호출하는 문장을 쓰고, 함수 안의 세 대입문(`tmp = *px;`, `*px = *py;`, `*py = tmp;`) 실행 직후마다 `(a, b, tmp)`의 값을 순서대로 추적하세요.
- (b) 매개변수가 포인터가 아닌 `void swap_val(int x, int y)`처럼 값에 의한 호출(call by value)로 작성해 `x`와 `y`를 교환하면 호출자의 `a`, `b`가 바뀌는지를 이유와 함께 설명하세요.

<details><summary>강의 예제 보기</summary>

S3 p22 · Software_3_ArrayStructureList.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

```c
void swap(int *px, int *py)
{
    int tmp;
    tmp = *px;
    *px = *py;
    *py = tmp;
}
```

</details>

<details><summary>힌트 보기</summary>

주소 연산자 `&`로 `a`, `b`의 위치를 넘겨요. 함수는 주소의 복사본 `px`, `py`를 받지만 역참조 `*px`, `*py`로 원래 객체에 접근해요.

</details>

<details><summary>풀이 보기</summary>

- (a) 주소 연산자 `&`를 써서 `swap(&a, &b);`로 호출해요. `tmp = *px;` 뒤 `a`의 값 `1`이 `tmp`에 보관되어 `(1, 2, 1)`이 되고, `*px = *py;` 뒤 `a`에 `2`가 대입되어 `(2, 2, 1)`이 되며, `*py = tmp;` 뒤 `b`에 `1`이 대입되어 `(2, 1, 1)`이 돼요.
- (b) 값 전달 함수는 인자 값만 복사한 별도의 지역 변수 `x`, `y`만 서로 바꾸므로 호출자의 `a`, `b`는 `1`, `2` 그대로 유지돼요.

**정답:** (a) `swap(&a,&b);`, `tmp=*px` 뒤 `(1,2,1)`, `*px=*py` 뒤 `(2,2,1)`, `*py=tmp` 뒤 `(2,1,1)` (b) 값 매개변수 `x,y`만 바꾸면 별도 지역 변수만 바뀌므로 호출자의 `a,b`는 `1,2` 그대로다.

`px = py`는 포인터 변수에 담긴 주소만 바꿀 뿐 가리키는 값을 바꾸지 않아요. `*px = *py`와 구별하세요.

</details>

---

<a id="p6"></a>

### P6. 동적 구조체 배열의 두 원소

**강의 예제 기반 자체 출제** S3 p31

아래 코드는 `struct Example` 원소 `2`개 분량의 메모리를 동적으로 할당받아 값을 저장한 뒤 해제해요(할당은 성공했다고 가정해요).

```c
struct Example { int number; char name[10]; };
struct Example *p;
p = (struct Example *)malloc(2*sizeof(struct Example));
if(p==NULL) { fprintf(stderr,"can't allocate memory\n"); exit(1); }
p->number=1;
strcpy(p->name,"Park");
(p+1)->number=2;
strcpy((p+1)->name,"Kim");
free(p);
```

- (a) `free(p);` 직전 시점에 두 원소 `p[0]`, `p[1]`에 저장된 필드 값을 쓰고, 포인터 연산 `p + 1`이 `p`로부터 몇 바이트 뒤 주소를 가리키는지 `sizeof`로 표현하세요.
- (b) 이 코드에 쓰인 함수들을 위해 필요한 표준 헤더 `3`개와 `free`에 넘겨야 할 주소를 쓰고, `free(p);` 이후 `p->number`를 읽으면 왜 안 되는지 설명하세요.

<details><summary>강의 예제 보기</summary>

S3 p31 · Software_3_ArrayStructureList.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

```c
struct Example { int number; char name[10]; };
struct Example *p;
p = (struct Example *)malloc(2*sizeof(struct Example));
if(p==NULL) { fprintf(stderr,"can't allocate memory\n"); exit(1); }
p->number=1;
strcpy(p->name,"Park");
(p+1)->number=2;
strcpy((p+1)->name,"Kim");
free(p);
```

</details>

<details><summary>힌트 보기</summary>

`malloc`의 크기는 구조체 `2`개 분량이에요. `sizeof`에는 패딩도 포함되므로 필드 크기 단순 합으로 바꾸지 않아요.

</details>

<details><summary>풀이 보기</summary>

- (a) `p->`는 첫 원소 `p[0]`, `(p+1)->`는 두 번째 원소 `p[1]`의 필드에 접근하므로 `p[0] = {1, "Park"}`, `p[1] = {2, "Kim"}`이 저장돼요. 포인터 덧셈은 가리키는 원소 크기 단위로 이동하므로 `p + 1`은 `sizeof(struct Example)`바이트 뒤 주소예요.
- (b) `malloc`·`free`·`exit`는 `stdlib.h`, `fprintf`·`stderr`는 `stdio.h`, `strcpy`는 `string.h`에 선언되어 있어요. 반납할 때는 `free(p)`로 최초 할당 주소를 넘겨야 하며, 해제 뒤 저장 공간을 역참조하면 미정의 동작(dangling pointer 접근)이므로 읽으면 안 돼요.

**정답:** (a) `p[0]={1,"Park"}`, `p[1]={2,"Kim"}`, `p+1`은 `sizeof(struct Example)`바이트 뒤 (b) `stdlib.h, stdio.h, string.h`, `free(p)`로 최초 할당 주소를 넘기고 해제 뒤 역참조하면 안 된다.

`free(p + 1)`은 최초 할당 주소가 아니므로 사용할 수 없어요. 패딩이 있을 수 있으므로 구조체 크기를 `14`바이트로 단정하지 마세요.

</details>

---

<a id="p7"></a>

### P7. 역참조·후위 증가·이중 포인터 추적

**강의 예제 기반 자체 출제** S3 p20

아래 코드는 `sizeof(int) == 4`인 환경에서 포인터 `p`와 이중 포인터 `pp`로 배열 `a`를 조작해요.

```c
int a[] = {10, 20, 30};
int *p = a;
int **pp = &p;
int x = *p++;
int y = (*p)++;
**pp = 40;
```

- (a) `int x = *p++;`, `int y = (*p)++;`, `**pp = 40;` 각 문장 실행 직후 `p`가 가리키는 원소와 배열 `a`의 상태 및 최종 `x`, `y` 값을 쓰고, `*p++`와 `(*p)++`가 바꾸는 대상이 어떻게 다른지 설명하세요.
- (b) `pp`, `*pp`, `**pp`가 각각 무엇을 나타내는지 구별하고, `p = a + 1`일 때 `a`와 `p`의 바이트 간격을 쓰세요.

<details><summary>강의 예제 보기</summary>

S3 p20 · 추가 근거 p19,23,25,26 · Software_3_ArrayStructureList.pdf. 강의의 개념·그림·코드 연산을 바탕으로 조건과 질문을 새로 작성한 자체 출제예요. 제시 코드는 있는 경우 학습 확인용 자체 코드이며 강의 원문 발췌가 아니에요. 질문·입력 조건·검산은 자체 작성했어요.

```c
int a[] = {10,20,30};
int *p = a;
int **pp = &p;
int x = *p++;
int y = (*p)++;
**pp = 40;
```

</details>

<details><summary>힌트 보기</summary>

초기 상태는 `p → a[0]`, `pp → p`, 배열 `[10, 20, 30]`이에요. `*p++`는 `*(p++)`로 묶여요.

</details>

<details><summary>풀이 보기</summary>

- (a) `*p++`는 `*(p++)`이므로 현재 `a[0] = 10`을 `x`에 대입한 뒤 포인터 `p`만 `a[1]`로 이동시켜 배열은 `[10, 20, 30]`이에요. `(*p)++`는 `p`가 가리키는 `a[1] = 20`을 `y`에 넘긴 뒤 그 원소 값을 `21`로 증가시키고 `p`는 `a[1]`에 그대로 남아요(배열 `[10, 21, 30]`). 이어서 `**pp = 40;`은 현재 `p`가 가리키는 `a[1]`에 `40`을 대입해 배열은 `[10, 40, 30]`이 돼요.
- (b) `pp`는 포인터 변수 `p`의 주소(`&p`), `*pp`는 `p`에 담긴 값(현재 `a[1]`의 주소), `**pp`는 그 주소의 원소 `a[1]`이에요. `sizeof(int) == 4`이므로 `p = a + 1`과 `a`의 간격은 `4`바이트예요.

**정답:** (a) `x=10, y=20`이며, `x` 대입 뒤 `p`는 `a[1]`·배열 `[10,20,30]`(포인터 `p` 증가), `y` 대입 뒤 `p`는 계속 `a[1]`·배열 `[10,21,30]`(가리키는 원소 증가), `**pp=40` 뒤 배열 `[10,40,30]`이다. (b) `pp`는 `p`의 주소, `*pp`는 `p`의 값(현재 `a[1]`의 주소), `**pp`는 그 원소이며, 바이트 간격은 `4`바이트다.

`pp`를 배열 원소의 주소와 혼동하지 마세요. 후위 증가 연산자 `++`가 포인터에 걸리는지 역참조된 값에 걸리는지 괄호부터 확인해요.

</details>

---

<a id="p8"></a>

### P8. 포인터 초기화·void 포인터와 할당 방식

**강의 예제 기반 자체 출제** S3 p27

아래는 포인터 초기화, `void *` 형변환, 그리고 정적·동적 메모리 할당을 비교하기 위한 코드 조각이에요.

```c
char *pc;
*pc = 'E';          /* 미초기화 역참조 */

char c;
void *v = &c;       /* 범용 포인터 저장 */
char buffer[100];   /* 고정 크기 정적 배열 */
```

- (a) 지역 코드에서 `char *pc; *pc = 'E';`나 `pc = NULL; *pc = 'E';`를 실행하면 안 되는 이유를 설명하고, `char c;`를 실제 저장 대상으로 연결해 `'E'`를 대입하는 코드와 `void *v = &c;`에서 `char *q`로 형변환해 되돌려 받는 식을 쓰세요.
- (b) 고정 배열 `buffer[100]`과 실행 중 필요한 크기를 `malloc`으로 받는 방식을 비교하고, 동적 할당 직후와 반납 시 지켜야 할 안전 규칙을 설명하세요.

<details><summary>강의 예제 보기</summary>

S3 p27 · 추가 근거 p21,28,29 · Software_3_ArrayStructureList.pdf. 강의의 개념·그림·코드 연산을 바탕으로 조건과 질문을 새로 작성한 자체 출제예요. 제시 코드는 있는 경우 학습 확인용 자체 코드이며 강의 원문 발췌가 아니에요. 질문·입력 조건·검산은 자체 작성했어요.

</details>

<details><summary>힌트 보기</summary>

포인터 변수 `pc`가 어느 실제 `char` 객체를 가리키고 있는지부터 확인해요.

</details>

<details><summary>풀이 보기</summary>

- (a) 초기화하지 않은 `pc`는 쓰레기 주소를 담고 있어 역참조하면 미정의 동작이고, `NULL`은 가리키는 객체가 없음을 뜻하므로 역시 역참조할 수 없어요. 실제 변수 `char c; char *pc = &c; *pc = 'E';`처럼 유효한 저장소를 먼저 연결해야 하며, `void *v = &c;`는 `char *q = (char *)v;`로 형변환해 원래 `char` 객체에 접근해요.
- (b) 고정 배열은 컴파일 시 정해진 용량이라 공간 부족이나 낭비가 생길 수 있지만, 동적 할당은 실행 중 필요한 크기를 결정해요. `malloc` 호출 직후 반환값이 `NULL`인지 확인해야 하고, 사용이 끝나면 최초 할당 주소를 한 번 `free`한 뒤 다시 접근하지 않아야 해요.

**정답:** (a) 초기화되지 않은 `pc`를 역참조하면 미정의 동작이고, `NULL`도 가리킬 객체가 없으므로 역참조할 수 없다. `char c; char *pc=&c; *pc='E';`로 유효한 저장소를 연결하며, `char *q=(char *)v;`로 원래 `char` 객체에 접근한다. (b) 고정 배열은 정해진 용량의 부족·낭비 가능성이 있고 동적 할당은 실행 중 크기를 정한다. `malloc` 결과가 `NULL`인지 확인하고 사용 뒤 최초 할당 주소를 한 번 `free`하며 이후 접근하지 않는다.

`void *` 선언을 `NULL` 초기화와 같은 뜻으로 읽지 마세요. 캐스트만으로 잘못된 주소가 유효해지는 것도 아니에요.

</details>

---

<a id="p9"></a>

### P9. sizeof·패딩과 배열 원소 수

**강의 예제 기반 자체 출제** S3 p30

`sizeof(char) == 1`, `sizeof(int) == 4`이고 `int`가 `4`바이트 경계에 정렬되는 환경에서 아래 구조체와 배열을 보아요(`c`의 오프셋은 `0`, `i`의 오프셋은 `4`, 구조체 전체 크기는 `8`바이트예요).

```c
struct AlignDepends {
    char c;
    int i;
};
int array[] = {1, 2, 3, 4, 5};
```

- (a) `sizeof(struct AlignDepends)`가 멤버 크기의 단순 합 `1 + 4 = 5`바이트가 아니라 `8`바이트가 되는 이유를 오프셋과 패딩(padding)으로 설명하세요.
- (b) `sizeof(array)`, `sizeof(array[0])`의 값과 두 값의 비 `sizeof(array) / sizeof(array[0])`의 값·단위를 쓰고, 다른 C 환경에서도 `int`와 구조체 크기가 무조건 `4`·`8`바이트인지(반면 `sizeof(char)`는 어떠한지) 설명하세요.

<details><summary>강의 예제 보기</summary>

S3 p30 · Software_3_ArrayStructureList.pdf. 강의의 개념·그림·코드 연산을 바탕으로 조건과 질문을 새로 작성한 자체 출제예요. 제시 코드는 있는 경우 학습 확인용 자체 코드이며 강의 원문 발췌가 아니에요. 질문·입력 조건·검산은 자체 작성했어요.

</details>

<details><summary>힌트 보기</summary>

`c`: 오프셋 `0`, 패딩: 오프셋 `1~3`, `i`: 오프셋 `4~7`로 배치를 적어 보세요.

</details>

<details><summary>풀이 보기</summary>

- (a) 오프셋 `0`에 `1`바이트 `c`를 놓은 뒤, `4`바이트 정렬을 요구하는 `int i`가 `4`의 배수인 오프셋 `4`에서 시작하도록 오프셋 `1~3`에 `3`바이트 패딩이 들어가요. `i`가 오프셋 `4~7`을 차지하므로 전체 구조체 크기는 `8`바이트가 돼요.
- (b) `array`는 원소 `5`개 × `4`바이트 = `20`바이트이고 원소 하나 `sizeof(array[0])`은 `4`바이트이므로, 두 값의 비는 `20 / 4 = 5`개(배열 원소 개수)예요. `int`와 구조체 크기는 컴파일러·환경에 따라 달라질 수 있어 고정할 수 없지만, `sizeof(char)`는 C 표준에서 항상 `1`바이트로 보장돼요.

**정답:** (a) `c` 다음 오프셋 `1~3`에 `3`바이트 패딩이 있어 `i`가 `4`의 배수 오프셋에서 시작하므로 전체 `8`바이트다. (b) `array` 전체 `20`바이트, 원소 하나 `4`바이트, 비 `20/4=5`개이며, `int` 및 구조체 크기는 환경에 따라 달라 고정할 수 없고 `sizeof(char)`는 C에서 항상 `1`이다.

패딩으로 비워 둔 바이트는 `malloc` 후 `free`하지 않은 메모리 누수와 달라요. 배열이 포인터로 변환된 함수 매개변수에서는 `sizeof` 비로 배열 길이를 구할 수 없어요.

</details>

---

기출·교과서 원문과 강의 예제 기반 자체 출제. 강의 코드는 발췌 여부를 표시했으며 질문·풀이·실행 검산은 별도로 작성했습니다.
