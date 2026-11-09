/* S8 p10·p13 의사코드를 C11 로 옮긴 실행 harness (자체 번역; main·출력 함수는 추가) */
#include <stdio.h>
#define MAX_ELEMENT 200
typedef struct { int key; } element;
typedef struct { element heap[MAX_ELEMENT]; int heap_size; } HeapType;
static int PARENT(int i) { return i / 2; }
static int CHILD(int i) { return i * 2; }
static void swap(HeapType *h, int a, int b) { element t = h->heap[a]; h->heap[a] = h->heap[b]; h->heap[b] = t; }
static void insert_max_heap(HeapType *h, int key) {
    h->heap_size = h->heap_size + 1;
    int i = h->heap_size;
    h->heap[i].key = key;
    while (i != 1 && h->heap[i].key > h->heap[PARENT(i)].key) { swap(h, i, PARENT(i)); i = PARENT(i); }
}
/* literal=1 이면 슬라이드 조건 그대로, 0 이면 오른쪽 자식이 없을 때 왼쪽을 고르게 보정 */
static int delete_max_heap(HeapType *h, int literal) {
    int item = h->heap[1].key;
    h->heap[1] = h->heap[h->heap_size];
    h->heap_size = h->heap_size - 1;
    int i = 2, largest;
    while (i <= h->heap_size) {
        if (literal) largest = (i < h->heap_size && h->heap[i].key > h->heap[i + 1].key) ? i : i + 1;
        else largest = (i < h->heap_size && h->heap[i + 1].key > h->heap[i].key) ? i + 1 : i;
        printf("  i=%d largest=%d\n", i, largest);
        if (h->heap[PARENT(largest)].key > h->heap[largest].key) break;
        swap(h, PARENT(largest), largest);
        i = CHILD(largest);
    }
    return item;
}
static void show(const char *tag, HeapType *h) {
    printf("%s [", tag);
    for (int k = 1; k <= h->heap_size; k++) printf("%d%s", h->heap[k].key, k < h->heap_size ? ", " : "");
    printf("]\n");
}
static void load(HeapType *h, const int *v, int n) { h->heap_size = n; for (int k = 0; k < n; k++) h->heap[k + 1].key = v[k]; }
int main(void) {
    HeapType h = {0};
    int ins[] = {1, 23, 7, 8, 20};
    for (int k = 0; k < 5; k++) insert_max_heap(&h, ins[k]);
    show("board build", &h);
    int s1[] = {9, 7, 6, 5, 4, 3, 2, 2, 1, 3};
    load(&h, s1, 10); printf("p11a item=%d\n", delete_max_heap(&h, 1)); show("p11a", &h);
    int s2[] = {50, 40, 30, 20, 10};
    load(&h, s2, 5); printf("p11b literal item=%d\n", delete_max_heap(&h, 1)); show("p11b literal", &h);
    load(&h, s2, 5); printf("p11b fixed item=%d\n", delete_max_heap(&h, 0)); show("p11b fixed", &h);
    return 0;
}
