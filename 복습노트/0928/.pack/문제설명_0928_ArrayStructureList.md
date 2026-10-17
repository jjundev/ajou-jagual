# 자료구조및알고리즘이해 복습 0928 문제설명

왼쪽 목차로 문항을 고르고, 오른쪽 문제를 보며 해설을 따라가요.

문제의 첫 줄부터 검산까지 설명해요.

**목차**

- [문항별 설명](#problems)
  - [P1. 배열 크기를 sizeof로 비교](#p1)
  - [P2. 복소수 구조체 더하기](#p2)
  - [P3. 구조체를 동적으로 만들고 반납](#p3)
  - [P4. 배열 접근·전체 방문의 복잡도](#p4)
  - [P5. swap: 주소 전달과 값 전달](#p5)
  - [P6. 동적 구조체 배열의 두 원소](#p6)

<a id="problems"></a>

## 문항별 설명

<a id="p1"></a>

### P1. 배열 크기를 sizeof로 비교

textbook-ch03-q03 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_0928_ArrayStructureList.html#p1)

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

#### 문제를 내 말로 읽어요

네 배열의 전체 크기를 주어진 검산 환경의 바이트 수로 비교해요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

sizeof는 byte 단위의 객체 크기예요. array 크기는 원소 수×sizeof(타입)이에요. 여기의 int=4,double=8,char=1,float=4는 현재 환경 조건이에요.

#### 종이에 적을 첫 줄

array1=10×4=40바이트라고 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

array1=40, array2=80, array3=40, array4=40바이트예요. 최대는 (2) double array2[10]이에요.

#### 완성 답과 검산

C sizeof 출력에서 40,80,40,40을 독립 확인해요. 현재 타입 크기 전제가 바뀌면 비교도 다시 해야 하므로 모든 C 구현에 8바이트 double을 단정하지 않아요.

#### 이 문제에서 조심할 점

원소 개수만 비교하면 char[40]을 고르게 돼요.

#### 설명을 닫고 다시 해 봐요

1. array1=10×4=40바이트라고 적어요.
2. 개수×타입 크기 → double[10] 80
3. 조건·끝 상태와 검산 근거를 직접 다시 확인해요.

**페이지 요약**

#### 첫 줄

array1=10×4=40바이트라고 적어요.

#### 떠올릴 개념·공식

개수×타입 크기 → double[10] 80

#### 검산

본문의 조건과 독립 추적을 함께 확인해요.

---

<a id="p2"></a>

### P2. 복소수 구조체 더하기

textbook-ch03-q07 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_0928_ArrayStructureList.html#p2)

복소수를 구조체로 표현해보자. 복소수 a와 복소수 b를 받아서 a+b를 계산하는 함수를 작성해보자. 함수는 구조체를 반환할 수 있다. 알다시피 복소수는 real+imag\*i와 같은 형태를 갖는다.

`Complex complex_add(Complex a, Complex b) {
    ...
}`

<details><summary>교과서 원문 보기</summary>

3장 배열, 구조체, 포인터 · 07번 · 책 98쪽

복소수를 구조체로 표현해보자. 복소수 a와 복소수 b를 받아서 a+b를 계산하는 함수를 작성해보자. 함수는 구조체를 반환할 수 있다. 알다시피 복소수는 real+imag\*i와 같은 형태를 갖는다.

`Complex complex_add(Complex a, Complex b) {
    ...
}`

</details>

#### 문제를 내 말로 읽어요

두 복소수 a,b를 받고 합을 Complex 값으로 반환해요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

real+imag×i의 합은 같은 성분끼리 더하는 componentwise addition이에요. C 구조체는 값으로 전달·반환할 수 있어요. 여기서는 멤버 이름을 real,imag로 정의해요.

#### 종이에 적을 첫 줄

`Complex result;`

#### 왜 이렇게 푸는지 함께 따라가요

`typedef struct { float real, imag; } Complex;
Complex complex_add(Complex a, Complex b) {
    Complex result;
    result.real = a.real + b.real;
    result.imag = a.imag + b.imag;
    return result;
}`

#### 완성 답과 검산

a=(1,2),b=(3,4)이면 result=(4,6), 즉 4+6i예요. 실수부와 허수부를 별도로 확인해요. 함수는 복사본을 받으므로 result 계산이 호출자의 a,b를 변경하지 않아요. 부동소수점 일반 입력은 반올림될 수 있어요.

#### 이 문제에서 조심할 점

real과 imag를 섞어 더하거나 지역 result의 주소를 반환하지 않아요.

#### 설명을 닫고 다시 해 봐요

1. Complex result;
2. 같은 성분끼리 합, 구조체 값 반환
3. 조건·끝 상태와 검산 근거를 직접 다시 확인해요.

**페이지 요약**

#### 첫 줄

Complex result;

#### 떠올릴 개념·공식

같은 성분끼리 합, 구조체 값 반환

#### 검산

본문의 조건과 독립 추적을 함께 확인해요.

---

<a id="p3"></a>

### P3. 구조체를 동적으로 만들고 반납

textbook-ch03-q12 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_0928_ArrayStructureList.html#p3)

1개의 정수와 최대 크기가 20인 문자열로 이루어진 구조체를 저장할 수 있도록 동적 메모리를 할당받고 여기에 정수 100과 문자열 “just testing”을 저장한 다음, 동적 메모리를 반납하는 프로그램을 작성하라.

<details><summary>교과서 원문 보기</summary>

3장 배열, 구조체, 포인터 · 12번 · PDF 2쪽

1개의 정수와 최대 크기가 20인 문자열로 이루어진 구조체를 저장할 수 있도록 동적 메모리를 할당받고 여기에 정수 100과 문자열 “just testing”을 저장한 다음, 동적 메모리를 반납하는 프로그램을 작성하라.

</details>

#### 문제를 내 말로 읽어요

구조체 하나를 heap에 만들고 100과 문자열을 저장한 뒤 반납해요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

동적 할당 dynamic allocation은 malloc(sizeof \*p), 실패는 NULL, 멤버 접근은 p-&gt;field, 해제는 free(p)예요. 최대 20문자를 보관하려고 종료 널을 포함한 21칸을 선택해요.

#### 종이에 적을 첫 줄

`struct Item { int number; char text[21]; };`

#### 왜 이렇게 푸는지 함께 따라가요

`#include <stdio.h>
#include <stdlib.h>
#include <string.h>
struct Item { int number; char text[21]; };
int main(void) {
    struct Item *p = malloc(sizeof *p);
    if (p == NULL) return 1;
    p->number = 100;
    strcpy(p->text, "just testing");
    printf("%d %s\n", p->number, p->text);
    free(p);
    return 0;
}`

#### 완성 답과 검산

just testing은 12문자라 종료 널까지 13칸으로 21칸 안에 들어가요. C 출력은 100 just testing이고 성공한 malloc 1회와 free 1회가 짝이에요. 문자열 한계가 널 포함 20칸이라는 해석에서도 이 예시는 20칸에 들어가요.

#### 이 문제에서 조심할 점

sizeof p는 포인터 크기여서 구조체 크기가 아니에요. free 뒤 p-&gt;number를 읽지 않아요.

#### 설명을 닫고 다시 해 봐요

1. struct Item { int number; char text[21]; };
2. malloc(sizeof \*p) → NULL 검사 → 저장 → free
3. 조건·끝 상태와 검산 근거를 직접 다시 확인해요.

**페이지 요약**

#### 첫 줄

struct Item { int number; char text[21]; };

#### 떠올릴 개념·공식

malloc(sizeof \*p) → NULL 검사 → 저장 → free

#### 검산

본문의 조건과 독립 추적을 함께 확인해요.

---

<a id="p4"></a>

### P4. 배열 접근·전체 방문의 복잡도

textbook-ch01-q17 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_0928_ArrayStructureList.html#p4)

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

#### 문제를 내 말로 읽어요

배열 인덱스 접근, 최솟값 찾기, 합의 최선·최악 시간 복잡도를 각각 구해요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

배열은 random access라 주소=시작주소+인덱스×원소크기로 바로 찾아요. 정렬 등 추가 정보가 없는 임의의 배열에서 최솟값과 합은 모든 값을 봐야 해요. n은 여기서 전체 원소 수예요.

#### 종이에 적을 첫 줄

세 행 표에 접근 / 최소 / 합을 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

(1) n번째 원소 출력: 최선·최악 O(1)이에요. 유효 인덱스 접근과 정수 출력의 비용을 상수로 세어요. (2) 최소: 첫 원소를 후보로 놓고 나머지 n−1개를 비교하므로 최선·최악 O(n)이에요. (3) 합: n개를 읽어 누적하므로 최선·최악 O(n)이에요.

#### 완성 답과 검산

아직 읽지 않은 한 값을 더 작게 바꾸면 최소가 바뀌고, 어떤 값도 바꾸면 합이 바뀔 수 있어요. 그러므로 임의 배열에서 생략한 원소가 있는 정확한 알고리즘은 불가능해요. 이미 정렬됨 같은 추가 가정은 원문에 없어요.

#### 이 문제에서 조심할 점

최소가 첫 칸에 있어도 그 사실을 확인하려면 나머지를 읽어야 해요.

#### 설명을 닫고 다시 해 봐요

1. 세 행 표에 접근 / 최소 / 합을 적어요.
2. 접근 O(1), 최소·합 O(n), 최선=최악
3. 조건·끝 상태와 검산 근거를 직접 다시 확인해요.

**페이지 요약**

#### 첫 줄

세 행 표에 접근 / 최소 / 합을 적어요.

#### 떠올릴 개념·공식

접근 O(1), 최소·합 O(n), 최선=최악

#### 검산

본문의 조건과 독립 추적을 함께 확인해요.

---

<a id="p5"></a>

### P5. swap: 주소 전달과 값 전달

lecture-s03-p22-swap · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_0928_ArrayStructureList.html#p5)

**강의 예제 기반 자체 출제** S3 p22

int a=1,b=2;에서 위 함수를 부르는 문장을 쓰고 각 대입 뒤의 (a,b,tmp)를 추적하세요. 매개변수가 int x,int y이고 값만 서로 바꾸는 함수라면 호출자의 a,b가 바뀌는지도 설명하세요.

`void swap(int *px, int *py)
{
    int tmp;
    tmp = *px;
    *px = *py;
    *py = tmp;
}`

<details><summary>강의 예제 보기</summary>

S3 p22 · Software_3_ArrayStructureList.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`void swap(int *px, int *py)
{
    int tmp;
    tmp = *px;
    *px = *py;
    *py = tmp;
}`

</details>

#### 문제를 내 말로 읽어요

int a=1,b=2;에서 위 함수를 부르는 문장을 쓰고 각 대입 뒤의 (a,b,tmp)를 추적하세요. 매개변수가 int x,int y이고 값만 서로 바꾸는 함수라면 호출자의 a,b가 바뀌는지도 설명하세요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “swap: 주소 전달과 값 전달”예요. 주소 연산자 &로 a,b의 위치를 넘겨요. 함수는 주소의 복사본 px,py를 받지만 역참조로 원래 객체에 접근해요. b에 tmp를 대입하면 2,1이 돼요. 값 전달 함수는 별도 지역 변수만 바꾸므로 호출자에게 반영되지 않아요.

#### 종이에 적을 첫 줄

swap(&a,&b); 다음 tmp=\*px에서 tmp=1을 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

1. 주소 연산자 &로 a,b의 위치를 넘겨요. 함수는 주소의 복사본 px,py를 받지만 역참조로 원래 객체에 접근해요.
2. 먼저 a의 값 1을 tmp에 보관해요. a에 b의 값 2를 대입해도 1은 tmp에 남아요.
3. b에 tmp를 대입하면 2,1이 돼요. 값 전달 함수는 별도 지역 변수만 바꾸므로 호출자에게 반영되지 않아요.

swap(&a,&b);. tmp=\*px 뒤 (1,2,1), \*px=\*py 뒤 (2,2,1), \*py=tmp 뒤 (2,1,1). 값 매개변수 x,y만 바꾸면 호출자의 a,b는 1,2 그대로다.

#### 완성 답과 검산

swap(&a,&b);. tmp=\*px 뒤 (1,2,1), \*px=\*py 뒤 (2,2,1), \*py=tmp 뒤 (2,1,1). 값 매개변수 x,y만 바꾸면 호출자의 a,b는 1,2 그대로다.

시작 조건에서 다시 추적한 결과가 위 답과 일치해요. b에 tmp를 대입하면 2,1이 돼요. 값 전달 함수는 별도 지역 변수만 바꾸므로 호출자에게 반영되지 않아요.

#### 이 문제에서 조심할 점

px=py는 주소 변수만 바꿔요. \*px=\*py와 의미가 달라요.

#### 설명을 닫고 다시 해 봐요

1. 주어진 시작 상태와 필요한 입력 조건을 적어요.
2. 첫 줄부터 연산 순서를 따라 답을 완성해요.
3. 경계 경우와 오류 경로를 확인해요.

**페이지 요약**

#### 첫 줄

swap(&a,&b); 다음 tmp=\*px에서 tmp=1을 적어요.

#### 떠올릴 개념·공식

주소 연산자 &로 a,b의 위치를 넘겨요. 함수는 주소의 복사본 px,py를 받지만 역참조로 원래 객체에 접근해요.

#### 검산

swap(&a,&b);. tmp=\*px 뒤 (1,2,1), \*px=\*py 뒤 (2,2,1), \*py=tmp 뒤 (2,1,1). 값 매개변수 x,y만 바꾸면 호출자의 a,b는 1,2 그대로다.

---

<a id="p6"></a>

### P6. 동적 구조체 배열의 두 원소

lecture-s03-p31-malloc-record · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_0928_ArrayStructureList.html#p6)

**강의 예제 기반 자체 출제** S3 p31

할당이 성공했다고 가정해요. 두 원소의 필드 값을 쓰고 p+1의 바이트 이동량을 sizeof로 표현하세요. 필요한 표준 헤더, free에 넘길 주소, free 뒤 p-&gt;number를 읽어도 되는지 설명하세요.

`struct Example { int number; char name[10]; };
struct Example *p;
p = (struct Example *)malloc(2*sizeof(struct Example));
if(p==NULL) { fprintf(stderr,"can't allocate memory\n"); exit(1); }
p->number=1;
strcpy(p->name,"Park");
(p+1)->number=2;
strcpy((p+1)->name,"Kim");
free(p);`

<details><summary>강의 예제 보기</summary>

S3 p31 · Software_3_ArrayStructureList.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`struct Example { int number; char name[10]; };
struct Example *p;
p = (struct Example *)malloc(2*sizeof(struct Example));
if(p==NULL) { fprintf(stderr,"can't allocate memory\n"); exit(1); }
p->number=1;
strcpy(p->name,"Park");
(p+1)->number=2;
strcpy((p+1)->name,"Kim");
free(p);`

</details>

#### 문제를 내 말로 읽어요

할당이 성공했다고 가정해요. 두 원소의 필드 값을 쓰고 p+1의 바이트 이동량을 sizeof로 표현하세요. 필요한 표준 헤더, free에 넘길 주소, free 뒤 p-&gt;number를 읽어도 되는지 설명하세요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “동적 구조체 배열의 두 원소”예요. malloc의 크기는 구조체 2개 분량이에요. sizeof에는 패딩도 포함되므로 필드 크기 합으로 바꾸지 않아요. free 뒤 포인터 변수 자체가 자동 NULL이 되지는 않아요. 해제된 저장 공간을 읽으면 미정의 동작이므로 정상 출력값을 구하지 않아요.

#### 종이에 적을 첫 줄

할당 크기=2\*sizeof(struct Example)와 p[0],p[1] 두 칸을 그려요.

#### 왜 이렇게 푸는지 함께 따라가요

1. malloc의 크기는 구조체 2개 분량이에요. sizeof에는 패딩도 포함되므로 필드 크기 합으로 바꾸지 않아요.
2. p-&gt;는 첫 원소, (p+1)-&gt;는 두 번째 원소의 필드에 접근해요. 포인터 덧셈은 바이트가 아닌 원소 단위예요.
3. malloc/free/exit는 stdlib.h, fprintf/stderr는 stdio.h, strcpy는 string.h가 선언해요.
4. free 뒤 포인터 변수 자체가 자동 NULL이 되지는 않아요. 해제된 저장 공간을 읽으면 미정의 동작이므로 정상 출력값을 구하지 않아요.

p[0]={1,"Park"}, p[1]={2,"Kim"}. p+1은 sizeof(struct Example)바이트 뒤. stdlib.h,stdio.h,string.h. free(p)로 최초 할당 주소를 넘기고 해제 뒤 역참조하면 안 된다.

#### 완성 답과 검산

p[0]={1,"Park"}, p[1]={2,"Kim"}. p+1은 sizeof(struct Example)바이트 뒤. stdlib.h,stdio.h,string.h. free(p)로 최초 할당 주소를 넘기고 해제 뒤 역참조하면 안 된다.

시작 조건에서 다시 추적한 결과가 위 답과 일치해요. free 뒤 포인터 변수 자체가 자동 NULL이 되지는 않아요. 해제된 저장 공간을 읽으면 미정의 동작이므로 정상 출력값을 구하지 않아요.

#### 이 문제에서 조심할 점

free(p+1)은 최초 할당 주소가 아니므로 사용할 수 없어요. 구조체 크기를 14바이트로 단정하지 마세요.

#### 설명을 닫고 다시 해 봐요

1. 주어진 시작 상태와 필요한 입력 조건을 적어요.
2. 첫 줄부터 연산 순서를 따라 답을 완성해요.
3. 경계 경우와 오류 경로를 확인해요.

**페이지 요약**

#### 첫 줄

할당 크기=2\*sizeof(struct Example)와 p[0],p[1] 두 칸을 그려요.

#### 떠올릴 개념·공식

malloc의 크기는 구조체 2개 분량이에요. sizeof에는 패딩도 포함되므로 필드 크기 합으로 바꾸지 않아요.

#### 검산

p[0]={1,"Park"}, p[1]={2,"Kim"}. p+1은 sizeof(struct Example)바이트 뒤. stdlib.h,stdio.h,string.h. free(p)로 최초 할당 주소를 넘기고 해제 뒤 역참조하면 안 된다.

---

원 문제·정리노트·PDF는 보존해요.
