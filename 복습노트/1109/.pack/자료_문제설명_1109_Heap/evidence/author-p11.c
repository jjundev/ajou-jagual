/* P11 독립 C11 번역 (저작자 작성). 슬라이드 S8 p13 delete_max_heap 를 글자 그대로(mode 0)와
   고친 조건(mode 1)으로 옮겼다. 배열은 200칸이며 접근 인덱스를 매번 범위 검사한다. */
#include <stdio.h>
#include <assert.h>
#define MAX_ELEMENT 200
static int A[MAX_ELEMENT];
static int heap_size;

static int at(int k) { assert(0 <= k && k < MAX_ELEMENT); return A[k]; }
static void exch(int x, int y) { assert(0 <= x && x < MAX_ELEMENT && 0 <= y && y < MAX_ELEMENT);
    int t = A[x]; A[x] = A[y]; A[y] = t; }

static int delete_max_heap(int fixed) {
    int item = at(1);
    A[1] = at(heap_size);
    heap_size = heap_size - 1;
    int i = 2, largest;
    while (i <= heap_size) {
        if (!fixed) { if (i < heap_size && at(i) > at(i + 1)) largest = i; else largest = i + 1; }
        else        { if (i < heap_size && at(i + 1) > at(i)) largest = i + 1; else largest = i; }
        if (at(largest / 2) > at(largest)) { printf("  (i=%d, largest=%d, break)\n", i, largest); break; }
        exch(largest / 2, largest);
        printf("  (i=%d, largest=%d, swap) A[%d] value moved up=%d%s\n", i, largest, largest, at(largest / 2),
               largest > heap_size ? " [outside heap]" : "");
        i = largest * 2;
    }
    return item;
}
static void run(const char *tag, const int *v, int n, int fixed) {
    for (int k = 0; k < MAX_ELEMENT; k++) A[k] = 0;
    for (int k = 0; k < n; k++) A[k + 1] = v[k];
    heap_size = n;
    printf("%s\n", tag);
    int item = delete_max_heap(fixed);
    printf("  item=%d A[1..%d]=", item, heap_size);
    int ok = 1;
    for (int k = 1; k <= heap_size; k++) { printf("%d ", A[k]); if (k > 1 && A[k / 2] < A[k]) ok = 0; }
    printf("max-heap=%s\n", ok ? "yes" : "no");
}
int main(void) {
    const int a[] = {9, 7, 6, 5, 4, 3, 2, 2, 1, 3};
    const int b[] = {50, 40, 30, 20, 10};
    run("(a) literal", a, 10, 0);
    run("(b) literal", b, 5, 0);
    run("(b) fixed", b, 5, 1);
    return 0;
}
