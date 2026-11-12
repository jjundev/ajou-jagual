/* S8 p15 heap_sort 그대로 + 교과서식 insert/delete_max_heap (S8 p10/p13 의사코드의 C 판, 오른쪽 자식 없을 때 왼쪽) */
#include <stdio.h>
#define MAX_ELEMENT 200
typedef struct { int key; } element;
typedef struct { element heap[MAX_ELEMENT]; int heap_size; } HeapType;
void init(HeapType *h) { h->heap_size = 0; }
static void show(const char *tag, HeapType *h) {
  printf("%s [", tag);
  for (int k = 1; k <= h->heap_size; k++) printf("%s%d", k > 1 ? " " : "", h->heap[k].key);
  printf("]\n");
}
void insert_max_heap(HeapType *h, element item) {
  int i = ++(h->heap_size);
  while ((i != 1) && (item.key > h->heap[i / 2].key)) { h->heap[i] = h->heap[i / 2]; i /= 2; }
  h->heap[i] = item;
}
element delete_max_heap(HeapType *h) {
  int parent = 1, child = 2;
  element item = h->heap[1], temp = h->heap[(h->heap_size)--];
  while (child <= h->heap_size) {
    if ((child < h->heap_size) && (h->heap[child].key < h->heap[child + 1].key)) child++;
    if (temp.key >= h->heap[child].key) break;
    h->heap[parent] = h->heap[child]; parent = child; child *= 2;
  }
  h->heap[parent] = temp;
  return item;
}
void heap_sort(element a[], int n) {
  int i; HeapType h; init(&h);
  for (i = 0; i < n; i++) { insert_max_heap(&h, a[i]); show("insert", &h); }
  for (i = (n - 1); i >= 0; i--) {
    a[i] = delete_max_heap(&h);
    printf("i=%d a[i]=%d ", i, a[i].key); show("heap", &h);
  }
}
int main(void) {
  element a[] = {{1}, {23}, {7}, {8}, {20}};
  heap_sort(a, 5);
  for (int i = 0; i < 5; i++) printf("%d ", a[i].key);
  printf("\n");
  return 0;
}
