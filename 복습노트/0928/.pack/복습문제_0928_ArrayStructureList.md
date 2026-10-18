# 복습문제 9선 — 0928 수업 범위

강의노트의 핵심 개념과 예제 코드를 함께 복습해요. 먼저 직접 풀고 원문·힌트·풀이를 확인하세요.

> 원문, 힌트, 풀이는 접혀 있어요. 먼저 풀어 보고 펼쳐 보세요.

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

int a=1,b=2;에서 위 함수를 부르는 문장을 쓰고 각 대입 뒤의 (a,b,tmp)를 추적하세요. 매개변수가 int x,int y이고 값만 서로 바꾸는 함수라면 호출자의 a,b가 바뀌는지도 설명하세요.

```c
void swap(int *px, int *py)
{
    int tmp;
    tmp = *px;
    *px = *py;
    *py = tmp;
}
```

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

주소 연산자 &로 a,b의 위치를 넘겨요. 함수는 주소의 복사본 px,py를 받지만 역참조로 원래 객체에 접근해요.

</details>

<details><summary>풀이 보기</summary>

1. 주소 연산자 &로 a,b의 위치를 넘겨요. 함수는 주소의 복사본 px,py를 받지만 역참조로 원래 객체에 접근해요.
2. 먼저 a의 값 1을 tmp에 보관해요. a에 b의 값 2를 대입해도 1은 tmp에 남아요.
3. b에 tmp를 대입하면 2,1이 돼요. 값 전달 함수는 별도 지역 변수만 바꾸므로 호출자에게 반영되지 않아요.

**정답:** swap(&a,&b);. tmp=\*px 뒤 (1,2,1), \*px=\*py 뒤 (2,2,1), \*py=tmp 뒤 (2,1,1). 값 매개변수 x,y만 바꾸면 호출자의 a,b는 1,2 그대로다.

px=py는 주소 변수만 바꿔요. \*px=\*py와 의미가 달라요.

</details>

---

<a id="p6"></a>

### P6. 동적 구조체 배열의 두 원소

**강의 예제 기반 자체 출제** S3 p31

할당이 성공했다고 가정해요. 두 원소의 필드 값을 쓰고 p+1의 바이트 이동량을 sizeof로 표현하세요. 필요한 표준 헤더, free에 넘길 주소, free 뒤 p-&gt;number를 읽어도 되는지 설명하세요.

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

malloc의 크기는 구조체 2개 분량이에요. sizeof에는 패딩도 포함되므로 필드 크기 합으로 바꾸지 않아요.

</details>

<details><summary>풀이 보기</summary>

1. malloc의 크기는 구조체 2개 분량이에요. sizeof에는 패딩도 포함되므로 필드 크기 합으로 바꾸지 않아요.
2. p-&gt;는 첫 원소, (p+1)-&gt;는 두 번째 원소의 필드에 접근해요. 포인터 덧셈은 바이트가 아닌 원소 단위예요.
3. malloc/free/exit는 stdlib.h, fprintf/stderr는 stdio.h, strcpy는 string.h가 선언해요.
4. free 뒤 포인터 변수 자체가 자동 NULL이 되지는 않아요. 해제된 저장 공간을 읽으면 미정의 동작이므로 정상 출력값을 구하지 않아요.

**정답:** p\[0\]={1,"Park"}, p\[1\]={2,"Kim"}. p+1은 sizeof(struct Example)바이트 뒤. stdlib.h,stdio.h,string.h. free(p)로 최초 할당 주소를 넘기고 해제 뒤 역참조하면 안 된다.

free(p+1)은 최초 할당 주소가 아니므로 사용할 수 없어요. 구조체 크기를 14바이트로 단정하지 마세요.

</details>

---

<a id="p7"></a>

### P7. 역참조·후위 증가·이중 포인터 추적

**강의 예제 기반 자체 출제** S3 p20 · 추가 근거 p19,23,25,26

다음은 강의 개념을 확인하는 자체 코드예요. 각 문장 뒤 p가 가리키는 원소와 배열 값을 추적하고 x,y의 최종값을 쓰세요. \*p++와 (\*p)++가 바꾸는 대상이 어떻게 다른지, pp와 \*pp와 **pp가 각각 무엇인지 설명하세요. int 크기가4바이트일 때 p=a+1과 a의 바이트 간격도 쓰세요.

```c
int a[] = {10,20,30};
int *p = a;
int **pp = &p;
int x = *p++;
int y = (*p)++;
**pp = 40;
```

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

초기: p→a\[0\], pp→p, 배열\[10,20,30\]이라고 적어요.

</details>

<details><summary>풀이 보기</summary>

1. p=a는 첫 원소 주소이고 pp=&p는 포인터 변수 p의 주소예요.
2. \*p++는 \*(p++)이므로 첫 값10을 읽고 p만 다음 원소로 이동해요.
3. (\*p)++는 p가 가리키는20을 먼저 y에 넘기고 그 원소를21로 바꿔요. p는 이동하지 않아요.
4. \*pp는 현재 p이므로 **pp=40은 a\[1\]에40을 저장해요.

**정답:** x=10,y=20이에요. x 대입 뒤 p는 a\[1\], 배열 \[10,20,30\]; y 대입 뒤 p는 계속 a\[1\], 배열 \[10,21,30\]; **pp=40 뒤 배열 \[10,40,30\]이에요. pp는 p의 주소, \*pp는 p의 값(현재 a\[1\]의 주소), **pp는 그 원소예요. 간격은4바이트예요.

pp를 배열 원소의 주소와 혼동하지 않아요. 후위 증가가 어느 괄호 안 객체에 적용되는지 먼저 확인해요.

</details>

---

<a id="p8"></a>

### P8. 포인터 초기화·void 포인터와 할당 방식

**강의 예제 기반 자체 출제** S3 p27 · 추가 근거 p21,28,29

char \*pc; \*pc='E';가 지역 코드에 있으면 왜 정상 출력값을 구하면 안 되나요? pc=NULL;만 추가하면 역참조가 안전해지나요? char c를 실제 저장 대상으로 써서 고치세요. void \*v=&c;에서 char \*q로 되돌려 쓰는 식도 쓰세요. 이어 고정 크기 buffer\[100\]과 실행 중 필요한 크기를 malloc으로 받는 방식을 비교하고, 할당 실패와 반납 시 확인할 일을 설명하세요.

<details><summary>강의 예제 보기</summary>

S3 p27 · 추가 근거 p21,28,29 · Software_3_ArrayStructureList.pdf. 강의의 개념·그림·코드 연산을 바탕으로 조건과 질문을 새로 작성한 자체 출제예요. 제시 코드는 있는 경우 학습 확인용 자체 코드이며 강의 원문 발췌가 아니에요. 질문·입력 조건·검산은 자체 작성했어요.

</details>

<details><summary>힌트 보기</summary>

pc가 어느 실제 char 객체를 가리키는지부터 적어요.

</details>

<details><summary>풀이 보기</summary>

1. 선언한 포인터 변수만으로 저장 대상 char 객체가 생기지 않아요.
2. NULL은 미연결 상태를 표현하며 쓰기 가능한 메모리를 만들지 않아요.
3. 실제 char c의 주소를 pc에 넣은 다음 쓰면 유효한 객체를 수정해요.
4. void \*는 특정 대상 타입을 지정하지 않은 주소 저장이고, 원래 대상이 char임을 아는 경우 char \*로 돌려 접근해요.
5. 고정 용량과 실행 중 결정하는 크기를 비교하고, 동적 자원은 실패 검사와 반납 책임까지 정해요.

**정답:** 초기화되지 않은 pc를 역참조하면 미정의 동작이에요. NULL도 가리킬 객체가 없으므로 역참조할 수 없어요. char c; char \*pc=&c; \*pc='E';로 유효한 저장소를 연결할 수 있어요. char \*q=(char \*)v;로 원래 char 객체에 접근해요. 고정 배열은 정해진 용량의 부족·낭비 가능성이 있고 동적 할당은 실행 중 크기를 정해요. malloc 결과가 NULL인지 확인하고 사용 뒤 최초 할당 주소를 한 번 free하며 이후 접근하지 않아요.

void \* 선언을 NULL 초기화와 같은 뜻으로 읽지 않아요. 캐스트만으로 잘못된 주소가 유효해지는 것도 아니에요.

</details>

---

<a id="p9"></a>

### P9. sizeof·패딩과 배열 원소 수

**강의 예제 기반 자체 출제** S3 p30

강의의 struct AlignDepends { char c; int i; };를 봐요. 이 문제의 환경은 sizeof(char)=1, sizeof(int)=4, int 정렬4바이트이고 c 오프셋0, i 오프셋4, 구조체 크기8바이트예요. 왜 크기가1+4=5가 아닌지 설명하세요. int array\[\]={1,2,3,4,5};의 sizeof(array), sizeof(array\[0\]), 두 값의 비와 단위도 쓰세요. 이 값을 다른 C 환경에서도 무조건4·8이라고 할 수 있나요?

<details><summary>강의 예제 보기</summary>

S3 p30 · Software_3_ArrayStructureList.pdf. 강의의 개념·그림·코드 연산을 바탕으로 조건과 질문을 새로 작성한 자체 출제예요. 제시 코드는 있는 경우 학습 확인용 자체 코드이며 강의 원문 발췌가 아니에요. 질문·입력 조건·검산은 자체 작성했어요.

</details>

<details><summary>힌트 보기</summary>

c:0, 패딩:1~3, i:4~7이라고 배치를 적어요.

</details>

<details><summary>풀이 보기</summary>

1. 문제에서 정한 배치 조건에 따라 c1바이트 뒤에 패딩3바이트를 넣어요.
2. i가 오프셋4~7을 사용하므로 객체 범위는0~7, 총8바이트예요.
3. 원소5개×4바이트=20바이트이고 같은 단위끼리 나누면 원소 수5가 돼요.
4. 고정 수치는 이 문제 환경의 조건이에요. C에서 sizeof(char)=1은 보장되지만 int4와 구조체8은 일반 보장이 아니에요.

**정답:** c 다음 오프셋1~3에3바이트 패딩이 있어 i가4의 배수 오프셋에서 시작해요. 따라서 전체8바이트예요. array 전체20바이트, 원소 하나4바이트, 비20/4=5개예요. int 및 구조체 크기는 환경에 따라 달라 고정할 수 없고 sizeof(char)는 C에서 항상1이에요.

패딩으로 비워 둔 바이트는 malloc 후 free하지 않은 메모리 누수와 달라요. 배열이 포인터로 전달된 매개변수에서는 이 sizeof 비로 배열 길이를 구할 수 없어요.

</details>

---

기출·교과서 원문과 강의 예제 기반 자체 출제. 강의 코드는 발췌 여부를 표시했으며 질문·풀이·실행 검산은 별도로 작성했습니다.
