/* p6 독립 검산: 문제의 코드를 그대로 옮김.
 * 덧붙인 것: #include <stdio.h>, #include <string.h>(main 의 독성 채우기용),
 *            #define MAX_ELEMENT 200, typedef 를 앞으로 이동,
 *            함수 원형 3줄(원문은 heap_sort 가 init·insert·delete 정의보다 앞에 있어
 *            C99 이후 암시적 선언 오류가 난다), 상태 출력용 main.
 * heap_sort 본문·init·insert_max_heap·delete_max_heap 은 원문 그대로다. */
#include <stdio.h>
#include <string.h>
#define MAX_ELEMENT 200

typedef struct {
    int key;
} element;
typedef struct{
    element heap[MAX_ELEMENT];
    int heap_size;
} HeapType;

void init(HeapType *h);
void insert_max_heap(HeapType *h, element item);
element delete_max_heap(HeapType *h);

// 우선순위 큐인 히프를 이용한 정렬
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

/* 이 문제를 위해 쓴 자체 코드: 삽입(upheap), 삭제(downheap) */
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
        if ((child < h->heap_size) &&
            (h->heap[child].key < h->heap[child + 1].key)) child++;
        if (temp.key >= h->heap[child].key) break;
        h->heap[parent] = h->heap[child];
        parent = child; child *= 2;
    }
    h->heap[parent] = temp;
    return item;
}

/* ---------------- 덧붙인 main ---------------- */
static void print_heap(const HeapType *h)
{
    printf("[");
    for (int k = 1; k <= h->heap_size; k++)
        printf("%s%d", k > 1 ? ", " : "", h->heap[k].key);
    printf("]");
}

int main(void)
{
    const int keys[5] = {1, 23, 7, 8, 20};
    const int n = 5;
    const int POISON = (int)0xABABABAB;

    /* 1) 원문 heap_sort 그대로 호출 → 최종 a[] */
    element a[5];
    for (int k = 0; k < n; k++) a[k].key = keys[k];
    heap_sort(a, n);
    printf("heap_sort(a,5) 최종 a[] = [");
    for (int k = 0; k < n; k++) printf("%s%d", k ? ", " : "", a[k].key);
    printf("]\n");

    /* 2) 같은 두 루프를 main 에서 되풀이하며 상태 출력.
     *    h 를 독성 값으로 채워, 초기화 안 된 칸을 읽어 결과에 섞이면 드러나게 한다. */
    element b[5];
    for (int k = 0; k < n; k++) b[k].key = keys[k];
    HeapType h;
    memset(&h, 0xAB, sizeof h);
    init(&h);
    for (int i = 0; i < n; i++) {
        insert_max_heap(&h, b[i]);
        printf("insert %2d → heap[1..%d] = ", b[i].key, h.heap_size);
        print_heap(&h);
        printf("\n");
    }
    printf("(a) 첫 루프 직후 heap[1..5] = ");
    print_heap(&h);
    printf("\n");
    printf("    (참고) heap[0].key = 0x%X (독성 그대로 = 0번 칸 미사용 확인)\n",
           (unsigned)h.heap[0].key);

    int poison_seen = 0;
    printf("(b) 두 번째 루프\n");
    for (int i = n - 1; i >= 0; i--) {
        b[i] = delete_max_heap(&h);
        if (b[i].key == POISON) poison_seen = 1;
        for (int k = 1; k <= h.heap_size; k++)
            if (h.heap[k].key == POISON) poison_seen = 1;
        printf("    i=%d  a[%d]=%2d  남은 heap[1..%d] = ", i, i, b[i].key, h.heap_size);
        print_heap(&h);
        printf("\n");
    }
    printf("    최종 a[] = [");
    for (int k = 0; k < n; k++) printf("%s%d", k ? ", " : "", b[k].key);
    printf("]\n");

    int same = 1;
    for (int k = 0; k < n; k++) if (a[k].key != b[k].key) same = 0;
    printf("원문 heap_sort 결과와 계측 루프 결과 일치: %s\n", same ? "예" : "아니오");
    printf("독성 값이 결과·남은 힙에 나타남: %s\n", poison_seen ? "예(초기화 안 된 칸 읽음)" : "아니오");
    return 0;
}
